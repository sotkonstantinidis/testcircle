COUNTRY_MAPPING = {
    'country_GRE': 'country_GRC',
    'country_SPA': 'country_ESP',
    'country_AS': 'country_AFG',
    'country_SWI': 'country_CHE',
    'country_ZIM': 'country_ZWE',
    'country_RSA': 'country_ZAF',
    'country_TAJ': 'country_TJK',
    'country_KYR': 'country_KGZ',
    'country_TUM': 'country_TKM',
    'country_COS': 'country_CRI',
    'country_CHA': 'country_TCD',
    'country_CAM': 'country_CMR',
    'country_BOT': 'country_BWA',
    'country_BAN': 'country_BGD',
    'country_TOG': 'country_TGO',
    'country_TAN': 'country_TZA',
    'country_NEP': 'country_NPL',
    'country_MOR': 'country_MAR',
    'country_UNK': 'country_GBR',
    'country_POR': 'country_PRT',
    'country_PHI': 'country_PHL',
    'country_ZAM': 'country_ZMB',
    'country_BHU': 'country_BTN',
    'country_NIG': 'country_NER',
    'country_IDS': 'country_IDN',
    'country_BRK': 'country_BFA',
    'country_HON': 'country_HND',
    'country_BUR': 'country_BDI',
    'country_LEB': 'country_LBN',
    'country_MAD': 'country_MDG',
    'country_HAI': 'country_HTI',
    'country_OMA': 'country_OMN',
    'country_SUD': 'country_SDN',
    'country_GER': 'country_DEU',
    'country_VIE': 'country_VNM',
    'country_NET': 'country_NLD',
    'country_ROM': 'country_ROU',
    'country_SLA': 'country_SVK',
    'country_CBD': 'country_KHM',
    'country_ICE': 'country_ISL',
    'country_VAN': 'country_VUT',
}
LANDUSE_MAPPING = {
    114: 'tech_lu_cropland',
    115: 'tech_lu_cropland',
    116: 'tech_lu_cropland',
    117: 'tech_lu_grazingland',
    118: 'tech_lu_grazingland',
    119: 'tech_lu_forest',
    120: 'tech_lu_forest',
    121: 'tech_lu_forest',
    122: 'tech_lu_mixed',
    123: 'tech_lu_mixed',
    124: 'tech_lu_mixed',
    125: 'tech_lu_mixed',
    126: 'tech_lu_mixed',
    127: 'tech_lu_mines',
    128: 'tech_lu_settlements',
    129: 'tech_lu_waterways',
    130: 'tech_lu_other',
}
LANDUSE_MAPPING_VERBOSE = {
    114: 'Cropland: Ca: Annual cropping',
    115: 'Cropland: Cp: Perennial (non-woody) cropping',
    116: 'Cropland: Ct: Tree and shrub cropping',
    117: 'Grazing land: Ge: Extensive grazing land',
    118: 'Grazing land: Gi: Intensive grazing/ fodder production',
    119: 'Forests / woodlands: Fn: Natural',
    120: 'Forests / woodlands: Fp: Plantations, afforestations',
    121: 'Forests / woodlands: Fo: Other',
    122: 'Mixed: Mf: Agroforestry',
    123: 'Mixed: Mp: Agro-pastoralism',
    124: 'Mixed: Ma: Agro-silvopastoralism',
    125: 'Mixed: Ms: Silvo-pastoralism',
    126: 'Mixed: Mo: Other',
    127: 'Other: Oi: Mines and extractive industries',
    128: 'Other: Os: Settlements, infrastructure networks',
    129: 'Other: Ow: Waterways, drainage lines, ponds, dams',
    130: 'Other: Oo: Other: wastelands, deserts, glaciers, swamps, recreation areas, etc',
}
LANDUSE_CROPLAND_MAPPING = {
    114: 'lu_cropland_ca',
    115: 'lu_cropland_cp',
    116: 'lu_cropland_ct',
}
GROWING_SEASON_MAPPING = {
    131: 'growing_season_1',
    132: 'growing_season_2',
    133: 'growing_season_3',
}
SPREAD_AREA_COVERED = {
    6: 'tech_spread_less_01',
    7: 'tech_spread_01_1',
    8: 'tech_spread_1_10',
    9: 'tech_spread_10_100',
    10: 'tech_spread_100_1000',
    11: 'tech_spread_1000_10000',
    12: 'tech_spread_10000_plus',
}
MEASURE_MAPPING = {
    # Based on measure_type in qt_2_2_2_2_measure
    1: 'tech_measures_agronomic',
    2: 'tech_measures_vegetative',
    3: 'tech_measures_structural',
    4: 'tech_measures_management',
}
MEASURE_AGRONOMIC_MAPPING = {
    134: 'measures_agronomic_a1',
    135: 'measures_agronomic_a2',
    136: 'measures_agronomic_a3',
    137: 'measures_agronomic_a4',
    # measures_agronomic_a5 was newly introduced in QCAT
    138: 'measures_agronomic_a6',
}
MEASURE_VEGETATIVE_MAPPING = {
    139: 'measures_vegetative_v1',
    140: 'measures_vegetative_v2',
    141: 'measures_vegetative_v3',
    # measures_vegetative_v4 was newly introduced in QCAT
    142: 'measures_vegetative_v5',
}
MEASURE_STRUCTURAL_MAPPING = {
    # New categories in QCAT: s7, s8, s9, s10
    143: 'measures_structural_s1',
    144: 'measures_structural_s1',
    145: 'measures_structural_s2',
    146: 'measures_structural_s3',
    147: 'measures_structural_s4',
    148: 'measures_structural_s5',
    149: 'measures_structural_s11',
    150: 'measures_structural_s6',
    151: 'measures_structural_s11',
}
MEASURE_MANAGEMENT_MAPPING = {
    152: 'measures_management_m1',
    153: 'measures_management_m2',
    154: 'measures_management_m3',
    155: 'measures_management_m4',
    156: 'measures_management_m5',
    157: 'measures_management_m6',
    158: 'measures_management_m7',
}
DEGRADATION_TYPE_MAPPING = {
    165: 'degradation_erosion_water',
    166: 'degradation_erosion_water',
    167: 'degradation_erosion_water',
    168: 'degradation_erosion_water',
    169: 'degradation_erosion_water',
    170: 'degradation_erosion_water',
    171: 'degradation_erosion_wind',
    172: 'degradation_erosion_wind',
    173: 'degradation_erosion_wind',
    174: 'degradation_chemical',
    175: 'degradation_chemical',
    176: 'degradation_chemical',
    177: 'degradation_chemical',
    178: 'degradation_physical',
    179: 'degradation_physical',
    180: 'degradation_physical',
    181: 'degradation_physical',
    182: 'degradation_physical',
    183: 'degradation_biological',
    184: 'degradation_biological',
    185: 'degradation_biological',
    186: 'degradation_biological',
    187: 'degradation_biological',
    188: 'degradation_biological',
    189: 'degradation_biological',
    190: 'degradation_water',
    191: 'degradation_water',
    192: 'degradation_water',
    193: 'degradation_water',
    194: 'degradation_water',
    195: 'degradation_water',
}
DEGRADATION_TYPE_MAPPING_WATER_EROSION = {
    165: 'degradation_wt',
    166: 'degradation_wg',
    167: 'degradation_wm',
    168: 'degradation_wr',
    169: 'degradation_wc',
    170: 'degradation_wo',
}
DEGRADATION_TYPE_MAPPING_WIND_EROSION = {
    171: 'degradation_et',
    172: 'degradation_ed',
    173: 'degradation_eo',
}
DEGRADATION_TYPE_MAPPING_CHEMICAL = {
    174: 'degradation_cn',
    175: 'degradation_ca',
    176: 'degradation_cp',
    177: 'degradation_cs',
}
DEGRADATION_TYPE_MAPPING_PHYSICAL = {
    178: 'degradation_pc',
    179: 'degradation_pk',
    180: 'degradation_pw',
    181: 'degradation_ps',
    182: 'degradation_pu',
}
DEGRADATION_TYPE_MAPPING_BIOLOGICAL = {
    183: 'degradation_bc',
    184: 'degradation_bh',
    185: 'degradation_bq',
    186: 'degradation_bf',
    187: 'degradation_bs',
    188: 'degradation_bl',
    189: 'degradation_bp',
}
DEGRADATION_TYPE_MAPPING_WATER = {
    190: 'degradation_ha',
    191: 'degradation_hs',
    192: 'degradation_hg',
    193: 'degradation_hp',
    194: 'degradation_hq',
    195: 'degradation_hw',
}

