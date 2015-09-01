"""
Place this file as "unccd.data_import.py" to make the import work.

Don't forget to adapt the file paths!
"""
PATH_LEG1 = '/home/lukas/dev/qcat2/unccd_data/Fourthleg1BPData.xlsx'
PATH_LEG2 = '/home/lukas/dev/qcat2/unccd_data/Fourthleg2BPData.xlsx'


from xlrd import open_workbook, xldate_as_tuple
from datetime import datetime

from configuration.cache import get_configuration
from questionnaire.utils import clean_questionnaire_data
from questionnaire.models import Questionnaire
from accounts.models import User
from search.index import put_questionnaire_data

NULL_VALUES = ['', '---', 'NULL']
NULL_VALUES_STRING = ['---', 'NULL']

MAPPING_LEG1 = {
    # qg_name
    # name (text)
    'Title of the best practice': 'name',

    # unccd_qg_1
    # unccd_property_rights (bool)
    # unccd_property_rights_description (text)
    'Property rights': 'propertyrights',

    # unccd_qg_3
    # unccd_landuse (checkbox)
    # unccd_qg_4
    # unccd_specify (text)
    'Prevailing land use within the specified location': 'prevailinglanduse',

    # unccd_qg_5
    # unccd_contribution_measures
    'With respect to DLDD, the best practice directly contributes to:': 'dlddcontribution',

    # unccd_qg_6
    # unccd_contribution_objectives
    'Specify to which strategic objectives of The Strategy the technology contributes (more than one box can be ticked)': 'strategicobjectives',

    # unccd_qg_8
    # unccd_linkages (checkbox)
    'Specify if the technology relates to one or more of the other UNCCD themes': 'unccdthemes',

    # unccd_qg_10
    # unccd_description
    'Short description of the best practice': 'description',

    # unccd_qg_9
    # unccd_location
    'Location (if available, also include a map)': 'location',
    # unccd_qg_9
    # unccd_location_extension
    'If the location has well defined boundaries, specify its extension in hectares': 'locationextent',
    # unccd_qg_9
    # unccd_population
    'Estimated population living in the location': 'population',

    # unccd_qg_11
    # unccd_natural_environment
    'Brief description of the natural environment within the specified location.': 'descriptionnaturalenvironment',

    # unccd_qg_12
    # unccd_socioeconomic
    'Prevailing socio-economic conditions of those living in the location and/or nearby': 'socioeconomicconditions',

    # unccd_qg_13
    # unccd_best_practice_criteria
    'On the basis of which criteria and/or indicator(s) (not related to The Strategy) the proposed practice and corresponding technology has been considered as ‘best’?': 'bestindicator',

    # unccd_qg_14
    # unccd_main_problems_addressed
    'Main problems addressed by the best practice': 'mainproblems',

    # unccd_qg_15
    # unccd_land_degradation_addressed
    'Outline specific land degradation problems addressed by the best practice': 'landdegradation',

    # unccd_qg_16
    # unccd_objectives
    'Specify the objectives of the best practice': 'objectives',

    # unccd_qg_17
    # unccd_description_objective
    'Brief description of main activities, by objective': 'descriptionobjectives',

    # unccd_qg_21
    # unccd_technology_description
    'Short description of the technology': 'descriptiontechnical1',
    'Technical specifications of the technology – if any': 'descriptiontechnical2',

    # unccd_qg_22
    # unccd_institution_name
    'Name and address of the institution developing the technology': 'nameaddress',

    # unccd_qg_23
    # unccd_partnership (bool)
    # unccd_partnership_partners (text)
    'Was the technology developed in partnership?': 'partnership',

    # unccd_qg_25
    # unccd_promotion_framework (checkbox)
    # unccd_promotion_framework_specify (text)
    'Specify the framework within which the technology was promoted': 'framework',

    # unccd_qg_27
    # unccd_local_stakeholders (boolean)
    # unccd_local_stakeholders_list (text)
    'Was the participation of local stakeholders, including CSOs, fostered in the development of the technology?': 'localstakeholders',

    # unccd_qg_29
    # unccd_stakeholder_roles
    'For the stakeholders listed above, specify their role in the design, introduction, use and maintenance of the technology, if any.': 'stakeholderroles',

    # unccd_qg_30
    # unccd_population_involved (boolean)
    # unccd_population_involved_means (checkbox)
    # unccd_population_involved_specify (text)
    'Was the population living in the location and/or nearby involved in the development of the technology?': 'populationinvolved',

    # unccd_qg_33
    # unccd_onsite_impacts
    'Describe on-site impacts (the major two impacts by category)': 'onsiteimpacts',

    # unccd_qg_37
    # unccd_offsite_impacts
    'Describe the major two off-site (i.e. not occurring in the location but in the surrounding areas) impacts': 'offsiteimpacts',

    # unccd_qg_38
    # unccd_impact_reasons
    'Impact on biodiversity and climate change': 'impactbiodiversity',

    # unccd_qg_39
    # unccd_cost_benefit_analysis (bool)
    # unccd_cost_benefit_analysis_text (text)
    'Has a cost-benefit analysis been carried out?': 'costbenefit',

    # unccd_qg_40
    # unccd_technology_disseminated (boolean)
    # unccd_technology_disseminated_where (text)
    'Was the technology disseminated/introduced to other locations?': 'techdissemination',

    # unccd_qg_42
    # unccd_incentives (boolean)
    # unccd_incentives_types (checkbox)
    'Were incentives to facilitate the take up of the technology provided?': 'incentives',

    # unccd_qg_44
    # unccd_success_conditions
    'Can you identify the three main conditions that led to the success of the presented best practice/technology?': 'successconditions',

    # unccd_qg_45
    # unccd_replicability (boolean)
    # unccd_replicability_level (checkbox)
    'In your opinion, the best practice/technology you have proposed can be replicated, although with some level of adaptation, elsewhere?': 'replicability',

    # unccd_qg_47
    # unccd_lessons_human_resources
    'Related to human resources': 'humanresources',

    # unccd_qg_48
    # unccd_lessons_financial
    'Related to financial aspects': 'financialaspects',

    # unccd_qg_49
    # unccd_lessons_technical
    'Related to technical aspects': 'technicalaspects',

    # unccd_qg_50
    # unccd_questions_leg1
    'Amount committed': 'questionsleg1',
    'Beneficiaries': 'questionsleg1',
    'Civil Society Organizations (CSOs) and Science & Technology Institutions (STIs)': 'questionsleg1',
    'Commitment date': 'questionsleg1',
    'Funding organization': 'questionsleg1',
    'Name of activity funded': 'questionsleg1',
    'Operational objectives': 'questionsleg1',
    'Recipient country(ies) or (sub)region(s)': 'questionsleg1',
    'Recipient organization(s)': 'questionsleg1',
    'Relevant Activity Codes (RACs)': 'questionsleg1',
    'Reporting Entity': 'questionsleg1',
    'Reporting entity(ies)': 'questionsleg1',
    'Rio Marker for desertification': 'questionsleg1',
    'Role of the Organization(s) in the Programme/Project': 'questionsleg1',
    'Status': 'questionsleg1',
    'Target area size/administrative unit': 'questionsleg1',
    'Target Group': 'questionsleg1',
    'Title': 'questionsleg1',
    'United Nations Conventions’ Rio Markers': 'questionsleg1',

    # qg_country
    # country

    # unccd_qg_7
    # unccd_impact_type (not available)

    # unccd_qg_38
    # unccd_impact_biodiversity_conservation (not available, but part of unccd_impact_reasons)
    # unccd_impact_cc_mitigation (not available, but part of unccd_impact_reasons)
    # unccd_impact_cc_adaptation (not available, but part of unccd_impact_reasons)
}


MAPPING_LEG2 = {
    # unccd_qg_1
    # unccd_property_rights (bool)
    # unccd_property_rights_description (text)
    'Property rights': 'propertyrights',

    # qg_name
    # name (text)
    'Title of the best practice': 'name',

    # unccd_qg_9
    # unccd_location
    'Location (if available, also include a map)': 'location',

    # unccd_qg_11
    # unccd_natural_environment
    'Brief description of the natural environment within the specified location.': 'descriptionnaturalenvironment',

    # unccd_qg_12
    # unccd_socioeconomic
    'Prevailing socio-economic conditions of those living in the location and/or nearby': 'socioeconomicconditions',

    # unccd_qg_10
    # unccd_description
    'Short description of the best practice': 'description',

    # unccd_qg_13
    # unccd_best_practice_criteria
    'On the basis of which criteria and/or indicator(s) (not related to The Strategy) the proposed practice and corresponding technology has been considered as ‘best’?': 'bestindicator',

    # unccd_qg_14
    # unccd_main_problems_addressed
    'Main problems addressed by the best practice': 'mainproblems',

    # unccd_qg_15
    # unccd_land_degradation_addressed
    'Outline specific land degradation problems addressed by the best practice': 'landdegradation',

    # unccd_qg_16
    # unccd_objectives
    'Specify the objectives of the best practice': 'objectives',

    # unccd_qg_17
    # unccd_description_objective
    'Brief description of main activities, by objective': 'descriptionobjectives',

    # unccd_qg_21
    # unccd_technology_description
    'Short description and technical specifications of the technology': 'descriptiontechnical',

    # unccd_qg_22
    # unccd_institution_name
    'Name and address of the institution developing the technology': 'nameaddress',

    # unccd_qg_23
    # unccd_partnership (bool)
    # unccd_partnership_partners (text)
    'Was the technology developed in partnership?': 'partnership',

    # unccd_qg_25
    # unccd_promotion_framework (checkbox)
    # unccd_promotion_framework_specify (text)
    'Specify the framework within which the technology was promoted': 'framework',

    # unccd_qg_27
    # unccd_local_stakeholders (boolean)
    # unccd_local_stakeholders_list (text)
    'Was the participation of local stakeholders, including CSOs, fostered in the development of the technology?': 'localstakeholders',

    # unccd_qg_29
    # unccd_stakeholder_roles
    'For the stakeholders listed above, specify their role in the design, introduction, use and maintenance of the technology, if any.': 'stakeholderroles',

    # unccd_qg_30
    # unccd_population_involved (boolean)
    # unccd_population_involved_means (checkbox)
    # unccd_population_involved_specify (text)
    'Was the population living in the location and/or nearby involved in the development of the technology?': 'populationinvolved',

    # unccd_qg_33
    # unccd_onsite_impacts
    'Describe on-site impacts (the major two impacts by category)': 'onsiteimpacts',

    # unccd_qg_37
    # unccd_offsite_impacts
    'Describe the major two off-site (i.e. not occurring in the location but in the surrounding areas) impacts': 'offsiteimpacts',

    # unccd_qg_38
    # unccd_impact_reasons
    'Impact on biodiversity and climate change': 'impactbiodiversity',

    # unccd_qg_39
    # unccd_cost_benefit_analysis (bool)
    # unccd_cost_benefit_analysis_text (text) - not available in leg 2
    'Has a cost-benefit analysis been carried out?': 'costbenefit',

    # unccd_qg_40
    # unccd_technology_disseminated (boolean)
    # unccd_technology_disseminated_where (text)
    'Was the technology disseminated/introduced to other locations?': 'techdissemination',

    # unccd_qg_42
    # unccd_incentives (boolean)
    # unccd_incentives_types (checkbox)
    'Were incentives to facilitate the take up of the technology provided?': 'incentives',

    # unccd_qg_44
    # unccd_success_conditions
    'Can you identify the three main conditions that led to the success of the presented best practice/technology?': 'successconditions',

    # unccd_qg_45
    # unccd_replicability (boolean)
    # unccd_replicability_level (checkbox)
    'Replicability': 'replicability',

    # unccd_qg_47
    # unccd_lessons_human_resources
    'Related to human resources': 'humanresources',

    # unccd_qg_48
    # unccd_lessons_financial
    'Related to financial aspects': 'financialaspects',

    # unccd_qg_49
    # unccd_lessons_technical
    'Related to technical aspects': 'technicalaspects',

    # Left away
    'Classify the best practice according to classification adopted by decision 15/COP.10.': 'notmatchable',
}


