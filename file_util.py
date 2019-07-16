from constant import *
import json
import os.path
import gdal
import numpy as np
import util
# import read_input

MASKED_VALUE = -9999
MEAN = 'mean'
CV = 'cv'
PATH = 'Path'

# import pcraster


def load_map(path, masked_value=MASKED_VALUE):
    if os.path.isfile(path):
        original_arr = gdal.Open(path).ReadAsArray().astype(np.float32)
        return np.ma.masked_where(original_arr <= masked_value, original_arr)


def load_maps(map_model):
    def get_map(model, data={}):
        for map_obj in model:
            for key in map_obj.keys():
                if (type(map_obj[key]) is dict):
                    data[key] = load_map(map_obj[key][PATH])
                else:
                    data[key] = {}
                    get_map(map_obj[key], data[key])
    data = {}
    get_map(map_model, data)
    return data


def check_map_input(data):
    for datum in data:
        key = datum.keys()[0]
        if (type(datum[key]) is dict):
            print key, os.path.isfile(datum[key][PATH])
        else:
            check_map_input(datum[key])


def arraystat(array, statistics_data):
    rows, cols = array.shape
    return statistics_data[MEAN] * (
        1 + np.random.normal(0, 1, [rows, cols]) * statistics_data[CV]
    )


def arrayuper(array, value):
    arraymax = np.full(array.shape, value, dtype=np.float32)
    return np.ma.maximum(array, arraymax)


def arraylower(array, value):
    arraymin = np.full(array.shape, value, dtype=np.float32)
    return np.ma.minimum(array, arraymin)


def arraytotal(array):
    return np.ma.sum(array)


def arrayfull(array, value):
    return np.full(array.shape, value, dtype=np.float32)


def arrayfill(array, value):
    return np.ma.filled(array, value)


def uniform(array):
    [x, y] = array.shape
    rm = np.random.uniform(0, 1, (x, y))
    result = boolean2scalar(array) * rm
    result = np.ma.masked_where(result == 0, result)
    return result


def spreadmap(array, prototype):
    elevation = prototype.GetRasterBand(1).ReadAsArray()
    geoTransform = prototype.GetGeoTransform()
    pcraster.setclone(elevation.shape[0], elevation.shape[1], geoTransform[1],
                      geoTransform[0], geoTransform[3])
    sarray = 1.0 * array
    farr = np.ma.filled(sarray, -9999)
    n2p = pcraster.numpy2pcr(pcraster.Nominal, farr, -9999)
    n2p = pcraster.spread(n2p, 0, 1)
    p2n = pcraster.pcr2numpy(n2p, -9999)
    temp = np.ma.masked_where(p2n == -9999, p2n)
    return temp


def boolean2scalar(array):
    return 1.0 * array


def scalar2boolean(array):
    return array == 1


def calculate_statistics(statistics_data):
    return statistics_data[MEAN] * (1 + np.random.normal(0, 1) * statistics_data[CV])


def stat(statistics_data):
    return statistics_data[MEAN] * (1 + np.random.normal(0, 1) * statistics_data[CV])


def standardize(data):
    if (data is None):
        return None
    max_value = data.max()
    if max_value == 0:
        return 0.0 * data
    return data / float(max_value)


def create_zero_map(original_data):
    return 0 * original_data

# OFF_NONFARM = 'Off-/Non-farm'
# NON_TIMBER_FOREST_PRODUCT = 'Non-timber forest product'
# TIMBER = 'Timber'

# ANNUAL_CROPS = ['Annual crop ' + str(x) for x in xrange(1, 5, 1)]
# TREE_BASED_SYSTEMS = ['Tree-based system ' + str(x) for x in range(1, 9, 1)]


# PRODUCTS = [
#     NON_TIMBER_FOREST_PRODUCT,
#     TIMBER
# ] + ANNUAL_CROPS + TREE_BASED_SYSTEMS

# LAND_PERIODS = ['Period ' + str(x) for x in xrange(1, 5, 1)]

with open('./maps.json', 'r') as data_file:
    maps_data = json.load(data_file)
    map_data_object = load_maps(maps_data)
    # print map_data_object[DISTANCE_TO_FACTORY][NON_TIMBER_FOREST_PRODUCT]
    distance_to_factory_maps_array = {
        tree: [
            map_data_object[DISTANCE_TO_FACTORY][tree][period] for period in LAND_PERIODS
        ] for tree in PRODUCTS
    }
    distance_to_settlement_maps_array = [
        map_data_object[DISTANCE_TO_SETTLEMENT][period] for period in LAND_PERIODS
    ]
    distance_to_market_maps_array = [
        map_data_object[DISTANCE_TO_MARKET][period] for period in LAND_PERIODS
    ]
    distance_to_road_maps_array = [
        map_data_object[DISTANCE_TO_ROAD][period] for period in LAND_PERIODS
    ]
    distance_to_river_maps_array = [
        map_data_object[DISTANCE_TO_RIVER][period] for period in LAND_PERIODS
    ]

area_map = map_data_object[SIMULATED_AREA]
init_landcover_map = map_data_object[INITIAL_LANDCOVER]

landuse_map = create_zero_map(map_data_object[SIMULATED_AREA])
landage_map = create_zero_map(map_data_object[INITIAL_LANDCOVER])

for land in LANDCOVER:
    if type(land) is str:
        landage_map += util.arraystat(area_map, read_input.biophysical1[land][LANDCOVER_AGE][INITIAL_LANDCOVER_AGE]) * \
            (init_landcover_map == LANDCOVER_MAP[land])
    else:
        for key in land.keys():
            for land_stage in land[key]:
                landage_map += util.arraystat(area_map, read_input.biophysical1[key][land_stage][LANDCOVER_AGE][INITIAL_LANDCOVER_AGE]) * (
                    init_landcover_map == LANDCOVER_MAP[key][land_stage])

for land in LANDCOVER:
    if type(land) is str:
        landuse_map += (init_landcover_map ==
                        LANDCOVER_MAP[land]) * LANDUSE_MAP[land]
    else:
        for key in land.keys():
            for land_stage in land[key]:
                landuse_map += (init_landcover_map ==
                                LANDCOVER_MAP[key][land_stage]) * LANDUSE_MAP[key]
