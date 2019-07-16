SIMULATED_AREA = 'Simulated area'
INITIAL_LANDCOVER = 'Initial landcover'
SUBCATCHMENT_AREA = 'Sub-catchment area'
INITIAL_LOGGING_AREA = 'Initial logging area'
SOIL_FERTILITY = 'Soil fertility'
INITIAL_SOIL_FERTILITY = 'Initial soil fertility'
MAXIMUM_SOIL_FERTILITY = 'Maximum soil fertility'
SLOPE = 'Slope'
SUITABLE_AREA = 'Suitable area'
DISTANCE_TO_ROAD = 'Distance to road'
DISTANCE_TO_RIVER = 'Distance to river'
DISTANCE_TO_MARKET = 'Distance to market'
DISTANCE_TO_FACTORY = 'Distance to factory'
DISTANCE_TO_SETTLEMENT = 'Distance to settlement'
PROTECTED_AREA = 'Protected area'
DISASTERED_AREA = 'Disastered area'
DEPLETION_RATE = 'Depletion rate'
HALFT_TIME_RECOVERY = 'Half time recovery'

SUBCATCHMENT = ['Subcatchment ' + str(index + 1) for index in range(25)]
SUBCATCHMENT_IDS = {
    subcatchment: index for index, subcatchment in enumerate(SUBCATCHMENT)
}

OFF_NONFARM = 'Off-/Non-farm'
NON_TIMBER_FOREST_PRODUCT = 'Non-timber forest product'
TIMBER = 'Timber'
ANNUAL_CROP1 = 'Annual crop 1'
ANNUAL_CROP2 = 'Annual crop 2'
ANNUAL_CROP3 = 'Annual crop 3'
ANNUAL_CROP4 = 'Annual crop 4'
TREE_BASED_SYSTEM1 = 'Tree-based system 1'
TREE_BASED_SYSTEM2 = 'Tree-based system 2'
TREE_BASED_SYSTEM3 = 'Tree-based system 3'
TREE_BASED_SYSTEM4 = 'Tree-based system 4'
TREE_BASED_SYSTEM5 = 'Tree-based system 5'
TREE_BASED_SYSTEM6 = 'Tree-based system 6'
TREE_BASED_SYSTEM7 = 'Tree-based system 7'
TREE_BASED_SYSTEM8 = 'Tree-based system 8'
LAND_PERIODS = ['Period ' + str(x) for x in range(1, 5, 1)]

# ANNUAL_CROPS = [ANNUAL_CROP1, ANNUAL_CROP2, ANNUAL_CROP3, ANNUAL_CROP4]
ANNUAL_CROPS = ['Annual crop ' + str(x) for x in range(1, 5, 1)]
TREE_BASED_SYSTEMS = ['Tree-based system ' + str(x) for x in range(1, 9, 1)]
PRODUCTS = [
    NON_TIMBER_FOREST_PRODUCT,
    TIMBER
] + ANNUAL_CROPS + TREE_BASED_SYSTEMS

LIVELIHOOD = [
    OFF_NONFARM,
    NON_TIMBER_FOREST_PRODUCT,
    TIMBER
] + ANNUAL_CROPS + TREE_BASED_SYSTEMS

MAP_OBJECT = {
    "path": "",
    "description": ""
}

TREE_AREAS = ANNUAL_CROPS + TREE_BASED_SYSTEMS

MAPS_MODEL = [
    {
        SIMULATED_AREA: MAP_OBJECT
    },
    {
        INITIAL_LANDCOVER: MAP_OBJECT
    },
    {
        SUBCATCHMENT_AREA: MAP_OBJECT
    },
    {
        INITIAL_LOGGING_AREA: MAP_OBJECT
    },
    {
        SOIL_FERTILITY: [
            {
                INITIAL_SOIL_FERTILITY: MAP_OBJECT
            },
            {
                MAXIMUM_SOIL_FERTILITY: MAP_OBJECT
            }
        ]
    },
    {
        SLOPE: MAP_OBJECT
    },
    {
        SUITABLE_AREA: [
            {
                key: MAP_OBJECT for key in TREE_AREAS
            }
        ]
    },
    {
        DISTANCE_TO_ROAD: [
            {
                key: MAP_OBJECT for key in LAND_PERIODS
            }
        ]
    },
    {
        DISTANCE_TO_MARKET: [
            {
                key: MAP_OBJECT for key in LAND_PERIODS
            }
        ]
    },
    {
        DISTANCE_TO_RIVER: [
            {
                key: MAP_OBJECT for key in LAND_PERIODS
            }
        ]
    },
    {
        DISTANCE_TO_FACTORY: [
            {
                tree: [
                    {
                        period: MAP_OBJECT for period in LAND_PERIODS
                    }
                ] for tree in PRODUCTS
            }
        ]
    },
    {
        DISTANCE_TO_SETTLEMENT: [
            {
                key: MAP_OBJECT for key in LAND_PERIODS
            }
        ]
    },
    {
        PROTECTED_AREA: MAP_OBJECT
    },
    {
        DISASTERED_AREA: MAP_OBJECT
    }
]

