import os
import json
import bisect
import copy
import numpy as np

from PyQt5 import QtCore

from constant import *
from util import *
from read_data import load_data
from read_map import load_map


# constants
TIME_SIMULATION = 30
PERIODS = [0, 50, 100, 150, 200]
PIXEL_SIZE = 4
USING_TIMESERIES = False
lctype = [
    set,
    for_pion, for_ysec, for_osec, for_prim,
    agr1, agr2, agr3, agr4,
    af1_pion, af1_eprod, af1_lprod, af1_pprod,
    af2_pion, af2_eprod, af2_lprod, af2_pprod,
    af3_pion, af3_eprod, af3_lprod, af3_pprod,
    af4_pion, af4_eprod, af4_lprod, af4_pprod,
    af5_pion, af5_eprod, af5_lprod, af5_pprod,
    af6_pion, af6_eprod, af6_lprod, af6_pprod,
    af7_pion, af7_eprod, af7_lprod, af7_pprod,
    af8_pion, af8_eprod, af8_lprod, af8_pprod,
] = np.arange(41)

livelihood = [offfarm, ntfp, timber, food1, food2, food3, food4, af1, af2, af3, af4, af5, af6, af7, af8] = np.arange(15)

lutype = [SET, FOR, AGR1, AGR2, AGR3, AGR4, AF1, AF2, AF3, AF4, AF5, AF6, AF7, AF8] = np.arange(14)

sctype = [
    sc1, sc2, sc3, sc4, sc5,
    sc6, sc7, sc8, sc9, sc10,
    sc11, sc12, sc13, sc14, sc15,
    sc16, sc17, sc18, sc19, sc20,
    sc21, sc22, sc23, sc24, sc25
] = np.arange(25)

LU2LC = [
    [set],
    [for_pion, for_ysec, for_osec, for_prim],
    [agr1],
    [agr2],
    [agr3],
    [agr4],
    [af1_pion, af1_eprod, af1_lprod, af1_pprod],
    [af2_pion, af2_eprod, af2_lprod, af2_pprod],
    [af3_pion, af3_eprod, af3_lprod, af3_pprod],
    [af4_pion, af4_eprod, af4_lprod, af4_pprod],
    [af5_pion, af5_eprod, af5_lprod, af5_pprod],
    [af6_pion, af6_eprod, af6_lprod, af6_pprod],
    [af7_pion, af7_eprod, af7_lprod, af7_pprod],
    [af8_pion, af8_eprod, af8_lprod, af8_pprod]
]

NEW_PLOTS = [food1, food2, food3, food4, af1, af2, af3, af4, af5, af6, af7, af8]

LIVELIHOOD2LC = [
    [set],
    [],
    [for_pion, for_ysec, for_osec, for_prim],
    [agr1],
    [agr2],
    [agr3],
    [agr4],
    [af1_pion, af1_eprod, af1_lprod, af1_pprod],
    [af2_pion, af2_eprod, af2_lprod, af2_pprod],
    [af3_pion, af3_eprod, af3_lprod, af3_pprod],
    [af4_pion, af4_eprod, af4_lprod, af4_pprod],
    [af5_pion, af5_eprod, af5_lprod, af5_pprod],
    [af6_pion, af6_eprod, af6_lprod, af6_pprod],
    [af7_pion, af7_eprod, af7_lprod, af7_pprod],
    [af8_pion, af8_eprod, af8_lprod, af8_pprod]
]

LC2CRITICALZONE = [for_pion, for_ysec, for_osec, for_prim, af1_pprod, af2_pprod, af3_pprod, af4_pprod, af5_pprod, af6_pprod, af7_pprod, af8_pprod]

lcproperties = [agb, floorbiomassfrac, pfirespread] = np.arange(3)
agentproperties = [popfraction, alpha_learning, beta_learning, prioritization] = np.arange(4)
demographicalproperties = [initpop, annualgrowthrate, laborfraction, workingdays, initfinance, secconsumptionfrac] = np.arange(6)
[agent1, agent2] = [0, 1]

def stat(mean, cv):
    return mean * (1 + np.random.normal(size=mean.shape) * cv)


def normal(mean, cv, array):
    return mean * (1 + np.random.normal(0, 1, array.shape) * cv)

def single_stat(mean, cv):
    return mean * (1 + cv * np.random.normal())

def make_file_path(folder, filename):
    return os.path.join(folder, filename)


class SimulatingThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(dict, int, name='update')

    def __init__(self, prj, time_simulation=30, pixel_size=4):
        super(SimulatingThread, self).__init__()
        self.prj = prj
        print(self.prj)
        self.data_file = os.path.join(prj, 'data.xlsx')
        self.map_file = os.path.join(prj, 'maps.json')
        self.time_simulation = time_simulation
        self.pixel_size = pixel_size
        self.output = os.path.join(prj, 'output')

    def run(self):
        # Load maps and data
        input_map = load_map(self.map_file)
        input_data = load_data(self.data_file)

        # Initialization

        rotation = input_data['rotation']
        allow_change = input_data['allow_change']
        landcover_age_boundary = input_data['landcover_age_boundary']
        initial_landcover_age_mean = input_data['initial_landcover_age_mean']
        initial_landcover_age_cv = input_data['initial_landcover_age_cv']
        depletion_rate_mean = input_data['depletion_rate_mean']
        depletion_rate_cv = input_data['depletion_rate_cv']
        halftime_recovery_mean = input_data['halftime_recovery_mean']
        halftime_recovery_cv = input_data['halftime_recovery_cv']
        aboveground_biomass_mean = input_data['aboveground_biomass_mean']
        aboveground_biomass_cv = input_data['aboveground_biomass_cv']
        floor_biomass_fraction_mean = input_data['floor_biomass_fraction_mean']
        floor_biomass_fraction_cv = input_data['floor_biomass_fraction_cv']
        land_yield_mean = input_data['land_yield_mean']
        land_yield_cv = input_data['land_yield_cv']
        probably_of_fire_mean = input_data['probably_of_fire_mean']
        probably_of_fire_cv = input_data['probably_of_fire_cv']
        harvesting_production_mean = input_data['harvesting_production_mean']
        harvesting_production_cv = input_data['harvesting_production_cv']
        demand_per_capital = input_data['demand_per_capital']
        probably_to_sell = input_data['probably_to_sell']
        soil_fertility = input_data['soil_fertility']
        land_productivity = input_data['land_productivity']
        land_suitability = input_data['land_suitability']
        transportation_access = input_data['transportation_access']
        plot_maintainance = input_data['plot_maintainance']
        slope = input_data['slope']
        floor_biomass = input_data['floor_biomass']
        loss_fraction = input_data['loss_fraction']
        price_mean = input_data['price_mean']
        price_cv = input_data['price_cv']
        return_to_land_farmer_1 = input_data['return_to_land_farmer_1']
        return_to_land_farmer_2 = input_data['return_to_land_farmer_2']
        init_return_to_land = input_data['init_return_to_land']
        return_to_labour_farmer_1 = input_data['return_to_labour_farmer_1']
        return_to_labour_farmer_2 = input_data['return_to_labour_farmer_2']
        init_return_to_labour = input_data['init_return_to_labour']
        expect_return_to_land = input_data['expect_return_to_land']
        expect_return_to_labour = input_data['expect_return_to_labour']
        establishment_cost_mean = input_data['establishment_cost_mean']
        establishment_cost_cv = input_data['establishment_cost_cv']
        establishment_labour_mean = input_data['establishment_labour_mean']
        establishment_labour_cv = input_data['establishment_labour_cv']
        external_labour_mean = input_data['external_labour_mean']
        external_labour_cv = input_data['external_labour_cv']
        subsidy_mean = input_data['subsidy_mean']
        subsidy_cv = input_data['subsidy_cv']
        non_labour_cost_mean = input_data['non_labour_cost_mean']
        non_labour_cost_cv = input_data['non_labour_cost_cv']
        cultural_influence = input_data['cultural_influence']
        availability = input_data['availability']
        credibility = input_data['credibility']
        demography = input_data['demography']
        farmer_prop_1 = input_data['farmer_prop_1']
        farmer_prop_2 = input_data['farmer_prop_2']
        agentprop = input_data['agentprop']
        impact_of_disaster = input_data['impact_of_disaster']
        time_of_disaster = input_data['time_of_disaster']
        conversion = input_data['conversion']
        subsidy_est = input_data['subsidy_est']
        subsidy_mnt = input_data['subsidy_mnt']
        ex = input_data['ex']
        sub = input_data['sub']
        price_ = input_data['price_']
        explabor = input_data['explabor']
        expland = input_data['expland']

        totpop = demography[initpop]
        totfinance = demography[initfinance]
        store = totpop * demand_per_capital

        simulated_area = input_map['simulated_area']
        prototype = input_map['prototype']
        initial_landcover_area = input_map['initial_landcover_area']
        subcatchment_area = input_map['subcatchment_area']
        initlog = input_map['initlog']
        initial_logging_area = input_map['initial_logging_area']
        initial_soil_fertility_area = input_map['initial_soil_fertility_area']
        maximul_soil_fertility_area = input_map['maximul_soil_fertility_area']

        slope_area = input_map['slope_area']
        suitfood1 = input_map['suitfood1']
        suitfood2 = input_map['suitfood2']
        suitfood3 = input_map['suitfood3']
        suitfood4 = input_map['suitfood4']
        suitaf1 = input_map['suitaf1']
        suitaf2 = input_map['suitaf2']
        suitaf3 = input_map['suitaf3']
        suitaf4 = input_map['suitaf4']
        suitaf5 = input_map['suitaf5']
        suitaf6 = input_map['suitaf6']
        suitaf7 = input_map['suitaf7']
        suitaf8 = input_map['suitaf8']
        droad1 = input_map['droad1']
        droad2 = input_map['droad2']
        droad3 = input_map['droad3']
        droad4 = input_map['droad4']
        dmart1 = input_map['dmart1']
        dmart2 = input_map['dmart2']
        dmart3 = input_map['dmart3']
        dmart4 = input_map['dmart4']
        driver1 = input_map['driver1']
        driver2 = input_map['driver2']
        driver3 = input_map['driver3']
        driver4 = input_map['driver4']
        dfactory_ntfp1 = input_map['dfactory_ntfp1']
        dfactory_ntfp2 = input_map['dfactory_ntfp2']
        dfactory_ntfp3 = input_map['dfactory_ntfp3']
        dfactory_ntfp4 = input_map['dfactory_ntfp4']
        dfactory_timber1 = input_map['dfactory_timber1']
        dfactory_timber2 = input_map['dfactory_timber2']
        dfactory_timber3 = input_map['dfactory_timber3']
        dfactory_timber4 = input_map['dfactory_timber4']
        dfactory_food1_1 = input_map['dfactory_food1_1']
        dfactory_food1_2 = input_map['dfactory_food1_2']
        dfactory_food1_3 = input_map['dfactory_food1_3']
        dfactory_food1_4 = input_map['dfactory_food1_4']
        dfactory_food2_1 = input_map['dfactory_food2_1']
        dfactory_food2_2 = input_map['dfactory_food2_2']
        dfactory_food2_3 = input_map['dfactory_food2_3']
        dfactory_food2_4 = input_map['dfactory_food2_4']
        dfactory_food3_1 = input_map['dfactory_food3_1']
        dfactory_food3_2 = input_map['dfactory_food3_2']
        dfactory_food3_3 = input_map['dfactory_food3_3']
        dfactory_food3_4 = input_map['dfactory_food3_4']
        dfactory_food4_1 = input_map['dfactory_food4_1']
        dfactory_food4_2 = input_map['dfactory_food4_2']
        dfactory_food4_3 = input_map['dfactory_food4_3']
        dfactory_food4_4 = input_map['dfactory_food4_4']
        dfactory_af1_2 = input_map['dfactory_af1_2']
        dfactory_af1_3 = input_map['dfactory_af1_3']
        dfactory_af1_4 = input_map['dfactory_af1_4']
        dfactory_af1_1 = input_map['dfactory_af1_1']
        dfactory_af2_1 = input_map['dfactory_af2_1']
        dfactory_af2_2 = input_map['dfactory_af2_2']
        dfactory_af2_3 = input_map['dfactory_af2_3']
        dfactory_af2_4 = input_map['dfactory_af2_4']
        dfactory_af3_1 = input_map['dfactory_af3_1']
        dfactory_af3_2 = input_map['dfactory_af3_2']
        dfactory_af3_3 = input_map['dfactory_af3_3']
        dfactory_af3_4 = input_map['dfactory_af3_4']
        dfactory_af4_1 = input_map['dfactory_af4_1']
        dfactory_af4_2 = input_map['dfactory_af4_2']
        dfactory_af4_3 = input_map['dfactory_af4_3']
        dfactory_af4_4 = input_map['dfactory_af4_4']
        dfactory_af5_1 = input_map['dfactory_af5_1']
        dfactory_af5_2 = input_map['dfactory_af5_2']
        dfactory_af5_3 = input_map['dfactory_af5_3']
        dfactory_af5_4 = input_map['dfactory_af5_4']
        dfactory_af6_1 = input_map['dfactory_af6_1']
        dfactory_af6_2 = input_map['dfactory_af6_2']
        dfactory_af6_3 = input_map['dfactory_af6_3']
        dfactory_af6_4 = input_map['dfactory_af6_4']
        dfactory_af7_1 = input_map['dfactory_af7_1']
        dfactory_af7_2 = input_map['dfactory_af7_2']
        dfactory_af7_3 = input_map['dfactory_af7_3']
        dfactory_af7_4 = input_map['dfactory_af7_4']
        dfactory_af8_1 = input_map['dfactory_af8_1']
        dfactory_af8_2 = input_map['dfactory_af8_2']
        dfactory_af8_3 = input_map['dfactory_af8_3']
        dfactory_af8_4 = input_map['dfactory_af8_4']
        dset1 = input_map['dset1']
        dset2 = input_map['dset2']
        dset3 = input_map['dset3']
        dset4 = input_map['dset4']
        protected_area = input_map['protected_area']
        disastered_area = input_map['disastered_area']

        zslope = standardize(slope_area)
        zroad1 = standardize(droad1)
        zroad2 = standardize(droad2)
        zroad3 = standardize(droad3)
        zroad4 = standardize(droad4)

        zriver1 = standardize(driver1)
        zriver2 = standardize(driver2)
        zriver3 = standardize(driver3)
        zriver4 = standardize(driver4)

        zmart1 = standardize(dmart1)
        zmart2 = standardize(dmart2)
        zmart3 = standardize(dmart3)
        zmart4 = standardize(dmart4)

        ztimb1 = standardize(dfactory_timber1)
        ztimb2 = standardize(dfactory_timber2)
        ztimb3 = standardize(dfactory_timber3)
        ztimb4 = standardize(dfactory_timber4)

        zntfp1 = standardize(dfactory_ntfp1)
        zntfp2 = standardize(dfactory_ntfp2)
        zntfp3 = standardize(dfactory_ntfp3)
        zntfp4 = standardize(dfactory_ntfp4)

        zfd1_1 = standardize(dfactory_food1_1)
        zfd1_2 = standardize(dfactory_food1_2)
        zfd1_3 = standardize(dfactory_food1_3)
        zfd1_4 = standardize(dfactory_food1_4)

        zfd2_1 = standardize(dfactory_food2_1)
        zfd2_2 = standardize(dfactory_food2_2)
        zfd2_3 = standardize(dfactory_food2_3)
        zfd2_4 = standardize(dfactory_food2_4)

        zfd3_1 = standardize(dfactory_food3_1)
        zfd3_2 = standardize(dfactory_food3_2)
        zfd3_3 = standardize(dfactory_food3_3)
        zfd3_4 = standardize(dfactory_food3_4)

        zfd4_1 = standardize(dfactory_food4_1)
        zfd4_2 = standardize(dfactory_food4_2)
        zfd4_3 = standardize(dfactory_food4_3)
        zfd4_4 = standardize(dfactory_food4_4)

        zaf1_1 = standardize(dfactory_af1_1)
        zaf1_2 = standardize(dfactory_af1_2)
        zaf1_3 = standardize(dfactory_af1_3)
        zaf1_4 = standardize(dfactory_af1_4)

        zaf2_1 = standardize(dfactory_af2_1)
        zaf2_2 = standardize(dfactory_af2_2)
        zaf2_3 = standardize(dfactory_af2_3)
        zaf2_4 = standardize(dfactory_af2_4)

        zaf3_1 = standardize(dfactory_af3_1)
        zaf3_2 = standardize(dfactory_af3_2)
        zaf3_3 = standardize(dfactory_af3_3)
        zaf3_4 = standardize(dfactory_af3_4)

        zaf4_1 = standardize(dfactory_af4_1)
        zaf4_2 = standardize(dfactory_af4_2)
        zaf4_3 = standardize(dfactory_af4_3)
        zaf4_4 = standardize(dfactory_af4_4)

        zaf5_1 = standardize(dfactory_af5_1)
        zaf5_2 = standardize(dfactory_af5_2)
        zaf5_3 = standardize(dfactory_af5_3)
        zaf5_4 = standardize(dfactory_af5_4)

        zaf6_1 = standardize(dfactory_af6_1)
        zaf6_2 = standardize(dfactory_af6_2)
        zaf6_3 = standardize(dfactory_af6_3)
        zaf6_4 = standardize(dfactory_af6_4)

        zaf7_1 = standardize(dfactory_af7_1)
        zaf7_2 = standardize(dfactory_af7_2)
        zaf7_3 = standardize(dfactory_af7_3)
        zaf7_4 = standardize(dfactory_af7_4)

        zaf8_1 = standardize(dfactory_af8_1)
        zaf8_2 = standardize(dfactory_af8_2)
        zaf8_3 = standardize(dfactory_af8_3)
        zaf8_4 = standardize(dfactory_af8_4)

        zset1 = standardize(dset1)
        zset2 = standardize(dset2)
        zset3 = standardize(dset3)
        zset4 = standardize(dset4)

        exppayofftoland = np.copy(init_return_to_land)
        exppayofftolabor = np.copy(init_return_to_labour)

        non_protected_area = protected_area != 1
        soil_fert = np.copy(initial_soil_fertility_area)


        agbiomass = 0.0 * initial_landcover_area
        floorbiomassfraction = 0.0 * initial_landcover_area
        pfireuse = [0 for i in livelihood]

        allnewplots = simulated_area != 1
        sumscrit = simulated_area.copy()
        logzone = initlog.copy()
        ntfpzone = simulated_area != 1
        marginalagriculture = simulated_area != 1
        marginalAF = simulated_area != 1
        newplot = list(range(15))

        for i in livelihood:
            newplot[i] = 0.0 * initial_landcover_area

        landuse = initial_landcover_area * 0.0
        for i in lutype:
            for j in LU2LC[i]:
                landuse += (initial_landcover_area == j) * i

        lcage = initial_landcover_area * 0.0
        for i in lctype:
            lcage += np.maximum(
                0,
                normal(
                    initial_landcover_age_mean[i],
                    initial_landcover_age_cv[i],
                    simulated_area
                )
            ) * (initial_landcover_area == i)
        output_timeseries = dict()
        # Simulation
        for time in range(self.time_simulation):
            balance = totfinance
            totbuying = 0
            totselling = 0
            disasterimpactonhuman = impact_of_disaster[0] if time == time_of_disaster else 0
            disasterimpactonmoney = impact_of_disaster[1] if time == time_of_disaster else 0
            disasterimpactonworkingday = impact_of_disaster[2] if time == time_of_disaster else 0
            disasterimpactedzone = disastered_area.copy() if time == time_of_disaster else 0 * simulated_area

            currentPeriod = bisect.bisect(PERIODS, time)
            zroad = [zroad1, zroad2, zroad3, zroad4][currentPeriod]
            zmart = [zmart1, zmart2, zmart3, zmart4][currentPeriod]
            zriver = [zriver1, zriver2, zriver3, zriver4][currentPeriod]
            zntfp = [zntfp1, zntfp2, zntfp3, zntfp4][currentPeriod]
            ztimb = [ztimb1, ztimb2, ztimb3, ztimb4][currentPeriod]
            zfd1 = [zfd1_1, zfd1_2, zfd1_3, zfd1_4][currentPeriod]
            zfd2 = [zfd2_1, zfd2_2, zfd2_3, zfd2_4][currentPeriod]
            zfd3 = [zfd3_1, zfd3_2, zfd3_3, zfd3_4][currentPeriod]
            zfd4 = [zfd4_1, zfd4_2, zfd4_3, zfd4_4][currentPeriod]
            zaf1 = [zaf1_1, zaf1_2, zaf1_3, zaf1_4][currentPeriod]
            zaf2 = [zaf2_1, zaf2_2, zaf2_3, zaf2_4][currentPeriod]
            zaf3 = [zaf3_1, zaf3_2, zaf3_3, zaf3_4][currentPeriod]
            zaf4 = [zaf4_1, zaf4_2, zaf4_3, zaf4_4][currentPeriod]
            zaf5 = [zaf5_1, zaf5_2, zaf5_3, zaf5_4][currentPeriod]
            zaf6 = [zaf6_1, zaf6_2, zaf6_3, zaf6_4][currentPeriod]
            zaf7 = [zaf7_1, zaf7_2, zaf7_3, zaf7_4][currentPeriod]
            zaf8 = [zaf8_1, zaf8_2, zaf8_3, zaf8_4][currentPeriod]
            dset = [dset1, dset2, dset3, dset4][currentPeriod]
            zset = [zset1, zset2, zset3, zset4][currentPeriod]

            price = price_[time] if USING_TIMESERIES else stat(price_mean, price_cv)
            harvestingefficiency = stat(harvesting_production_mean, harvesting_production_cv)
            estcost = np.maximum(0, stat(establishment_cost_mean, establishment_cost_cv))
            estlabor = np.maximum(0, stat(establishment_labour_mean, establishment_labour_cv))
            extlabor = np.maximum(0, stat(external_labour_mean, external_labour_cv))

            totlabor = totpop * agentprop[0] * demography[2] * demography[3] * (1 - disasterimpactonworkingday / 100)
            labormoneyfrac = np.power((cultural_influence[:, np.newaxis] * np.maximum(0, exppayofftolabor)), agentprop[3])

            labormoneyfrac_sum = np.sum(labormoneyfrac, axis=0)

            # labormoneyfrac_arg = np.ones(labormoneyfrac_sum.shape) * len(lctype)
            labormoneyfrac = np.divide(labormoneyfrac, labormoneyfrac_sum, out=np.ones(labormoneyfrac.shape)/len(livelihood), where=labormoneyfrac_sum!=0)

            availablelabor = extlabor + np.sum(totlabor * labormoneyfrac, axis=1)

            landfrac = np.power((cultural_influence[:, np.newaxis] * np.maximum(0, exppayofftoland)), agentprop[3])
            landfrac_sum = np.sum(landfrac, axis=0)
            landfrac = np.divide(landfrac, landfrac_sum, out=np.ones(landfrac.shape)/len(livelihood), where=landfrac_sum != 0)

            landfrac[0, :] = 0

            lu_ = (dset == 0) * SET + (dset != 0) * landuse

            lcSET = (lu_ == SET) * offfarm
            lcFOR = (lu_ == FOR) * (
                    (lcage >= landcover_age_boundary[for_pion]) * (lcage < landcover_age_boundary[2]) * 1 + (
                            lcage >= landcover_age_boundary[2]) * (
                            lcage < landcover_age_boundary[3]) * 2 + (
                            lcage >= landcover_age_boundary[3]) * (
                            lcage < landcover_age_boundary[4]) * 3 + (
                            lcage >= landcover_age_boundary[4]) * 4)
            lcFOOD1 = (lu_ == AGR1) * 5
            lcFOOD2 = (lu_ == AGR2) * 6
            lcFOOD3 = (lu_ == AGR3) * 7
            lcFOOD4 = (lu_ == AGR4) * 8

            lcAF1 = (lu_ == AF1) * (
                    (lcage > landcover_age_boundary[9]) * (
                    lcage < landcover_age_boundary[10]) * 9 + (
                            lcage > landcover_age_boundary[10]) * (
                            lcage < landcover_age_boundary[11]) * 10 + (
                            lcage > landcover_age_boundary[11]) * (
                            lcage < landcover_age_boundary[12]) * 11 + (
                            lcage > landcover_age_boundary[12]) * 12)

            lcAF2 = (lu_ == AF2) * (
                    (lcage > landcover_age_boundary[13]) * (
                    lcage < landcover_age_boundary[14]) * 13 + (
                            lcage > landcover_age_boundary[14]) * (
                            lcage < landcover_age_boundary[15]) * 14 + (
                            lcage > landcover_age_boundary[15]) * (
                            lcage < landcover_age_boundary[16]) * 15 + (
                            lcage > landcover_age_boundary[16]) * 16)

            lcAF3 = (lu_ == AF3) * (
                    (lcage > landcover_age_boundary[17]) * (
                    lcage < landcover_age_boundary[18]) * 17 + (
                            lcage > landcover_age_boundary[18]) * (
                            lcage < landcover_age_boundary[19]) * 18 + (
                            lcage > landcover_age_boundary[19]) * (
                            lcage < landcover_age_boundary[20]) * 19 + (
                            lcage > landcover_age_boundary[20]) * 20)

            lcAF4 = (lu_ == AF4) * (
                    (lcage > landcover_age_boundary[21]) * (
                    lcage < landcover_age_boundary[22]) * 21 + (
                            lcage > landcover_age_boundary[22]) * (
                            lcage < landcover_age_boundary[23]) * 22 + (
                            lcage > landcover_age_boundary[23]) * (
                            lcage < landcover_age_boundary[24]) * 23 + (
                            lcage > landcover_age_boundary[24]) * 24)

            lcAF5 = (lu_ == AF5) * (
                    (lcage > landcover_age_boundary[25]) * (
                    lcage < landcover_age_boundary[26]) * 25 + (
                            lcage > landcover_age_boundary[26]) * (
                            lcage < landcover_age_boundary[27]) * 26 + (
                            lcage > landcover_age_boundary[27]) * (
                            lcage < landcover_age_boundary[28]) * 27 + (
                            lcage > landcover_age_boundary[28]) * 28)

            lcAF6 = (lu_ == AF6) * (
                    (lcage > landcover_age_boundary[29]) * (
                    lcage < landcover_age_boundary[30]) * 29 + (
                            lcage > landcover_age_boundary[30]) * (
                            lcage < landcover_age_boundary[31]) * 30 + (
                            lcage > landcover_age_boundary[31]) * (
                            lcage < landcover_age_boundary[32]) * 31 + (
                            lcage > landcover_age_boundary[32]) * 32)

            lcAF7 = (lu_ == AF7) * (
                    (lcage > landcover_age_boundary[33]) * (
                    lcage < landcover_age_boundary[34]) * 33 + (
                            lcage > landcover_age_boundary[34]) * (
                            lcage < landcover_age_boundary[35]) * 34 + (
                            lcage > landcover_age_boundary[35]) * (
                            lcage < landcover_age_boundary[36]) * 35 + (
                            lcage > landcover_age_boundary[36]) * 36)

            lcAF8 = (lu_ == AF8) * (
                    (lcage > landcover_age_boundary[37]) * (
                    lcage < landcover_age_boundary[38]) * 37 + (
                            lcage > landcover_age_boundary[38]) * (
                            lcage < landcover_age_boundary[39]) * 38 + (
                            lcage > landcover_age_boundary[39]) * (
                            lcage < landcover_age_boundary[40]) * 39 + (
                            lcage > landcover_age_boundary[40]) * 40)

            lc = lcSET + lcFOOD1 + lcFOOD2 + lcFOOD3 + lcFOOD4 + lcFOR + lcAF1 + lcAF2 + lcAF3 + lcAF4 + lcAF5 + lcAF6 + lcAF7 + lcAF8
            lcname = make_file_path(self.output, 'landcover[%s].tif' % str(time))
            save2file(lc, lcname)
            lcarea = np.array(list(np.sum(lc == i) * PIXEL_SIZE for i in lctype))
            output_timeseries['Land cover area'] = lcarea
            luarea = np.array(list(np.sum(lu_ == i) * PIXEL_SIZE for i in lutype))
            output_timeseries['Land use area'] = luarea
            # lcarea = np.sum(lc_layers, axis=(1, 2)) * PIXEL_SIZE
            # luarea = np.sum(landuse.reshape((1, *landuse.shape)) == LANDUSEID,
            #                 axis=(1, 2)) * PIXEL_SIZE

            # scl_ = []
            # for i in lctype:
            #     x = []
            #     for j in sctype:
            #         x.append(np.logical_and(lc == i, subcatchment_area == j))
            #     scl_.append(x)
            #
            # scl = np.array(scl_)
            # scl_area = np.sum(scl, axis=(2, 3)) * PIXEL_SIZE
            # sc_area_ = np.sum(scl_area, axis=0) * PIXEL_SIZE
            # sc_area = np.sum(sc_layers, axis=(1, 2)) * PIXEL_SIZE

            # sclcareafrac = scl_area * sc_area_reverse

            criticalzone = marginalagriculture | marginalAF
            for i in LC2CRITICALZONE:
                criticalzone = criticalzone | (lc == i)
            criticalzone = criticalzone & non_protected_area

            randcritzone = (arrayfill(uniform(criticalzone), 1) * simulated_area)
            # save2file(randcritzone, 'randcritzone.tif')


            totcritzonearea = np.sum(criticalzone) * PIXEL_SIZE


            critzonearea = totcritzonearea * (np.dot(landfrac, agentprop[0].reshape(2, 1))).reshape(15, )
            critzonearea[offfarm] = 0
            critzone = [None] * 15
            critzoneprob = [None] * 15

            all = simulated_area != 1
            # the cumulative probability
            sumcrit = simulated_area * 0.0

            critzoneprob[offfarm] = critzonearea[offfarm] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[offfarm]
            critzone[offfarm] = (randcritzone < sumcrit) & (~all) & criticalzone
            all = all | critzone[offfarm]
            critzoneprob[ntfp] = critzonearea[ntfp] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[ntfp]
            critzone[ntfp] = (randcritzone < sumcrit) & (~all) & criticalzone
            all = all | critzone[ntfp]
            critzoneprob[timber] = critzonearea[timber] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[timber]
            critzone[timber] = (randcritzone < sumcrit) & (~all) & criticalzone
            all = all | critzone[timber]
            critzoneprob[food1] = critzonearea[food1] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[food1]
            critzone[food1] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitfood1 == 1)
            all = all | critzone[food1]
            critzoneprob[food2] = critzonearea[food2] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[food2]
            critzone[food2] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitfood2 == 1)
            all = all | critzone[food2]
            critzoneprob[food3] = critzonearea[food3] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[food3]
            critzone[food3] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitfood3 == 1)
            all = all | critzone[food3]
            critzoneprob[food4] = critzonearea[food4] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[food4]
            critzone[food4] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitfood4 == 1)
            all = all | critzone[food4]
            critzoneprob[af1] = critzonearea[af1] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af1]
            critzone[af1] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf1 == 1)
            all = all | critzone[af1]
            critzoneprob[af2] = critzonearea[af2] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af2]
            critzone[af2] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf2 == 1)
            all = all | critzone[af2]
            critzoneprob[af3] = critzonearea[af3] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af3]
            critzone[af3] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf3 == 1)
            all = all | critzone[af3]
            critzoneprob[af4] = critzonearea[af4] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af4]
            critzone[af4] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf4 == 1)
            all = all | critzone[af4]
            critzoneprob[af5] = critzonearea[af5] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af5]
            critzone[af5] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf5 == 1)
            all = all | critzone[af5]
            critzoneprob[af6] = critzonearea[af6] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af6]
            critzone[af6] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf6 == 1)
            all = all | critzone[af6]
            critzoneprob[af7] = critzonearea[af7] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af7]
            critzone[af7] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf7 == 1)
            all = all | critzone[af7]
            critzoneprob[af8] = critzonearea[af8] / totcritzonearea
            sumcrit = sumcrit + critzoneprob[af8]
            critzone[af8] = (randcritzone < sumcrit) & (~all) & criticalzone & (suitaf8 == 1)
            all = all | critzone[af8]

            phzone = list(range(15))
            for i in livelihood:
                phzone[i] = simulated_area != 1
                for j in LIVELIHOOD2LC[i]:
                    phzone[i] = (lc == j) | phzone[i]
                phzone[i] = phzone[i] & non_protected_area

            phzone[offfarm] = simulated_area != 1
            phzone[ntfp] = phzone[ntfp] & ntfpzone
            phzone[timber] = logzone == 1

            harvestingarea = np.arange(len(livelihood))
            for i in livelihood:
                harvestingarea[i] = np.sum(phzone[i])


            dexistingplot = np.array(list(spreadmap(phzone[i], prototype) * simulated_area for i in livelihood))

            soildepletionrate = 0.0 * lc
            soilrecoverytime = 0.0 * lc

            for i in lctype:
                soildepletionrate += np.maximum(0, (lc == i) * normal(depletion_rate_mean[i], depletion_rate_cv[i], simulated_area))
                soilrecoverytime += np.maximum(0, (lc == i) * normal(halftime_recovery_mean[i], halftime_recovery_cv[i], simulated_area))

            soildepletion = np.maximum(0, np.minimum(1, soildepletionrate * soil_fert))
            pyield = list(range(15))
            nlabcosts = list(range(15))
            for i in livelihood:
                pyield[i] = 0.0 * lc
                nlabcosts[i] = 0.0 * lc
                for j in LIVELIHOOD2LC[i]:
                    pyield[i] += (lc == j) * np.maximum(0, normal(land_yield_mean[j], land_yield_cv[j], simulated_area))
                    nlabcosts[i] += (lc == j) * np.maximum(0, normal(non_labour_cost_mean[j], non_labour_cost_cv[j], simulated_area))

            pyield[agr1] = pyield[agr1] * soildepletion
            pyield[agr2] = pyield[agr2] * soildepletion
            pyield[agr3] = pyield[agr3] * soildepletion
            pyield[agr4] = pyield[agr4] * soildepletion

            nonlaborcosts= np.arange(15)
            # revenue = list(range(15))
            potyield = np.arange(15)
            # attyield = list(range(15))
            # profit = list(range(15))
            payofftolabor = np.arange(15)
            payofftoland = np.arange(15)
            for i in livelihood:
                potyield[i] = np.sum(pyield[i] * phzone[i])
                nonlaborcosts[i] = np.maximum(0, np.sum(nlabcosts[i] * phzone[i])-(subsidy_mnt[i] * sub[time][i])) if USING_TIMESERIES else np.maximum(0, np.sum(nlabcosts[i] * phzone[i]) - subsidy_mnt[i])
            output_timeseries['Potential yield'] = potyield
            output_timeseries['Non-labour costs'] = nonlaborcosts
            attyield = np.minimum(potyield, availablelabor * harvestingefficiency)
            output_timeseries['Actual yield'] = attyield
            revenue = attyield * price
            output_timeseries['Revenue'] = revenue
            profit = revenue - nonlaborcosts - (extlabor * price[offfarm])
            output_timeseries['Profit'] = profit

            totnonlaborcosts = np.sum(nonlaborcosts)

            for i in livelihood:
                payofftolabor[i] = profit[i] / availablelabor[i] if (availablelabor[i] > 0) else 0
                payofftoland[i] = profit[i] / harvestingarea[i] if (harvestingarea[i] > 0 and profit[i] > 0) else 0

            totlaborcosts = np.sum(extlabor * price[offfarm])

            payofftolabor[offfarm] = price[offfarm] if availablelabor[offfarm] > 0 else 0
            payofftoland[offfarm] = 0.0
            marginalagricultureAGR1 = (lc == agr1) & ((pyield[food1] <= 0.5 * PIXEL_SIZE) | ((exppayofftoland[food1][agent1] <= 0) & (exppayofftoland[food1][agent2] <= 0)) | ((exppayofftolabor[food1][agent1] <= 0) & (exppayofftolabor[food1][agent2] <= 0)))
            marginalagricultureAGR2 = (lc == agr2) & ((pyield[food2] <= 0.5 * PIXEL_SIZE) | ((exppayofftoland[food2][agent1] <= 0) & (exppayofftoland[food1][agent2] <= 0)) | ((exppayofftolabor[food2][agent1] <= 0) & (exppayofftolabor[food2][agent2] <= 0)))
            marginalagricultureAGR3 = (lc == agr3) & ((pyield[food3] <= 0.5 * PIXEL_SIZE) | ((exppayofftoland[food3][agent1] <= 0) & (exppayofftoland[food1][agent2] <= 0)) | ((exppayofftolabor[food3][agent1] <= 0) & (exppayofftolabor[food3][agent2] <= 0)))
            marginalagricultureAGR4 = (lc == agr4) & ((pyield[food4] <= 0.5 * PIXEL_SIZE) | ((exppayofftoland[food4][agent1] <= 0) & (exppayofftoland[food1][agent2] <= 0)) | ((exppayofftolabor[food4][agent1] <= 0) & (exppayofftolabor[food4][agent2] <= 0)))

            marginalagriculture = marginalagricultureAGR1 | marginalagricultureAGR2 | marginalagricultureAGR3 | marginalagricultureAGR1

            marginalAF1 = (lc == af1_lprod) | (lc == af1_pprod) & (profit[af1] < 0)
            marginalAF2 = (lc == af2_lprod) | (lc == af2_pprod) & (profit[af2] < 0)
            marginalAF3 = (lc == af3_lprod) | (lc == af3_pprod) & (profit[af3] < 0)
            marginalAF4 = (lc == af4_lprod) | (lc == af4_pprod) & (profit[af4] < 0)
            marginalAF5 = (lc == af5_lprod) | (lc == af5_pprod) & (profit[af5] < 0)
            marginalAF6 = (lc == af6_lprod) | (lc == af6_pprod) & (profit[af6] < 0)
            marginalAF7 = (lc == af7_lprod) | (lc == af7_pprod) & (profit[af7] < 0)
            marginalAF8 = (lc == af8_lprod) | (lc == af8_pprod) & (profit[af8] < 0)

            for ma in [marginalAF1, marginalAF2, marginalAF3, marginalAF4, marginalAF5, marginalAF6, marginalAF7, marginalAF8]:
                marginalAF = marginalAF | ma
            # marginalAF = np.logical_or()marginalAF1 or marginalAF2 or marginalAF3 or marginalAF4 or marginalAF5 or marginalAF6 or marginalAF7 or marginalAF8

            # save2file(marginalAF, 'marginalAF.tif')

            # break

            floorbiomassfraction = 0.0 * lc
            pfireescape = 0.0 * lc
            for i in lctype:
                agbiomass += (lc == i) * np.maximum(0, normal(aboveground_biomass_mean[i], aboveground_biomass_cv[i], simulated_area))
                floorbiomassfraction += (lc == i) * np.maximum(0, normal(floor_biomass_fraction_mean[i], floor_biomass_fraction_cv[i], simulated_area))
                pfireescape += (lc == i) * (np.maximum(0, normal(probably_of_fire_mean[i], probably_of_fire_cv[i], simulated_area)))

            loggedtimber = attyield[timber] * phzone[timber] / harvestingarea[timber] if harvestingarea[timber] > 0 else 0

            loggedbiomass = (logzone == 1) * agbiomass + 0.01
            agbiomass = np.maximum(0, agbiomass - loggedbiomass)
            agcarbon = agbiomass * conversion[1]

            agcarbon_name = make_file_path(self.output, 'aboveground_carbon[%s].tif' % str(time))
            save2file(agcarbon, agcarbon_name)
            floorbiom = agbiomass * floorbiomassfraction
            totagb = np.sum(agbiomass)
            totagc = np.sum(agcarbon)
            output_timeseries['Aboveground carbon'] = totagc
            # store_ = list(range(15))
            store = np.maximum(0, store * (1 - loss_fraction) + attyield)

            zfert = standardize(soil_fert)
            zdplot = np.array(list(standardize(dexistingplot[i]) for i in livelihood))

            maxy = np.amax(attyield)
            zyield = list(range(15))
            for i in livelihood:
                zyield[i] = np.divide(attyield[i], maxy, out=np.zeros(maxy.shape), where=maxy > 0)

            zfb = standardize(floorbiom)
            min_transportation = zroad
            for x in [zroad, zmart, zriver, zntfp]:
                min_transportation = np.minimum(min_transportation, x)
            attr = [None] * 15

            for i in range(1, 15):
                attr[i] = (critzone[i] * non_protected_area) * (
                    soil_fertility[i] * zfert +
                    land_productivity[i] * zyield[ntfp] +
                    land_suitability[ntfp] * 0
                ) / (
                        1 +
                        transportation_access[i] * min_transportation +
                        plot_maintainance[i] * np.minimum(zset, zdplot[i]) +
                        slope[i] * zslope + floor_biomass[i] * zfb
                )


            attr[0] = 0 * simulated_area

            # attr = np.array(attr)
            # for i in livelihood:
            #     save2file(attr[i], "attr[%s].tif" % str(i))

            zattr = [None] * 15
            for i in livelihood:
                n = np.sum(critzone[i])
                sattr = np.sum(attr[i])
                ssattr = np.sum(np.square(attr[i]))
                meanattr = sattr / n if n > 0 else 0
                sdattr = np.sqrt(ssattr / n - np.square(meanattr)) if n > 0 else 0
                err = np.square(attr[i] - meanattr) / n if n > 0 else 0
                toterr = np.sum(err)
                sdt = np.sqrt(toterr)
                zattr[i] = (attr[i] - meanattr) / sdattr if sdattr != 0 else simulated_area * -5

            # for i in livelihood:
            #     save2file(zattr[i], "zattr[%s].tif" % str(i))

            zattrclass1 = [None] * 15
            zattrclass2 = [None] * 15
            zattrclass3 = [None] * 15
            zattrclass4 = [None] * 15
            zattrclass5 = [None] * 15

            for i in livelihood:
                zattrclass1[i] = zattr[i] < 0
                zattrclass2[i] = (zattr[i] >= 0) & (zattr[i] < 1)
                zattrclass3[i] = (zattr[i] >= 1) & (zattr[i] < 2)
                zattrclass4[i] = (zattr[i] >= 2) & (zattr[i] < 3)
                zattrclass5[i] = zattr[i] > 3

            zattrclass = [zattrclass1, zattrclass2, zattrclass3, zattrclass4, zattrclass5]

            zfreq = copy.deepcopy(zattrclass)
            for i in range(5):
                for j in range(15):
                    zfreq[i][j] = np.sum(zattrclass[i][j])

            zexc = copy.deepcopy(zfreq)
            for i in livelihood:
                zexc[4][i] = 0
                zexc[3][i] = zexc[4][i] + zfreq[4][i]
                zexc[2][i] = zexc[3][i] + zfreq[3][i]
                zexc[1][i] = zexc[2][i] + zfreq[2][i]
                zexc[0][i] = zexc[1][i] + zfreq[1][i]

            availablemoney_ = np.sum(balance * labormoneyfrac, axis=1)
            availablemoney = availablemoney_ + subsidy_est * sub[time] if USING_TIMESERIES else availablemoney_ + subsidy_est
            output_timeseries['Available money'] = availablemoney
            exparealabor = np.divide(availablemoney, estlabor, out=np.zeros(estlabor.shape), where=estlabor > 0)
            output_timeseries['Return to labour'] = exparealabor
            expareamoney = np.divide(availablemoney, estcost, out=np.zeros(estcost.shape), where=estcost > 0)
            exparea = np.minimum(exparealabor, np.minimum(expareamoney, critzonearea))
            output_timeseries['Return to land'] = expareamoney
            exparea[offfarm] = 0

            expprob = copy.deepcopy(zexc)
            for i in range(5):
                for j in livelihood:
                    expprob[i][j] = np.maximum(0, np.minimum(zfreq[i][j], (exparea[i]-zexc[i][j]))) / zfreq[i][j] if zfreq[i][j] > 0 else 0

            allfireignition = simulated_area != 1
            expansionprobability = [None] * 15
            newplot = [None] * 15
            newplotarea = [None] * 15
            fireignition = [None] * 15
            for i in livelihood:
                expansionprobability[i] = 0.0
                for j in range(5):
                    expansionprobability[i] += zattrclass[j][i] * expprob[j][i]
                expansionprobability[i] = expansionprobability[i] * critzone[i]
                randommatrix = np.random.uniform(0, 1, simulated_area.shape)
                newplot[i] = np.logical_and(randommatrix <= expansionprobability[i], non_protected_area)
                newplotarea[i] = np.sum(newplot[i])
                fireignition[i] = np.logical_and(arrayfill(uniform(newplot[i]), 1), simulated_area < pfireuse[i])
                allfireignition= allfireignition | fireignition[i]
            output_timeseries['New cultivated areas'] = newplotarea
            allnewplots = simulated_area != 1
            for i in NEW_PLOTS:
                allnewplots = allnewplots | newplot[i]
            totestcost = 0.0
            for i in NEW_PLOTS:
                totestcost += estcost[i] * np.sum(newplot[i])
            output_timeseries['Establishment cost'] = totestcost
            totdemand = totpop * demand_per_capital
            buying = np.minimum(np.maximum(0, totdemand - (store * (1 - loss_fraction))), np.divide(balance, price, out=np.zeros(price.shape), where=price>0))
            output_timeseries['Buying'] = buying
            totbuying = np.sum(buying * price)
            selling = np.maximum(0, store * (1 - loss_fraction) - totdemand) * probably_to_sell
            output_timeseries['Selling'] = selling
            totselling = np.sum(selling * price)
            supplysufficiency = np.maximum(0, np.minimum(1, 1 - np.divide((totdemand-(store + buying - selling)), totdemand, out=np.zeros(totdemand.shape), where=totdemand>0)))
            store = np.maximum(0, store * (1 - loss_fraction) + buying - totdemand - selling)
            totnetincome = np.maximum(0, totselling - totbuying - totnonlaborcosts - totlaborcosts - totestcost)
            totsecconsumption = np.maximum(0, totnetincome * demography[5])
            totsecconsumptionpercapita = totsecconsumption / totpop if totpop > 0 else 0
            output_timeseries['Secondary consumption'] = totsecconsumptionpercapita
            totnetincomepercapita = totnetincome / totpop if totpop > 0 else 0
            output_timeseries['Net income'] = totnetincomepercapita
            balance = balance + totnetincome - totsecconsumption
            balance = balance * (1 - (disasterimpactonmoney / 100))
            nonselectedagricplot = (~allnewplots) & (marginalagriculture | marginalAF)
            dfireignition = arrayfill(spreadmap(allfireignition, prototype), 1e11)
            fire = (arrayfill(uniform(dfireignition < 2 * PIXEL_SIZE ** 0.5), 1) < pfireescape) | allfireignition
            firename = make_file_path(self.output, "fire[%s].tif" % str(time))
            save2file(fire, firename)
            firearea = np.sum(fire)
            ntfpzone = newplot[ntfp]
            totpop = (totpop * (1 + demography[1])) * (1 - (disasterimpactonhuman / 100))
            output_timeseries['Population'] = totpop
            exavail = ex if USING_TIMESERIES else availability
            # break

            # print(exppayofftolabor)
            exppayofftolabor = (payofftolabor[:, np.newaxis] > 0) * (
                    exppayofftolabor + agentprop[1][np.newaxis, :] * (payofftolabor[:, np.newaxis] - exppayofftolabor) +
                    agentprop[2][np.newaxis, :] * exavail[:, np.newaxis] * credibility[:, np.newaxis]) * availability[:, np.newaxis] * (
                agentprop[1][np.newaxis, :] * (payofftolabor[:, np.newaxis] - exppayofftolabor)
            )
            exppayofftoland = (payofftoland[:, np.newaxis] > 0) * (
                    exppayofftoland + agentprop[1][np.newaxis, :] * (payofftoland[:, np.newaxis] - exppayofftoland) +
                    agentprop[2][np.newaxis, :] * exavail[:, np.newaxis] * credibility[:, np.newaxis]) * availability[:, np.newaxis] * (
                                       agentprop[1][np.newaxis, :] * (payofftoland[:, np.newaxis] - exppayofftoland))

            soilrecovery = np.divide((maximul_soil_fertility_area - soil_fert)**2, ((1+soilrecoverytime)*maximul_soil_fertility_area - soil_fert), out=np.zeros(simulated_area.shape),where=(((1+soilrecoverytime) * maximul_soil_fertility_area - soil_fert) > 0)) * simulated_area
            soil_fert = np.minimum(maximul_soil_fertility_area, np.maximum(0, soil_fert + soilrecovery - soildepletion))
            soilname = make_file_path(self.output, "soil[%s].tif" % str(time))
            save2file(soil_fert, soilname)
            forest_plots = (fire & (~allnewplots)) | (disasterimpactedzone == 1) | nonselectedagricplot
            plt = (landuse == SET) | forest_plots
            updatingLU = (landuse == SET) * SET + forest_plots * FOR
            for i in NEW_PLOTS:
                updatingLU += newplot[i] * i
                plt = np.logical_or(plt, newplot[i])

            updatingLU = updatingLU + (~plt) * landuse
            landuse = updatingLU

            luname = make_file_path(self.output, "landuse[%s].tif" % str(time))
            save2file(landuse, luname)

            agebasedbiomass1 = ((agbiomass > 0) & (agbiomass < aboveground_biomass_mean[for_ysec])) * normal(initial_landcover_age_mean[for_pion], initial_landcover_age_cv[for_pion], simulated_area)
            agebasedbiomass2 = ((agbiomass > (aboveground_biomass_mean[for_ysec])) & (agbiomass < aboveground_biomass_mean[for_osec])) * normal(initial_landcover_age_mean[for_ysec], initial_landcover_age_cv[for_ysec], simulated_area)
            agebasedbiomass3 = ((agbiomass > (aboveground_biomass_mean[for_osec])) & (agbiomass < aboveground_biomass_mean[for_prim])) * normal(initial_landcover_age_mean[for_osec], initial_landcover_age_cv[for_osec], simulated_area)
            agebasedbiomass4 = (agbiomass > aboveground_biomass_mean[for_prim]) * normal(initial_landcover_age_mean[for_prim], initial_landcover_age_cv[for_prim], simulated_area)

            agebasedbiomass = agebasedbiomass1 + agebasedbiomass2 + agebasedbiomass3 + agebasedbiomass4
            agbasedbiomassname = make_file_path(self.output, 'aboveground_biomass[%s].tif' % str(time))
            save2file(agebasedbiomass, agbasedbiomassname)

            lcage = (phzone[timber] * agebasedbiomass) + (~(allnewplots | fire | (disasterimpactedzone == 1) | nonselectedagricplot | phzone[timber])) * (lcage + 1)
            totfinance = balance

            print(time)

            self.signal.emit(output_timeseries, time)