def data_import():
    configuration = get_configuration('unccd')

    errors = []
    inserted = []

    # for objects in [parse_leg1(), parse_leg2()][:5]:
    # for objects in [parse_leg1()]:
    for objects in [parse_leg1(), parse_leg2()]:

        for obj in objects:

            qg_data = prepare_questiongroups(obj)

            # print("------")
            # print(qg_data)

            cleaned_qg_data = {}
            for qg, qg_d in qg_data.items():
                # print(qg_d)
                clean_qg_list = []
                for single_qg_data in qg_d:
                    # print(single_qg_data)
                    clean_single_qg = {}
                    for key, value in single_qg_data.items():
                        if not isinstance(value, dict):
                            clean_single_qg[key] = value
                            continue
                        clean_v_dict = {}
                        for lang, v in value.items():
                            if v in NULL_VALUES_STRING:
                                v = 'No Data'
                                # print("************")
                                # print(v)
                                # continue
                            clean_v_dict[lang] = v
                        clean_single_qg[key] = clean_v_dict
                    clean_qg_list.append(clean_single_qg)
                cleaned_qg_data[qg] = clean_qg_list

            # Check the data against the configuration
            data, data_errors = clean_questionnaire_data(
                cleaned_qg_data, configuration)

            if data_errors:
                errors.append((obj, data_errors))

            obj['qg_data'] = data

            # print("=======")
            # print(data)

        if len(errors) > 0:
            return False, errors

        # Insert the data

        # TODO
        user = User.objects.first()

        for obj in objects:
            questionnaire = Questionnaire.create_new(
                'unccd', obj.get('qg_data'), user, status=3,
                created=obj.get('created'), updated=obj.get('updated'))
            put_questionnaire_data('unccd', [questionnaire])
            inserted.append(questionnaire)

    return True, inserted