# print MAPS_MODEL

FOREST_STAGES = [
    'Pioneer',
    'Young secondary',
    'Old secondary',
    'Primary'
]

TREE_BASED_STAGES = [
    'Pioneer',
    'Early production',
    'Peak production',
    'Post production',
]

SETTLEMENT = 'Settlement'
FOREST = 'Forest'

LANDUSE = [
    SETTLEMENT,
    FOREST
] + ANNUAL_CROPS + TREE_BASED_SYSTEMS

SC_NAME = [
    'sc' + str(x) for x in range(26)
]

LANDCOVER = [
    SETTLEMENT,
    {
        FOREST: FOREST_STAGES
    },
] + ANNUAL_CROPS + [
    {key: TREE_BASED_STAGES} for key in TREE_BASED_SYSTEMS
]

# LAND =[
#   SETTLEMENT,
#   {
#     FOREST: FOREST_STAGES
#   },
# ] + ANNUAL_CROPS + [
#   { key: TREE_BASED_STAGES } for key in TREE_BASED_SYSTEMS
# ]


def make_land_map(land_shape):
    data = dict()

    def assign_value(or_land_shape, or_data):
        for land in or_land_shape:
            if (type(land) is str):
                or_data[land] = assign_value.index
                assign_value.index += 1
            else:
                for key in land.keys():
                    or_data[key] = dict()
                    assign_value(land[key], or_data[key])

    assign_value.index = 0
    assign_value(land_shape, data)
    return data


LANDUSE_MAP = make_land_map(LANDUSE)
LANDCOVER_MAP = make_land_map(LANDCOVER)

LAND_SPECS = ['rotation', 'alow_change']

STATISTICS = ['mean', 'cv']
LANDCOVER_AGE = 'Landcover age'
LANDCOVER_AGE_BOUNDARY = 'Landcover age boundary'
INITIAL_LANDCOVER_AGE = 'Initial landcover age'
SOIL_FERTILITY = 'Soil fertility'
DEPLETION_RATE = 'Depletion rate'
HALFT_TIME_RECOVERY = 'Half time recovery'
LANDCOVER_PROPERTY = 'Landcover property'
ABOVEGROUND_BIOMASS = 'Aboveground biomass'
FLOOR_BIOMASS_FRACTION = 'Floor biomass fraction'
YIELD = 'Yield'
PROBABLY_OF_FIRE_SPREADING = 'Probability of file spreading'

BIOPHYSICAL1 = [
    {
        'Landcover age': [
            'Landcover age boundary',
            {
                'Initial landcover age': STATISTICS
            }
        ]
    },
    {
        'Soil fertility': [
            {
                'Depletion rate': STATISTICS
            },
            {
                'Half time recovery': STATISTICS
            }
        ]
    },
    {
        'Landcover property': [
            {
                'Aboveground biomass': STATISTICS,
            },
            {
                'Floor biomass fraction': STATISTICS
            },
            {
                'Yield': STATISTICS
            },
            {
                'Probability of file spreading': STATISTICS
            }
        ]
    }
]
HARVESTING = 'Harvesting'
DEMAND_PER_CAPITA = 'Demand per capita'
PROBABLY_TO_SELL = 'Probably to sell'
SOIL_FERTILITY = 'Soil fertility'
LAND_PRODUCT = 'Land product'
LAND_SUITABILITY = 'Land suitability'
TRANSPORT_ACCESS = 'Transport access'
PLOT_MAINTAINANCE = 'Plot maintainance'
FLOOR_BIOMASS = 'Floor biomass'
LOSS_FRACTION = 'Loss fraction'
STEEPNESS = 'Steep ness'

BIOPHISICAL2 = [
    {
        HARVESTING: STATISTICS
    },
    DEMAND_PER_CAPITA,
    PROBABLY_TO_SELL,
    SOIL_FERTILITY,
    LAND_PRODUCT,
    LAND_SUITABILITY,
    TRANSPORT_ACCESS,
    PLOT_MAINTAINANCE,
    FLOOR_BIOMASS,
    LOSS_FRACTION,
    STEEPNESS,
    YIELD
]
FARMER1 = 'Farmer1'
FARMER2 = 'Farmer2'

FARMERS = [FARMER1, FARMER2]

PRICE = 'Price'
ACTUAL_PROFITABILITY = 'Actual profitability'
RETURN_TO_LAND = 'Return to land'
RETURN_TO_LABOUR = 'Return to labour'
EXPECTED_PROFITABILITY = 'Expected profitability'
ESTABLISTMENT_COST = 'Establishment cost'
ESTABLISTMENT_LABOUR = 'Establisment labour'
EXTERNAL_LABOUR = 'External labour'
SUBSIDY = 'Subsidy'

