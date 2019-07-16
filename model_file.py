from constant import *
import bisect
import copy
import read_input
import util
import file_util
import numpy as np

TIMESERIES = 'timeseries'
MAPS = 'maps'

output = {}
output[TIMESERIES] = {}
output[MAPS] = {}

standardized_potential_class_maps = {}


def create_nested_output(pattern, value=[]):
    data = dict()

    def make_nested_output(nested_pattern, current_data):
        for item in nested_pattern:
            if type(item) == str:
                current_data[item] = value
            else:
                for key in item.keys():
                    current_data[key] = {}
                    make_nested_output(item[key], current_data[key])

    make_nested_output(pattern, data)
    return data


output_timeseries = output[TIMESERIES]
output_maps = output[MAPS]

output_timeseries['Fire area'] = fire_area_timeseries = []
output_timeseries['Secondary consumption'] = secondary_consumption_timeseries = []
output_timeseries['Net income'] = net_income_timeseries = []
output_timeseries['Population'] = total_population_timeseries = [
    read_input.demography[read_input.DEMOGRAPHY[0]]]
output_timeseries['Aboveground biomass'] = aboveground_biomass_timeseries = []
output_timeseries['Aboveground carbon'] = aboveground_carbon_timeseries = []
output_timeseries['Establishment cost'] = establisment_cost_timeseries = []
output_timeseries['Potential area expansion'] = potential_area_expansion_timseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Non-labour costs'] = non_labour_cost_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Revenue'] = revenue_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Return to labour'] = return_to_labour_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Return to land'] = return_to_land_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Supply sufficiency'] = supply_sufficiency_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Land expansion labour'] = land_expansion_labour_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Land expansion budget'] = land_expansion_budget_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Actual area expansion'] = actual_area_expansion_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['New cultivated areas'] = new_cultivate_areas_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Available labour'] = available_labour_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Available money'] = available_money_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Expense'] = expense_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Income'] = income_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Potential yield'] = potential_yield_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)
output_timeseries['Actual yield'] = actual_yield_timeseries = create_nested_output(
    read_input.LIVELIHOOD
)

output_timeseries['Land cover area'] = landcover_area_timeseries = create_nested_output(
    read_input.LAND
)

output_timeseries['Land use area'] = landuse_area_timeseries = create_nested_output(
    read_input.LANDUSE
)

output_timeseries['Subcatchment area '] = subcatchment_area_timeseries = create_nested_output(
    SUBCATCHMENT)

labour_money_fraction = create_nested_output(read_input.LIVELIHOOD, {})
land_money_fraction = create_nested_output(read_input.LIVELIHOOD, {})

balance = read_input.demography[read_input.DEMOGRAPHY[4]]

# Simulating

PERIODS = [0, 50, 100, 150, 200]
PIXEL_SIZE = 4
simulation_time = 2
using_timeseries = False
# print util.get_shape(read_input.economic1, PRICE)
# print util.calstat_shape(util.get_shape(read_input.economic1, PRICE))
# print read_input.economic1['Tree-based system 6'].keys()


def create_zero_map(original_data):
    return 0 * original_data


def create_bool_map(original_data, value):
    return original_data == value


store = {}
for livetype in LIVELIHOOD:
    store[livetype] = read_input.demography[INITIAL_POPULATION] * \
        read_input.biophysical2[livetype][DEMAND_PER_CAPITA]

area_map = file_util.map_data_object[SIMULATED_AREA]
landcover_map = file_util.map_data_object[INITIAL_LANDCOVER]
irreversed_map = ~create_bool_map(file_util.map_data_object[PROTECTED_AREA], 1)
marginal_agriculture_map = create_bool_map(area_map, 0)
marginalAF_map = create_bool_map(area_map, 0)

# print create_zero_map(file_util.map_data_object[SIMULATED_AREA])
profitability = {}

price_timeseries = create_nested_output(LIVELIHOOD)
aboveground_biomass_map = create_zero_map(landcover_map)
standardized_distance_to_factory_maps = {}
standardized_slope_map = file_util.standardize(
    file_util.map_data_object[SLOPE])

