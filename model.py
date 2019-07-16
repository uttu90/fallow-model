import os
import json
import bisect
import copy
import numpy

from PyQt5 import QtCore

from constant import *
import read_input
import util


class SimulatingThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(dict, dict, int, name='update')

    def __init__(self, prj):
        super(SimulatingThread, self).__init__()
        self.prj = prj
        self.data_file = os.path.join(prj, 'data.xlsx')
        self.map_file = os.path.join(prj, 'maps.json')

    def run(self):
        input_data, input_ts = read_input.get_data(self.data_file)
        with open(os.path.join(self.prj, 'maps.json'), 'r') as data_file:
            maps_data = json.load(data_file)
            map_data_object = util.load_maps(maps_data)
            prototype = util.get_prototype(maps_data)
            # print map_data_object[DISTANCE_TO_FACTORY][NON_TIMBER_FOREST_PRODUCT]
            distance_to_factory_maps_array = {
                tree: [
                    map_data_object[DISTANCE_TO_FACTORY][tree][period] for
                    period in LAND_PERIODS
                ] for tree in PRODUCTS
            }
            distance_to_settlement_maps_array = [
                map_data_object[DISTANCE_TO_SETTLEMENT][period] for period in
                LAND_PERIODS
            ]
            distance_to_market_maps_array = [
                map_data_object[DISTANCE_TO_MARKET][period] for period in
                LAND_PERIODS
            ]
            distance_to_road_maps_array = [
                map_data_object[DISTANCE_TO_ROAD][period] for period in
                LAND_PERIODS
            ]
            distance_to_river_maps_array = [
                map_data_object[DISTANCE_TO_RIVER][period] for period in
                LAND_PERIODS
            ]

        TIMESERIES = 'timeseries'
        MAPS = 'maps'

        # output = {}
        # output[TIMESERIES] = {}
        # output[MAPS] = {}

        standardized_potential_class_maps = {}

        area_map = map_data_object[SIMULATED_AREA]
        init_landcover_map = map_data_object[INITIAL_LANDCOVER]

        landuse_map = util.create_zero_map(map_data_object[SIMULATED_AREA])
        landage_map = util.create_zero_map(map_data_object[INITIAL_LANDCOVER])

        biophysical1 = input_data['biophysical1']
        land_specs = input_data['land_specs']
        biophysical2 = input_data['biophysical2']
        economic1 = input_data['economic1']
        economic2 = input_data['economic2']
        social = input_data['social']
        farmer = input_data['farmer']
        demography = input_data['demography']
        impact = input_data['impact']
        subsidy = input_data['subsidy']

        product_price = input_ts['product_price']
        extension_availability = input_ts['extension_availability']
        subsidy_availability = input_ts['subsidy_availability']

        output_timeseries = dict()
        output_maps = dict()

        # output_timeseries = output[TIMESERIES]
        # output_maps = output[MAPS]

        output_timeseries['Fire area'] = fire_area_timeseries = []
        output_timeseries[
            'Secondary consumption'] = secondary_consumption_timeseries = []
        output_timeseries['Net income'] = net_income_timeseries = []
        output_timeseries['Population'] = total_population_timeseries = [
            demography[DEMOGRAPHY[0]]]
        output_timeseries[
            'Aboveground biomass'] = aboveground_biomass_timeseries = []
        output_timeseries[
            'Aboveground carbon'] = aboveground_carbon_timeseries = []
        output_timeseries[
            'Establishment cost'] = establisment_cost_timeseries = []
        output_timeseries[
            'Potential area expansion'] = potential_area_expansion_timseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Non-labour costs'] = non_labour_cost_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Revenue'] = revenue_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Return to labour'] = return_to_labour_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Return to land'] = return_to_land_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Supply sufficiency'] = supply_sufficiency_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Land expansion labour'] = land_expansion_labour_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Land expansion budget'] = land_expansion_budget_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Actual area expansion'] = actual_area_expansion_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'New cultivated areas'] = new_cultivate_areas_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Available labour'] = available_labour_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Available money'] = available_money_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Expense'] = expense_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries['Income'] = income_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Potential yield'] = potential_yield_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )
        output_timeseries[
            'Actual yield'] = actual_yield_timeseries = util.create_nested_output(
            LIVELIHOOD, []
        )

        output_timeseries[
            'Land cover area'] = landcover_area_timeseries = util.create_nested_output(
            LANDCOVER, []
        )

        output_timeseries[
            'Land use area'] = landuse_area_timeseries = util.create_nested_output(
            LANDUSE, []
        )

        output_timeseries[
            'Subcatchment area '] = subcatchment_area_timeseries = util.create_nested_output(
            SUBCATCHMENT, [])

        output_maps['Landcover'] = output_landcover_maps = []
        output_maps['Aboveground carbon'] = output_aboveground_carbon_maps = []
        output_maps['Fire'] = output_fire_maps = []
        output_maps['Soil'] = output_soil_maps = []
        output_maps['Land use'] = ouput_land_use_maps = []
        output_maps['Aboveground biomass'] = output_aboveground_biomass_maps = []

        labour_money_fraction = util.create_nested_output(LIVELIHOOD, {})
        land_money_fraction = util.create_nested_output(LIVELIHOOD, {})

        balance = demography[DEMOGRAPHY[4]]
        store = {}
        PERIODS = [0, 50, 100, 150, 200]
        PIXEL_SIZE = 4
        simulation_time = 30
        using_timeseries = False


        for land in LANDCOVER:
            if type(land) is str:
                landage_map += util.arraystat(area_map,
                                              biophysical1[land][
                                                  LANDCOVER_AGE][
                                                  INITIAL_LANDCOVER_AGE]) * \
                               (init_landcover_map == LANDCOVER_MAP[land])
            else:
                for key in land.keys():
                    for land_stage in land[key]:
                        landage_map += util.arraystat(area_map,
                                                      biophysical1[
                                                          key][land_stage][
                                                          LANDCOVER_AGE][
                                                          INITIAL_LANDCOVER_AGE]) * (
                                               init_landcover_map ==
                                               LANDCOVER_MAP[key][land_stage])

        for land in LANDCOVER:
            if type(land) is str:
                landuse_map += (init_landcover_map ==
                                LANDCOVER_MAP[land]) * LANDUSE_MAP[land]
            else:
                for key in land.keys():
                    for land_stage in land[key]:
                        landuse_map += (init_landcover_map ==
                                        LANDCOVER_MAP[key][land_stage]) * \
                                       LANDUSE_MAP[key]

        for livetype in LIVELIHOOD:
            store[livetype] = demography[INITIAL_POPULATION] * biophysical2[livetype][
                                  DEMAND_PER_CAPITA]

        landcover_map = map_data_object[INITIAL_LANDCOVER]
        irreversed_map = ~util.create_bool_map(
            map_data_object[PROTECTED_AREA], 1)
        marginal_agriculture_map = util.create_bool_map(area_map, 0)
        marginalAF_map = util.create_bool_map(area_map, 0)

        profitability = {}

        price_timeseries = util.create_nested_output(LIVELIHOOD, [])
        aboveground_biomass_map = util.create_zero_map(landcover_map)
        standardized_distance_to_factory_maps = {}
        standardized_slope_map = util.standardize(map_data_object[SLOPE])
        self.signal.emit(output_timeseries, output_maps, 0)
        for time in range(simulation_time):

            total_buying = 0
            total_selling = 0
            current_period = bisect.bisect(PERIODS, time)
            if (time > 0):
                total_population_timeseries.append(
                    total_population_timeseries[time - 1])
            if (using_timeseries):
                price_timeseries = copy.deepcopy(product_price)[
                    time]
            else:
                for livetype in LIVELIHOOD:
                    price_timeseries[livetype].append(util.calstat_shape(
                        util.get_shape(economic1, PRICE))[livetype])
            harvesting_efficiency = util.calstat_shape(
                util.get_shape(biophysical2, HARVESTING))
            establistment_cost = util.calstat_shape(
                util.get_shape(economic1, ESTABLISTMENT_COST))
            establistment_labour = util.calstat_shape(
                util.get_shape(economic1, ESTABLISTMENT_LABOUR))
            external_labour = util.calstat_shape(
                util.get_shape(economic1, EXTERNAL_LABOUR))
            total_labour = {
                farmerType: (total_population_timeseries[time] *
                         farmer[POPULATION_FRACTION][farmerType] *
                         demography[LABOUR_FRACTION] *
                         demography[WORKING_DAYS] * (
                                 1 - impact[IMPACT_OF_DISASTER][
                             TO_WORKING_DAY] / 100.0)
                         ) for farmerType in FARMERS
            }
            standardized_distance_to_road_map = util.standardize(
                distance_to_road_maps_array[current_period])
            standardized_distance_to_market_map = util.standardize(
                distance_to_market_maps_array[current_period])
            standardized_distance_to_factory_maps = {
                tree: util.standardize(
                    distance_to_factory_maps_array[tree][
                        current_period]) for tree in PRODUCTS
            }
            standardized_distance_to_river_map = util.standardize(
                distance_to_river_maps_array[current_period])
            for farmerType in FARMERS:
                land_sum = 0
                count = 0
                labour_sum = 0
                for livetype in LIVELIHOOD:
                    land_sum += social[livetype][
                                    CULTURAL_INFLUENCE] * max(
                        0,
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LAND][farmerType]) ** \
                                farmer[LANDUSE_PRIORITY][farmerType]
                    labour_sum += social[livetype][
                                      CULTURAL_INFLUENCE] * max(
                        0,
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LABOUR][farmerType]) ** \
                                  farmer[LANDUSE_PRIORITY][farmerType]
                    count += 1

                for livetype in LIVELIHOOD:
                    land_money_fraction[livetype][farmerType] = \
                    social[livetype][CULTURAL_INFLUENCE] * max(
                        0,
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LAND][farmerType]) ** (
                                farmer[LANDUSE_PRIORITY][
                                    farmerType] / land_sum) if land_sum > 0 else 1 / count
                    labour_money_fraction[livetype][farmerType] = \
                    social[livetype][CULTURAL_INFLUENCE] * max(
                        0,
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LABOUR][farmerType]) ** (
                                farmer[LANDUSE_PRIORITY][
                                    farmerType] / labour_sum) if labour_sum > 0 else 1 / count

                land_money_fraction[OFF_NONFARM][farmerType] = 0
            for livetype in LIVELIHOOD:
                for farmerType in FARMERS:
                    available_labour_timeseries[livetype].append(
                        external_labour[livetype] +
                        labour_money_fraction[livetype][farmerType] * total_labour[farmerType]
                    )

            current_landcover_map = util.create_zero_map(
                map_data_object[INITIAL_LANDCOVER]
            )
            current_landuse_map = util.create_zero_map(
                area_map
            ) if distance_to_settlement_maps_array[
                     current_period] is None else landuse_map

            standardized_settlement_map = util.standardize(
                distance_to_settlement_maps_array[current_period])
            for land in LANDCOVER:
                if type(land) is str:
                    current_landcover_map += (
                                                     current_landuse_map ==
                                                     LANDCOVER_MAP[land]
                                             ) * LANDCOVER_MAP[land]
                else:
                    for key in land.keys():
                        for idx, land_stage in enumerate(land[key][:-1]):
                            landage = biophysical1[key][land_stage][
                                LANDCOVER_AGE][LANDCOVER_AGE_BOUNDARY]
                            landage_upper = \
                            biophysical1[key][land[key]
                            [idx + 1]][LANDCOVER_AGE][LANDCOVER_AGE_BOUNDARY]
                            current_landcover_map += (current_landuse_map ==
                                                      LANDUSE_MAP[key]) * (
                                                                 landage_map >= landage) * (
                                                             landage_map < landage_upper) * \
                                                     LANDCOVER_MAP[key][
                                                         land_stage]
                        current_landcover_map += (current_landuse_map ==
                                                  LANDUSE_MAP[key]) * (
                                                         landage_map >= landage_upper) * \
                                                 LANDCOVER_MAP[key][
                                                     land[key][-1]]
            output_landcover_maps.append(current_landcover_map)
            for land in LANDCOVER:
                if type(land) is str:
                    landcover_area_timeseries[land].append(
                        util.arraytotal(
                            current_landcover_map == LANDCOVER_MAP[land]))
                else:
                    for key in land.keys():
                        for land_stage in land[key]:
                            landcover_area_timeseries[key][land_stage].append(
                                util.arraytotal(current_landcover_map ==
                                                     LANDCOVER_MAP[key][
                                                         land_stage]))

            for land in LANDUSE:
                landuse_area_timeseries[land].append(util.arraytotal(
                    landuse_map == LANDUSE_MAP[land]) * PIXEL_SIZE)

            subcatchment_landcover_area = {}
            for subcatchment in SUBCATCHMENT:
                subcatchment_area = 0
                for land in LANDCOVER:
                    if type(land) is str:
                        subcatchment_area += util.arraytotal((
                              map_data_object[
                                  SUBCATCHMENT_AREA] ==
                              SUBCATCHMENT_IDS[
                                  subcatchment]) * (
                          landcover_map ==
                          LANDCOVER_MAP[
                              land])) * PIXEL_SIZE
                    else:
                        for key in land.keys():
                            for land_stage in land[key]:
                                subcatchment_area += util.arraytotal((
                                      map_data_object[
                                          SUBCATCHMENT_AREA] ==
                                      SUBCATCHMENT_IDS[
                                          subcatchment]) * (
                                  landcover_map ==
                                  LANDCOVER_MAP[
                                      key][
                                      land_stage])) * PIXEL_SIZE
                subcatchment_landcover_area[subcatchment] = subcatchment_area
                subcatchment_area_timeseries[subcatchment].append(
                    util.arraytotal(
                        map_data_object[SUBCATCHMENT_AREA] ==
                        SUBCATCHMENT_IDS[subcatchment]) * PIXEL_SIZE)

            current_criticalzone_map = util.create_zero_map(area_map) == 1
            for forest_stage in FOREST_STAGES:
                current_criticalzone_map |= (current_landcover_map ==
                                             LANDCOVER_MAP[FOREST][
                                                 forest_stage])
            for tree in TREE_BASED_SYSTEMS:
                current_criticalzone_map |= (current_landcover_map ==
                                             LANDCOVER_MAP[tree][
                                                 TREE_BASED_STAGES[-1]])
            current_criticalzone_map = current_criticalzone_map | marginal_agriculture_map | marginalAF_map & (
                ~util.create_bool_map(map_data_object[PROTECTED_AREA], 1))
            criticalzone_area = util.arraytotal(
                current_criticalzone_map) * PIXEL_SIZE
            for livetype in LIVELIHOOD:
                population_fraction = 0
                for farmerType in FARMERS:
                    population_fraction += farmer[POPULATION_FRACTION][farmerType]
                potential_area_expansion_timseries[livetype].append(criticalzone_area * population_fraction)

            potential_area_expansion_timseries[OFF_NONFARM][time] = 0

            random_criticalzone_map = util.arrayfill(
                util.uniform(current_criticalzone_map), 1) * area_map
            all_new_plots_map = util.create_bool_map(area_map, 0)
            cummulate_criticalzone_map = util.create_zero_map(area_map)
            criticalzone_prob = {}
            criticalzone_maps = {}

            for livetype in LIVELIHOOD:
                criticalzone_prob[livetype] = \
                potential_area_expansion_timseries[livetype][time] / \
                criticalzone_area if criticalzone_area > 0 else 0
                cummulate_criticalzone_map += criticalzone_prob[livetype]
                criticalzone_maps[livetype] = (
                      random_criticalzone_map < cummulate_criticalzone_map) & (
              ~all_new_plots_map) & current_criticalzone_map
                if livetype in map_data_object[SUITABLE_AREA].keys():
                    criticalzone_maps[livetype] &= (
                            map_data_object[SUITABLE_AREA][
                                livetype] == 1)
                all_new_plots_map |= criticalzone_maps[livetype]

            phzone_maps = {}
            phzone_maps[OFF_NONFARM] = util.create_bool_map(area_map, 0)
            phzone_maps[TIMBER] = copy.deepcopy(
                map_data_object[INITIAL_LOGGING_AREA])
            for crop in ANNUAL_CROPS:
                phzone_maps[crop] = (landcover_map == LANDCOVER_MAP[crop]) & irreversed_map
            phzone_maps[NON_TIMBER_FOREST_PRODUCT] = util.create_bool_map(area_map, 0)

            for forest_stage in FOREST_STAGES:
                phzone_maps[NON_TIMBER_FOREST_PRODUCT] |= landcover_map == \
                                                          LANDCOVER_MAP[
                                                              FOREST][
                                                              forest_stage]

            for tree in TREE_BASED_SYSTEMS:
                phzone_maps[tree] = util.create_bool_map(area_map, 0)
                for tree_stage in TREE_BASED_STAGES:
                    phzone_maps[tree] |= (
                            landcover_map == LANDCOVER_MAP[tree][tree_stage])
                phzone_maps[tree] = phzone_maps[tree] & irreversed_map

            harvesting_area = {}
            existing_plot_maps = {}
            for livetype in LIVELIHOOD:
                harvesting_area[livetype] = util.arraytotal(
                    phzone_maps[livetype])
                existing_plot_map = util.spreadmap(phzone_maps[livetype], prototype)
                existing_plot_maps[livetype] = existing_plot_map

            soil_depletion_map = util.create_zero_map(area_map)
            soil_recoverytime_map = util.create_zero_map(area_map)
            for land in LANDCOVER:
                if (type(land) is str):
                    soil_depletion_map += (landcover_map == LANDCOVER_MAP[
                        land]) * util.arraystat(
                        area_map,
                        biophysical1[land][SOIL_FERTILITY][
                            DEPLETION_RATE])
                    soil_recoverytime_map += (landcover_map == LANDCOVER_MAP[
                        land]) * util.arraystat(
                        area_map,
                        biophysical1[land][SOIL_FERTILITY][
                            HALFT_TIME_RECOVERY])
                else:
                    for key in land.keys():
                        for land_stage in land[key]:
                            soil_depletion_map += (landcover_map ==
                                                   LANDCOVER_MAP[key][
                                                       land_stage]) * util.arraystat(
                                area_map,
                                biophysical1[key][land_stage][
                                    SOIL_FERTILITY][DEPLETION_RATE])
                            soil_recoverytime_map += (landcover_map ==
                                                      LANDCOVER_MAP[key][
                                                          land_stage]) * util.arraystat(
                                area_map,
                                biophysical1[key][land_stage][
                                    SOIL_FERTILITY][HALFT_TIME_RECOVERY])

            soil_depletion_map = soil_depletion_map * \
                                 map_data_object[SOIL_FERTILITY][
                                     INITIAL_SOIL_FERTILITY]
            soil_depletion_map = util.arrayuper(
                util.arraylower(soil_depletion_map, 1), 0)

            total_labour_costs = 0
            total_nonlabor_costs = 0
            crop_area_map = util.create_bool_map(area_map, 0)
            for crop in ANNUAL_CROPS:
                crop_area_map |= landcover_map == LANDCOVER_MAP[crop]

            pyield = {}
            non_labour_cost = {}
            for livetype in LIVELIHOOD:
                pyield[livetype] = 0.0

                for land in LANDCOVER:
                    if land in ANNUAL_CROPS:
                        pyield[livetype] += (landcover_map == LANDCOVER_MAP[
                            land]) * util.arraystat(
                            area_map,
                            biophysical1[land][LANDCOVER_PROPERTY][
                                YIELD]) * soil_depletion_map
                    else:
                        if (type(land) is str):
                            pyield[livetype] += (landcover_map ==
                                                 LANDCOVER_MAP[
                                                     land]) * util.arraystat(
                                area_map, biophysical1[land][
                                    LANDCOVER_PROPERTY][YIELD])
                        else:
                            for key in land.keys():
                                for land_stage in land[key]:
                                    pyield[livetype] += (landcover_map ==
                                                         LANDCOVER_MAP[key][
                                                             land_stage]) * util.arraystat(
                                        area_map, biophysical1[key][
                                            land_stage][LANDCOVER_PROPERTY][
                                            YIELD])

            for livetype in LIVELIHOOD:
                non_labour_cost[livetype] = 0.0
                for land in LANDCOVER:
                    if type(land) is str:
                        non_labour_cost[livetype] += util.arraystat(
                            area_map,
                            economic2[land][NONLABOUR_COST])
                    else:
                        for key in land.keys():
                            for land_stage in land[key]:
                                non_labour_cost[
                                    livetype] += util.arraystat(
                                    area_map,
                                    economic2[key][land_stage][
                                        NONLABOUR_COST])

            for livetype in LIVELIHOOD:
                potential_yield_timeseries[livetype].append(
                    util.arraytotal(pyield[livetype] * phzone_maps[livetype]))
                actual_yield_timeseries[livetype].append(min(
                    potential_yield_timeseries[livetype][time],
                    available_labour_timeseries[livetype][time] *
                    harvesting_efficiency[livetype]))

                subsidy_ts = subsidy[livetype][MANAGEMENT_SUBSIDY] * \
                          subsidy_availability[livetype][
                              time] if using_timeseries else \
                subsidy[livetype][MANAGEMENT_SUBSIDY]
                non_labour_cost_timeseries[livetype].append(
                    max(util.arraytotal(
                        non_labour_cost[livetype] * phzone_maps[
                            livetype]) - subsidy_ts, 0))

                total_nonlabor_costs += non_labour_cost_timeseries[livetype][
                    time]
                revenue_timeseries[livetype].append(
                    actual_yield_timeseries[livetype][time] *
                    price_timeseries[livetype][time])
                profitability[livetype] = revenue_timeseries[livetype][time] - \
                                          non_labour_cost_timeseries[livetype][
                                              time] - \
                                          external_labour[livetype] * \
                                          price_timeseries[livetype][time]
                return_to_labour_timeseries[livetype].append(
                    profitability[livetype] /
                    available_labour_timeseries[livetype][time] if
                    available_labour_timeseries[livetype][time] > 0 else 0)
                return_to_land_timeseries[livetype].append(
                    profitability[livetype] / harvesting_area[livetype] if
                    harvesting_area[livetype] > 0 else 0)

                return_to_land_timeseries[OFF_NONFARM][time] = 0
                return_to_labour_timeseries[OFF_NONFARM][time] = max(
                    return_to_labour_timeseries[OFF_NONFARM][time], 0)
            marginal_agriculture_map = util.create_bool_map(area_map, 0)

            for crop in ANNUAL_CROPS:
                marginal_agriculture_map |= (
                            landcover_map == LANDCOVER_MAP[crop] |
                            ((pyield[crop] < 0.5 * PIXEL_SIZE) |
                             ((economic1[crop][
                                   ACTUAL_PROFITABILITY][RETURN_TO_LAND][
                                   FARMER1] < 0) & (economic1[crop][
                                                        ACTUAL_PROFITABILITY][
                                                        RETURN_TO_LAND][
                                                        FARMER2] < 0)) |
                             ((economic1[crop][
                                   ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][
                                   FARMER1] < 0) & (economic1[crop][
                                                        ACTUAL_PROFITABILITY][
                                                        RETURN_TO_LABOUR][
                                                        FARMER2] < 0)) & util.create_bool_map(
                                        area_map, 1)))
            marginalAF_map = util.create_bool_map(area_map, 0)
            for tree in TREE_BASED_SYSTEMS:
                for tree_stage in TREE_BASED_STAGES[-2:]:
                    marginalAF_map |= (
                            (landcover_map == LANDCOVER_MAP[tree][
                                tree_stage]) & (profitability[tree] < 0))

            floor_biomass_fraction_map = util.create_zero_map(area_map)
            potential_fire_escape_map = util.create_zero_map(area_map)

            for land in LANDCOVER:
                if (type(land) is str):
                    aboveground_biomass_map += (landcover_map == LANDCOVER_MAP[
                        land]) * util.stat(
                        biophysical1[land][LANDCOVER_PROPERTY][
                            ABOVEGROUND_BIOMASS])
                    floor_biomass_fraction_map += (landcover_map ==
                                                   LANDCOVER_MAP[
                                                       land]) * util.stat(
                        biophysical1[land][LANDCOVER_PROPERTY][
                            FLOOR_BIOMASS_FRACTION]
                    )
                    potential_fire_escape_map += (landcover_map ==
                                                  LANDCOVER_MAP[
                                                      land]) * util.stat(
                        biophysical1[land][LANDCOVER_PROPERTY][
                            PROBABLY_OF_FIRE_SPREADING]
                    )
                else:
                    for key in land.keys():
                        for land_stage in land[key]:
                            aboveground_biomass_map += (landcover_map ==
                                                        LANDCOVER_MAP[key][
                                                            land_stage]) * util.stat(
                                biophysical1[key][land_stage][
                                    LANDCOVER_PROPERTY][ABOVEGROUND_BIOMASS])
                            floor_biomass_fraction_map += (landcover_map ==
                                                           LANDCOVER_MAP[key][
                                                               land_stage]) * util.stat(
                                biophysical1[key][land_stage][
                                    LANDCOVER_PROPERTY][FLOOR_BIOMASS_FRACTION]
                            )
                            potential_fire_escape_map += (landcover_map ==
                                                          LANDCOVER_MAP[key][
                                                              land_stage]) * util.stat(
                                biophysical1[key][land_stage][
                                    LANDCOVER_PROPERTY][
                                    PROBABLY_OF_FIRE_SPREADING]
                            )

            logged_timber_map = potential_yield_timeseries[TIMBER][time] * \
                                phzone_maps[TIMBER] / \
                                harvesting_area[TIMBER] if (
                                                               harvesting_area[
                                                                   TIMBER]) > 0 else util.create_zero_map(
                area_map)
            logged_biomass_map = (
                    map_data_object[
                        INITIAL_LOGGING_AREA] * aboveground_biomass_map * 0.01)
            aboveground_biomass_map = aboveground_biomass_map - logged_biomass_map
            aboveground_biomass_map[aboveground_biomass_map < 0] = 0
            aboveground_carbon_map = aboveground_biomass_map * \
                                     impact[CONVERTION][
                                         BIOMASS_TO_CARBON]
            floor_biomass_map = aboveground_biomass_map * floor_biomass_fraction_map
            aboveground_biomass_timeseries.append(
                util.arraytotal(aboveground_biomass_map))
            aboveground_carbon_timeseries.append(
                util.arraytotal(aboveground_carbon_map))
            output_aboveground_carbon_maps.append(aboveground_carbon_map)
            for livetype in LIVELIHOOD:
                store[livetype] = max(0, store[livetype] * (1 -
                                                            biophysical2[
                                                                livetype][
                                                                LOSS_FRACTION]) +
                                      potential_yield_timeseries[livetype][
                                          time])
            standardized_fertility_map = util.standardize(
                map_data_object[SOIL_FERTILITY][
                    INITIAL_SOIL_FERTILITY])
            standardized_floor_biomass_map = util.standardize(
                floor_biomass_map)
            standardized_existing_plot_maps = {}
            for livetype in LIVELIHOOD:
                standardized_existing_plot_maps[
                    livetype] = util.standardize(
                    existing_plot_maps[livetype])
            max_potential_yield = 0
            for livetype in LIVELIHOOD:
                max_potential_yield = max(
                    max_potential_yield,
                    potential_yield_timeseries[livetype][time])
            standardized_yield = {}
            for livetype in LIVELIHOOD:
                standardized_yield[
                    livetype] = 0 if max_potential_yield == 0 else \
                potential_yield_timeseries[livetype][
                    time] / max_potential_yield

            potential_area_maps = {}
            able_area_maps = {}
            suitable_maps = {}
            distance_maps = {}

            for livetype in [NON_TIMBER_FOREST_PRODUCT, TIMBER]:
                able_area_maps[livetype] = irreversed_map
                suitable_maps[livetype] = util.create_zero_map(area_map)
            for livetype in ANNUAL_CROPS:
                able_area_maps[
                    livetype] = ~marginal_agriculture_map & irreversed_map
                suitable_maps[livetype] = biophysical2[livetype][
                                              LAND_SUITABILITY] * \
                                          map_data_object[
                                              SUITABLE_AREA][livetype]
            for livetype in TREE_BASED_SYSTEMS:
                able_area_maps[livetype] = ~marginalAF_map & irreversed_map
                suitable_maps[livetype] = biophysical2[livetype][
                                              LAND_SUITABILITY] * \
                                          map_data_object[
                                              SUITABLE_AREA][livetype]

            minimum_distance = standardized_distance_to_market_map
            minimum_distance = numpy.ma.minimum(
                minimum_distance, standardized_distance_to_river_map)
            minimum_distance = numpy.ma.minimum(
                minimum_distance, standardized_distance_to_road_map)
            maintainance_maps = {}
            steepness_maps = {}
            floor_biomass_maps = {}
            fertility_maps = {}
            yield_maps = {}
            for livetype in LIVELIHOOD[1:]:
                fertility_maps[livetype] = biophysical2[livetype][
                                               SOIL_FERTILITY] * \
                                           standardized_fertility_map
                yield_maps[livetype] = biophysical2[livetype][
                                           YIELD] * \
                                       standardized_yield[livetype]
                distance_maps[livetype] = biophysical2[livetype][
                                              TRANSPORT_ACCESS] * \
                                          numpy.ma.minimum(minimum_distance,
                                                        standardized_distance_to_factory_maps[
                                                            livetype])
                maintainance_maps[livetype] = \
                biophysical2[livetype][PLOT_MAINTAINANCE] * \
                numpy.ma.minimum(standardized_settlement_map,
                              standardized_existing_plot_maps[livetype])
                steepness_maps[livetype] = biophysical2[livetype][
                                               STEEPNESS] * \
                                           standardized_slope_map
                floor_biomass_maps[livetype] = \
                biophysical2[livetype][
                    FLOOR_BIOMASS] * standardized_floor_biomass_map
                potential_area_maps[livetype] = able_area_maps[livetype] * (
                            fertility_maps[livetype] + yield_maps[livetype] +
                            suitable_maps[livetype]) / (1 + distance_maps[
                    livetype] + maintainance_maps[livetype] +
                                                        floor_biomass_maps[
                                                            livetype])
            potential_area_maps[OFF_NONFARM] = util.create_zero_map(area_map)

            # Calculating standardized potential area
            n = {}
            attr = {}
            sattr = {}
            ssattr = {}
            meanattr = {}
            sdattr = {}
            err = {}
            toterr = {}
            std = {}
            standardized_potential_maps = {}

            for livetype in LIVELIHOOD:
                n[livetype] = util.arraytotal(criticalzone_maps[livetype])
                sattr[livetype] = util.arraytotal(
                    potential_area_maps[livetype])
                ssattr[livetype] = util.arraytotal(
                    potential_area_maps[livetype] * potential_area_maps[
                        livetype])
                meanattr[livetype] = sattr[livetype] / n[livetype] if n[
                                                                          livetype] > 0 else 0
                sdattr[livetype] = 0 if n[livetype] <= 0 else numpy.sqrt(
                    ssattr[livetype] / n[livetype] - meanattr[livetype] *
                    meanattr[livetype])
                err[livetype] = numpy.sqrt(
                    potential_area_maps[livetype] - meanattr[livetype]) / n[
                                    livetype] if n[livetype] > 0 else 0
                toterr[livetype] = util.arraytotal(err[livetype])
                std[livetype] = numpy.sqrt(toterr[livetype])
                standardized_potential_maps[livetype] = -5 * area_map if \
                sdattr[livetype] == 0 else (potential_area_maps[livetype] -
                                            meanattr[livetype]) / sdattr[
                                               livetype]
            standardized_potential_class_maps = {}
            for livetype in LIVELIHOOD:
                standardized_potential_class_maps[livetype] = {}
                standardized_potential_class_maps[livetype][Z1] = (
                            standardized_potential_maps[livetype] < 0)
                standardized_potential_class_maps[livetype][Z2] = (
                                                                              standardized_potential_maps[
                                                                                  livetype] < 1) & (
                                                                              standardized_potential_maps[
                                                                                  livetype] >= 0)
                standardized_potential_class_maps[livetype][Z3] = (
                                                                              standardized_potential_maps[
                                                                                  livetype] < 2) & (
                                                                              standardized_potential_maps[
                                                                                  livetype] >= 1)
                standardized_potential_class_maps[livetype][Z4] = (
                                                                              standardized_potential_maps[
                                                                                  livetype] >= 2) & (
                                                                              standardized_potential_maps[
                                                                                  livetype] < 3)
                standardized_potential_class_maps[livetype][Z5] = \
                standardized_potential_maps[
                    livetype] >= 4
            standardized_potential_class_area = {}
            for livetype in LIVELIHOOD:
                standardized_potential_class_area[livetype] = {}
                for z in Zs:
                    standardized_potential_class_area[livetype][
                        z] = util.arraytotal(
                        standardized_potential_class_maps[livetype][z])
            total_potential_class_area = {}
            for livetype in LIVELIHOOD:
                total_potential_class_area[livetype] = {}
                total_potential_class_area[livetype][Z5] = 0
                for idx, z in enumerate(Zs[::-1][1:]):
                    total_potential_class_area[livetype][z] = \
                    total_potential_class_area[livetype][
                        Zs[5 - idx - 1]] + \
                    standardized_potential_class_area[livetype][
                        Zs[5 - idx - 1]]

            for livetype in LIVELIHOOD:
                available_money = 0
                for farmerType in FARMERS:
                    available_money += labour_money_fraction[livetype][
                                           farmerType] * total_labour[farmerType]
                available_money = available_money + \
                                  subsidy[livetype][
                                      ESTABLISHMENT_SUBSIDY] * \
                                  subsidy_availability[livetype][
                                      time] if using_timeseries else available_money + \
                                                                     subsidy[
                                                                         livetype][
                                                                         ESTABLISHMENT_SUBSIDY]
                available_labour_timeseries[livetype].append(available_money)

            for livetype in LIVELIHOOD:
                temp = 0
                for farmerType in FARMERS:
                    temp += labour_money_fraction[livetype][farmerType] * balance

                if using_timeseries:
                    temp += subsidy[livetype][ESTABLISHMENT_SUBSIDY] * subsidy_availability[livetype][time]
                else:
                    temp += subsidy[livetype][ESTABLISHMENT_SUBSIDY]
                available_money_timeseries[livetype].append(temp)
            for livetype in LIVELIHOOD[1:]:
                land_expansion_labour_timeseries[livetype].append(
                    available_labour_timeseries[livetype][time] /
                    establistment_labour[livetype] if establistment_labour[
                                                          livetype] > 0 else 0)
                land_expansion_budget_timeseries[livetype].append(
                    available_money_timeseries[livetype][time] /
                    establistment_cost[livetype] if establistment_cost[livetype] > 0 else 0)
                actual_area_expansion_timeseries[livetype].append(
                    min(min(land_expansion_budget_timeseries[livetype][time],
                            land_expansion_labour_timeseries[livetype][time]),
                        potential_area_expansion_timseries[livetype][time]))
            actual_area_expansion_timeseries[OFF_NONFARM].append(0)

            expansion_probably = {}
            for livetype in LIVELIHOOD:
                expansion_probably[livetype] = {}
                for z in Zs:
                    expansion_probably[livetype][z] = (
                        max(0,
                            min(standardized_potential_class_area[livetype][z],
                                actual_area_expansion_timeseries[livetype][
                                    time] -
                                total_potential_class_area[livetype][z])) /
                        standardized_potential_class_area[livetype][z] if
                        standardized_potential_class_area[livetype][
                            z] > 0 else 0
                    )
            # print expansion_probably
            all_fire_ignition_map = util.create_bool_map(area_map, 0)
            new_plot_maps = {}
            fire_ignition_maps = {}
            pfireuse = 0
            for livetype in LIVELIHOOD:
                expansion = 0
                for z in Zs:
                    expansion += standardized_potential_class_maps[livetype][
                                     z] * expansion_probably[livetype][z]
                expansion *= criticalzone_maps[livetype]
                new_plot_maps[livetype] = (numpy.random.uniform(0, 1,
                                                             area_map.shape) < expansion) & irreversed_map
                new_cultivate_areas_timeseries[livetype].append(
                    util.arraytotal(new_plot_maps[livetype]))
                fire_ignition_maps[livetype] = util.arrayfill(
                    util.uniform(
                        new_plot_maps[livetype]),
                    1) * area_map < 0  # pfireuse => add to input
                all_fire_ignition_map |= fire_ignition_maps[livetype]
            all_new_plot_map = util.create_bool_map(area_map, 0)
            cost = 0
            for product in ANNUAL_CROPS + TREE_BASED_SYSTEMS:
                all_new_plot_map = all_new_plot_map | new_plot_maps[livetype]
                cost += establistment_cost[product] * util.arraytotal(
                    new_plot_maps[product])
            establisment_cost_timeseries.append(cost)

            total_demand = {}
            for livetype in LIVELIHOOD:
                total_demand[livetype] = total_population_timeseries[time] * \
                                         biophysical2[livetype][
                                             DEMAND_PER_CAPITA]
                price = balance / price_timeseries[livetype][time] if \
                price_timeseries[livetype][time] > 0 else 0
                remain = store[livetype] * (
                            1 - biophysical2[livetype][
                        LOSS_FRACTION])
                expense_timeseries[livetype].append(
                    min(price, max(total_demand[livetype] - remain, 0), 0))
                income_timeseries[livetype].append(max(0, remain *
                                                       biophysical2[
                                                           livetype][
                                                           PROBABLY_TO_SELL]))
                if total_demand[livetype] <= 0:
                    effective = 0
                else:
                    effective = 1 - (
                                store[livetype] + expense_timeseries[livetype][
                            time] - income_timeseries[livetype][time]) / \
                                total_demand[livetype]
                supply_sufficiency_timeseries[livetype].append(effective)
                store[livetype] = max(
                    remain + expense_timeseries[livetype][time] - total_demand[
                        livetype] - income_timeseries[livetype][time], 0)
            total_net_income = max(
                total_selling - total_buying - total_nonlabor_costs - total_labour_costs - cost,
                0)
            total_secondary_consumption = max(
                total_net_income * demography[
                    SECONDARY_CONSUMPTION_FRACTION], 0)
            balance = balance + total_net_income - total_secondary_consumption
            balance = balance * (1 - impact[IMPACT_OF_DISASTER][
                TO_MONEY_CAPITAL] / 100)
            non_selected_agriculture_plot_map = ~all_new_plot_map & marginal_agriculture_map & marginalAF_map
            standardized_fire_ignition_map = util.arrayfill(util.spreadmap(all_fire_ignition_map, prototype), 1e11)
            # standardized_fire_ignition_map = util.create_zero_map(area_map)
            fire_map = (util.arrayfill(util.uniform(
                standardized_fire_ignition_map < 2 * PIXEL_SIZE),
                                            1) < pfireuse) | all_fire_ignition_map
            output_fire_maps.append(fire_map)
            fire_area_timeseries.append(util.arraytotal(fire_map))
            total_population_timeseries[time] = total_population_timeseries[
                                                    time] * (1 +
                                                             demography[
                                                                 ANNUAL_GROWTH_RATE]) * (
                                                            1 -
                                                            impact[
                                                                IMPACT_OF_DISASTER][
                                                                TO_HUMAN] / 100)

            extension_availability = {}
            for livetype in LIVELIHOOD:
                extension_availability[livetype] = \
                extension_availability[livetype][
                    time] if using_timeseries else \
                social[OFF_NONFARM][CULTURAL_INFLUENCE]
            expected_return_to_labour = {}
            expected_return_to_land = {}

            for livetype in LIVELIHOOD:
                expected_return_to_labour[livetype] = {}
                expected_return_to_land[livetype] = {}
                for farmerType in FARMERS:
                    if (return_to_labour_timeseries[livetype][time] <= 0):
                        expected_return_to_labour[livetype][farmerType] = 0
                    else:
                        expected_return = \
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LABOUR][farmerType] + (
                                    farmer[ALPHA_FACTOR][farmerType] * (
                                        return_to_labour_timeseries[livetype][
                                            time] -
                                        economic1[livetype][
                                            ACTUAL_PROFITABILITY][
                                            RETURN_TO_LABOUR][farmerType]))
                        expected_return_to_labour[livetype][
                            farmerType] = expected_return + farmer[
                            BETA_FACTOR][farmerType] * extension_availability[livetype] * \
                                      social[livetype][
                                          EXTENSION_PROPERTY][CREDIBILITY] * \
                                      social[livetype][
                                          EXTENSION_PROPERTY][AVAILABILITY] * (
                                                  economic1[
                                                      livetype][
                                                      EXPECTED_PROFITABILITY][
                                                      RETURN_TO_LABOUR] - expected_return)
                for farmerType in FARMERS:
                    if (return_to_land_timeseries[livetype][time] <= 0):
                        expected_return_to_land[livetype][farmerType] = 0
                    else:
                        expected_return = \
                        economic1[livetype][ACTUAL_PROFITABILITY][
                            RETURN_TO_LAND][farmerType] + (
                                    farmer[ALPHA_FACTOR][farmerType] * (
                                    return_to_labour_timeseries[livetype][
                                        time] - economic1[livetype][
                                        ACTUAL_PROFITABILITY][RETURN_TO_LAND][
                                        farmerType]))
                        expected_return_to_land[livetype] = expected_return + \
                                                            farmer[
                                                                BETA_FACTOR][farmerType] * \
                                                            extension_availability[
                                                                livetype] * \
                                                            social[
                                                                livetype][
                                                                EXTENSION_PROPERTY][
                                                                CREDIBILITY] * \
                                                            social[
                                                                livetype][
                                                                EXTENSION_PROPERTY][
                                                                AVAILABILITY] * (
                                                                    economic1[
                                                                        livetype][
                                                                        EXPECTED_PROFITABILITY][
                                                                        RETURN_TO_LAND] - expected_return)

            soil_map = (1 + soil_recoverytime_map) * \
                       map_data_object[SOIL_FERTILITY][
                           MAXIMUM_SOIL_FERTILITY] - \
                       map_data_object[SOIL_FERTILITY][
                           INITIAL_SOIL_FERTILITY]
            soil_recovery_map = (soil_map > 0) * numpy.square(
                map_data_object[SOIL_FERTILITY][
                    MAXIMUM_SOIL_FERTILITY] -
                map_data_object[SOIL_FERTILITY][
                    INITIAL_SOIL_FERTILITY]) / \
                                map_data_object[SOIL_FERTILITY][
                                    INITIAL_SOIL_FERTILITY]
            soil_recovery_map = util.arrayfill(soil_recovery_map,
                                                    0) * area_map
            soil_ferlity_map = numpy.minimum(
                map_data_object[SOIL_FERTILITY][
                    MAXIMUM_SOIL_FERTILITY], numpy.maximum(
                    map_data_object[SOIL_FERTILITY][
                        INITIAL_SOIL_FERTILITY] + soil_recovery_map - soil_depletion_map,
                    0))

            output_soil_maps.append(soil_ferlity_map)

            forest_plot_map = (fire_map > 0) & (
                ~all_new_plot_map) | util.create_bool_map(
                map_data_object[DISASTERED_AREA],
                1) | non_selected_agriculture_plot_map
            plot_map = (landuse_map == LANDUSE_MAP[SETTLEMENT]) * \
                       LANDUSE_MAP[SETTLEMENT] * new_plot_maps[OFF_NONFARM] + (
                                   landuse_map == LANDUSE_MAP[
                               FOREST]) * LANDUSE_MAP[FOREST] * new_plot_maps[
                           TIMBER]

            for land in LANDUSE[2:]:
                plot_map += (landuse_map == LANDUSE_MAP[land]) * \
                            LANDUSE_MAP[land] + new_plot_maps[land]

            landuse_map = plot_map + forest_plot_map + (
                        plot_map > 0) * landuse_map

            ouput_land_use_maps.append(landuse_map)

            age_biomass_stats_maps = {}
            for forest_stage in FOREST_STAGES:
                age_biomass_stats_maps[forest_stage] = util.arraystat(
                    area_map,
                    biophysical1[FOREST][forest_stage][
                        LANDCOVER_AGE][INITIAL_LANDCOVER_AGE])
            agebased_biomass_map = 0

            for idx, forest_stage in enumerate(FOREST_STAGES[:-1]):
                agebased_biomass_map += ((aboveground_biomass_map > biophysical1[FOREST][forest_stage][LANDCOVER_PROPERTY][ABOVEGROUND_BIOMASS][MEAN]) & (aboveground_biomass_map < biophysical1[FOREST][FOREST_STAGES[idx + 1]][LANDCOVER_PROPERTY][ABOVEGROUND_BIOMASS][MEAN])) * age_biomass_stats_maps[forest_stage]

            output_aboveground_biomass_maps.append(agebased_biomass_map)

            self.signal.emit(output_timeseries, output_maps, time)
