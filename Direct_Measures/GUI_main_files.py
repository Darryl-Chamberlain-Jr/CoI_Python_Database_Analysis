#from email import message
import sys
from sys import path_importer_cache
from Python_Scripts.For_GUI_main_files.upload_to_main import *
import glob
import os
import shutil
import traceback
from progress.bar import ChargingBar
#from datetime import datetime # Timestamps for recovery databases

### GLOBAL VARIABLES ###
headers_without_modify=['Speaker ID', 'Speaker Type', 'Class ID', 'Term', 'Year', 'Cohort', 'Module Number', 'Analysis Unit', 'Analysis Unit Index']
static_headers=headers_without_modify+['Modify']
researcher_names=['Emily', 'Syaza', 'Abigail', 'Patrick', 'Amina', 'Qaisara', 'Andrea', 'Emma', 'Elizabeth'] # Update when adding researchers
database_header_array=static_headers+researcher_names

# For casting certain columns to strings 
headers_to_str_dict={}
for key in headers_without_modify:
    headers_to_str_dict[key]='str'

# Variables for print statement in Task 2 - Download partial database
acceptable_speaker_types_partial=['All', 'Student', 'Instructor']
acceptable_class_ID_partial=['All', 'MATH', 'PHY']
acceptable_term_partial=['All', 'AUG', 'SEP', 'MAR']
acceptable_year_partial=['All', '2021', '2022', '2023']
acceptable_term_year=['AUG 2021', 'SEP 2021', 'MAR 2022', 'AUG 2022', 'SEP 2022', 'MAR 2023', 'AUG All', 'SEP All', 'MAR All', 'All All']
acceptable_cohort_partial=['All', '1', '2', '3', '4', '5', '6', '7']
acceptable_module_partial=['All', '1', '2', '3', '4', '5', '6', '7', '8', '9']
acceptable_codes_partial=['Yes', 'No']
### END OF GLOBAL VARIABLES ###

### NECESSARY STATICS THAT SHOULD NOT BE CHANGED ###
base_dir=os.getcwd()
if os.name == 'nt':
    path_break='\\'
else:
    path_break='/'
path_to_main_database=f'{base_dir}{path_break}Main_Database{path_break}main_database.xlsx'

# Creates backup before performing any modifications
path_to_backup_main=f'{base_dir}{path_break}Main_Database{path_break}Recovery_Files{path_break}main_database.xlsx'
if os.path.exists(path_to_backup_main)==True:
    os.remove(path_to_backup_main)
if os.path.exists(path_to_main_database)==True and os.path.exists(path_to_backup_main)==True:
    shutil.copy(path_to_main_database, path_to_backup_main)

### END OF NECESSARY STATICS ###

### DEFINITIONS FOR USER PRINT STATEMENTS ###
def message_for_input(input_type, options):
    options_string=', '.join(str(opt) for opt in options)
    user_input=input(f'{input_type} Options: {options_string}\n{input_type}: ')
    while user_input not in options: 
        print(f'\nError. You typed {user_input}, which is not a valid {input_type} Option.\n')
        user_input=input(f'{input_type} Options: {options_string}\n{input_type}')
    return user_input

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)
### END OF DEFINITIONS FOR USER PRINT STATEMENTS ###

def strip_func(string):
    return string.strip()