qg_name = {
    'qg_name': {
        'questions': {
            'name': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'cmn_name',
                    }
                ],
                'type': 'string',
            },
            'name_local': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'other_names',
                    }
                ],
                'type': 'string',
            },
        }
    },
}

qg_location = {
    'qg_location': {
        'questions': {
            'country': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'country_code',
                        'mapping_prefix': 'country_',
                    }
                ],
                'type': 'dropdown',
                'value_mapping_list': COUNTRY_MAPPING,
            },
            'state_province': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'state_province',
                    }
                ],
                'type': 'string',
            },
            'further_location': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'district_commune',
                    }
                ],
                'type': 'string',
            },
        }
    },
}

qg_import = {
    'qg_import': {
        'questions': {
            'import_old_code': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'technology_code',
                    }
                ],
                'type': 'string',
            }
        }
    },
}

qg_accept_conditions = {
    'qg_accept_conditions': {
        'questions': {
            'date_documentation': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'data_collection_date',
                    }
                ],
                'type': 'date',
            },
            'accept_conditions': {
                'type': 'constant',
                'value': 1
            },
        }
    },
}

# Definition
tech_qg_1 = {
    'tech_qg_1': {
        'questions': {
            'tech_definition': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_1',
                        'wocat_column': 'definition',
                    }
                ],
                'type': 'string',
            },
        }
    },
}

