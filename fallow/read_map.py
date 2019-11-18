import os
import json
from osgeo import gdal
import numpy as np
from constant import *

# file_path = os.path.dirname(__file__)
# map_file = os.path.join(file_path, 'maps.json')

MASKED_VALUE = -9999


def file2array(path, masked_value=MASKED_VALUE):
    if os.path.isfile(path):
        original_arr = gdal.Open(path).ReadAsArray().astype(np.float32)
        return np.ma.masked_where(original_arr <= masked_value, original_arr)


def load_map(path):
    with open(path, 'r') as map_source:
        maps_data = json.load(map_source)

    data = dict()

    data['simulated_area'] = file2array(maps_data[0][SIMULATED_AREA]['path'])
    data['prototype'] = gdal.Open(maps_data[0][SIMULATED_AREA]['path'])
    data['initial_landcover_area'] = file2array(maps_data[1][INITIAL_LANDCOVER]['path'])
    data['subcatchment_area'] = file2array(maps_data[2][SUBCATCHMENT_AREA]['path'])
    data['initlog'] = 0 * data['simulated_area']
    data['initial_logging_area'] = 0 * data['simulated_area']
    data['initial_soil_fertility_area'] = file2array(maps_data[4][SOIL_FERTILITY][0][INITIAL_SOIL_FERTILITY]['path'])
    data['maximul_soil_fertility_area'] = 5 * data['initial_soil_fertility_area']
    data['slope_area'] = file2array(maps_data[5][SLOPE]['path'])
    data['suitfood1'] = file2array(maps_data[6][SUITABLE_AREA][0][ANNUAL_CROP1]['path'])
    data['suitfood2'] = file2array(maps_data[6][SUITABLE_AREA][1][ANNUAL_CROP2]['path'])
    data['suitfood3'] = file2array(maps_data[6][SUITABLE_AREA][2][ANNUAL_CROP3]['path'])
    data['suitfood4'] = file2array(maps_data[6][SUITABLE_AREA][3][ANNUAL_CROP4]['path'])
    data['suitaf1'] = file2array(maps_data[6][SUITABLE_AREA][4][TREE_BASED_SYSTEM1]['path'])
    data['suitaf2'] = file2array(maps_data[6][SUITABLE_AREA][5][TREE_BASED_SYSTEM2]['path'])
    data['suitaf3'] = file2array(maps_data[6][SUITABLE_AREA][6][TREE_BASED_SYSTEM3]['path'])
    data['suitaf4'] = file2array(maps_data[6][SUITABLE_AREA][7][TREE_BASED_SYSTEM4]['path'])
    data['suitaf5'] = file2array(maps_data[6][SUITABLE_AREA][8][TREE_BASED_SYSTEM5]['path'])
    data['suitaf6'] = file2array(maps_data[6][SUITABLE_AREA][9][TREE_BASED_SYSTEM6]['path'])
    data['suitaf7'] = file2array(maps_data[6][SUITABLE_AREA][10][TREE_BASED_SYSTEM7]['path'])
    data['suitaf8'] = file2array(maps_data[6][SUITABLE_AREA][11][TREE_BASED_SYSTEM8]['path'])

    data['droad1'] = file2array(maps_data[7][DISTANCE_TO_ROAD][0]['Period 1']['path'])
    data['droad2'] = file2array(maps_data[7][DISTANCE_TO_ROAD][1]['Period 2']['path'])
    data['droad3'] = file2array(maps_data[7][DISTANCE_TO_ROAD][2]['Period 3']['path'])
    data['droad4'] = file2array(maps_data[7][DISTANCE_TO_ROAD][3]['Period 4']['path'])

    data['dmart1'] = file2array(maps_data[8][DISTANCE_TO_MARKET][0]['Period 1']['path'])
    data['dmart2'] = file2array(maps_data[8][DISTANCE_TO_MARKET][1]['Period 2']['path'])
    data['dmart3'] = file2array(maps_data[8][DISTANCE_TO_MARKET][2]['Period 3']['path'])
    data['dmart4'] = file2array(maps_data[8][DISTANCE_TO_MARKET][3]['Period 4']['path'])

    data['driver1'] = file2array(maps_data[9][DISTANCE_TO_RIVER][0]['Period 1']['path'])
    data['driver2'] = file2array(maps_data[9][DISTANCE_TO_RIVER][1]['Period 2']['path'])
    data['driver3'] = file2array(maps_data[9][DISTANCE_TO_RIVER][2]['Period 3']['path'])
    data['driver4'] = file2array(maps_data[9][DISTANCE_TO_RIVER][3]['Period 4']['path'])

    data['dfactory_ntfp1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][0][NON_TIMBER_FOREST_PRODUCT][0]['Period 1']['path'])
    data['dfactory_ntfp2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][0][NON_TIMBER_FOREST_PRODUCT][1]['Period 2']['path'])
    data['dfactory_ntfp3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][0][NON_TIMBER_FOREST_PRODUCT][2]['Period 3']['path'])
    data['dfactory_ntfp4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][0][NON_TIMBER_FOREST_PRODUCT][3]['Period 4']['path'])

    data['dfactory_timber1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][1][TIMBER][0]['Period 1']['path'])
    data['dfactory_timber2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][1][TIMBER][1]['Period 2']['path'])
    data['dfactory_timber3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][1][TIMBER][2]['Period 3']['path'])
    data['dfactory_timber4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][1][TIMBER][3]['Period 4']['path'])

    data['dfactory_food1_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][2][ANNUAL_CROP1][0]['Period 1']['path'])
    data['dfactory_food1_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][2][ANNUAL_CROP1][1]['Period 2']['path'])
    data['dfactory_food1_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][2][ANNUAL_CROP1][2]['Period 3']['path'])
    data['dfactory_food1_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][2][ANNUAL_CROP1][3]['Period 4']['path'])

    data['dfactory_food2_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][3][ANNUAL_CROP2][0]['Period 1']['path'])
    data['dfactory_food2_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][3][ANNUAL_CROP2][1]['Period 2']['path'])
    data['dfactory_food2_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][3][ANNUAL_CROP2][2]['Period 3']['path'])
    data['dfactory_food2_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][3][ANNUAL_CROP2][3]['Period 4']['path'])

    data['dfactory_food3_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][4][ANNUAL_CROP3][0]['Period 1']['path'])
    data['dfactory_food3_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][4][ANNUAL_CROP3][1]['Period 2']['path'])
    data['dfactory_food3_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][4][ANNUAL_CROP3][2]['Period 3']['path'])
    data['dfactory_food3_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][4][ANNUAL_CROP3][3]['Period 4']['path'])

    data['dfactory_food4_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][5][ANNUAL_CROP4][0]['Period 1']['path'])
    data['dfactory_food4_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][5][ANNUAL_CROP4][1]['Period 2']['path'])
    data['dfactory_food4_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][5][ANNUAL_CROP4][2]['Period 3']['path'])
    data['dfactory_food4_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][5][ANNUAL_CROP4][3]['Period 4']['path'])

    data['dfactory_af1_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][6][TREE_BASED_SYSTEM1][1]['Period 2']['path'])
    data['dfactory_af1_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][6][TREE_BASED_SYSTEM1][2]['Period 3']['path'])
    data['dfactory_af1_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][6][TREE_BASED_SYSTEM1][3]['Period 4']['path'])
    data['dfactory_af1_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][6][TREE_BASED_SYSTEM1][0]['Period 1']['path'])

    data['dfactory_af2_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][7][TREE_BASED_SYSTEM2][0]['Period 1']['path'])
    data['dfactory_af2_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][7][TREE_BASED_SYSTEM2][1]['Period 2']['path'])
    data['dfactory_af2_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][7][TREE_BASED_SYSTEM2][2]['Period 3']['path'])
    data['dfactory_af2_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][7][TREE_BASED_SYSTEM2][3]['Period 4']['path'])

    data['dfactory_af3_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][8][TREE_BASED_SYSTEM3][0]['Period 1']['path'])
    data['dfactory_af3_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][8][TREE_BASED_SYSTEM3][1]['Period 2']['path'])
    data['dfactory_af3_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][8][TREE_BASED_SYSTEM3][2]['Period 3']['path'])
    data['dfactory_af3_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][8][TREE_BASED_SYSTEM3][3]['Period 4']['path'])

    data['dfactory_af4_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][9][TREE_BASED_SYSTEM4][0]['Period 1']['path'])
    data['dfactory_af4_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][9][TREE_BASED_SYSTEM4][1]['Period 2']['path'])
    data['dfactory_af4_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][9][TREE_BASED_SYSTEM4][2]['Period 3']['path'])
    data['dfactory_af4_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][9][TREE_BASED_SYSTEM4][3]['Period 4']['path'])

    data['dfactory_af5_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][10][TREE_BASED_SYSTEM5][0]['Period 1']['path'])
    data['dfactory_af5_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][10][TREE_BASED_SYSTEM5][1]['Period 2']['path'])
    data['dfactory_af5_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][10][TREE_BASED_SYSTEM5][2]['Period 3']['path'])
    data['dfactory_af5_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][10][TREE_BASED_SYSTEM5][3]['Period 4']['path'])

    data['dfactory_af6_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][11][TREE_BASED_SYSTEM6][0]['Period 1']['path'])
    data['dfactory_af6_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][11][TREE_BASED_SYSTEM6][1]['Period 2']['path'])
    data['dfactory_af6_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][11][TREE_BASED_SYSTEM6][2]['Period 3']['path'])
    data['dfactory_af6_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][11][TREE_BASED_SYSTEM6][3]['Period 4']['path'])

    data['dfactory_af7_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][12][TREE_BASED_SYSTEM7][0]['Period 1']['path'])
    data['dfactory_af7_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][12][TREE_BASED_SYSTEM7][1]['Period 2']['path'])
    data['dfactory_af7_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][12][TREE_BASED_SYSTEM7][2]['Period 3']['path'])
    data['dfactory_af7_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][12][TREE_BASED_SYSTEM7][3]['Period 4']['path'])

    data['dfactory_af8_1'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][13][TREE_BASED_SYSTEM8][0]['Period 1']['path'])
    data['dfactory_af8_2'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][13][TREE_BASED_SYSTEM8][1]['Period 2']['path'])
    data['dfactory_af8_3'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][13][TREE_BASED_SYSTEM8][2]['Period 3']['path'])
    data['dfactory_af8_4'] = file2array(maps_data[10][DISTANCE_TO_FACTORY][13][TREE_BASED_SYSTEM8][3]['Period 4']['path'])

    data['dset1'] = file2array(maps_data[11][DISTANCE_TO_SETTLEMENT][0]['Period 1']['path'])
    data['dset2'] = file2array(maps_data[11][DISTANCE_TO_SETTLEMENT][1]['Period 2']['path'])
    data['dset3'] = file2array(maps_data[11][DISTANCE_TO_SETTLEMENT][2]['Period 3']['path'])
    data['dset4'] = file2array(maps_data[11][DISTANCE_TO_SETTLEMENT][3]['Period 4']['path'])

    data['protected_area'] = file2array(maps_data[12][PROTECTED_AREA]['path'])

    data['disastered_area'] = data['simulated_area'] * 0

    return data
