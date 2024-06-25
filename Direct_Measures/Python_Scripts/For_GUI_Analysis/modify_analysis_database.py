#modify_analysis_database
import os
from .upload_to_master import *
matching_keys=['Class ID', 'Speaker Type', 'Term', 'Year', 'Cohort']

def define_stats_by_module(code_dict):
    list_of_new_dicts=[]
    for module in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        temp_dict={}
        for key in matching_keys:
            temp_dict[key]=code_dict[key]
        temp_dict['Module Number']=module
        temp_dict['Lines Uploaded']=0
        temp_dict['Lines Coded']=0
        temp_dict['Progress']=0
        for researcher in researcher_names:
            temp_dict[researcher]=0
        list_of_new_dicts.append(temp_dict)
    return list_of_new_dicts

def add_fine_dict_stats_to_summary_dict(fine_dict, summary_dict):
    match_all_five=0
    for key in matching_keys:
        if fine_dict[key]==summary_dict[key]:
            match_all_five+=1
    if match_all_five==4:
        summary_dict.update({'Lines Uploaded': fine_dict['Lines Uploaded']+summary_dict['Lines Uploaded']})
        summary_dict.update({'Lines Coded': fine_dict['Lines Coded']+summary_dict['Lines Coded']})
        for researcher in researcher_names:
            summary_dict.update({researcher: fine_dict[researcher]+summary_dict[researcher]})
    return summary_dict

def sections_to_code():
    # Currently want PHY AUG 2021 Cohorts 1-5 and MATH AUG 2021 Cohorts 1-7
    array_of_sections_to_code=[]
    for phy_cohort in ['1', '2', '3', '4', '5']:
        temp_dict={}
        temp_dict.update({'Class ID': 'PHY'})
        temp_dict.update({'Speaker Type': 'Student'})
        temp_dict.update({'Term': 'AUG'})
        temp_dict.update({'Year': '2021'})
        temp_dict.update({'Cohort': phy_cohort})
        temp_dict['Lines Uploaded']=0
        temp_dict['Lines Coded']=0
        temp_dict['Progress']=0
        for researcher in researcher_names:
            temp_dict[researcher]=0
        array_of_sections_to_code.append(temp_dict)
    
    for math_cohort in ['1', '2', '3', '4', '5', '6', '7']:
        temp_dict={}
        temp_dict.update({'Class ID': 'MATH'})
        temp_dict.update({'Speaker Type': 'Student'})
        temp_dict.update({'Term': 'AUG'})
        temp_dict.update({'Year': '2021'})
        temp_dict.update({'Cohort': math_cohort})
        temp_dict['Lines Uploaded']=0
        temp_dict['Lines Coded']=0
        temp_dict['Progress']=0
        for researcher in researcher_names:
            temp_dict[researcher]=0
        array_of_sections_to_code.append(temp_dict)
    
    return array_of_sections_to_code