# Description
tech_qg_2 = {
    'tech_qg_2': {
        'questions': {
            'tech_description': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_1',
                        'wocat_column': 'description',
                        'mapping_prefix': '',
                    },
                    {
                        'wocat_table': 'qt_2_1',
                        'wocat_column': 'purpose',
                        'mapping_prefix': 'Purpose of the Technology: ',
                    },
                    {
                        'wocat_table': 'qt_2_1',
                        'wocat_column': 'maintenance',
                        'mapping_prefix': 'Establishment / maintenance activities and inputs: ',
                    },
                    {
                        'wocat_table': 'qt_2_1',
                        'wocat_column': 'environment',
                        'mapping_prefix': 'Natural / human environment: ',
                    }
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge'
                }
            }
        }
    },
}

qg_location_map = {
    'qg_location_map': {
        'questions': {
            'location_map': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'latitude',
                    },
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'longitude'
                    }
                ],
                'type': 'dropdown',
                'composite': {
                    'type': 'geom_point'
                }
            },
        }
    },
}

# Location comments
tech_qg_225 = {
    'tech_qg_225': {
        'questions': {
            'location_comments': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'outline_boundary_points',
                        'mapping_prefix': 'Boundary points of the Technology area: '
                    }
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge'
                }
            }
        }
    },
}

# Land use types
tech_qg_9 = {
    'tech_qg_9': {
         'questions': {
             'tech_landuse': {
                 'mapping': [
                     {
                         'wocat_table': 'qt_2_2_2_1',
                         'wocat_column': 'landuse_sub1'
                     },
                     {
                         'wocat_table': 'qt_2_2_2_1',
                         'wocat_column': 'landuse_sub2'
                     },
                 ],
                 'type': 'checkbox',
                 'composite': {
                     'type': 'checkbox'
                 },
                 'value_mapping_list': LANDUSE_MAPPING,
             }
         }
     },
}

# Cropland subcategories
tech_qg_10 = {
    'tech_qg_10': {
        'questions': {
            'tech_lu_cropland_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub1'
                    },
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub2'
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': LANDUSE_CROPLAND_MAPPING,
            }
        }
    },
}

# Grazing land subcategories.
# Only add if main category "grazing land" was selected in
# qt_2_2_2_1.landuse_sub1 or qt_2_2_2_1.landuse_sub1 (QCAT condition
# tech_qg_11). Else use comments (QCAT tech_qg_7.tech_lu_comments).
tech_qg_11 = {
    'tech_qg_11': {
        'questions': {
            'tech_lu_grazingland_extensive': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'nomadism',
                        'value_mapping': 'tech_lu_grazingland_nomadism'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'semi_nomadism',
                        'value_mapping': 'tech_lu_grazingland_pastoralism'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'ranching',
                        'value_mapping': 'tech_lu_grazingland_ranching'
                    },
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                }
            },
            'tech_lu_grazingland_intensive': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'cut_carry',
                        'value_mapping': 'tech_lu_grazingland_zerograzing'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'improved_pasture',
                        'value_mapping': 'tech_lu_grazingland_improvedpasture'
                    },
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                }
            },
            'tech_lu_grazingland_specify': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'nomadism_comment',
                        'mapping_prefix': 'Nomadism: '
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'semi_nomadism_comment',
                        'mapping_prefix': 'Semi-nomadism/ pastoralism: '
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'ranching_comment',
                        'mapping_prefix': 'Ranching: '
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'cut_carry_comment',
                        'mapping_prefix': 'Cut-and-carry/ zero grazing: '
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'improved_pasture_comment',
                        'mapping_prefix': 'Improved pastures: '
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'mixed_comment',
                        'mapping_prefix': 'Mixed: (eg agro-pastoralism, silvo-pastoralism): '
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other12_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other12_comment'
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other22_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other22_comment'
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other32_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other32_comment'
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                        }
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other42_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other42_comment'
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                        }
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'comments',
                        'mapping_prefix': 'Grazingland comments: '
                    }
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge',
                    'separator': ': '
                }
            }
        },
        'conditions': [
            {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub1'
                    },
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub2'
                    }
                ],
                'operator': 'contains',
                'value': 'tech_lu_grazingland',
                'value_mapping_list': LANDUSE_MAPPING
            }
        ]
    },
}