def parse_leg1():
    file = PATH_LEG1

    book = open_workbook(file, on_demand=True)
    sheet = book.sheet_by_index(0)

    objects = []

    for row_idx in range(1, sheet.nrows):
        row = sheet.row(row_idx)

        reporting_entity_id = row[0].value
        answergroup_id = row[4].value
        # answer_answered = row[6].value
        question_title = row[7].value
        fieldcontent = row[8].value

        if question_title == '':
            continue

        # if question_title not in available_questions:
        #     available_questions.append(question_title)

        # A questionnaire is identified by its Reporting Entity and its Answergroup
        identifier = '{}__{}'.format(reporting_entity_id, answergroup_id)

        # Check if the questionnaire already exists
        obj = next((o for o in objects if o.get('id') == identifier), None)
        if obj is None:
            # Add the questionnaire to the list if it does not yet exist
            obj = {
                'id': identifier,
                'data': {},
            }
            objects.append(obj)

        # if question_title != 'Related to financial aspects':
        #     continue
        # print(identifier)
        # print(fieldcontent)

        question_mapped = MAPPING_LEG1[question_title]

        # Creation date
        obj['created'] = datetime(*xldate_as_tuple(row[10].value, book.datemode))

        # Update
        obj['updated'] = datetime(*xldate_as_tuple(row[11].value, book.datemode))

        # qg_country
        # country
        country = row[1].value
        if obj.get('data', {}).get('qg_country') is None:
            obj['data']['qg_country'] = country

        # unccd_qg_2
        # unccd_reporting_entity
        reporting_entity = row[1].value
        obj['data']['unccd_qg_2'] = reporting_entity

        # unccd_qg_1
        # unccd_property_rights (bool)
        # unccd_property_rights_description (text)
        if question_mapped == 'propertyrights':
            qg_data = obj.get('data', {}).get('unccd_qg_1')
            if qg_data is None:
                obj['data']['unccd_qg_1'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_property_rights', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_1']['unccd_property_rights'] = q
            except ValueError:
                q = qg_data.get('unccd_property_rights_description', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_1']['unccd_property_rights_description'] = q

        # qg_name
        # name (text)
        if question_mapped == 'name':
            qg_data = obj.get('data', {}).get('qg_name')
            if qg_data is None:
                obj['data']['qg_name'] = {}
                qg_data = {}
            q = qg_data.get('name', [])
            q.append(fieldcontent)
            obj['data']['qg_name']['name'] = q

        # unccd_qg_9
        # unccd_location
        if question_mapped == 'location':
            qg_data = obj.get('data', {}).get('unccd_qg_9')
            if qg_data is None:
                obj['data']['unccd_qg_9'] = {}
                qg_data = {}
            q = qg_data.get('location', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_9']['unccd_location'] = q
        # unccd_qg_9
        # unccd_location_extension
        if question_mapped == 'locationextent':
            qg_data = obj.get('data', {}).get('unccd_qg_9')
            if qg_data is None:
                obj['data']['unccd_qg_9'] = {}
                qg_data = {}
            q = qg_data.get('location', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_9']['unccd_location_extension'] = q
        # unccd_qg_9
        # unccd_population
        if question_mapped == 'population':
            qg_data = obj.get('data', {}).get('unccd_qg_9')
            if qg_data is None:
                obj['data']['unccd_qg_9'] = {}
                qg_data = {}
            q = qg_data.get('location', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_9']['unccd_population'] = q

        # unccd_qg_3
        # unccd_landuse (checkbox)
        # unccd_qg_4
        # unccd_specify (text)
        if question_mapped == 'prevailinglanduse':
            qg_data = obj.get('data', {}).get('unccd_qg_3')
            if qg_data is None:
                obj['data']['unccd_qg_3'] = {}
                qg_data = {}
            q = qg_data.get('unccd_landuse', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_3']['unccd_landuse'] = q

        # unccd_qg_11
        # unccd_natural_environment
        if question_mapped == 'descriptionnaturalenvironment':
            qg_data = obj.get('data', {}).get('unccd_qg_11')
            if qg_data is None:
                obj['data']['unccd_qg_11'] = {}
                qg_data = {}
            q = qg_data.get('unccd_natural_environment', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_11']['unccd_natural_environment'] = q

        # unccd_qg_12
        # unccd_socioeconomic
        if question_mapped == 'socioeconomicconditions':
            qg_data = obj.get('data', {}).get('unccd_qg_12')
            if qg_data is None:
                obj['data']['unccd_qg_12'] = {}
                qg_data = {}
            q = qg_data.get('unccd_socioeconomic', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_12']['unccd_socioeconomic'] = q

        # unccd_qg_10
        # unccd_description
        if question_mapped == 'description':
            qg_data = obj.get('data', {}).get('unccd_qg_10')
            if qg_data is None:
                obj['data']['unccd_qg_10'] = {}
                qg_data = {}
            q = qg_data.get('unccd_description', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_10']['unccd_description'] = q

        # unccd_qg_13
        # unccd_best_practice_criteria
        if question_mapped == 'bestindicator':
            qg_data = obj.get('data', {}).get('unccd_qg_13')
            if qg_data is None:
                obj['data']['unccd_qg_13'] = {}
                qg_data = {}
            q = qg_data.get('unccd_best_practice_criteria', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_13']['unccd_best_practice_criteria'] = q

        # unccd_qg_5
        # unccd_contribution_measures (checkbox)
        if question_mapped == 'dlddcontribution':
            qg_data = obj.get('data', {}).get('unccd_qg_5')
            if qg_data is None:
                obj['data']['unccd_qg_5'] = {}
                qg_data = {}
            q = qg_data.get('unccd_contribution_measures', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_5']['unccd_contribution_measures'] = q

        # unccd_qg_14
        # unccd_main_problems_addressed
        if question_mapped == 'mainproblems':
            qg_data = obj.get('data', {}).get('unccd_qg_14')
            if qg_data is None:
                obj['data']['unccd_qg_14'] = {}
                qg_data = {}
            q = qg_data.get('unccd_main_problems_addressed', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_14']['unccd_main_problems_addressed'] = q

        # unccd_qg_15
        # unccd_land_degradation_addressed
        if question_mapped == 'landdegradation':
            qg_data = obj.get('data', {}).get('unccd_qg_15')
            if qg_data is None:
                obj['data']['unccd_qg_15'] = {}
                qg_data = {}
            q = qg_data.get('unccd_land_degradation_addressed', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_15']['unccd_land_degradation_addressed'] = q

        # unccd_qg_16
        # unccd_objectives
        if question_mapped == 'objectives':
            qg_data = obj.get('data', {}).get('unccd_qg_16')
            if qg_data is None:
                obj['data']['unccd_qg_16'] = {}
                qg_data = {}
            q = qg_data.get('unccd_objectives', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_16']['unccd_objectives'] = q

        # unccd_qg_17
        # unccd_description_objective
        if question_mapped == 'descriptionobjectives':
            qg_data = obj.get('data', {}).get('unccd_qg_17')
            if qg_data is None:
                obj['data']['unccd_qg_17'] = {}
                qg_data = {}
            q = qg_data.get('unccd_description_objective', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_17']['unccd_description_objective'] = q

        # unccd_qg_21
        # unccd_technology_description
        if question_mapped == 'descriptiontechnical1':
            qg_data = obj.get('data', {}).get('unccd_qg_21')
            if qg_data is None:
                obj['data']['unccd_qg_21'] = {}
                qg_data = {}
            q = qg_data.get('unccd_technology_description1', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_21']['unccd_technology_description1'] = q
        # unccd_qg_21
        # unccd_technology_description
        if question_mapped == 'descriptiontechnical2':
            qg_data = obj.get('data', {}).get('unccd_qg_21')
            if qg_data is None:
                obj['data']['unccd_qg_21'] = {}
                qg_data = {}
            q = qg_data.get('unccd_technology_description2', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_21']['unccd_technology_description2'] = q

        # unccd_qg_22
        # unccd_institution_name
        if question_mapped == 'nameaddress':
            qg_data = obj.get('data', {}).get('unccd_qg_22')
            if qg_data is None:
                obj['data']['unccd_qg_22'] = {}
                qg_data = {}
            q = qg_data.get('unccd_institution_name', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_22']['unccd_institution_name'] = q

        # unccd_qg_23
        # unccd_partnership (bool)
        # unccd_partnership_partners (text)
        if question_mapped == 'partnership':
            qg_data = obj.get('data', {}).get('unccd_qg_23')
            if qg_data is None:
                obj['data']['unccd_qg_23'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_partnership', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_23']['unccd_partnership'] = q
            except ValueError:
                q = qg_data.get('unccd_partnership_partners', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_23']['unccd_partnership_partners'] = q

        # unccd_qg_25
        # unccd_promotion_framework (checkbox)
        # unccd_promotion_framework_specify (text)
        if question_mapped == 'framework':
            qg_data = obj.get('data', {}).get('unccd_qg_25')
            if qg_data is None:
                obj['data']['unccd_qg_25'] = {}
                qg_data = {}
            q = qg_data.get('unccd_promotion_framework', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_25']['unccd_promotion_framework'] = q

        # unccd_qg_27
        # unccd_local_stakeholders (boolean)
        # unccd_local_stakeholders_list (text)
        if question_mapped == 'localstakeholders':
            qg_data = obj.get('data', {}).get('unccd_qg_27')
            if qg_data is None:
                obj['data']['unccd_qg_27'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_local_stakeholders', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_27']['unccd_local_stakeholders'] = q
            except ValueError:
                q = qg_data.get('unccd_local_stakeholders_list', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_27']['unccd_local_stakeholders_list'] = q

        # unccd_qg_29
        # unccd_stakeholder_roles
        if question_mapped == 'stakeholderroles':
            qg_data = obj.get('data', {}).get('unccd_qg_29')
            if qg_data is None:
                obj['data']['unccd_qg_29'] = {}
                qg_data = {}
            q = qg_data.get('unccd_stakeholder_roles', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_29']['unccd_stakeholder_roles'] = q

        # unccd_qg_30
        # unccd_population_involved (boolean)
        # unccd_population_involved_means (checkbox)
        # unccd_population_involved_specify (text)
        if question_mapped == 'populationinvolved':
            qg_data = obj.get('data', {}).get('unccd_qg_30')
            if qg_data is None:
                obj['data']['unccd_qg_30'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_population_involved', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_30']['unccd_population_involved'] = q
            except ValueError:
                q = qg_data.get('unccd_population_involved_specify', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_30']['unccd_population_involved_specify'] = q

        # unccd_qg_6
        # unccd_contribution_objectives (checkbox)
        if question_mapped == 'strategicobjectives':
            qg_data = obj.get('data', {}).get('unccd_qg_6')
            if qg_data is None:
                obj['data']['unccd_qg_6'] = {}
                qg_data = {}
            q = qg_data.get('unccd_contribution_objectives', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_6']['unccd_contribution_objectives'] = q

        # unccd_qg_33
        # unccd_onsite_impacts
        if question_mapped == 'onsiteimpacts':
            qg_data = obj.get('data', {}).get('unccd_qg_33')
            if qg_data is None:
                obj['data']['unccd_qg_33'] = {}
                qg_data = {}
            q = qg_data.get('unccd_onsite_impacts', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_33']['unccd_onsite_impacts'] = q

        # unccd_qg_37
        # unccd_offsite_impacts
        if question_mapped == 'offsiteimpacts':
            qg_data = obj.get('data', {}).get('unccd_qg_37')
            if qg_data is None:
                obj['data']['unccd_qg_37'] = {}
                qg_data = {}
            q = qg_data.get('unccd_offsite_impacts', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_37']['unccd_offsite_impacts'] = q

        # unccd_qg_38
        # unccd_impact_reasons
        if question_mapped == 'impactbiodiversity':
            qg_data = obj.get('data', {}).get('unccd_qg_38')
            if qg_data is None:
                obj['data']['unccd_qg_38'] = {}
                qg_data = {}
            q = qg_data.get('unccd_impact_reasons', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_38']['unccd_impact_reasons'] = q

        # unccd_qg_39
        # unccd_cost_benefit_analysis (bool)
        # unccd_cost_benefit_analysis_text (text)
        if question_mapped == 'costbenefit':
            qg_data = obj.get('data', {}).get('unccd_qg_39')
            if qg_data is None:
                obj['data']['unccd_qg_39'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_cost_benefit_analysis', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_39']['unccd_cost_benefit_analysis'] = q
            except ValueError:
                q = qg_data.get('unccd_cost_benefit_analysis_text', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_39']['unccd_cost_benefit_analysis_text'] = q

        # unccd_qg_8
        # unccd_linkages (checkbox)
        if question_mapped == 'unccdthemes':
            qg_data = obj.get('data', {}).get('unccd_qg_8')
            if qg_data is None:
                obj['data']['unccd_qg_8'] = {}
                qg_data = {}
            q = qg_data.get('unccd_linkages', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_8']['unccd_linkages'] = q

        # unccd_qg_40
        # unccd_technology_disseminated (boolean)
        # unccd_technology_disseminated_where (text)
        if question_mapped == 'techdissemination':
            qg_data = obj.get('data', {}).get('unccd_qg_40')
            if qg_data is None:
                obj['data']['unccd_qg_40'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_technology_disseminated', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_40']['unccd_technology_disseminated'] = q
            except ValueError:
                q = qg_data.get('unccd_technology_disseminated_where', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_40']['unccd_technology_disseminated_where'] = q

        # unccd_qg_42
        # unccd_incentives (boolean)
        # unccd_incentives_types (checkbox)
        if question_mapped == 'incentives':
            qg_data = obj.get('data', {}).get('unccd_qg_42')
            if qg_data is None:
                obj['data']['unccd_qg_42'] = {}
                qg_data = {}
            q = qg_data.get('unccd_incentives', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_42']['unccd_incentives'] = q

        # unccd_qg_44
        # unccd_success_conditions
        if question_mapped == 'successconditions':
            qg_data = obj.get('data', {}).get('unccd_qg_44')
            if qg_data is None:
                obj['data']['unccd_qg_44'] = {}
                qg_data = {}
            q = qg_data.get('unccd_success_conditions', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_44']['unccd_success_conditions'] = q

        # unccd_qg_45
        # unccd_replicability (boolean)
        # unccd_replicability_level (checkbox)
        if question_mapped == 'replicability':
            qg_data = obj.get('data', {}).get('unccd_qg_45')
            if qg_data is None:
                obj['data']['unccd_qg_45'] = {}
                qg_data = {}
            q = qg_data.get('unccd_replicability', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_45']['unccd_replicability'] = q

        # unccd_qg_47
        # unccd_lessons_human_resources
        if question_mapped == 'humanresources':
            qg_data = obj.get('data', {}).get('unccd_qg_47')
            if qg_data is None:
                obj['data']['unccd_qg_47'] = {}
                qg_data = {}
            q = qg_data.get('unccd_lessons_human_resources', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_47']['unccd_lessons_human_resources'] = q

        # unccd_qg_48
        # unccd_lessons_financial
        if question_mapped == 'financialaspects':
            qg_data = obj.get('data', {}).get('unccd_qg_48')
            if qg_data is None:
                obj['data']['unccd_qg_48'] = {}
                qg_data = {}
            q = qg_data.get('unccd_lessons_financial', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_48']['unccd_lessons_financial'] = q

        # unccd_qg_49
        # unccd_lessons_technical
        if question_mapped == 'technicalaspects':
            qg_data = obj.get('data', {}).get('unccd_qg_49')
            if qg_data is None:
                obj['data']['unccd_qg_49'] = {}
                qg_data = {}
            q = qg_data.get('unccd_lessons_technical', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_49']['unccd_lessons_technical'] = q

        # unccd_qg_50
        # unccd_questions_leg1
        if question_mapped == 'questionsleg1':
            qg_data = obj.get('data', {}).get('unccd_qg_50')
            if qg_data is None:
                obj['data']['unccd_qg_50'] = {}
                qg_data = {}
            q = qg_data.get('unccd_questions_leg1', [])
            if str(fieldcontent) not in NULL_VALUES:
                q.append('{}: {}'.format(question_title, fieldcontent))
            obj['data']['unccd_qg_50']['unccd_questions_leg1'] = q

    return objects


def parse_leg2():
    file = PATH_LEG2

    book = open_workbook(file, on_demand=True)
    sheet = book.sheet_by_index(0)

    objects = []

    for row_idx in range(1, sheet.nrows):
        row = sheet.row(row_idx)

        reporting_entity_id = row[0].value
        answergroup_id = row[4].value
        # answer_answered = row[6].value
        question_title = row[7].value
        fieldcontent = row[8].value

        if question_title == '':
            continue

        # if question_title not in available_questions:
        #     available_questions.append(question_title)

        # A questionnaire is identified by its Reporting Entity and its Answergroup
        identifier = '{}__{}'.format(reporting_entity_id, answergroup_id)

        # if question_title != 'Replicability':
        #     continue
        # print(identifier)
        # print(fieldcontent)

        # Check if the questionnaire already exists
        obj = next((o for o in objects if o.get('id') == identifier), None)
        if obj is None:
            # Add the questionnaire to the list if it does not yet exist
            obj = {
                'id': identifier,
                'data': {},
            }
            objects.append(obj)

        question_mapped = MAPPING_LEG2[question_title]
        # if obj.get(question_mapped) is None:
        #     obj[question_mapped] = {}

        # Creation date
        if row[10].value != '':
            obj['created'] = datetime(*xldate_as_tuple(row[10].value, book.datemode))

        # Update
        if row[11].value != '':
            obj['updated'] = datetime(*xldate_as_tuple(row[11].value, book.datemode))

        # qg_country
        # country
        country = row[1].value
        if obj.get('data', {}).get('qg_country') is None:
            obj['data']['qg_country'] = country

        # unccd_qg_2
        # unccd_reporting_entity
        reporting_entity = row[1].value
        obj['data']['unccd_qg_2'] = reporting_entity

        # unccd_qg_1
        # unccd_property_rights (bool)
        # unccd_property_rights_description (text)
        if question_mapped == 'propertyrights':
            qg_data = obj.get('data', {}).get('unccd_qg_1')
            if qg_data is None:
                obj['data']['unccd_qg_1'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_property_rights', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_1']['unccd_property_rights'] = q
            except ValueError:
                q = qg_data.get('unccd_property_rights_description', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_1']['unccd_property_rights_description'] = q

        # qg_name
        # name (text)
        if question_mapped == 'name':
            qg_data = obj.get('data', {}).get('qg_name')
            if qg_data is None:
                obj['data']['qg_name'] = {}
                qg_data = {}
            q = qg_data.get('name', [])
            q.append(fieldcontent)
            obj['data']['qg_name']['name'] = q

        # unccd_qg_9
        # unccd_location
        if question_mapped == 'location':
            qg_data = obj.get('data', {}).get('unccd_qg_9')
            if qg_data is None:
                obj['data']['unccd_qg_9'] = {}
                qg_data = {}
            q = qg_data.get('location', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_9']['unccd_location'] = q

        # unccd_qg_11
        # unccd_natural_environment
        if question_mapped == 'descriptionnaturalenvironment':
            qg_data = obj.get('data', {}).get('unccd_qg_11')
            if qg_data is None:
                obj['data']['unccd_qg_11'] = {}
                qg_data = {}
            q = qg_data.get('unccd_natural_environment', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_11']['unccd_natural_environment'] = q

        # unccd_qg_12
        # unccd_socioeconomic
        if question_mapped == 'socioeconomicconditions':
            qg_data = obj.get('data', {}).get('unccd_qg_12')
            if qg_data is None:
                obj['data']['unccd_qg_12'] = {}
                qg_data = {}
            q = qg_data.get('unccd_socioeconomic', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_12']['unccd_socioeconomic'] = q

        # unccd_qg_10
        # unccd_description
        if question_mapped == 'description':
            qg_data = obj.get('data', {}).get('unccd_qg_10')
            if qg_data is None:
                obj['data']['unccd_qg_10'] = {}
                qg_data = {}
            q = qg_data.get('unccd_description', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_10']['unccd_description'] = q

        # unccd_qg_13
        # unccd_best_practice_criteria
        if question_mapped == 'bestindicator':
            qg_data = obj.get('data', {}).get('unccd_qg_13')
            if qg_data is None:
                obj['data']['unccd_qg_13'] = {}
                qg_data = {}
            q = qg_data.get('unccd_best_practice_criteria', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_13']['unccd_best_practice_criteria'] = q

        # unccd_qg_14
        # unccd_main_problems_addressed
        if question_mapped == 'mainproblems':
            qg_data = obj.get('data', {}).get('unccd_qg_14')
            if qg_data is None:
                obj['data']['unccd_qg_14'] = {}
                qg_data = {}
            q = qg_data.get('unccd_main_problems_addressed', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_14']['unccd_main_problems_addressed'] = q

        # unccd_qg_15
        # unccd_land_degradation_addressed
        if question_mapped == 'landdegradation':
            qg_data = obj.get('data', {}).get('unccd_qg_15')
            if qg_data is None:
                obj['data']['unccd_qg_15'] = {}
                qg_data = {}
            q = qg_data.get('unccd_land_degradation_addressed', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_15']['unccd_land_degradation_addressed'] = q

        # unccd_qg_16
        # unccd_objectives
        if question_mapped == 'objectives':
            qg_data = obj.get('data', {}).get('unccd_qg_16')
            if qg_data is None:
                obj['data']['unccd_qg_16'] = {}
                qg_data = {}
            q = qg_data.get('unccd_objectives', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_16']['unccd_objectives'] = q

        # unccd_qg_17
        # unccd_description_objective
        if question_mapped == 'descriptionobjectives':
            qg_data = obj.get('data', {}).get('unccd_qg_17')
            if qg_data is None:
                obj['data']['unccd_qg_17'] = {}
                qg_data = {}
            q = qg_data.get('unccd_description_objective', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_17']['unccd_description_objective'] = q

        # unccd_qg_21
        # unccd_technology_description
        if question_mapped == 'descriptiontechnical':
            qg_data = obj.get('data', {}).get('unccd_qg_21')
            if qg_data is None:
                obj['data']['unccd_qg_21'] = {}
                qg_data = {}
            q = qg_data.get('unccd_technology_description1', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_21']['unccd_technology_description1'] = q

        # unccd_qg_22
        # unccd_institution_name
        if question_mapped == 'nameaddress':
            qg_data = obj.get('data', {}).get('unccd_qg_22')
            if qg_data is None:
                obj['data']['unccd_qg_22'] = {}
                qg_data = {}
            q = qg_data.get('unccd_institution_name', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_22']['unccd_institution_name'] = q

        # unccd_qg_23
        # unccd_partnership (bool)
        # unccd_partnership_partners (text)
        if question_mapped == 'partnership':
            qg_data = obj.get('data', {}).get('unccd_qg_23')
            if qg_data is None:
                obj['data']['unccd_qg_23'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_partnership', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_23']['unccd_partnership'] = q
            except ValueError:
                q = qg_data.get('unccd_partnership_partners', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_23']['unccd_partnership_partners'] = q

        # unccd_qg_25
        # unccd_promotion_framework (checkbox)
        # unccd_promotion_framework_specify (text)
        if question_mapped == 'framework':
            qg_data = obj.get('data', {}).get('unccd_qg_25')
            if qg_data is None:
                obj['data']['unccd_qg_25'] = {}
                qg_data = {}
            q = qg_data.get('unccd_promotion_framework', [])
            q.append(fieldcontent)
            obj['data']['unccd_qg_25']['unccd_promotion_framework'] = q

        # unccd_qg_27
        # unccd_local_stakeholders (boolean)
        # unccd_local_stakeholders_list (text)
        if question_mapped == 'localstakeholders':
            qg_data = obj.get('data', {}).get('unccd_qg_27')
            if qg_data is None:
                obj['data']['unccd_qg_27'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_local_stakeholders', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_27']['unccd_local_stakeholders'] = q
            except ValueError:
                q = qg_data.get('unccd_local_stakeholders_list', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_27']['unccd_local_stakeholders_list'] = q

        # unccd_qg_29
        # unccd_stakeholder_roles
        if question_mapped == 'stakeholderroles':
            qg_data = obj.get('data', {}).get('unccd_qg_29')
            if qg_data is None:
                obj['data']['unccd_qg_29'] = {}
                qg_data = {}
            q = qg_data.get('unccd_stakeholder_roles', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_29']['unccd_stakeholder_roles'] = q

        # unccd_qg_30
        # unccd_population_involved (boolean)
        # unccd_population_involved_means (checkbox)
        # unccd_population_involved_specify (text)
        if question_mapped == 'populationinvolved':
            qg_data = obj.get('data', {}).get('unccd_qg_30')
            if qg_data is None:
                obj['data']['unccd_qg_30'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_population_involved', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_30']['unccd_population_involved'] = q
            except ValueError:
                q = qg_data.get('unccd_population_involved_specify', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_30']['unccd_population_involved_specify'] = q

        # unccd_qg_33
        # unccd_onsite_impacts
        if question_mapped == 'onsiteimpacts':
            qg_data = obj.get('data', {}).get('unccd_qg_33')
            if qg_data is None:
                obj['data']['unccd_qg_33'] = {}
                qg_data = {}
            q = qg_data.get('unccd_onsite_impacts', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_33']['unccd_onsite_impacts'] = q

        # unccd_qg_37
        # unccd_offsite_impacts
        if question_mapped == 'offsiteimpacts':
            qg_data = obj.get('data', {}).get('unccd_qg_37')
            if qg_data is None:
                obj['data']['unccd_qg_37'] = {}
                qg_data = {}
            q = qg_data.get('unccd_offsite_impacts', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_37']['unccd_offsite_impacts'] = q

        # unccd_qg_38
        # unccd_impact_reasons
        if question_mapped == 'impactbiodiversity':
            qg_data = obj.get('data', {}).get('unccd_qg_38')
            if qg_data is None:
                obj['data']['unccd_qg_38'] = {}
                qg_data = {}
            q = qg_data.get('unccd_impact_reasons', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_38']['unccd_impact_reasons'] = q

        # unccd_qg_39
        # unccd_cost_benefit_analysis (bool)
        # unccd_cost_benefit_analysis_text (text)
        if question_mapped == 'costbenefit':
            qg_data = obj.get('data', {}).get('unccd_qg_39')
            if qg_data is None:
                obj['data']['unccd_qg_39'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_cost_benefit_analysis', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_39']['unccd_cost_benefit_analysis'] = q
            except ValueError:
                q = qg_data.get('unccd_cost_benefit_analysis_text', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_39']['unccd_cost_benefit_analysis_text'] = q

        # unccd_qg_40
        # unccd_technology_disseminated (boolean)
        # unccd_technology_disseminated_where (text)
        if question_mapped == 'techdissemination':
            qg_data = obj.get('data', {}).get('unccd_qg_40')
            if qg_data is None:
                obj['data']['unccd_qg_40'] = {}
                qg_data = {}
            try:
                i = int(fieldcontent)
                q = qg_data.get('unccd_technology_disseminated', [])
                # 0: True
                # 1: False
                if i == 0:
                    q.append(True)
                elif i == 1:
                    q.append(False)
                obj['data']['unccd_qg_40']['unccd_technology_disseminated'] = q
            except ValueError:
                q = qg_data.get('unccd_technology_disseminated_where', [])
                content = str(fieldcontent)
                if content not in NULL_VALUES:
                    q.append(content)
                obj['data']['unccd_qg_40']['unccd_technology_disseminated_where'] = q

        # unccd_qg_42
        # unccd_incentives (boolean)
        # unccd_incentives_types (checkbox)
        if question_mapped == 'incentives':
            qg_data = obj.get('data', {}).get('unccd_qg_42')
            if qg_data is None:
                obj['data']['unccd_qg_42'] = {}
                qg_data = {}
            q = qg_data.get('unccd_incentives', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_42']['unccd_incentives'] = q

        # unccd_qg_44
        # unccd_success_conditions
        if question_mapped == 'successconditions':
            qg_data = obj.get('data', {}).get('unccd_qg_44')
            if qg_data is None:
                obj['data']['unccd_qg_44'] = {}
                qg_data = {}
            q = qg_data.get('unccd_success_conditions', [])
            content = str(fieldcontent)
            if content not in NULL_VALUES:
                q.append(content)
            obj['data']['unccd_qg_44']['unccd_success_conditions'] = q

        # unccd_qg_45
        # unccd_replicability (boolean)
        # unccd_replicability_level (checkbox)
        if question_mapped == 'replicability':
            qg_data = obj.get('data', {}).get('unccd_qg_45')
            if qg_data is None:
                obj['data']['unccd_qg_45'] = {}
                qg_data = {}
            q = qg_data.get('unccd_replicability', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_45']['unccd_replicability'] = q

        # unccd_qg_47
        # unccd_lessons_human_resources
        if question_mapped == 'humanresources':
            qg_data = obj.get('data', {}).get('unccd_qg_47')
            if qg_data is None:
                obj['data']['unccd_qg_47'] = {}
                qg_data = {}
            q = qg_data.get('unccd_lessons_human_resources', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_47']['unccd_lessons_human_resources'] = q

        # unccd_qg_49
        # unccd_lessons_technical
        if question_mapped == 'technicalaspects':
            qg_data = obj.get('data', {}).get('unccd_qg_49')
            if qg_data is None:
                obj['data']['unccd_qg_49'] = {}
                qg_data = {}
            q = qg_data.get('unccd_lessons_technical', [])
            q.append(str(fieldcontent))
            obj['data']['unccd_qg_49']['unccd_lessons_technical'] = q

    return objects



def prepare_questiongroups(object):
    data = object.get('data')

    clean_data = {}

    # print(data)

    for qg_keyword, qg_data in data.items():

        if qg_keyword == 'qg_country':
            # qg_country
            # country
            country = qg_data
            countries = {
                'Armenia': 'country_ARM',
                'Iran (Islamic Republic of)': 'country_IRN',
                'Italy': 'country_ITA',
                'Jamaica': 'country_JAM',
                'Kazakhstan': 'country_KAZ',
                'Kenya': 'country_KEN',
                'Kyrgyzstan': 'country_KGZ',
                'Saint Kitts and Nevis': 'country_KNA',
                'Kuwait': 'country_KWT',
                'Lebanon': 'country_LBN',
                'Libya': 'country_LBY',
                'Saint Lucia': 'country_LCA',
                'Sri Lanka': 'country_LKA',
                'Lesotho': 'country_LSO',
                'Morocco': 'country_MAR',
                'Republic of Moldova': 'country_MDA',
                'Mexico': 'country_MEX',
                'Antigua and Barbuda': 'country_ATG',
                'Mongolia': 'country_MNG',
                'Australia': 'country_AUS',
                'Namibia': 'country_NAM',
                'Niger': 'country_NER',
                'Nigeria': 'country_NGA',
                'Nepal': 'country_NPL',
                'Nauru': 'country_NRU',
                'Oman': 'country_OMN',
                'Pakistan': 'country_PAK',
                'Peru': 'country_PER',
                'Philippines': 'country_PHL',
                'Palau': 'country_PLW',
                'Romania': 'country_ROU',
                'Burundi': 'country_BDI',
                'Rwanda': 'country_RWA',
                'Saudi Arabia': 'country_SAU',
                'Senegal': 'country_SEN',
                'El Salvador': 'country_SLV',
                'Suriname': 'country_SUR',
                'Benin': 'country_BEN',
                'Syrian Arab Republic': 'country_SYR',
                'Togo': 'country_TGO',
                'Thailand': 'country_THA',
                'Tajikistan': 'country_TJK',
                'Turkmenistan': 'country_TKM',
                'Burkina Faso': 'country_BFA',
                'Tonga': 'country_TON',
                'Tunisia': 'country_TUN',
                'United Republic of Tanzania': 'country_TZA',
                'Uganda': 'country_UGA',
                'Ukraine': 'country_UKR',
                'Uzbekistan': 'country_UZB',
                'Viet Nam': 'country_VNM',
                'Bulgaria': 'country_BGR',
                'Samoa': 'country_WSM',
                'Yemen': 'country_YEM',
                'Serbia': 'country_SRB',
                'South Africa': 'country_ZAF',
                'Bahamas': 'country_BHS',
                'Belarus': 'country_BLR',
                'Brazil': 'country_BRA',
                'Bhutan': 'country_BTN',
                'Central African Republic': 'country_CAF',
                'Canada': 'country_CAN',
                'Chile': 'country_CHL',
                'China': 'country_CHN',
                "Côte d'Ivoire": 'country_CIV',
                'Congo': 'country_COG',
                'Colombia': 'country_COL',
                'Cape Verde': 'country_CPV',
                'Albania': 'country_ALB',
                'Cuba': 'country_CUB',
                'Germany': 'country_DEU',
                'Djibouti': 'country_DJI',
                'Dominica': 'country_DMA',
                'Denmark': 'country_DNK',
                'Dominican Republic': 'country_DOM',
                'Ecuador': 'country_ECU',
                'Eritrea': 'country_ERI',
                'Fiji': 'country_FJI',
                'France': 'country_FRA',
                'Gabon': 'country_GAB',
                'Ghana': 'country_GHA',
                'United Arab Emirates': 'country_ARE',
                'Guinea': 'country_GIN',
                'Grenada': 'country_GRD',
                'Argentina': 'country_ARG',
                'Honduras': 'country_HND',
                'Hungary': 'country_HUN',
                'Indonesia': 'country_IDN',
                'India': 'country_IND',
                'The former Yugoslav Republic of Macedonia': 'country_MKD',
                'Mali': 'country_MLI',
                'Netherlands': 'country_NLD',
                'Russian Federation': 'country_RUS',
                'Democratic Republic of the Congo': 'country_COD',
                'Switzerland': 'country_CHE',
                'Spain': 'country_ESP',
                'Georgia': 'country_GEO',
                'Guinea-Bissau': 'country_GNB',
                'Guyana': 'country_GUY',

                # Special "countries"
                # Mapping often through http://www.unccd.int/en/Stakeholders/civil-society/Documents/PreRegistered%20Participants%20COP%2010.pdf

                # Leg 1 (possibly also in leg 2)
                'European Union': '',
                "Centre d'actions et de réalisations internationales": 'country_FRA',
                'Gram Bharati Samiti': 'country_IND',
                'Social Fund "Socium" of Support and Realization Youth\'s Initiatives': 'country_KGZ',
                'Association malienne pour la protection de l\'environnement "Stop-Sahel"': 'country_MLI',
                'Fundación del Sur': 'country_ARG',
                'Drylands Coordination Group - Norway': '',
                'Society for Conservation & Protection of Environment': 'country_PAK',
                'Environnement Développement Action dans le Tiers Monde': '',
                'Nongovernmental Organization BIOS': 'country_MDA',
                "Association pour l'environnement et le développement durable": 'country_COG',
                'Man and Nature': 'country_TJK',
                'Emirates Environmental Group': 'country_ARE',
                'Fundación Agreste (ecología y medio ambiente, desarrollo sustentable y cooperación)': 'country_ARG',
                'Grupo Ambiental para el Desarrollo': 'country_ARG',
                'Association Prudence au Sahel': 'country_BFA',
                'Fundazija Zemja Zavinagi': 'country_BGR',
                'Asociación para la Investigación y el Desarrollo Integral': 'country_PER',
                'Participatory Ecological Land Use Management - Uganda': 'country_UGA',
                'Gramin Vikas Trust': 'country_IND',
                'Watershed Organisation Trust': 'country_IND',

                # Leg 2
                'Association Nigérienne des Scouts de l’Environnement': 'country_NER',
                'Association Rélwendé pour le Développement': 'country_BFA',
                'Central Asia SRAP': '',
            }
            qg = {'country': countries[country]}

            clean_data['qg_country'] = [qg]

        if qg_keyword == 'unccd_qg_2':
            # unccd_qg_2
            # unccd_reporting_entity
            reporting_entity = qg_data
            if reporting_entity:
                clean_data['unccd_qg_2'] = [{
                    'unccd_reporting_entity': {'en': reporting_entity}}]

        if qg_keyword == 'unccd_qg_1':
            # unccd_qg_1
            # unccd_property_rights (bool)
            # unccd_property_rights_description (text)
            prop_rights = qg_data.get('unccd_property_rights', [])
            prop_rights_desc = qg_data.get(
                'unccd_property_rights_description', [])
            if object.get('id') in [
                '4570-700-CCD-152__1.0',
                '4570-700-CCD-163__4.0',
                '4570-700-CCD-180__1.0',
                '4570-700-CCD-180__2.0',
                '4570-700-CCD-180__3.0',
                '4570-700-CCD-180__4.0',
                '4570-700-CCD-180__5.0',
                '4570-700-CCD-180__6.0',
                '4570-700-CCD-21__10.0',
                '4570-700-CCD-21__12.0',
                '4570-700-CCD-42__2.0',
                '4570-700-CCD-42__3.0',
                '4570-700-CCD-64__1.0',
            ]:
                prop_rights = [prop_rights[0]]
            if len(prop_rights) > 1:
                raise Exception(
                    'Object {}: More than one boolean for unccd_property_rights: {} / {}'.format(object.get('id'), prop_rights, data))
            qg = {}
            if prop_rights:
                qg['unccd_property_rights'] = prop_rights[0]
            if prop_rights_desc:
                qg['unccd_property_rights_description'] = {}
                qg['unccd_property_rights_description']['en'] = '<br>'.join(
                    prop_rights_desc)
            clean_data['unccd_qg_1'] = [qg]

        if qg_keyword == 'qg_name':
            # qg_name
            # name (text)
            name = qg_data.get('name', [])
            if len(name) == 1 and name[0] == '':
                name = ['Unknown']
            qg = {}
            if name:
                qg['name'] = {}
                qg['name']['en'] = '<br>'.join(name)
            clean_data['qg_name'] = [qg]

        if qg_keyword == 'unccd_qg_9':
            # unccd_qg_9
            # unccd_location
            # unccd_location_extension
            # unccd_population
            location = qg_data.get('unccd_location', [])
            locationextent = qg_data.get('unccd_location_extension', [])
            population = qg_data.get('unccd_population', [])
            qg = {}
            if location:
                qg['unccd_location'] = {}
                qg['unccd_location']['en'] = '<br>'.join(location)
            if len(locationextent) == 1 and locationextent[0] == '':
                locationextent = []
            if locationextent:
                qg['unccd_location_extension'] = {}
                if len(locationextent) > 1:
                    qg['unccd_location_extension']['en'] = '<br>'.join(
                        str(locationextent))
                else:
                    qg['unccd_location_extension']['en'] = str(
                        locationextent[0])
            if len(population) == 1 and population[0] == '':
                population = []
            if population:
                qg['unccd_population'] = {}
                if len(population) > 1:
                    qg['unccd_population']['en'] = '<br>'.join(
                        str(population))
                else:
                    qg['unccd_population']['en'] = str(
                        population[0])
            clean_data['unccd_qg_9'] = [qg]

        if qg_keyword == 'unccd_qg_3':
            # unccd_qg_3
            # unccd_landuse (checkbox)
            # unccd_qg_4
            # unccd_specify (text)
            landuse = qg_data.get('unccd_landuse', [])
            checkboxes = []
            specify = []
            for undefined_answer in landuse:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            checkboxes.append(int(answer))
                        except:
                            specify.append(answer)
                except AttributeError:
                    # Only one number value, must be checkbox
                    checkboxes.append(int(undefined_answer))
            cb_qg = {}
            cb_values = [
                'unccd_landuse_cropland',
                'unccd_landuse_grazing_land',
                'unccd_landuse_woodland',
                'unccd_landuse_unproductive_land',
                'unccd_landuse_human_settlement',
                'unccd_landuse_other',
            ]
            if checkboxes:
                cb_qg['unccd_landuse'] = [cb_values[cb] for cb in checkboxes]
            specify_qg = {}
            if specify:
                specify_qg['unccd_specify'] = {}
                specify_qg['unccd_specify']['en'] = '<br>'.join(specify)
            clean_data['unccd_qg_4'] = [specify_qg]
            clean_data['unccd_qg_3'] = [cb_qg]
            if len(specify) == 1 and specify[0] == '':
                specify = []

        if qg_keyword == 'unccd_qg_11':
            # unccd_qg_11
            # unccd_natural_environment
            natenvironment = qg_data.get('unccd_natural_environment', [])
            if len(natenvironment) == 1 and natenvironment[0] == '':
                natenvironment = []
            qg = {}
            if natenvironment:
                qg['unccd_natural_environment'] = {}
                qg['unccd_natural_environment']['en'] = '<br>'.join(
                    natenvironment)
            clean_data['unccd_qg_11'] = [qg]

        if qg_keyword == 'unccd_qg_12':
            # unccd_qg_12
            # unccd_socioeconomic
            socioeconomic = qg_data.get('unccd_socioeconomic', [])
            if len(socioeconomic) == 1 and socioeconomic[0] == '':
                socioeconomic = []
            qg = {}
            if socioeconomic:
                qg['unccd_socioeconomic'] = {}
                qg['unccd_socioeconomic']['en'] = '<br>'.join(
                    socioeconomic)
            clean_data['unccd_qg_12'] = [qg]

        if qg_keyword == 'unccd_qg_10':
            # unccd_qg_10
            # unccd_description
            description = qg_data.get('unccd_description', [])
            if len(description) == 1 and description[0] == '':
                description = []
            qg = {}
            if description:
                qg['unccd_description'] = {}
                qg['unccd_description']['en'] = '<br>'.join(
                    description)
            clean_data['unccd_qg_10'] = [qg]

        if qg_keyword == 'unccd_qg_13':
            # unccd_qg_13
            # unccd_best_practice_criteria
            bestpractice = qg_data.get('unccd_best_practice_criteria', [])
            if len(bestpractice) == 1 and bestpractice[0] == '':
                bestpractice = []
            qg = {}
            if bestpractice:
                qg['unccd_best_practice_criteria'] = {}
                qg['unccd_best_practice_criteria']['en'] = '<br>'.join(
                    bestpractice)
            clean_data['unccd_qg_13'] = [qg]

        if qg_keyword == 'unccd_qg_5':
            # unccd_qg_5
            # unccd_contribution_measures (checkbox)
            landuse = qg_data.get('unccd_contribution_measures', [])
            checkboxes = []
            for undefined_answer in landuse:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            checkboxes.append(int(answer))
                        except:
                            pass
                except AttributeError:
                    # Only one number value, must be checkbox
                    checkboxes.append(int(undefined_answer))
            cb_qg = {}
            cb_values = [
                'unccd_dldd_measures_prevention',
                'unccd_dldd_measures_mitigation',
                'unccd_dldd_measures_adaptation',
                'unccd_dldd_measures_rehabilitation',
            ]
            if checkboxes:
                cb_qg['unccd_contribution_measures'] = [
                    cb_values[cb] for cb in checkboxes]
            clean_data['unccd_qg_5'] = [cb_qg]

        if qg_keyword == 'unccd_qg_14':
            # unccd_qg_14
            # unccd_main_problems_addressed
            mainproblems = qg_data.get('unccd_main_problems_addressed', [])
            if len(mainproblems) == 1 and mainproblems[0] == '':
                mainproblems = []
            qg = {}
            if mainproblems:
                qg['unccd_main_problems_addressed'] = {}
                qg['unccd_main_problems_addressed']['en'] = '<br>'.join(
                    mainproblems)
            clean_data['unccd_qg_14'] = [qg]

        if qg_keyword == 'unccd_qg_15':
            # unccd_qg_15
            # unccd_land_degradation_addressed
            ldegradation = qg_data.get('unccd_land_degradation_addressed', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_land_degradation_addressed'] = {}
                qg['unccd_land_degradation_addressed']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_15'] = [qg]

        if qg_keyword == 'unccd_qg_16':
            # unccd_qg_16
            # unccd_objectives
            ldegradation = qg_data.get('unccd_objectives', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_objectives'] = {}
                qg['unccd_objectives']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_16'] = [qg]

        if qg_keyword == 'unccd_qg_17':
            # unccd_qg_17
            # unccd_description_objective
            ldegradation = qg_data.get('unccd_description_objective', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_description_objective'] = {}
                qg['unccd_description_objective']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_17'] = [qg]

        if qg_keyword == 'unccd_qg_21':
            # unccd_qg_21
            # unccd_technology_description
            techdescription1 = qg_data.get('unccd_technology_description1', [])
            techdescription2 = qg_data.get('unccd_technology_description2', [])
            description = techdescription1 + techdescription2
            if len(description) == 1 and description[0] == '':
                description = []
            qg = {}
            if description:
                qg['unccd_technology_description'] = {}
                qg['unccd_technology_description']['en'] = '<br>'.join(
                    description)
            clean_data['unccd_qg_21'] = [qg]

        if qg_keyword == 'unccd_qg_22':
            # unccd_qg_22
            # unccd_institution_name
            ldegradation = qg_data.get('unccd_institution_name', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_institution_name'] = {}
                qg['unccd_institution_name']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_22'] = [qg]

        if qg_keyword == 'unccd_qg_23':
            # unccd_qg_23
            # unccd_partnership (bool)
            # unccd_partnership_partners (text)
            prop_rights = qg_data.get('unccd_partnership', [])
            prop_rights_desc = qg_data.get(
                'unccd_partnership_partners', [])
            if object.get('id') in [
                '4570-700-CCD-135__3.0',
                '4570-700-CCD-152__1.0',
                '4570-700-CCD-163__1.0',
                '4570-700-CCD-180__2.0',
                '4570-700-CCD-180__4.0',
                '4570-700-CCD-180__5.0',
                '4570-700-CCD-180__6.0',
                '570-700-CCD-21__2.0',
                '4570-700-CCD-21__2.0',
                '4570-700-CCD-21__16.0',
                '4570-700-CCD-34__2.0',
                '4570-700-CCD-42__2.0',
                '4570-700-CCD-42__3.0',
                '4570-700-CCD-64__1.0',
            ]:
                prop_rights = [prop_rights[0]]
            if len(prop_rights) > 1:
                raise Exception(
                    'Object {}: More than one boolean for unccd_partnership: {} / {}'.format(object.get('id'), prop_rights, data))
            qg = {}
            if prop_rights:
                qg['unccd_partnership'] = prop_rights[0]
            if prop_rights_desc:
                qg['unccd_partnership_partners'] = {}
                qg['unccd_partnership_partners']['en'] = '<br>'.join(
                    prop_rights_desc)
            clean_data['unccd_qg_23'] = [qg]

        if qg_keyword == 'unccd_qg_25':
            # unccd_qg_25
            # unccd_promotion_framework (checkbox)
            # unccd_promotion_framework_specify (text)
            framework = qg_data.get('unccd_promotion_framework', [])
            checkboxes = []
            specify = []
            for undefined_answer in framework:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            checkboxes.append(int(answer))
                        except:
                            specify.append(answer)
                except AttributeError:
                    # Only one number value, must be checkbox
                    checkboxes.append(int(undefined_answer))
            cb_qg = {}
            cb_values = [
                'unccd_framework_local',
                'unccd_framework_national_government',
                'unccd_framework_national_nongovernment',
                'unccd_framework_international',
                'unccd_framework_programme',
                'unccd_framework_other',
            ]
            if checkboxes:
                cb_qg['unccd_promotion_framework'] = [
                    cb_values[cb] for cb in checkboxes]
            # specify_qg = {}
            if specify:
                cb_qg['unccd_promotion_framework_specify'] = {}
                cb_qg['unccd_promotion_framework_specify'][
                    'en'] = '<br>'.join(specify)
            # clean_data['unccd_qg_4'] = [specify_qg]
            clean_data['unccd_qg_25'] = [cb_qg]
            if len(specify) == 1 and specify[0] == '':
                specify = []

        if qg_keyword == 'unccd_qg_27':
            # unccd_qg_27
            # unccd_local_stakeholders (boolean)
            # unccd_local_stakeholders_list (text)
            prop_rights = qg_data.get('unccd_local_stakeholders', [])
            prop_rights_desc = qg_data.get(
                'unccd_local_stakeholders_list', [])
            if object.get('id') in [
                '4570-700-CCD-130__2.0',
                '4570-700-CCD-135__6.0',
                '4570-700-CCD-152__1.0',
                '4570-700-CCD-163__1.0',
                '4570-700-CCD-21__17.0',
                '4570-700-CCD-42__3.0',
                '4570-700-CCD-64__1.0',
                '4570-700-CCD-9__37.0',
                '4570-700-CCD-91__1.0',
            ]:
                prop_rights = [prop_rights[0]]
            if len(prop_rights) > 1:
                raise Exception(
                    'Object {}: More than one boolean for unccd_local_stakeholders: {} / {}'.format(object.get('id'), prop_rights, data))
            qg = {}
            if prop_rights:
                qg['unccd_local_stakeholders'] = prop_rights[0]
            if prop_rights_desc:
                qg['unccd_local_stakeholders_list'] = {}
                qg['unccd_local_stakeholders_list']['en'] = '<br>'.join(
                    prop_rights_desc)
            clean_data['unccd_qg_27'] = [qg]

        if qg_keyword == 'unccd_qg_29':
            # unccd_qg_29
            # unccd_stakeholder_roles
            ldegradation = qg_data.get('unccd_stakeholder_roles', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_stakeholder_roles'] = {}
                qg['unccd_stakeholder_roles']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_29'] = [qg]

        if qg_keyword == 'unccd_qg_30':
            # unccd_qg_30
            # unccd_population_involved (boolean)
            # unccd_population_involved_means (checkbox)
            # unccd_population_involved_specify (text)
            pop_bool = qg_data.get('unccd_population_involved', [])
            pop_text = qg_data.get(
                'unccd_population_involved_specify', [])
            pop_specify = []
            pop_checkbox = []
            for undefined_answer in pop_text:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            pop_checkbox.append(int(answer))
                        except:
                            pop_specify.append(answer)
                except AttributeError:
                    # Only one number value, must be checkbox
                    pop_checkbox.append(int(undefined_answer))
            if len(pop_bool) > 1:
                new_pop_bool = []
                for p in pop_bool:
                    # False is 1
                    if p is False and 1 not in pop_checkbox:
                        pop_checkbox.append(1)
                        continue
                    new_pop_bool.append(p)
                pop_bool = new_pop_bool
                if object.get('id') in [
                    '4570-700-CCD-130__1.0',
                    '4570-700-CCD-152__1.0',
                    '4570-700-CCD-163__1.0',
                    '4570-700-CCD-163__2.0',
                    '4570-700-CCD-163__4.0',
                    '4570-700-CCD-21__17.0',
                    '4570-700-CCD-34__1.0',
                    '4570-700-CCD-62__8.0',
                    '4570-700-CCD-62__10.0',
                    '4570-700-CCD-64__1.0',
                    '4570-700-CCD-99__6.0',
                    '4570-700-CCD-99__7.0',
                    '4570-700-CCD-99__8.0',
                    '4570-701-CCD-958__2.0',
                ]:
                    continue
                if len(pop_bool) > 1:
                    raise Exception(
                        'Object {}: More than one boolean for unccd_population_involved: {} / {}'.format(object.get('id'), pop_bool, data))
            qg = {}
            cb_values = [
                'unccd_involvement_consultation',
                'unccd_involvement_participatory',
                'unccd_involvement_other',
            ]
            if pop_checkbox:
                qg['unccd_population_involved_means'] = [
                    cb_values[cb] for cb in pop_checkbox]
            if pop_bool:
                qg['unccd_population_involved'] = pop_bool[0]
            if pop_specify:
                qg['unccd_population_involved_specify'] = {}
                qg['unccd_population_involved_specify']['en'] = '<br>'.join(
                    pop_specify)
            clean_data['unccd_qg_30'] = [qg]

        if qg_keyword == 'unccd_qg_6':
            # unccd_qg_6
            # unccd_contribution_objectives (checkbox)
            landuse = qg_data.get('unccd_contribution_objectives', [])
            checkboxes = []
            for undefined_answer in landuse:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            checkboxes.append(int(answer))
                        except:
                            pass
                except AttributeError:
                    # Only one number value, must be checkbox
                    checkboxes.append(int(undefined_answer))
            cb_qg = {}
            cb_values = [
                'unccd_dldd_objectives_populations',
                'unccd_dldd_objectives_ecosystems',
                'unccd_dldd_objectives_implementation',
            ]
            if checkboxes:
                cb_qg['unccd_contribution_objectives'] = [
                    cb_values[cb] for cb in checkboxes]
            clean_data['unccd_qg_6'] = [cb_qg]

        if qg_keyword == 'unccd_qg_33':
            # unccd_qg_33
            # unccd_onsite_impacts
            ldegradation = qg_data.get('unccd_onsite_impacts', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_onsite_impacts'] = {}
                qg['unccd_onsite_impacts']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_33'] = [qg]

        if qg_keyword == 'unccd_qg_37':
            # unccd_qg_37
            # unccd_offsite_impacts
            ldegradation = qg_data.get('unccd_offsite_impacts', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_offsite_impacts'] = {}
                qg['unccd_offsite_impacts']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_37'] = [qg]

        if qg_keyword == 'unccd_qg_38':
            # unccd_qg_38
            # unccd_impact_reasons
            ldegradation = qg_data.get('unccd_impact_reasons', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            values = []
            for v in ldegradation:
                try:
                    float(v)
                except ValueError:
                    values.append(v)
            if values:
                qg['unccd_impact_reasons'] = {}
                qg['unccd_impact_reasons']['en'] = '<br>'.join(
                    values)
            clean_data['unccd_qg_38'] = [qg]

        if qg_keyword == 'unccd_qg_39':
            # unccd_qg_39
            # unccd_cost_benefit_analysis (bool)
            # unccd_cost_benefit_analysis_text (text)
            prop_rights = qg_data.get('unccd_cost_benefit_analysis', [])
            prop_rights_desc = qg_data.get(
                'unccd_cost_benefit_analysis_text', [])
            if object.get('id') in [
                '4570-700-CCD-138__1.0',
                '4570-700-CCD-152__1.0',
                '4570-700-CCD-163__1.0',
                '4570-700-CCD-180__1.0',
                '4570-700-CCD-180__3.0',
                '4570-700-CCD-180__4.0',
                '4570-700-CCD-180__5.0',
                '4570-700-CCD-180__6.0',
                '4570-700-CCD-21__1.0',
                '4570-700-CCD-21__4.0',
                '4570-700-CCD-64__1.0',
                '4570-700-CCD-9__9.0',
                '4570-700-CCD-9__15.0',
                '4570-700-CCD-9__18.0',
                '4570-700-CCD-9__38.0',
                '4570-700-CCD-9__40.0',
            ]:
                prop_rights = [prop_rights[0]]
            if len(prop_rights) > 1:
                raise Exception(
                    'Object {}: More than one boolean for unccd_cost_benefit_analysis: {} / {}'.format(object.get('id'), prop_rights, data))
            qg = {}
            if prop_rights:
                qg['unccd_cost_benefit_analysis'] = prop_rights[0]
            if prop_rights_desc:
                qg['unccd_cost_benefit_analysis_text'] = {}
                qg['unccd_cost_benefit_analysis_text']['en'] = '<br>'.join(
                    prop_rights_desc)
            clean_data['unccd_qg_39'] = [qg]

        if qg_keyword == 'unccd_qg_8':
            # unccd_qg_8
            # unccd_linkages (checkbox)
            landuse = qg_data.get('unccd_linkages', [])
            checkboxes = []
            for undefined_answer in landuse:
                try:
                    for answer in undefined_answer.split('|'):
                        try:
                            checkboxes.append(int(answer))
                        except:
                            pass
                except AttributeError:
                    # Only one number value, must be checkbox
                    checkboxes.append(int(undefined_answer))
            cb_qg = {}
            cb_values = [
                'unccd_linkages_capacity_building',
                'unccd_linkages_monitoring',
                'unccd_linkages_knowledge_management',
                'unccd_linkages_policy',
                'unccd_linkages_funding',
                'unccd_linkages_participation',
            ]
            if checkboxes:
                cb_qg['unccd_linkages'] = [
                    cb_values[cb] for cb in checkboxes]
            clean_data['unccd_qg_8'] = [cb_qg]

        if qg_keyword == 'unccd_qg_40':
            # unccd_qg_40
            # unccd_technology_disseminated (boolean)
            # unccd_technology_disseminated_where (text)
            prop_rights = qg_data.get('unccd_technology_disseminated', [])
            prop_rights_desc = qg_data.get(
                'unccd_technology_disseminated_where', [])
            if len(prop_rights) > 0 and object.get('id') in [
                '4570-700-CCD-9__4.0',
                '4570-700-CCD-135__2.0',
                '4570-700-CCD-152__1.0',
                '4570-700-CCD-163__1.0',
                '4570-700-CCD-180__1.0',
                '4570-700-CCD-180__3.0',
                '4570-700-CCD-180__5.0',
                '4570-700-CCD-180__6.0',
                '4570-700-CCD-42__3.0',
                '4570-700-CCD-64__1.0',
                '4570-700-CCD-9__28.0',
            ]:
                prop_rights = [prop_rights[0]]
            if len(prop_rights) > 1:
                raise Exception(
                    'Object {}: More than one boolean for unccd_technology_disseminated: {} / {}'.format(object.get('id'), prop_rights, data))
            qg = {}
            if prop_rights:
                qg['unccd_technology_disseminated'] = prop_rights[0]
            if prop_rights_desc:
                qg['unccd_technology_disseminated_where'] = {}
                qg['unccd_technology_disseminated_where']['en'] = '<br>'.join(
                    prop_rights_desc)
            clean_data['unccd_qg_40'] = [qg]

        if qg_keyword == 'unccd_qg_42':
            # unccd_qg_42
            # unccd_incentives (boolean)
            # unccd_incentives_types (checkbox)
            incentives = qg_data.get('unccd_incentives', [])
            checkbox_string = ''
            checkboxes = []
            boolean = None
            numbers = []
            text = []
            if len(incentives) == 1:
                boolean = incentives[0]
            else:
                try:
                    x = float(incentives[0])
                    numbers.append(0)
                except ValueError:
                    text.append(0)
                try:
                    x = float(incentives[1])
                    numbers.append(1)
                except ValueError:
                    text.append(1)
                if len(text) == 1 and len(numbers) == 1:
                    boolean = incentives[numbers[0]]
                    checkbox_string = incentives[text[0]]
                elif len(numbers) == 2:
                    # Assumption: boolean value is True (0), other is checkbox
                    if incentives[0] == '0.0':
                        boolean = incentives[0]
                        checkbox_string = incentives[1]
                    elif incentives[1] == '0.0':
                        boolean = incentives[1]
                        checkbox_string = incentives[0]
            if len(incentives) > 2:
                if object.get('id') in [
                    '4570-700-CCD-135__7.0',
                    '4570-700-CCD-152__1.0',
                    '4570-700-CCD-163__2.0',
                    '4570-700-CCD-163__1.0',
                    '4570-700-CCD-163__3.0',
                    '4570-700-CCD-163__4.0',
                    '4570-700-CCD-180__1.0',
                    '4570-700-CCD-180__3.0',
                    '4570-700-CCD-180__4.0',
                    '4570-700-CCD-180__5.0',
                    '4570-700-CCD-180__6.0',
                    '4570-700-CCD-21__3.0',
                    '4570-700-CCD-21__19.0',
                    '4570-700-CCD-42__1.0',
                    '4570-700-CCD-42__2.0',
                    '4570-700-CCD-42__3.0',
                    '4570-700-CCD-64__1.0',
                    '4570-701-CCD-958__4.0',
                ]:
                    continue
                raise Exception('Too many values: {} / {}'.format(object.get('id'), incentives))
            if boolean:
                # 0: True
                # 1: False
                if boolean == '0.0':
                    boolean = True
                elif boolean == '1.0':
                    boolean = False
                elif boolean in ['---', 'NULL']:
                    boolean = None
                else:
                    raise Exception('Boolean value "{}" not valid1'.format(
                        boolean))
            qg = {}
            if boolean:
                qg['unccd_incentives'] = boolean
            try:
                for answer in checkbox_string.split('|'):
                    try:
                        checkboxes.append(int(answer))
                    except:
                        if answer == '1.0':
                            checkboxes.append(1)
                        elif answer == '0.0':
                            checkboxes.append(0)
            except AttributeError:
                pass
            cb_values = [
                'unccd_incentives_policy',
                'unccd_incentives_financial',
                'unccd_incentives_fiscal',
            ]
            if checkboxes:
                qg['unccd_incentives_types'] = [
                    cb_values[cb] for cb in checkboxes]
            clean_data['unccd_qg_42'] = [qg]

        if qg_keyword == 'unccd_qg_44':
            # unccd_qg_44
            # unccd_success_conditions
            ldegradation = qg_data.get('unccd_success_conditions', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            values = []
            for v in ldegradation:
                try:
                    float(v)
                except ValueError:
                    values.append(v)
            if values:
                qg['unccd_success_conditions'] = {}
                qg['unccd_success_conditions']['en'] = '<br>'.join(
                    values)
            clean_data['unccd_qg_44'] = [qg]

        if qg_keyword == 'unccd_qg_45':
            # unccd_qg_45
            # unccd_replicability (boolean)
            # unccd_replicability_level (checkbox)
            incentives = qg_data.get('unccd_replicability', [])
            checkbox_string = ''
            checkboxes = []
            boolean = None
            numbers = []
            text = []
            if len(incentives) == 1:
                boolean = incentives[0]
            else:
                try:
                    x = float(incentives[0])
                    numbers.append(0)
                except ValueError:
                    text.append(0)
                try:
                    x = float(incentives[1])
                    numbers.append(1)
                except ValueError:
                    text.append(1)
                if len(text) == 1 and len(numbers) == 1:
                    boolean = incentives[numbers[0]]
                    checkbox_string = incentives[text[0]]
                elif len(numbers) == 2:
                    # Assumption: boolean value is True (0), other is checkbox
                    if incentives[0] == '0.0':
                        boolean = incentives[0]
                        checkbox_string = incentives[1]
                    elif incentives[1] == '0.0':
                        boolean = incentives[1]
                        checkbox_string = incentives[0]
            if len(incentives) > 2:
                if object.get('id') in [
                    '4570-700-CCD-152__1.0',
                    '4570-700-CCD-163__1.0',
                    '4570-700-CCD-180__1.0',
                    '4570-700-CCD-180__3.0',
                    '4570-700-CCD-180__4.0',
                    '4570-700-CCD-180__5.0',
                    '4570-700-CCD-180__6.0',
                    '4570-700-CCD-64__1.0',
                    '4570-700-CCD-21__15.0',
                    '4570-700-CCD-9__17.0',
                    '4570-700-CCD-9__19.0',
                    '4570-700-CCD-9__31.0',
                ]:
                    continue
                raise Exception('Too many values: {} / {}'.format(object.get('id'), incentives))
            if boolean:
                # 0: True
                # 1: False
                if boolean == '0.0':
                    boolean = True
                elif boolean == '1.0':
                    boolean = False
                elif boolean in ['---', 'NULL']:
                    boolean = None
                else:
                    raise Exception('Boolean value "{}" not valid'.format(
                        boolean))
            qg = {}
            if boolean:
                qg['unccd_replicability'] = boolean
            try:
                for answer in checkbox_string.split('|'):
                    try:
                        checkboxes.append(int(answer))
                    except:
                        if answer == '1.0':
                            checkboxes.append(1)
                        elif answer == '0.0':
                            checkboxes.append(0)
            except AttributeError:
                pass
            cb_values = [
                'unccd_replicability_local',
                'unccd_replicability_subnational',
                'unccd_replicability_national',
                'unccd_replicability_subregional',
                'unccd_replicability_regional',
                'unccd_replicability_international',
            ]
            if checkboxes:
                qg['unccd_replicability_level'] = [
                    cb_values[cb] for cb in checkboxes]
            clean_data['unccd_qg_45'] = [qg]

        if qg_keyword == 'unccd_qg_47':
            # unccd_qg_47
            # unccd_lessons_human_resources
            ldegradation = qg_data.get('unccd_lessons_human_resources', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            values = []
            for v in ldegradation:
                try:
                    float(v)
                except ValueError:
                    values.append(v)
            if values:
                qg['unccd_lessons_human_resources'] = {}
                qg['unccd_lessons_human_resources']['en'] = '<br>'.join(
                    values)
            clean_data['unccd_qg_47'] = [qg]

        if qg_keyword == 'unccd_qg_48':
            # unccd_qg_48
            # unccd_lessons_financial
            ldegradation = qg_data.get('unccd_lessons_financial', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            values = []
            for v in ldegradation:
                try:
                    float(v)
                except ValueError:
                    values.append(v)
            if values:
                qg['unccd_lessons_financial'] = {}
                qg['unccd_lessons_financial']['en'] = '<br>'.join(
                    values)
            clean_data['unccd_qg_48'] = [qg]

        if qg_keyword == 'unccd_qg_49':
            # unccd_qg_49
            # unccd_lessons_technical
            ldegradation = qg_data.get('unccd_lessons_technical', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            values = []
            for v in ldegradation:
                try:
                    float(v)
                except ValueError:
                    values.append(v)
            if values:
                qg['unccd_lessons_technical'] = {}
                qg['unccd_lessons_technical']['en'] = '<br>'.join(
                    values)
            clean_data['unccd_qg_49'] = [qg]

        if qg_keyword == 'unccd_qg_50':
            # unccd_qg_50
            # unccd_questions_leg1
            ldegradation = qg_data.get('unccd_questions_leg1', [])
            if len(ldegradation) == 1 and ldegradation[0] == '':
                ldegradation = []
            qg = {}
            if ldegradation:
                qg['unccd_questions_leg1'] = {}
                qg['unccd_questions_leg1']['en'] = '<br>'.join(
                    ldegradation)
            clean_data['unccd_qg_50'] = [qg]

    # print(clean_data)

    return clean_data

