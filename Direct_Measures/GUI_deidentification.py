import glob 
import traceback 
import os
import pandas

base_dir=os.getcwd()
if os.name == 'nt':
    path_break='\\'
else:
    path_break='/'

from Python_Scripts.For_GUI_deidentification.deidentify import *

# Collects names of files in the *_Documents_To_Deidentify folders. 
all_files=[]
for file in glob.glob(f'{base_dir}{path_break}Documents_To_Deidentify{path_break}*'):
    if '$' not in file:
        all_files.append(file)

list_of_error_dicts = []

# Loops through all files to deidentify each file
for file in all_files:
    dict_file_properties=define_dict_file_properties(file)

    from Python_Scripts.For_GUI_deidentification.deidentify import *
    try:
        encode_relations_dict=extract_preset_encoding(dict_file_properties)
        if dict_file_properties['Extension']=='xlsx':
            from Python_Scripts.For_GUI_deidentification.html_scrape_cleaning import *
            raw_df=extract_from_file(dict_file_properties)
            save_html_scrape_df_as_xlsx(encode_relations_dict, dict_file_properties, raw_df)
        else:
            raw_extracted_text=extract_from_file(dict_file_properties)
            clean_extracted_text=clean_array_of_sentences(raw_extracted_text, encode_relations_dict['Unitized Student Names'], encode_relations_dict['Unitized Instructor Names'])
            save_pdf_or_docs_sentences_as_xlsx(encode_relations_dict, dict_file_properties, clean_extracted_text)
        print('\nCompleted! Be sure to check xlsx files for irregularities.\n\n')
    except: 
        temp_error_dict = {
            "File Name": dict_file_properties['File Name'],
            "Error Code": traceback.format_exc()
        }
        #print(traceback.format_exc())
        list_of_error_dicts.append(temp_error_dict)
        print('\n\n An error has occured. If using Word files, be sure that the prompt from the discussion has been deleted and all hyperlinks have been removed.')

error_df = pandas.DataFrame.from_dict(list_of_error_dicts)
error_df.to_excel(f'{base_dir}{path_break}Error_Records{path_break}Deidentification_Errors.xlsx')