# Forest subcategories.
# Only add if main category "forest land" was selected in
# qt_2_2_2_1.landuse_sub1 or qt_2_2_2_1.landuse_sub1 (QCAT condition
# tech_qg_11). Else use comments (QCAT tech_qg_7.tech_lu_comments).
tech_qg_12 = {
    'tech_qg_12': {
        'questions': {
            'tech_lu_forest_natural': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'selective_felling',
                        'value_mapping': 'lu_forest_selectivefelling'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'clear_felling',
                        'value_mapping': 'lu_forest_clearfelling'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'shifting_cultivation',
                        'value_mapping': 'lu_forest_shiftingcultivation'
                    },
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                }
            },
            'tech_lu_forest_products': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'timber',
                        'value_mapping': 'tech_lu_forestproducts_timber'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'fuelwood',
                        'value_mapping': 'tech_lu_forestproducts_fuelwood'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'fruits_nuts',
                        'value_mapping': 'tech_lu_forestproducts_fruitsnuts'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'grazing',
                        'value_mapping': 'tech_lu_forestproducts_grazing'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'other_forest',
                        'value_mapping': 'tech_lu_forestproducts_otherproducts'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'nature_conservation',
                        'value_mapping': 'tech_lu_forestproducts_conservation'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'recreation',
                        'value_mapping': 'tech_lu_forestproducts_recreation'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'protection',
                        'value_mapping': 'tech_lu_forestproducts_hazards'
                    },
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                }
            },
            'tech_lu_forest_other': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'other13_specify'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'other23_specify'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'other33_specify'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_3',
                        'wocat_column': 'other43_specify'
                    },
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge',
                    'separator': ', '
                }
            },
        },
        'conditions': [
            {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub1'
                    },
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_sub2'
                    }
                ],
                'operator': 'contains',
                'value': 'tech_lu_forest',
                'value_mapping_list': LANDUSE_MAPPING
            }
        ]
    },
}

# Comments for 3.2 (land use types)
tech_qg_7 = {
    'tech_qg_7': {
        'questions': {
            'tech_lu_comments': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_1',
                        'wocat_column': 'landuse_problem_own',
                        'mapping_prefix': 'Major land use problems (compiler’s opinion): '
                    },
                    {
                        'wocat_table': 'qt_2_2_1',
                        'wocat_column': 'landuse_problem_user',
                        'mapping_prefix': 'Major land use problems (land users’ perception): '
                    },
                    # Start of conditional mapping of grazing land information.
                    # Only add if main category "grazing land" was not
                    # specified.
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'nomadism',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Nomadism: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'nomadism_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'nomadism_comment',
                        'mapping_prefix': 'Nomadism: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'semi_nomadism',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Semi-nomadism / pastoralism: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'semi_nomadism_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'semi_nomadism_comment',
                        'mapping_prefix': 'Semi-nomadism / pastoralism: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'ranching',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Ranching: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'ranching_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'ranching_comment',
                        'mapping_prefix': 'Ranching: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'cut_carry',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Cut-and-carry/ zero grazing: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'cut_carry_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'cut_carry_comment',
                        'mapping_prefix': 'Cut-and-carry/ zero grazing: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'improved_pasture',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Improved pasture: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'improved_pasture_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'improved_pasture_comment',
                        'mapping_prefix': 'Improved pasture: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'mixed',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Mixed: (eg agro-pastoralism, silvo-pastoralism): ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_9_2',
                                        'wocat_column': 'mixed_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'mixed_comment',
                        'mapping_prefix': 'Mixed: (eg agro-pastoralism, silvo-pastoralism): ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other12_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other12_comment',
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other22_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other22_comment',
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other32_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other32_comment',
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other42_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_2',
                                'wocat_column': 'other42_comment',
                            }
                        ],
                        'value_prefix': 'Other grazingland: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_2',
                        'wocat_column': 'comments',
                        'mapping_prefix': 'Grazingland comments: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_grazingland',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on grazing land in QT 2.8.9.2, but "grazing land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    # End of conditional mapping of grazing land information.

                    # Start of conditional mapping of forest land information.
                    # Only add if main category "forest land" was not specified.
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'selective_felling',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Selective felling of (semi-) natural forests: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_10_2',
                                        'wocat_column': 'selective_felling_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'selective_felling_comment',
                        'mapping_prefix': 'Selective felling of (semi-) natural forests: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'clear_felling',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Clear felling of (semi-)natural forests: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_10_2',
                                        'wocat_column': 'clear_felling_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'clear_felling_comment',
                        'mapping_prefix': 'Clear felling of (semi-)natural forests: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'shifting_cultivation',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Shifting cultivation: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            },
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_10_2',
                                        'wocat_column': 'shifting_cultivation_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.',
                        'conditions_join': 'and'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'shifting_cultivation_comment',
                        'mapping_prefix': 'Shifting cultivation: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.2, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'plantation_forestry',
                        'value_mapping': 'Yes',
                        'mapping_prefix': 'Plantation forestry: ',
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_10_2',
                                        'wocat_column': 'plantation_forestry_comment'
                                    }
                                ],
                                'operator': 'is_empty',
                            }
                        ],
                        'condition_message': 'Plantation forestry selected in QT 2.8.10.2, but no automatic mapping to one of plantation subcategories possible in QCAT 3.2. Using comment section of QCAT 3.2 for this data.',
                    },
                    {
                        'wocat_table': 'qt_2_8_10_2',
                        'wocat_column': 'plantation_forestry_comment',
                        'mapping_prefix': 'Plantation forestry: ',
                        'mapping_message': 'Plantation forestry selected in QT 2.8.10.2, but no automatic mapping to one of plantation subcategories possible in QCAT 3.2. Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other12_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other12_comment',
                            }
                        ],
                        'value_prefix': 'Other type of forest: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other22_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other22_comment',
                            }
                        ],
                        'value_prefix': 'Other type of forest: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other32_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other32_comment',
                            }
                        ],
                        'value_prefix': 'Other type of forest: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other42_specify',
                            },
                            {
                                'wocat_table': 'qt_2_8_10_2',
                                'wocat_column': 'other42_comment',
                            }
                        ],
                        'value_prefix': 'Other type of forest: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ': '
                        },
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'timber',
                                'value_mapping': 'timber'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'fuelwood',
                                'value_mapping': 'fuelwood'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'fruits_nuts',
                                'value_mapping': 'fruits and nuts'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'grazing',
                                'value_mapping': 'grazing / browsing'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'other_forest',
                                'value_mapping': 'other forest products / uses (honey, medical, etc.)'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'nature_conservation',
                                'value_mapping': 'nature conservation / protection'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'recreation',
                                'value_mapping': 'recreation / tourism'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'protection',
                                'value_mapping': 'protection against natural hazards'
                            },
                        ],
                        'value_prefix': 'Forest products and services: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.3, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'other13_specify'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'other23_specify'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'other33_specify'
                            },
                            {
                                'wocat_table': 'qt_2_8_10_3',
                                'wocat_column': 'other43_specify'
                            },
                        ],
                        'value_prefix': 'Other forest products and services: ',
                        'type': 'string',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub1'
                                    },
                                    {
                                        'wocat_table': 'qt_2_2_2_1',
                                        'wocat_column': 'landuse_sub2'
                                    }
                                ],
                                'operator': 'contains_not',
                                'value': 'tech_lu_forest',
                                'value_mapping_list': LANDUSE_MAPPING
                            }
                        ],
                        'condition_message': 'Indications on forest land in QT 2.8.10.3, but "forest land" not selected as land use type in QT 2.2.2.1 (QCAT 3.2). Using comment section of QCAT 3.2 for this data.'
                    },
                    # End of (conditional) mapping of forest land information.
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_1',
                                'wocat_column': 'landuse_future',
                            }
                        ],
                        'type': 'string',
                        'value_mapping_list': LANDUSE_MAPPING_VERBOSE,
                        'value_prefix': 'Future (final) land use (after implementation of SLM Technology): ',
                    }
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge'
                }
            },
            'tech_lu_change': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_1',
                        'wocat_column': 'landuse_original'
                    }
                ],
                'type': 'string',
                'value_mapping_list': LANDUSE_MAPPING_VERBOSE,
            }
        }
    },
}