while True:
    task=input("\nType the number of the task you would like to complete: \n (1) Upload all xlsx files to main database. \n (2) Download partial database. \n (3) Delete old main database in preparation for new one. \n (0) Exit. \n\nTask: ")
    if task=="0": # Exit GUI
        break

    elif task=="1": # Upload all xlsx files to split database
        number_of_files_uploaded=0
        number_of_files_processed=0
        exit_with_error=0

        list_of_files=glob.glob(f'{base_dir}{path_break}Deidentified_xlsx_Files{path_break}*.xlsx')
        bar=ChargingBar('Loading files: ', max=len(list_of_files))
        for file_name in list_of_files:
            # Used for printing file name without parent directory
            clean_file_name=file_name.replace(f'{base_dir}{path_break}Deidentified_xlsx_Files{path_break}', '') 
            print(f'\nWorking on file {clean_file_name} now.\n')

            # Extracts info from file 
            raw_dataframe=pandas.read_excel(file_name, index_col=[0])
            try: 
                new_dataframe=raw_dataframe.dropna(subset='Analysis Unit')
                new_dataframe=new_dataframe.astype(headers_to_str_dict) # Cast certain columns as strings
                new_df_size=new_dataframe.shape[0]

                # Print to user how many lines were extracted
                print(f"\n{new_df_size} lines extracted from {clean_file_name}.\n\n")

                # Extracts main dataframe
                try:
                    main_dataframe=pandas.read_excel(path_to_main_database, index_col=[0])
                    main_dataframe=main_dataframe.astype(headers_to_str_dict) # Cast certain columns as strings
                    initial_size_of_database=main_dataframe.shape[0]
                except:
                    initial_size_of_database = 0

                # Merge dataframes and drop duplicates
                potential_conflict_columns=['Modify']+researcher_names
                try:
                    new_dataframe = new_dataframe.astype(headers_to_str_dict)
                    new_dataframe['Analysis Unit'] = new_dataframe['Analysis Unit'].apply(strip_func)
                    combined_df=pandas.merge(main_dataframe, new_dataframe, how='outer', on=headers_without_modify)
                    # DEBUGGING FOR MERGE ISSUE - DELETE WHEN DONE
                    #for key in headers_without_modify:
                    #    print(combined_df[key].unique())
                except:
                    combined_df = new_dataframe

                for key in potential_conflict_columns:
                    try:
                        merge_drop_mask=~(pandas.isnull(combined_df[f'{key}_x'])) & (pandas.isnull(combined_df[f'{key}_y']))
                        merge_and_drop(combined_df, key, merge_drop_mask)
                    except:
                        pass
                combined_df.drop_duplicates(subset=static_headers, keep='first', inplace=True) # Drop duplicates with the same 'base' values 
                combined_df = combined_df.dropna(subset='Analysis Unit') # Drop rows with empty Analysis Unit values
                combined_df = combined_df[(combined_df['Module Number'] == '1') | (combined_df['Module Number'] == '2') | (combined_df['Module Number'] == '3') | (combined_df['Module Number'] == '4') | (combined_df['Module Number'] == '5') | (combined_df['Module Number'] == '6') | (combined_df['Module Number'] == '7') | (combined_df['Module Number'] == '8') | (combined_df['Module Number'] == '9')] # Remove any extra discussion posts

                # Make new modifications
                deleted_count, replaced_count=complete_modify(combined_df)
                modified_count=deleted_count+replaced_count
                combined_df.reset_index(drop=True, inplace=True)
                
                # Return to int, then cast as string
                convert_to_float={}
                return_to_int={}
                cast_to_int_str={}
                for int_col_label in ['Year', 'Cohort', 'Module Number']:
                    convert_to_float[int_col_label]='float'
                    return_to_int[int_col_label]='int'
                    cast_to_int_str[int_col_label]='str'
                combined_df=combined_df.astype(convert_to_float)
                combined_df=combined_df.astype(return_to_int)
                combined_df=combined_df.astype(cast_to_int_str)

                # Overwrite main_database with new_main_df
                if os.path.exists(path_to_main_database)==True:
                    os.remove(path_to_main_database)
                combined_df.to_excel(path_to_main_database)

                # Comparison of sizes for print statements
                updated_size_of_database=combined_df.shape[0]
                line_count_uploaded=updated_size_of_database-initial_size_of_database
                if initial_size_of_database==0: 
                    print(f"File {clean_file_name} is the first file uploaded to the database. Database now contains {updated_size_of_database} lines.\n\n")
                    number_of_files_uploaded+=1
                elif line_count_uploaded==0 and modified_count==0: 
                    print(f"File {clean_file_name} has been uploaded previously. Data was not added to master database.\n\n")
                else: 
                    print(f"File {clean_file_name} has been uploaded. {line_count_uploaded} lines have been added to the database, {replaced_count} lines have been modified and {deleted_count} lines have been deleted. Database now contains {updated_size_of_database} lines.\n\n")
                    number_of_files_uploaded+=1
            except: 
                print(traceback.format_exc())
                print('\n\n An error has occured.')
                #print(f'File {clean_file_name} is empty. Skipping for now.\n\n')
            number_of_files_processed+=1
            bar.next()
        
        bar.finish
        # If elif to modify print statement for how many file(s) were printed.
        if exit_with_error==1:
            break
        elif number_of_files_uploaded==0: 
            print("\nAll files have been previously uploaded to the master database.\n\n")
        elif number_of_files_uploaded==1:
            print(f"\n{number_of_files_processed} file has been uploaded to database.\n\n")
        else: 
            print(f"\n{number_of_files_processed} files have been uploaded to database.\n\n")

    elif task=="2": # Download partial database.
        print('\nPlease input the following options to download part of the data.\n')
        speaker_type=message_for_input('Speaker Type', acceptable_speaker_types_partial)
        class_ID=message_for_input('Class ID', acceptable_class_ID_partial)
        term=message_for_input('Term', acceptable_term_partial)
        year=message_for_input('Year', acceptable_year_partial)
        term_and_year=f'{term} {year}'
        while term_and_year not in acceptable_term_year:
            print("\n You input an invalid term/year combination. The acceptable values are 'AUG 2021', 'SEP 2021', 'MAR 2022', 'AUG 2022', 'SEP 2022', 'MAR 2023', 'AUG All', 'SEP All', 'MAR All', or 'All All'. Please try again.\n\n")
            term=message_for_input('Term', acceptable_term_partial)
            year=message_for_input('Year', acceptable_year_partial)
            term_and_year=f'{term} {year}'
        cohort=message_for_input('Cohort', acceptable_cohort_partial)
        module=message_for_input('Module', acceptable_module_partial)
        codes=message_for_input('Include Researcher Codes', acceptable_codes_partial)
        user_inputs={
            'Speaker Type': speaker_type, 
            'Class ID': class_ID, 
            'Term': term, 
            'Year': year, 
            'Cohort': cohort, 
            'Module Number': module, 
            'Include Researcher Codes': codes
        }
        new_file_name=create_partial_database_name(base_dir, path_break, user_inputs)
        download_partial_database(path_to_main_database, user_inputs, new_file_name, researcher_names, headers_to_str_dict)
        print("\nComplete! You can find your file saved in the 'Partial Database' folder.\n")

    elif task=="3": # Delete old master database in preparation for new one.
        if os.path.exists(path_to_main_database)==False:
            print("\nNo master database exists to be deleted.\n")
            break
        else: 
            warning=input("\nAre you sure you want to delete? Recovering the old database will be difficult. \n\n Y/N \n\n")
            if warning=="Y" or warning=="y" or warning=="Yes" or warning=="yes":
                os.remove(path_to_main_database)
                print("\nOld database has been deleted!\n")
                break
            else: 
                break

    else: # User input not 1 through 3, inclusive
        print("\nPlease input a valid command.\n")