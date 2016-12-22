from django.conf import settings  # noqa
from appconf import AppConf


class ConfigurationConf(AppConf):
    """
    Custom settings for the configuration module.
    """
    # Value-User relations
    VALUEUSER_UNCCD = 'unccd_fp'

    # Map country ISO codes 3 to 2
    COUNTRY_ISO_MAPPING = {
        'AFG': 'AF',
        'ALA': 'AX',
        'ALB': 'AL',
        'DZA': 'DZ',
        'ASM': 'AS',
        'AND': 'AD',
        'AGO': 'AO',
        'AIA': 'AI',
        'ATA': 'AQ',
        'ATG': 'AG',
        'ARG': 'AR',
        'ARM': 'AM',
        'ABW': 'AW',
        'AUS': 'AU',
        'AUT': 'AT',
        'AZE': 'AZ',
        'BHS': 'BS',
        'BHR': 'BH',
        'BGD': 'BD',
        'BRB': 'BB',
        'BLR': 'BY',
        'BEL': 'BE',
        'BLZ': 'BZ',
        'BEN': 'BJ',
        'BMU': 'BM',
        'BTN': 'BT',
        'BOL': 'BO',
        'BIH': 'BA',
        'BWA': 'BW',
        'BVT': 'BV',
        'BRA': 'BR',
        'IOT': 'IO',
        'BRN': 'BN',
        'BGR': 'BG',
        'BFA': 'BF',
        'BDI': 'BI',
        'KHM': 'KH',
        'CMR': 'CM',
        'CAN': 'CA',
        'CPV': 'CV',
        'CYM': 'KY',
        'CAF': 'CF',
        'TCD': 'TD',
        'CHL': 'CL',
        'CHN': 'CN',
        'CXR': 'CX',
        'CCK': 'CC',
        'COL': 'CO',
        'COM': 'KM',
        'COG': 'CG',
        'COD': 'CD',
        'COK': 'CK',
        'CRI': 'CR',
        'CIV': 'CI',
        'HRV': 'HR',
        'CUB': 'CU',
        'CYP': 'CY',
        'CZE': 'CZ',
        'DNK': 'DK',
        'DJI': 'DJ',
        'DMA': 'DM',
        'DOM': 'DO',
        'ECU': 'EC',
        'EGY': 'EG',
        'SLV': 'SV',
        'GNQ': 'GQ',
        'ERI': 'ER',
        'EST': 'EE',
        'ETH': 'ET',
        'FLK': 'FK',
        'FRO': 'FO',
        'FJI': 'FJ',
        'FIN': 'FI',
        'FRA': 'FR',
        'GUF': 'GF',
        'PYF': 'PF',
        'ATF': 'TF',
        'GAB': 'GA',
        'GMB': 'GM',
        'GEO': 'GE',
        'DEU': 'DE',
        'GHA': 'GH',
        'GIB': 'GI',
        'GRC': 'GR',
        'GRL': 'GL',
        'GRD': 'GD',
        'GLP': 'GP',
        'GUM': 'GU',
        'GTM': 'GT',
        'GGY': 'GG',
        'GIN': 'GN',
        'GNB': 'GW',
        'GUY': 'GY',
        'HTI': 'HT',
        'HMD': 'HM',
        'VAT': 'VA',
        'HND': 'HN',
        'HKG': 'HK',
        'HUN': 'HU',
        'ISL': 'IS',
        'IND': 'IN',
        'IDN': 'ID',
        'IRN': 'IR',
        'IRQ': 'IQ',
        'IRL': 'IE',
        'IMN': 'IM',
        'ISR': 'IL',
        'ITA': 'IT',
        'JAM': 'JM',
        'JPN': 'JP',
        'JEY': 'JE',
        'JOR': 'JO',
        'KAZ': 'KZ',
        'KEN': 'KE',
        'KIR': 'KI',
        'PRK': 'KP',
        'KOR': 'KR',
        'KWT': 'KW',
        'KGZ': 'KG',
        'LAO': 'LA',
        'LVA': 'LV',
        'LBN': 'LB',
        'LSO': 'LS',
        'LBR': 'LR',
        'LBY': 'LY',
        'LIE': 'LI',
        'LTU': 'LT',
        'LUX': 'LU',
        'MAC': 'MO',
        'MKD': 'MK',
        'MDG': 'MG',
        'MWI': 'MW',
        'MYS': 'MY',
        'MDV': 'MV',
        'MLI': 'ML',
        'MLT': 'MT',
        'MHL': 'MH',
        'MTQ': 'MQ',
        'MRT': 'MR',
        'MUS': 'MU',
        'MYT': 'YT',
        'MEX': 'MX',
        'FSM': 'FM',
        'MDA': 'MD',
        'MCO': 'MC',
        'MNG': 'MN',
        'MNE': 'ME',
        'MSR': 'MS',
        'MAR': 'MA',
        'MOZ': 'MZ',
        'MMR': 'MM',
        'NAM': 'NA',
        'NRU': 'NR',
        'NPL': 'NP',
        'NLD': 'NL',
        'ANT': 'AN',
        'NCL': 'NC',
        'NZL': 'NZ',
        'NIC': 'NI',
        'NER': 'NE',
        'NGA': 'NG',
        'NIU': 'NU',
        'NFK': 'NF',
        'MNP': 'MP',
        'NOR': 'NO',
        'OMN': 'OM',
        'PAK': 'PK',
        'PLW': 'PW',
        'PSE': 'PS',
        'PAN': 'PA',
        'PNG': 'PG',
        'PRY': 'PY',
        'PER': 'PE',
        'PHL': 'PH',
        'PCN': 'PN',
        'POL': 'PL',
        'PRT': 'PT',
        'PRI': 'PR',
        'QAT': 'QA',
        'REU': 'RE',
        'ROU': 'RO',
        'RUS': 'RU',
        'RWA': 'RW',
        'BLM': 'BL',
        'SHN': 'SH',
        'KNA': 'KN',
        'LCA': 'LC',
        'MAF': 'MF',
        'SPM': 'PM',
        'VCT': 'VC',
        'WSM': 'WS',
        'SMR': 'SM',
        'STP': 'ST',
        'SAU': 'SA',
        'SEN': 'SN',
        'SRB': 'RS',
        'SYC': 'SC',
        'SLE': 'SL',
        'SGP': 'SG',
        'SVK': 'SK',
        'SVN': 'SI',
        'SLB': 'SB',
        'SOM': 'SO',
        'ZAF': 'ZA',
        'SGS': 'GS',
        'ESP': 'ES',
        'LKA': 'LK',
        'SDN': 'SD',
        'SUR': 'SR',
        'SJM': 'SJ',
        'SWZ': 'SZ',
        'SWE': 'SE',
        'CHE': 'CH',
        'SYR': 'SY',
        'TWN': 'TW',
        'TJK': 'TJ',
        'TZA': 'TZ',
        'THA': 'TH',
        'TLS': 'TL',
        'TGO': 'TG',
        'TKL': 'TK',
        'TON': 'TO',
        'TTO': 'TT',
        'TUN': 'TN',
        'TUR': 'TR',
        'TKM': 'TM',
        'TCA': 'TC',
        'TUV': 'TV',
        'UGA': 'UG',
        'UKR': 'UA',
        'ARE': 'AE',
        'GBR': 'GB',
        'USA': 'US',
        'UMI': 'UM',
        'URY': 'UY',
        'UZB': 'UZ',
        'VUT': 'VU',
        'VEN': 'VE',
        'VNM': 'VN',
        'VGB': 'VG',
        'VIR': 'VI',
        'WLF': 'WF',
        'ESH': 'EH',
        'YEM': 'YE',
        'ZMB': 'ZM',
        'ZWE': 'ZW',
    }

    # Override default behaviour to change the access key or the callable
    # to get the value for the summary based on the full questionnaire data.
    SUMMARY_OVERRIDE = {
        'qg_weaknesses_landusers.weaknesses_overcome': {
            'override_key': 'weaknesses_landuser_overcome',
        },
        'qg_location_map.location_map': {
            'override_key': 'location_map_data',
            'override_fn': lambda self, child: self.get_map_values(child)
        },
        'tech_qg_5.location_who_implemented': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'app_qg_5.location_type': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'qg_photos.header_image_image': {
            'override_key': 'images_image'
        },
        'qg_photos.header_image_caption': {
            'override_key': 'images_caption'
        },
        'qg_photos.header_image_photographer': {
            'override_key': 'images_photographer'
        },
        'tech_qg_6.classification_main_purpose': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_9.classification_landuse': {
            'override_fn': lambda self, child: self.get_picto_and_nested_values(child)
        },
        'tech_qg_19.classification_watersupply': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_35.classification_purpose': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_8.classification_measures': {
            'override_fn': lambda self, child: self.get_picto_and_nested_values(child)
        },
        'tech_qg_27.classification_degradation': {
            'override_fn': lambda self, child: self.get_picto_and_nested_values(child)
        },
        'tech_qg_54.natural_env_rainfall': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_55.natural_env_climate_zone': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_56.natural_env_slope': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_56.natural_env_landforms': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_56.natural_env_altitude': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_58.natural_env_soil_depth': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_58.natural_env_soil_texture': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_58.natural_env_soil_texture_below': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_58.natural_env_soil_organic': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_60.natural_env_groundwater': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_60.natural_env_surfacewater': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_60.natural_env_waterquality': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_63.natural_env_flooding': {
            'override_fn': lambda self, child: self.get_full_range_values(child, True)
        },
        'tech_qg_61.natural_env_salinity': {
            'override_fn': lambda self, child: self.get_full_range_values(child, True)
        },
        'tech_qg_66.natural_env_species': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
        'tech_qg_66.natural_env_habitat': {
            'override_fn': lambda self, child: self.get_full_range_values(child)
        },
    }