# 3.5 Spread of the Technology
tech_qg_4 = {
    'tech_qg_4': {
        'questions': {
            'tech_spread_tech': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'approx_area_id',
                        'value_mapping': 'tech_spread_evenly'
                    }
                ],
                'type': 'dropdown',
            },
            'tech_spread_area': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'approx_area_id',
                    }
                ],
                'type': 'dropdown',
                'value_mapping_list': SPREAD_AREA_COVERED,
            },
            'tech_spread_tech_comments': {
                'mapping': [
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'precice_area',
                        'mapping_prefix': 'Total area covered by the SLM Technology is ',
                        'mapping_suffix': ' m2.'
                    },
                    {
                        'wocat_table': 'qt_1',
                        'wocat_column': 'comments',
                    }
                ],
                'type': 'string',
            },
        }
    }
}

# 3.3 Water supply
tech_qg_19 = {
    'tech_qg_19': {
        'questions': {
            'tech_watersupply': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_8_4',
                        'wocat_column': 'rainfed',
                        'value_mapping': 'tech_watersupply_rainfed'
                    },
                    {
                        'wocat_table': 'qt_2_8_8_4',
                        'wocat_column': 'mixed',
                        'value_mapping': 'tech_watersupply_mixed'
                    },
                    {
                        'wocat_table': 'qt_2_8_8_4',
                        'wocat_column': 'full_irrigation',
                        'value_mapping': 'tech_watersupply_irrigation'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_3',
                        'wocat_column': 'rainfed',
                        'value_mapping': 'tech_watersupply_rainfed'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_3',
                        'wocat_column': 'mixed',
                        'value_mapping': 'tech_watersupply_mixed'
                    },
                    {
                        'wocat_table': 'qt_2_8_9_3',
                        'wocat_column': 'full_irrigation',
                        'value_mapping': 'tech_watersupply_irrigation'
                    },
                ],
                'type': 'dropdown',
                'conditions': [
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'rainfed',
                            },
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'mixed',
                            },
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'full_irrigation',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'rainfed',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'mixed',
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'full_irrigation',
                            },
                        ],
                        'operator': 'len_lte',
                        'value': 1,
                    }
                ],
            },
            'tech_watersupply_comments': {
                'mapping': [
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'rainfed',
                                'value_mapping': 'rainfed'
                            },
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'mixed',
                                'value_mapping': 'mixed rainfed - irrigated'
                            },
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'full_irrigation',
                                'value_mapping': 'full irrigation'
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'rainfed',
                                'value_mapping': 'rainfed'
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'mixed',
                                'value_mapping': 'mixed rainfed - irrigated'
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'full_irrigation',
                                'value_mapping': 'full irrigation'
                            },
                        ],
                        'type': 'string',
                        'value_prefix': 'Water supply: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        },
                        'conditions': [
                            {
                                'mapping': [
                                    {
                                        'wocat_table': 'qt_2_8_8_4',
                                        'wocat_column': 'rainfed',
                                    },
                                    {
                                        'wocat_table': 'qt_2_8_8_4',
                                        'wocat_column': 'mixed',
                                    },
                                    {
                                        'wocat_table': 'qt_2_8_8_4',
                                        'wocat_column': 'full_irrigation',
                                    },
                                    {
                                        'wocat_table': 'qt_2_8_9_3',
                                        'wocat_column': 'rainfed',
                                    },
                                    {
                                        'wocat_table': 'qt_2_8_9_3',
                                        'wocat_column': 'mixed',
                                    },
                                    {
                                        'wocat_table': 'qt_2_8_9_3',
                                        'wocat_column': 'full_irrigation',
                                    },
                                ],
                                'operator': 'len_gte',
                                'value': 2
                            }
                        ],
                        'condition_message': 'More than one value found for QCAT 3.3 Water supply (QT 2.8.8.4). Using comments in QCAT 3.3 for this data.'
                    },
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_8_8_4',
                                'wocat_column': 'post_flooding',
                                'value_mapping': 'post-flooding'
                            },
                            {
                                'wocat_table': 'qt_2_8_9_3',
                                'wocat_column': 'post_flooding',
                                'value_mapping': 'post-flooding'
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Water supply: ',
                        'composite': {
                            'type': 'merge',
                        }
                    }
                ],
                'type': 'string'
            },
            'tech_growing_seasons': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_7_4',
                        'wocat_column': 'no_growing_seasons'
                    },
                ],
                'type': 'dropdown',
                'value_mapping_list': GROWING_SEASON_MAPPING,
            },
            'tech_growing_seasons_specify': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_7_4',
                        'wocat_column': 'longest_growing_season',
                        'mapping_prefix': 'Longest growing period in days: ',
                    },
                    {
                        'wocat_table': 'qt_2_7_4',
                        'wocat_column': 'longest_months',
                        'mapping_prefix': 'Longest growing period from month to month: ',
                    },
                    {
                        'wocat_table': 'qt_2_7_4',
                        'wocat_column': 'second_long_growing_season',
                        'mapping_prefix': 'Second longest growing period in days: ',
                    },
                    {
                        'wocat_table': 'qt_2_7_4',
                        'wocat_column': 'second_long_months',
                        'mapping_prefix': 'Second longest growing period from month to month: ',
                    },
                ],
                'type': 'string',
                'composite': {
                    'type': 'merge'
                }
            },
            'tech_livestock_density': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_8_9_3',
                        'wocat_column': 'livestock_density',
                        'lookup_table': True,
                    }
                ],
                'type': 'string',
            }
        }
    }
}

