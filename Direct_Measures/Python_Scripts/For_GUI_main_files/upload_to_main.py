import os # os is needed to define directory python script is being run in and determining os type to ensure path discovery breaks are correct.
#import shelve # shelve is needed for interacting with database (.db) files.
from pathlib import Path # To touch files within python
import pandas # Edit raw data
import numpy

### DEFINITIONS FOR GUI_main_files.py ###
# Task 1 - Upload xlsx files to database
def merge_and_drop(df, key, mask):
    df[key]=numpy.where(mask, df[f'{key}_x'], df[f'{key}_y'])
    df.drop(columns=[f'{key}_x', f'{key}_y'], inplace=True)

def complete_modify(df):
    before_del_len=len(df)
    delete_mask=df['Modify']=='DELETE'
    df.drop(df[delete_mask].index, inplace=True)
    number_rows_deleted=before_del_len-len(df)

    number_rows_replaced=len(df)-df['Modify'].isna().sum()
    replace_mask=~(pandas.isnull(df['Modify']))
    df['Analysis Unit']=numpy.where(replace_mask, df['Modify'], df['Analysis Unit'])
    df['Modify']=numpy.nan
    
    return [number_rows_deleted, number_rows_replaced]

#def validate_xlsx_file(file_name):
# END Task 1

# Task 2 - Download Partial Database 
def define_mask(df, key, user_inputs):
    all_true_mask=numpy.repeat(True, len(df.index))
    if user_inputs[key]=='All':
        mask=all_true_mask
    elif user_inputs[key]=='Include Research Codes':
        pass # We don't want a mask for this statement
    else:
        mask=df[key]==user_inputs[key]
    return mask

def download_partial_database(path_to_main_database, user_inputs, new_file_name, researcher_names, headers_to_str_dict):
    # Opens and downloads master dataframe dicts
    main_df=pandas.read_excel(path_to_main_database, index_col=[0])
    main_df=main_df.astype(headers_to_str_dict) # Convert all entries to strings

    speaker_mask=define_mask(main_df, 'Speaker Type', user_inputs)
    class_mask=define_mask(main_df, 'Class ID', user_inputs)
    term_mask=define_mask(main_df, 'Term', user_inputs)
    year_mask=define_mask(main_df, 'Year', user_inputs)
    cohort_mask=define_mask(main_df, 'Cohort', user_inputs)
    module_number_mask=define_mask(main_df, 'Module Number', user_inputs)
    final_partial_mask=speaker_mask & class_mask & term_mask & year_mask & cohort_mask & module_number_mask

    partial_df=main_df[final_partial_mask]

    # If we don't want to include researcher codes, we nan out these columns
    if user_inputs['Include Researcher Codes']=='No':
        for researcher in researcher_names:
            partial_df[researcher]=numpy.nan

    # If this file already exists, remove it for a fresh save.
    if os.path.exists(new_file_name): 
        os.remove(new_file_name)
    Path(new_file_name).touch()

    partial_df.to_excel(new_file_name)

def create_partial_database_name(base_dir, path_break, user_inputs):
    # Check acceptable user inputs in statics
        # acceptable_module_partial=['All', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        # acceptable_codes_partial=['Yes', 'No']
    if user_inputs['Speaker Type']=='All':
        speaker_abbrev='AllSpkrs'
    else:
        speaker_abbrev=user_inputs['Speaker Type']
    
    if user_inputs['Class ID']=='All':
        class_abbrev='AllCls'
    else:
        class_abbrev=user_inputs['Class ID']

    if user_inputs['Term']=='All':
        term_abbrev='AllTrms'
    else:
        term_abbrev=user_inputs['Term']

    if user_inputs['Year']=='All':
        year_abbrev='AllYrs'
    else:
        year_abbrev=user_inputs['Year']

    if user_inputs['Cohort']=='All':
        cohort_abbrev='AllScs'
    else:
        cohort_abbrev=f'Sc{user_inputs["Cohort"]}'

    if user_inputs['Module Number']=='All':
        module_abbrev='AllMds'
    else:
        module_abbrev=f'Md{user_inputs["Module Number"]}'
    
    new_file_name=f'{base_dir}{path_break}Partial_Databases{path_break}{speaker_abbrev}_{class_abbrev}_{term_abbrev}_{year_abbrev}_{cohort_abbrev}_{module_abbrev}_{user_inputs["Include Researcher Codes"]}Cds.xlsx'

    return new_file_name
# END Task 2