ECONOMIC = [
    {
        PRICE: STATISTICS
    },
    {
        ACTUAL_PROFITABILITY: [
            {RETURN_TO_LAND: FARMERS},
            {RETURN_TO_LABOUR: FARMERS}
        ],
        EXPECTED_PROFITABILITY: [
            RETURN_TO_LAND,
            RETURN_TO_LABOUR
        ]
    },
    {
        ESTABLISTMENT_COST: STATISTICS
    },
    {
        ESTABLISTMENT_LABOUR: STATISTICS
    },
    {
        EXTERNAL_LABOUR: STATISTICS
    },
    {
        SUBSIDY: STATISTICS
    }
]

NONLABOUR_COST = 'Nonlabour cost'

ECONOMIC2 = [
    {
        NONLABOUR_COST: STATISTICS
    }
]

EXTENSION_PROPERTY = 'Extension property'
CULTURAL_INFLUENCE = 'Cultural influence'
AVAILABILITY = 'Availability'
CREDIBILITY = 'Creadibility'

SOCIAL = [
    CULTURAL_INFLUENCE,
    {
        EXTENSION_PROPERTY: [
            AVAILABILITY,
            CREDIBILITY
        ]
    }
]

INITIAL_POPULATION = 'Initial population'
ANNUAL_GROWTH_RATE = 'Annual growth rate'
LABOUR_FRACTION = 'Labour fraction'
WORKING_DAYS = 'Working days'
INITIAL_FINANCIAL_CAPITAL = 'Initial financial capital'
SECONDARY_CONSUMPTION_FRACTION = 'Secondary consumption fraction'


DEMOGRAPHY = [
    INITIAL_POPULATION,
    ANNUAL_GROWTH_RATE,
    LABOUR_FRACTION,
    WORKING_DAYS,
    INITIAL_FINANCIAL_CAPITAL,
    SECONDARY_CONSUMPTION_FRACTION,
]

POPULATION_FRACTION = 'Population fraction'
ALPHA_FACTOR = 'Alpha factor'
BETA_FACTOR = 'Beta factor'
LANDUSE_PRIORITY = 'Landuse priority'

FARMER_PROPERTY = [
    POPULATION_FRACTION,
    ALPHA_FACTOR,
    BETA_FACTOR,
    LANDUSE_PRIORITY,
]

IMPACT_OF_DISASTER = 'Impact of disaster'
TO_HUMAN = 'To human'
TO_MONEY_CAPITAL = 'To money capital'
TO_WORKING_DAY = 'To working day'

TIME_OF_DISASTER_EVENT = 'Time of disaster event'

CONVERTION = 'Convertion'

TIMBER_VOLUME_TO_BIOMASS = 'Timber volume to biomass'
BIOMASS_TO_CARBON = 'Biomass to carbon'

IMPACT = [
    {
        IMPACT_OF_DISASTER: [
            TO_HUMAN,
            TO_MONEY_CAPITAL,
            TO_WORKING_DAY,
        ]
    },
    TIME_OF_DISASTER_EVENT,
    {
        CONVERTION: [
            TIMBER_VOLUME_TO_BIOMASS,
            BIOMASS_TO_CARBON,
        ]
    }
]

LAND_SPECS_PARAMETER = ['Rotation', 'Allow change']

SINGLE_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

ALPHABET = [a for a in SINGLE_ALPHABET] + [
    a + b for a in SINGLE_ALPHABET for b in SINGLE_ALPHABET
]


# print ALPHABET

# ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


LAND_SPECS_TABLE = [6, 20, 'D', 'E']

SIMULATED_AREA = 'Simulated area'
INITIAL_LANDCOVER = 'Initial landcover'
SUBCATCHMENT_AREA = 'Sub-catchment area'
INITIAL_LOGGING_AREA = 'Initial logging area'
SOIL_FERTILITY = 'Soil fertility'
INITIAL_SOIL_FERTILITY = 'Initial soil fertility'
MAXIMUM_SOIL_FERTILITY = 'Maximum soil fertility'
SLOPE = 'Slope'
SUITABLE_AREA = 'Suitable area'
DISTANCE_TO_ROAD = 'Distance to road'
DISTANCE_TO_RIVER = 'Distance to river'
DISTANCE_TO_MARKET = 'Distance to market'
DISTANCE_TO_FACTORY = 'Distance to factory'
DISTANCE_TO_SETTLEMENT = 'Distance to settlement'
PROTECTED_AREA = 'Protected area'
DISASTERED_AREA = 'Disastered area'

STATISTICS = ['mean', 'cv']
LANDCOVER_AGE = 'Landcover age'
LANDCOVER_AGE_BOUNDARY = 'Landcover age boundary'
INITIAL_LANDCOVER_AGE = 'Initial landcover age'

MANAGEMENT_SUBSIDY = 'Management subsidy'
ESTABLISHMENT_SUBSIDY = 'Establishment subsidy'
SUBSIDY_PARAMETER = [ESTABLISHMENT_SUBSIDY, MANAGEMENT_SUBSIDY]

Z1 = 'z1'
Z2 = 'z2'
Z3 = 'z3'
Z4 = 'z4'
Z5 = 'z5'

Zs = [Z1, Z2, Z3, Z4, Z5]

MASKED_VALUE = -9999
MEAN = 'mean'
CV = 'cv'
PATH = 'Path'