# 3.6 SLM measures
tech_qg_8 = {
    'tech_qg_8': {
        'questions': {
            'tech_measures': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_2_measure',
                        'wocat_column': 'measure_type',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox'
                },
                'value_mapping_list': MEASURE_MAPPING,
            }
        }
    }
}

# 3.6 SLM measures: Agronomic
tech_qg_21 = {
    'tech_qg_21': {
        'questions': {
            'tech_measures_agronomic_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_2_measure',
                        'wocat_column': 'measure',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': MEASURE_AGRONOMIC_MAPPING,
            }
        }
    }
}

# 3.6 SLM measures: Vegetative
tech_qg_22 = {
    'tech_qg_22': {
        'questions': {
            'tech_measures_vegetative_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_2_measure',
                        'wocat_column': 'measure',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': MEASURE_VEGETATIVE_MAPPING,
            }
        }
    }
}

# 3.6 SLM measures: Structural
tech_qg_23 = {
    'tech_qg_23': {
        'questions': {
            'tech_measures_structural_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_2_measure',
                        'wocat_column': 'measure',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': MEASURE_STRUCTURAL_MAPPING,
            }
        }
    }
}

# 3.6 SLM measures: Management
tech_qg_24 = {
    'tech_qg_24': {
        'questions': {
            'tech_measures_management_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_2_measure',
                        'wocat_column': 'measure',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': MEASURE_MANAGEMENT_MAPPING,
            }
        }
    }
}

