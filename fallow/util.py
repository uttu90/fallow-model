from constant import *
import os.path
from osgeo import gdal
import numpy as np
import copy

import pcraster

def get_prototype(mapmodel):
    return gdal.Open(list(mapmodel[0].values())[0][PATH])


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
        for key in datum.keys():
            if (type(datum[key]) is dict):
                print(key, os.path.isfile(datum[key][PATH]))
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
    return np.ma.masked_where(p2n == -9999, p2n)


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

def create_bool_map(original_data, value):
    return original_data == value


def  create_nested_output(pattern, value=None):
    data = dict()

    def make_nested_output(nested_pattern, current_data):
        for item in nested_pattern:
            if type(item) == str:
                current_data[item] = copy.deepcopy(value)
            else:
                for key in item.keys():
                    current_data[key] = {}
                    make_nested_output(item[key], current_data[key])

    make_nested_output(pattern, data)
    return data

# import numpy as np
# import bisect
#
# MEAN = 'mean'
# CV = 'cv'
#
#
# def arrayuper(array, value):
#     arraymax = np.full(array.shape, value, dtype=np.float32)
#     return np.ma.maximum(array, arraymax)
#
#
# def arraystat(array, prob):
#     rows, cols = array.shape
#     return arrayuper(
#         prob[MEAN] * (1 + np.random.normal(0, 1, [rows, cols]) * prob[CV]),
#         0
#     )
#
#
def calstat(prob):
    return max(0, prob[MEAN] * (1 + prob[CV]))


def get_shape(original_data, field):
    data = dict()

    def make_shape(odata, rdata):
        for key in odata.keys():
            if (odata[key].get(field) is None):
                rdata[key] = {}
                make_shape(odata[key], rdata[key])
            else:
                rdata[key] = odata[key].get(field)
    make_shape(original_data, data)
    return data


def calstat_shape(original_data):
    data = {}

    def make_cal_shape(odata, rdata):
        for key in odata.keys():
            if (odata[key].get(MEAN) is None):
                rdata[key] = {}
                make_cal_shape(odata[key], rdata[key])
            else:
                rdata[key] = calstat(odata[key])

    make_cal_shape(original_data, data)
    return data


def standardize(data):
    if (data is None):
        return None
    max_value = data.max()
    if max_value == 0:
        return 0.0 * data
    return data / float(max_value)


def array2map(array, filename, prototype):
    data = array.astype(np.float32)
    data = np.ma.filled(data, fill_value=-9999)
    [cols, rows] = array.shape
    outdriver = gdal.GetDriverByName("GTiff")
    outdata = outdriver.Create(filename, rows, cols, 1, gdal.GDT_Float32)
    outdata.SetGeoTransform(prototype.GetGeoTransform())
    outdata.SetProjection(prototype.GetProjection())
    outdata.GetRasterBand(1).WriteArray(data, 0, 0)

def save2file(array, filename):
    data = array.astype(np.float32)
    data = np.ma.filled(data, fill_value=-9999)
    [cols, rows] = array.shape
    outdriver = gdal.GetDriverByName("GTiff")
    outdata = outdriver.Create(filename, rows, cols, 1, gdal.GDT_Float32)
    outdata.GetRasterBand(1).WriteArray(data, 0, 0)

# def init_landcover_age_arr(init_landcover_arr, init_landcover_age, landcover_map, lands):
#   def calculate_landcover_age_arr(init_landcover_arr, init_landcover_age, landcover_map, lands):
#     for land in lands:
#       if (type(land) is str):
#         calculate_landcover_age_arr.data += (
#             arrayuper(arraystat(area_arr, init_landcover_age[land]), 0) *
#             boolean2scalar(init_landcover_arr == landcover_map[land])
#         )
#       else:
#         land_stage = land.keys[0]
#         calculate_landcover_age_arr(
#           init_landcover_arr,
#           init_landcover_age[land_stage],
#           landcover_map[land_stage],
#           land[land_stage]
#         )

#   calculate_landcover_age_arr.data = 0

#   calculate_landcover_age_arr(
#       init_landcover_arr, init_landcover_age, landcover_map, lands)
#   return calculate_landcover_age_arr.data


# def init_lanuse_arr(init_landcover_age_arr, landuse_map, landcover_map, lands):
#   data = 0
#   for land in lands:
#     if (type(land) is str):
#       data += (init_landcover_age_arr == landcover_map[land]) * landuse_map[land]
#     else:
#       land_multiple_stages = land.keys[0]
#       for land_stage in land[land_multiple_stages]:
#         data += (init_landcover_age_arr ==
#                  landcover_map[land][land_stage]) * landuse_map[land_multiple_stages]

#   return data

# def calculate_lc(landuse_arr, landuse_map, landcover_map, landcover_age_arr, landcover_time_bound, landcover_age, lands):
#   data = 0
#   for land in lands:
#     if(type(land) is str):
#       data += (landuse_arr == landuse_map[land]) * landcover_map[land]
#     else:
#       land_multiple_stages = land.keys[0]
#       current_land_age = bisect.bisect(landcover_time_bound, landcover_age) - 1
#       land_stage = land[land_multiple_stages][current_land_age].keys[0]
#       data += (landuse_arr == landuse_map[land_multiple_stages]) * landcover_map[land_multiple_stages][land_stage]