for time in xrange(simulation_time):
    total_buying = 0
    total_selling = 0
    current_period = bisect.bisect(PERIODS, time)
    if (time > 0):
        total_population_timeseries.append(
            total_population_timeseries[time - 1])
    if (using_timeseries):
        price_timeseries = copy.deepcopy(read_input.product_price)[time]
    else:
        for livetype in LIVELIHOOD:
            price_timeseries[livetype].append(util.calstat_shape(
                util.get_shape(read_input.economic1, PRICE)))
    harvesting_efficiency = util.calstat_shape(
        util.get_shape(read_input.biophysical2, HARVESTING))
    establistment_cost = util.calstat_shape(
        util.get_shape(read_input.economic1, ESTABLISTMENT_COST))
    establistment_labour = util.calstat_shape(
        util.get_shape(read_input.economic1, ESTABLISTMENT_LABOUR))
    external_labour = util.calstat_shape(
        util.get_shape(read_input.economic1, EXTERNAL_LABOUR))
    total_labour = {
        farmer: (total_population_timeseries[time] *
                 read_input.farmer[POPULATION_FRACTION][farmer] *
                 read_input.demography[LABOUR_FRACTION] *
                 read_input.demography[WORKING_DAYS] * (
            1 - read_input.impact[IMPACT_OF_DISASTER][TO_WORKING_DAY] / 100.0)
        ) for farmer in FARMERS
    }

    standardized_distance_to_road_map = file_util.standardize(
        file_util.distance_to_road_maps_array[current_period])
    standardized_distance_to_market_map = file_util.standardize(
        file_util.distance_to_market_maps_array[current_period])
    standardized_distance_to_factory_maps = {
        tree: file_util.standardize(file_util.distance_to_factory_maps_array[tree][current_period]) for tree in PRODUCTS
    }
    standardized_distance_to_river_map = file_util.standardize(
        file_util.distance_to_river_maps_array[current_period])
    for farmer in FARMERS:
        land_sum = 0
        count = 0
        labour_sum = 0
        for livetype in LIVELIHOOD:
            land_sum += read_input.social[livetype][CULTURAL_INFLUENCE] * max(
                0, read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LAND][farmer]) ** read_input.farmer[LANDUSE_PRIORITY][farmer]
            labour_sum += read_input.social[livetype][CULTURAL_INFLUENCE] * max(
                0, read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][farmer]) ** read_input.farmer[LANDUSE_PRIORITY][farmer]
            count += 1

        for livetype in LIVELIHOOD:
            land_money_fraction[livetype][farmer] = read_input.social[livetype][CULTURAL_INFLUENCE] * max(
                0, read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LAND][farmer]) ** (read_input.farmer[LANDUSE_PRIORITY][farmer] / land_sum) if land_sum > 0 else 1 / count
            labour_money_fraction[livetype][farmer] = read_input.social[livetype][CULTURAL_INFLUENCE] * max(
                0, read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][farmer]) ** (read_input.farmer[LANDUSE_PRIORITY][farmer] / labour_sum) if labour_sum > 0 else 1 / count

        land_money_fraction[OFF_NONFARM][farmer] = 0

    for livetype in LIVELIHOOD:
        available_labour_timeseries[livetype].append(
            external_labour[livetype] + labour_money_fraction[livetype][farmer] * total_labour[farmer] for farmer in FARMERS
        )

    current_landcover_map = create_zero_map(
        file_util.map_data_object[INITIAL_LANDCOVER]
    )
    current_landuse_map = create_zero_map(
        area_map
    ) if file_util.distance_to_settlement_maps_array[current_period] is None else file_util.landuse_map

    standardized_settlement_map = file_util.standardize(
        file_util.distance_to_settlement_maps_array[current_period])

    for land in LANDCOVER:
        if type(land) is str:
            current_landcover_map += (
                current_landuse_map == LANDCOVER_MAP[land]
            ) * LANDCOVER_MAP[land]
        else:
            for key in land.keys():
                for idx, land_stage in enumerate(land[key][:-1]):
                    landage = read_input.biophysical1[key][land_stage][LANDCOVER_AGE][LANDCOVER_AGE_BOUNDARY]
                    landage_upper = read_input.biophysical1[key][land[key]
                                                                 [idx + 1]][LANDCOVER_AGE][LANDCOVER_AGE_BOUNDARY]
                    current_landcover_map += (current_landuse_map == LANDUSE_MAP[key]) * (file_util.landage_map >= landage) * (
                        file_util.landage_map < landage_upper) * LANDCOVER_MAP[key][land_stage]
                current_landcover_map += (current_landuse_map == LANDUSE_MAP[key]) * (
                    file_util.landage_map >= landage_upper) * LANDCOVER_MAP[key][land[key][-1]]

    for land in LANDCOVER:
        if type(land) is str:
            landcover_area_timeseries[land].append(file_util.arraytotal(
                current_landcover_map == LANDCOVER_MAP[land]))
        else:
            for key in land.keys():
                for land_stage in land[key]:
                    landcover_area_timeseries[key][land_stage].append(
                        file_util.arraytotal(current_landcover_map == LANDCOVER_MAP[key][land_stage]))

    (landuse_area_timeseries[land].append(file_util.arraytotal(
        file_util.landuse_map == LANDUSE_MAP[land]) * PIXEL_SIZE) for land in LANDUSE)

    subcatchment_landcover_area = {}
    for subcatchment in SUBCATCHMENT:
        subcatchment_area = 0
        for land in LANDCOVER:
            if type(land) is str:
                subcatchment_area += file_util.arraytotal((file_util.map_data_object[SUBCATCHMENT_AREA] == SUBCATCHMENT_IDS[subcatchment]) * (
                    landcover_map == LANDCOVER_MAP[land])) * PIXEL_SIZE
            else:
                for key in land.keys():
                    for land_stage in land[key]:
                        subcatchment_area += file_util.arraytotal((file_util.map_data_object[SUBCATCHMENT_AREA] == SUBCATCHMENT_IDS[subcatchment]) * (
                            landcover_map == LANDCOVER_MAP[key][land_stage])) * PIXEL_SIZE
        subcatchment_landcover_area[subcatchment] = subcatchment_area
        subcatchment_area_timeseries[subcatchment].append(file_util.arraytotal(
            file_util.map_data_object[SUBCATCHMENT_AREA] == SUBCATCHMENT_IDS[subcatchment]) * PIXEL_SIZE)

    current_criticalzone_map = create_zero_map(area_map) == 1
    for forest_stage in FOREST_STAGES:
        current_criticalzone_map |= (current_landcover_map ==
                                     LANDCOVER_MAP[FOREST][forest_stage])
    for tree in TREE_BASED_SYSTEMS:
        current_criticalzone_map |= (current_landcover_map ==
                                     LANDCOVER_MAP[tree][TREE_BASED_STAGES[-1]])
    current_criticalzone_map = current_criticalzone_map | marginal_agriculture_map | marginalAF_map & (
        ~create_bool_map(file_util.map_data_object[PROTECTED_AREA], 1))
    criticalzone_area = file_util.arraytotal(
        current_criticalzone_map) * PIXEL_SIZE
    for livetype in LIVELIHOOD:
        population_fraction = 0
        for farmer in FARMERS:
            population_fraction += read_input.farmer[POPULATION_FRACTION][farmer]
        potential_area_expansion_timseries[livetype].append(
            criticalzone_area * population_fraction
        )
    potential_area_expansion_timseries[OFF_NONFARM][time] = 0
    random_criticalzone_map = file_util.arrayfill(
        file_util.uniform(current_criticalzone_map), 1) * area_map
    all_new_plots_map = create_bool_map(area_map, 0)
    cummulate_criticalzone_map = create_zero_map(area_map)
    criticalzone_prob = {}
    criticalzone_maps = {}

    for livetype in LIVELIHOOD:
        criticalzone_prob[livetype] = potential_area_expansion_timseries[livetype][time] / \
            criticalzone_area if criticalzone_area > 0 else 0
        cummulate_criticalzone_map += criticalzone_prob[livetype]
        criticalzone_maps[livetype] = (random_criticalzone_map < cummulate_criticalzone_map) & (
            ~all_new_plots_map) & current_criticalzone_map
        if livetype in file_util.map_data_object[SUITABLE_AREA].keys():
            criticalzone_maps[livetype] &= (
                file_util.map_data_object[SUITABLE_AREA][livetype] == 1)
        all_new_plots_map |= criticalzone_maps[livetype]

    phzone_maps = {}
    phzone_maps[OFF_NONFARM] = create_bool_map(area_map, 0)
    phzone_maps[TIMBER] = copy.deepcopy(
        file_util.map_data_object[INITIAL_LOGGING_AREA])
    for crop in ANNUAL_CROPS:
        phzone_maps[crop] = (
            landcover_map == LANDCOVER_MAP[crop]) & irreversed_map

    phzone_maps[NON_TIMBER_FOREST_PRODUCT] = create_bool_map(area_map, 0)
    for forest_stage in FOREST_STAGES:
        phzone_maps[NON_TIMBER_FOREST_PRODUCT] |= landcover_map == LANDCOVER_MAP[FOREST][forest_stage]

    for tree in TREE_BASED_SYSTEMS:
        phzone_maps[tree] = create_bool_map(area_map, 0)
        for tree_stage in TREE_BASED_STAGES:
            phzone_maps[tree] |= (
                landcover_map == LANDCOVER_MAP[tree][tree_stage])
        phzone_maps[tree] = phzone_maps[tree] & irreversed_map

    harvesting_area = {}
    existing_plot_maps = {}
    for livetype in LIVELIHOOD:
        harvesting_area[livetype] = file_util.arraytotal(phzone_maps[livetype])
        # existing_plot_map = file_util.spreadmap(phzone_maps[livetype], 0) windows
        existing_plot_maps[livetype] = area_map

    soil_depletion_map = create_zero_map(area_map)
    soil_recoverytime_map = create_zero_map(area_map)
    for land in LANDCOVER:
        if (type(land) is str):
            soil_depletion_map += (landcover_map == LANDCOVER_MAP[land]) * file_util.arraystat(
                area_map, read_input.biophysical1[land][SOIL_FERTILITY][DEPLETION_RATE])
            soil_recoverytime_map += (landcover_map == LANDCOVER_MAP[land]) * file_util.arraystat(
                area_map, read_input.biophysical1[land][SOIL_FERTILITY][HALFT_TIME_RECOVERY])
        else:
            for key in land.keys():
                for land_stage in land[key]:
                    soil_depletion_map += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.arraystat(
                        area_map, read_input.biophysical1[key][land_stage][SOIL_FERTILITY][DEPLETION_RATE])
                    soil_recoverytime_map += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.arraystat(
                        area_map, read_input.biophysical1[key][land_stage][SOIL_FERTILITY][HALFT_TIME_RECOVERY])

    soil_depletion_map = soil_depletion_map * \
        file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY]
    soil_depletion_map = file_util.arrayuper(
        file_util.arraylower(soil_depletion_map, 1), 0)

    total_labour_costs = 0
    total_nonlabor_costs = 0
    crop_area_map = create_bool_map(area_map, 0)
    for crop in ANNUAL_CROPS:
        crop_area_map |= landcover_map == LANDCOVER_MAP[crop]

    pyield = {}
    non_labour_cost = {}
    for livetype in LIVELIHOOD:
        pyield[livetype] = 0.0

        for land in LANDCOVER:
            if land in ANNUAL_CROPS:
                pyield[livetype] += (landcover_map == LANDCOVER_MAP[land]) * file_util.arraystat(
                    area_map, read_input.biophysical1[land][LANDCOVER_PROPERTY][YIELD]) * soil_depletion_map
            else:
                if (type(land) is str):
                    pyield[livetype] += (landcover_map == LANDCOVER_MAP[land]) * file_util.arraystat(
                        area_map, read_input.biophysical1[land][LANDCOVER_PROPERTY][YIELD])
                else:
                    for key in land.keys():
                        for land_stage in land[key]:
                            pyield[livetype] += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.arraystat(
                                area_map, read_input.biophysical1[key][land_stage][LANDCOVER_PROPERTY][YIELD])
    for livetype in LIVELIHOOD:
        non_labour_cost[livetype] = 0.0
        for land in LANDCOVER:
            if type(land) is str:
                non_labour_cost[livetype] += file_util.arraystat(
                    area_map, read_input.economic2[land][NONLABOUR_COST])
            else:
                for key in land.keys():
                    for land_stage in land[key]:
                        non_labour_cost[livetype] += file_util.arraystat(
                            area_map, read_input.economic2[key][land_stage][NONLABOUR_COST])

    for livetype in LIVELIHOOD:
        potential_yield_timeseries[livetype].append(
            file_util.arraytotal(pyield[livetype] * phzone_maps[livetype]))
        actual_yield_timeseries[livetype].append(min(
            potential_yield_timeseries[livetype][time], available_labour_timeseries[livetype][time] * harvesting_efficiency[livetype]))

        subsidy = read_input.subsidy[livetype][MANAGEMENT_SUBSIDY] * \
            read_input.subsidy_availability[livetype][
                time] if using_timeseries else read_input.subsidy[livetype][MANAGEMENT_SUBSIDY]
        non_labour_cost_timeseries[livetype].append(
            max(file_util.arraytotal(non_labour_cost[livetype] * phzone_maps[livetype]) - subsidy, 0))

        total_nonlabor_costs += non_labour_cost_timeseries[livetype][time]
        revenue_timeseries[livetype].append(
            actual_yield_timeseries[livetype][time] * price_timeseries[livetype][time])
        profitability[livetype] = revenue_timeseries[livetype][time] - \
            non_labour_cost_timeseries[livetype][time] - \
            external_labour[livetype] * price_timeseries[livetype][time]
        return_to_labour_timeseries[livetype].append(
            profitability[livetype] / available_labour_timeseries[livetype][time] if available_labour_timeseries[livetype][time] > 0 else 0)
        return_to_land_timeseries[livetype].append(
            profitability[livetype] / harvesting_area[livetype] if harvesting_area[livetype] > 0 else 0)

        return_to_land_timeseries[OFF_NONFARM][time] = 0
        return_to_labour_timeseries[OFF_NONFARM][time] = max(
            return_to_labour_timeseries[OFF_NONFARM][time], 0)
    marginal_agriculture_map = create_bool_map(area_map, 0)
    for crop in ANNUAL_CROPS:
        marginal_agriculture_map |= (landcover_map == LANDCOVER_MAP[crop] |
                                     ((pyield[crop] < 0.5 * PIXEL_SIZE) |
                                      ((read_input.economic1[crop][ACTUAL_PROFITABILITY][RETURN_TO_LAND][FARMER1] < 0) & (read_input.economic1[crop][ACTUAL_PROFITABILITY][RETURN_TO_LAND][FARMER2] < 0)) |
                                      ((read_input.economic1[crop][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][FARMER1] < 0) & (read_input.economic1[crop][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][FARMER2] < 0)) & create_bool_map(area_map, 1)))
    marginalAF_map = create_bool_map(area_map, 0)
    for tree in TREE_BASED_SYSTEMS:
        for tree_stage in TREE_BASED_STAGES[-2:]:
            marginalAF_map |= (
                (landcover_map == LANDCOVER_MAP[tree][tree_stage]) & (profitability[tree] < 0))

    floor_biomass_fraction_map = create_zero_map(area_map)
    potential_fire_escape_map = create_zero_map(area_map)
    for land in LANDCOVER:
        if (type(land) is str):
            aboveground_biomass_map += (landcover_map == LANDCOVER_MAP[land]) * file_util.stat(
                read_input.biophysical1[land][LANDCOVER_PROPERTY][ABOVEGROUND_BIOMASS])
            floor_biomass_fraction_map += (landcover_map == LANDCOVER_MAP[land]) * file_util.stat(
                read_input.biophysical1[land][LANDCOVER_PROPERTY][FLOOR_BIOMASS_FRACTION]
            )
            potential_fire_escape_map += (landcover_map == LANDCOVER_MAP[land]) * file_util.stat(
                read_input.biophysical1[land][LANDCOVER_PROPERTY][PROBABLY_OF_FIRE_SPREADING]
            )
        else:
            for key in land.keys():
                for land_stage in land[key]:
                    aboveground_biomass_map += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.stat(
                        read_input.biophysical1[key][land_stage][LANDCOVER_PROPERTY][ABOVEGROUND_BIOMASS])
                    floor_biomass_fraction_map += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.stat(
                        read_input.biophysical1[key][land_stage][LANDCOVER_PROPERTY][FLOOR_BIOMASS_FRACTION]
                    )
                    potential_fire_escape_map += (landcover_map == LANDCOVER_MAP[key][land_stage]) * file_util.stat(
                        read_input.biophysical1[key][land_stage][LANDCOVER_PROPERTY][PROBABLY_OF_FIRE_SPREADING]
                    )

    logged_timber_map = potential_yield_timeseries[TIMBER][time] * phzone_maps[TIMBER] / \
        harvesting_area[TIMBER] if (
            harvesting_area[TIMBER]) > 0 else create_zero_map(area_map)
    logged_biomass_map = (
        file_util.map_data_object[INITIAL_LOGGING_AREA] * aboveground_biomass_map * 0.01)
    aboveground_biomass_map = aboveground_biomass_map - logged_biomass_map
    aboveground_biomass_map[aboveground_biomass_map < 0] = 0
    aboveground_carbon_map = aboveground_biomass_map * \
        read_input.impact[CONVERTION][BIOMASS_TO_CARBON]
    floor_biomass_map = aboveground_biomass_map * floor_biomass_fraction_map
    aboveground_biomass_timeseries.append(
        file_util.arraytotal(aboveground_biomass_map))
    aboveground_carbon_timeseries.append(
        file_util.arraytotal(aboveground_carbon_map))
    for livetype in LIVELIHOOD:
        store[livetype] = max(0, store[livetype] * (1 -
                                                    read_input.biophysical2[livetype][LOSS_FRACTION]) + potential_yield_timeseries[livetype][time])
    standardized_fertility_map = file_util.standardize(
        file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY])
    standardized_floor_biomass_map = file_util.standardize(floor_biomass_map)
    standardized_existing_plot_maps = {}
    for livetype in LIVELIHOOD:
        standardized_existing_plot_maps[livetype] = file_util.standardize(
            existing_plot_maps[livetype])
    max_potential_yield = 0
    for livetype in LIVELIHOOD:
        max_potential_yield = max(
            max_potential_yield, potential_yield_timeseries[livetype][time])
    standardized_yield = {}
    for livetype in LIVELIHOOD:
        standardized_yield[livetype] = 0 if max_potential_yield == 0 else potential_yield_timeseries[livetype][time] / max_potential_yield

    potential_area_maps = {}
    able_area_maps = {}
    suitable_maps = {}
    distance_maps = {}

    for livetype in [NON_TIMBER_FOREST_PRODUCT, TIMBER]:
        able_area_maps[livetype] = irreversed_map
        suitable_maps[livetype] = create_zero_map(area_map)
    for livetype in ANNUAL_CROPS:
        able_area_maps[livetype] = ~marginal_agriculture_map & irreversed_map
        suitable_maps[livetype] = read_input.biophysical2[livetype][LAND_SUITABILITY] * \
            file_util.map_data_object[SUITABLE_AREA][livetype]
    for livetype in TREE_BASED_SYSTEMS:
        able_area_maps[livetype] = ~marginalAF_map & irreversed_map
        suitable_maps[livetype] = read_input.biophysical2[livetype][LAND_SUITABILITY] * \
            file_util.map_data_object[SUITABLE_AREA][livetype]

    minimum_distance = standardized_distance_to_market_map
    minimum_distance = np.ma.minimum(
        minimum_distance, standardized_distance_to_river_map)
    minimum_distance = np.ma.minimum(
        minimum_distance, standardized_distance_to_road_map)
    maintainance_maps = {}
    steepness_maps = {}
    floor_biomass_maps = {}
    fertility_maps = {}
    yield_maps = {}
    for livetype in LIVELIHOOD[1:]:
        fertility_maps[livetype] = read_input.biophysical2[livetype][SOIL_FERTILITY] * \
            standardized_fertility_map
        yield_maps[livetype] = read_input.biophysical2[livetype][YIELD] * \
            standardized_yield[livetype]
        distance_maps[livetype] = read_input.biophysical2[livetype][TRANSPORT_ACCESS] * \
            np.ma.minimum(minimum_distance,
                          standardized_distance_to_factory_maps[livetype])
        maintainance_maps[livetype] = read_input.biophysical2[livetype][PLOT_MAINTAINANCE] * \
            np.ma.minimum(standardized_settlement_map,
                          standardized_existing_plot_maps[livetype])
        steepness_maps[livetype] = read_input.biophysical2[livetype][STEEPNESS] * \
            standardized_slope_map
        floor_biomass_maps[livetype] = read_input.biophysical2[livetype][FLOOR_BIOMASS] * standardized_floor_biomass_map
        potential_area_maps[livetype] = able_area_maps[livetype] * (fertility_maps[livetype] + yield_maps[livetype] + suitable_maps[livetype]) / ( 1 + distance_maps[livetype] + maintainance_maps[livetype] + floor_biomass_maps[livetype])
    potential_area_maps[OFF_NONFARM] = create_zero_map(area_map)

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
        n[livetype] = file_util.arraytotal(criticalzone_maps[livetype])
        sattr[livetype] = file_util.arraytotal(potential_area_maps[livetype])
        ssattr[livetype] = file_util.arraytotal(potential_area_maps[livetype] * potential_area_maps[livetype])
        meanattr[livetype] = sattr[livetype] / n[livetype] if n[livetype] > 0 else 0
        sdattr[livetype] = 0 if n[livetype] <=0 else np.sqrt(ssattr[livetype]/n[livetype] - meanattr[livetype] * meanattr[livetype])
        err[livetype] = np.sqrt(potential_area_maps[livetype] - meanattr[livetype]) / n[livetype] if n[livetype] > 0 else 0
        toterr[livetype] = file_util.arraytotal(err[livetype])
        std[livetype] = np.sqrt(toterr[livetype])
        standardized_potential_maps[livetype] = -5 * area_map if sdattr[livetype] == 0 else (potential_area_maps[livetype] - meanattr[livetype]) / sdattr[livetype]
    standardized_potential_class_maps = {}
    for livetype in LIVELIHOOD:
        standardized_potential_class_maps[livetype] = {}
        standardized_potential_class_maps[livetype][Z1] = (standardized_potential_maps[livetype] < 0)
        standardized_potential_class_maps[livetype][Z2] = (standardized_potential_maps[
            livetype] < 1) & (standardized_potential_maps[livetype] >= 0)
        standardized_potential_class_maps[livetype][Z3] = (standardized_potential_maps[
            livetype] < 2) & (standardized_potential_maps[livetype] >=1)
        standardized_potential_class_maps[livetype][Z4] = (standardized_potential_maps[
            livetype] >= 2) & (standardized_potential_maps[livetype] < 3)
        standardized_potential_class_maps[livetype][Z5] = standardized_potential_maps[
            livetype] >= 4
    standardized_potential_class_area = {}
    for livetype in LIVELIHOOD:
        standardized_potential_class_area[livetype] = {}
        for z in Zs:
            standardized_potential_class_area[livetype][z] = file_util.arraytotal(standardized_potential_class_maps[livetype][z])
    total_potential_class_area = {}
    for livetype in LIVELIHOOD:
        total_potential_class_area[livetype] = {}
        total_potential_class_area[livetype][Z5] = 0
        for idx, z in enumerate(Zs[::-1][1:]):
            total_potential_class_area[livetype][z] = total_potential_class_area[livetype][
                Zs[5 - idx - 1]] + standardized_potential_class_area[livetype][Zs[5 - idx - 1]]

    for livetype in LIVELIHOOD:
        available_money = 0
        for farmer in FARMERS:
            available_money += labour_money_fraction[livetype][farmer] * total_labour[farmer]
        available_money = available_money + read_input.subsidy[livetype][ESTABLISHMENT_SUBSIDY]*read_input.subsidy_availability[livetype][time] if using_timeseries else available_money + read_input.subsidy[livetype][ESTABLISHMENT_SUBSIDY]
        available_labour_timeseries[livetype].append(available_money)

    for livetype in LIVELIHOOD[1:]:
        land_expansion_labour_timeseries[livetype].append(available_labour_timeseries[livetype][time] / establistment_labour[livetype] if establistment_labour[livetype] > 0 else 0)
        land_expansion_budget_timeseries[livetype].append(available_money_timeseries[livetype][time] / establistment_cost[livetype] if establistment_cost[livetype] > 0 else 0)
        actual_area_expansion_timeseries[livetype].append(min(min(land_expansion_budget_timeseries[livetype][time],
        land_expansion_labour_timeseries[livetype][time]),
        potential_area_expansion_timseries[livetype][time]))
    actual_area_expansion_timeseries[OFF_NONFARM].append(0)

    expansion_probably = {}
    for livetype in LIVELIHOOD:
        expansion_probably[livetype] = {}
        for z in Zs:
            expansion_probably[livetype][z] = (
                max(0, min(standardized_potential_class_area[livetype][z], actual_area_expansion_timeseries[livetype][time] - total_potential_class_area[livetype][z])) / standardized_potential_class_area[livetype][z] if standardized_potential_class_area[livetype][z] > 0 else 0
            )
    # print expansion_probably
    all_fire_ignition_map = create_bool_map(area_map, 0)
    new_plot_maps = {}
    fire_ignition_maps = {}
    pfireuse = 0
    for livetype in LIVELIHOOD:
        expansion = 0
        for z in Zs:
            expansion += standardized_potential_class_maps[livetype][z] * expansion_probably[livetype][z]
        expansion *= criticalzone_maps[livetype]
        new_plot_maps[livetype] = (np.random.uniform(0, 1, area_map.shape) < expansion) & irreversed_map
        new_cultivate_areas_timeseries[livetype].append(file_util.arraytotal(new_plot_maps[livetype]))
        fire_ignition_maps[livetype] = file_util.arrayfill(file_util.uniform(
            new_plot_maps[livetype]), 1) * area_map < 0 #pfireuse => add to input
        all_fire_ignition_map |= fire_ignition_maps[livetype]
    all_new_plot_map = create_bool_map(area_map, 0)
    cost = 0
    for product in ANNUAL_CROPS + TREE_BASED_SYSTEMS:
        all_new_plot_map = all_new_plot_map | new_plot_maps[livetype]
        cost += establistment_cost[product] * file_util.arraytotal(new_plot_maps[product])
    establisment_cost_timeseries.append(cost)

    total_demand = {}
    for livetype in LIVELIHOOD:
        total_demand[livetype] = total_population_timeseries[time] * read_input.biophysical2[livetype][DEMAND_PER_CAPITA]
        price = balance / price_timeseries[livetype][time] if price_timeseries[livetype][time] > 0 else 0
        remain = store[livetype] * (1 - read_input.biophysical2[livetype][LOSS_FRACTION])
        expense_timeseries[livetype].append(min(price, max(total_demand[livetype] - remain, 0), 0))
        income_timeseries[livetype].append(max(0, remain * read_input.biophysical2[livetype][PROBABLY_TO_SELL]))
        if total_demand[livetype] <= 0:
            effective = 0
        else:
            effective = 1 - (store[livetype] + expense_timeseries[livetype][time] - income_timeseries[livetype][time]) / total_demand[livetype]
        supply_sufficiency_timeseries[livetype].append(effective)
        store[livetype] = max(remain + expense_timeseries[livetype][time] - total_demand[livetype] - income_timeseries[livetype][time], 0)
    total_net_income = max(total_selling - total_buying - total_nonlabor_costs - total_labour_costs - cost, 0)
    total_secondary_consumption = max(total_net_income * read_input.demography[SECONDARY_CONSUMPTION_FRACTION], 0)
    balance = balance + total_net_income - total_secondary_consumption
    balance = balance * (1 - read_input.impact[IMPACT_OF_DISASTER][TO_MONEY_CAPITAL] / 100)
    non_selected_agriculture_plot_map = ~all_new_plot_map & marginal_agriculture_map & marginalAF_map
    # standardized_fire_ignition_map = file_util.arrayfill(file_util.spreadmap(all_fire_ignition_map), 1e11)
    standardized_fire_ignition_map = create_zero_map(area_map)
    fire_map = (file_util.arrayfill(file_util.uniform(standardized_fire_ignition_map < 2 * PIXEL_SIZE), 1) < pfireuse) | all_fire_ignition_map
    fire_area_timeseries.append(file_util.arraytotal(fire_map))
    total_population_timeseries[time] = total_population_timeseries[time] * (1 + read_input.demography[ANNUAL_GROWTH_RATE]) * (1 - read_input.impact[IMPACT_OF_DISASTER][TO_HUMAN] / 100)

    extension_availability = {}
    for livetype in LIVELIHOOD:
        extension_availability[livetype] = read_input.extension_availability[livetype][time] if using_timeseries else read_input.social[OFF_NONFARM][CULTURAL_INFLUENCE]
    expected_return_to_labour = {}
    expected_return_to_land = {}

    for livetype in LIVELIHOOD:
        expected_return_to_labour[livetype] = {}
        expected_return_to_land[livetype] = {}
        for farmer in FARMERS:
            if (return_to_labour_timeseries[livetype][time] <= 0):
                expected_return_to_labour[livetype][farmer] = 0
            else:
                expected_return = read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][farmer] + (read_input.farmer[ALPHA_FACTOR] * (return_to_labour_timeseries[livetype][time] - read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LABOUR][farmer]))
                expected_return_to_labour[livetype][farmer] = expected_return + read_input.farmer[BETA_FACTOR] * extension_availability[livetype] * read_input.social[livetype][EXTENSION_PROPERTY][CREDIBILITY] * read_input.social[livetype][EXTENSION_PROPERTY][AVAILABILITY] * (read_input.economic1[livetype][EXPECTED_PROFITABILITY][RETURN_TO_LABOUR] - expected_return)
        for farmer in FARMERS:
            if (return_to_land_timeseries[livetype][time] <= 0):
                expected_return_to_land[livetype][farmer] = 0
            else:
                expected_return = read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LAND][farmer] + (read_input.farmer[ALPHA_FACTOR] * (
                    return_to_labour_timeseries[livetype][time] - read_input.economic1[livetype][ACTUAL_PROFITABILITY][RETURN_TO_LAND][farmer]))
                expected_return_to_land[livetype] = expected_return + read_input.farmer[BETA_FACTOR] * extension_availability[livetype] * read_input.social[livetype][EXTENSION_PROPERTY][CREDIBILITY] * \
                    read_input.social[livetype][EXTENSION_PROPERTY][AVAILABILITY] * (
                        read_input.economic1[livetype][EXPECTED_PROFITABILITY][RETURN_TO_LAND] - expected_return)


    soil_map = (1 + soil_recoverytime_map) * file_util.map_data_object[SOIL_FERTILITY][MAXIMUM_SOIL_FERTILITY] - file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY]
    soil_recovery_map = (soil_map > 0) * np.square(file_util.map_data_object[SOIL_FERTILITY][MAXIMUM_SOIL_FERTILITY] - file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY]) / file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY]
    soil_recovery_map = file_util.arrayfill(soil_recovery_map, 0) * area_map
    soil_ferlity_map = np.minimum(file_util.map_data_object[SOIL_FERTILITY][MAXIMUM_SOIL_FERTILITY], np.maximum(file_util.map_data_object[SOIL_FERTILITY][INITIAL_SOIL_FERTILITY] + soil_recovery_map - soil_depletion_map, 0))
    forest_plot_map = (fire_map > 0) & (~all_new_plot_map) | create_bool_map(file_util.map_data_object[DISASTERED_AREA], 1) | non_selected_agriculture_plot_map
    plot_map = (file_util.landuse_map == LANDUSE_MAP[SETTLEMENT]) * LANDUSE_MAP[SETTLEMENT] * new_plot_maps[OFF_NONFARM] + (file_util.landuse_map == LANDUSE_MAP[FOREST]) * LANDUSE_MAP[FOREST] * new_plot_maps[TIMBER]

    for land in LANDUSE[2:]:
        plot_map += (file_util.landuse_map == LANDUSE_MAP[land]) * LANDUSE_MAP[land] + new_plot_maps[land]

    landuse_map = plot_map + forest_plot_map + (plot_map > 0) * file_util.landuse_map

    age_biomass_stats_maps = {}
    for forest_stage in FOREST_STAGES:
        age_biomass_stats_maps[forest_stage] = file_util.arraystat(
            file_util.area_map, read_input.biophysical1[FOREST][forest_stage][LANDCOVER_AGE][INITIAL_LANDCOVER_AGE])