# 3.6 SLM measures: comments
tech_qg_26 = {
    'tech_qg_26': {
        'questions': {
            'tech_measures_comments': {
                'mapping': [
                    # Rank: 131
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'agronomic_rank',
                                'value_mapping': 'agronomic measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'agronomic_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'vegetative_rank',
                                'value_mapping': 'vegetative measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'vegetative_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'structural_rank',
                                'value_mapping': 'structural measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'structural_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'management_rank',
                                'value_mapping': 'management measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'management_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Main measures: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                    # Rank: 132 or 133
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'agronomic_rank',
                                'value_mapping': 'agronomic measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'agronomic_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'vegetative_rank',
                                'value_mapping': 'vegetative measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'vegetative_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'structural_rank',
                                'value_mapping': 'structural measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                    'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'structural_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'management_rank',
                                'value_mapping': 'management measures',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_2',
                                                'wocat_column': 'management_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Secondary measures: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                    # Specify other agronomic measures (A5)
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'other1',
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Specification of other agronomic measures: '
                    },
                    # Specify other vegetative measures (V4)
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'other2',
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Specification of other vegetative measures: '
                    },
                    # Specify other structural measures (S9)
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'other3',
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Specification of other structural measures: '
                    },
                    # Specify other management measures (M7)
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_2',
                                'wocat_column': 'other4',
                            }
                        ],
                        'type': 'string',
                        'value_prefix': 'Specification of other management measures: '
                    }
                ],
                'type': 'string'
            }
        }
    }
}

# 3.7 Main types of land degradation
tech_qg_27 = {
    'tech_qg_27': {
        'questions': {
            'tech_degradation': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING,
            }
        }
    }
}

# 3.7 Main type of land degradation: Water erosion
tech_qg_28 = {
    'tech_qg_28': {
        'questions': {
            'degradation_erosion_water_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_WATER_EROSION,
            }
        }
    }
}

# 3.7 Main type of land degradation: Wind erosion
tech_qg_29 = {
    'tech_qg_29': {
        'questions': {
            'degradation_erosion_wind_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_WIND_EROSION,
            }
        }
    }
}

# 3.7 Main type of land degradation: Chemical
tech_qg_30 = {
    'tech_qg_30': {
        'questions': {
            'degradation_chemical_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_CHEMICAL,
            }
        }
    }
}

# 3.7 Main type of land degradation: Physical
tech_qg_31 = {
    'tech_qg_31': {
        'questions': {
            'degradation_physical_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_PHYSICAL,
            }
        }
    }
}

# 3.7 Main type of land degradation: Biological
tech_qg_32 = {
    'tech_qg_32': {
        'questions': {
            'degradation_biological_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_BIOLOGICAL,
            }
        }
    }
}

# 3.7 Main type of land degradation: Water
tech_qg_33 = {
    'tech_qg_33': {
        'questions': {
            'degradation_water_sub': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_4',
                        'wocat_column': 'degradation',
                    }
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                    'mapping': 'exclusive',
                },
                'value_mapping_list': DEGRADATION_TYPE_MAPPING_WATER,
            }
        }
    }
}

# 3.7 Main type of land degradation: Comments
tech_qg_34 = {
    'tech_qg_34': {
        'questions': {
            'degradation_comments': {
                'mapping': [
                    # Rank: 131
                    {
                        'mapping': [
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 165,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [165],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 166,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [166],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 167,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [167],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 168,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [168],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 169,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [169],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 170,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [170],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 171,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [171],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 172,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [172],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 173,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [173],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 174,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [174],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 175,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [175],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 176,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [176],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 177,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [177],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 178,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [178],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 179,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [179],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 180,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [180],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 181,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [181],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 182,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [182],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 183,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [183],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 184,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [184],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 185,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [185],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 186,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [186],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 187,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [187],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 188,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [188],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 189,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [189],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 190,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [190],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 191,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [191],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 192,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [192],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 193,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [193],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 194,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [194],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 195,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [131],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [195],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                        ],
                        'type': 'string',
                        'value_prefix': 'Main type of degradation addressed: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                    # Rank: 132 or 133
                    {
                        'mapping': [
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 165,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [165],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 166,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [166],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 167,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [167],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 168,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [168],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 169,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [169],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 170,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [170],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 171,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [171],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 172,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [172],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 173,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [173],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 174,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [174],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 175,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [175],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 176,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [176],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 177,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [177],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 178,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [178],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 179,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [179],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 180,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [180],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 181,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [181],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 182,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [182],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 183,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [183],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 184,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [184],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 185,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [185],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 186,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [186],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 187,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [187],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 188,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [188],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 189,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [189],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 190,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [190],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 191,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [191],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 192,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [192],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 193,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [193],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 194,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [194],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                            {
                                # Using a table/column which appears only 1x.
                                'wocat_table': 'qt_questionnaire_info',
                                'wocat_column': 'qt_id',
                                'value_mapping': 195,
                                'lookup_table': True,
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_4',
                                            },
                                        ],
                                        'operator': 'custom',
                                        'custom': [
                                            {
                                                'key': 'rank',
                                                'value': [132, 133],
                                                'operator': 'one_of',
                                            },
                                            {
                                                'key': 'degradation',
                                                'value': [195],
                                                'operator': 'one_of',
                                            }
                                        ]
                                    },
                                ]
                            },
                        ],
                        'type': 'string',
                        'value_prefix': 'Secondary types of degradation addressed: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                ],
                'type': 'string',
            }
        }
    }
}

# 3.8 Prevention of land degradation
tech_qg_35 = {
    'tech_qg_35': {
        'questions': {
            # TODO: This results in an Error
            'tech_prevention': {
                'mapping': [
                    {
                        'wocat_table': 'qt_2_2_2_3',
                        'wocat_column': 'prevention_rank',
                        'value_mapping': 'intervention_prevent_ld',
                    },
                    {
                        'wocat_table': 'qt_2_2_2_3',
                        'wocat_column': 'mitigation_rank',
                        'value_mapping': 'intervention_reduce_ld',
                    },
                    {
                        'wocat_table': 'qt_2_2_2_3',
                        'wocat_column': 'rehabilitation_rank',
                        'value_mapping': 'intervention_rehabilitate',
                    },
                ],
                'type': 'checkbox',
                'composite': {
                    'type': 'checkbox',
                }
            },
            'tech_prevention_comments': {
                'mapping': [
                    # Rank: 131
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'prevention_rank',
                                'value_mapping': 'prevention of land degradation',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'prevention_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'mitigation_rank',
                                'value_mapping': 'mitigation / reduction of land degradation',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'mitigation_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'rehabilitation_rank',
                                'value_mapping': 'rehabilitation / reclamation of denuded land',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'rehabilitation_rank',
                                            }
                                        ],
                                        'operator': 'contains',
                                        'value': '131'
                                    }
                                ]
                            },
                        ],
                        'type': 'string',
                        'value_prefix': 'Main goals: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                    # Rank: 132 or 133
                    {
                        'mapping': [
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'prevention_rank',
                                'value_mapping': 'prevention of land degradation',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'prevention_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'mitigation_rank',
                                'value_mapping': 'mitigation / reduction of land degradation',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'mitigation_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                            {
                                'wocat_table': 'qt_2_2_2_3',
                                'wocat_column': 'rehabilitation_rank',
                                'value_mapping': 'rehabilitation / reclamation of denuded land',
                                'conditions': [
                                    {
                                        'mapping': [
                                            {
                                                'wocat_table': 'qt_2_2_2_3',
                                                'wocat_column': 'rehabilitation_rank',
                                            }
                                        ],
                                        'operator': 'contains_not',
                                        'value': '131'
                                    }
                                ]
                            },
                        ],
                        'type': 'string',
                        'value_prefix': 'Secondary goals: ',
                        'composite': {
                            'type': 'merge',
                            'separator': ', '
                        }
                    },
                ],
                'type': 'string',
            }
        }
    }
}


questiongroups = [
    qg_name,
    qg_location,
    qg_import,
    qg_accept_conditions,
    tech_qg_1,  # Definition
    # tech_qg_2,  # Description
    qg_location_map,
    tech_qg_225,  # Location comments
    tech_qg_9,  # Land use types
    tech_qg_10,  # Land use subcategory: Cropland
    tech_qg_11,  # Land use subcategory: Grazing land
    tech_qg_12,  # Land use subcategory: Forest
    tech_qg_7,  # Land use: Comments
    tech_qg_4,  # Spread of the Technology,
    tech_qg_19,  # Water supply
    tech_qg_8,  # SLM measures
    tech_qg_21,  # SLM measures: Agronomic
    tech_qg_22,  # SLM measures: Vegetative
    tech_qg_23,  # SLM measures: Structural
    tech_qg_24,  # SLM measures: Management
    tech_qg_26,  # SLM measures: comments
    # tech_qg_35,  # Prevention of land degradation
    tech_qg_27,  # Main types of land degradation
    tech_qg_28,  # Main type of land degradation: Water erosion
    tech_qg_29,  # Main type of land degradation: Wind erosion
    tech_qg_30,  # Main type of land degradation: Chemical
    tech_qg_31,  # Main type of land degradation: Physical
    tech_qg_32,  # Main type of land degradation: Biological
    tech_qg_33,  # Main type of land degradation: Water
    tech_qg_34,  # Main type of land degradation: Comments
]

qt_mapping = {}
for qg in questiongroups:
    qt_mapping.update(qg)
