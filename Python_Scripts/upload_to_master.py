# Upload deidentified data to master database

import os # os is needed to define directory python script is being run in and determining os type to ensure path discovery breaks are correct.
import shelve # shelve is needed for interacting with database (.db) files.
from pathlib import Path # To touch files within python
import csv # Needed to read from csv file
import time

def check_if_database_empty(current_directory, path_break): 
    if os.name == "linux-gnu":
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database.db')
    else: 
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database')
    try: 
        prior_list_of_dicts=database["List of Dicts"]
        empty_check=0
    except: 
        empty_check=1
    finally: 
        database.close()
    return empty_check

def extract_deidentified_data(file_name):
    list_of_dicts=[]
    #with open(f'{file_name}', newline='', encoding='utf-8-sig') as csv_identified:
    with open(f'{file_name}', newline='', encoding='latin-1') as csv_identified:
        reader = csv.DictReader(csv_identified)
        for row in reader: 
            temp_dict_name=row["Speaker ID"]
            temp_dict={
                "Speaker ID": row["Speaker ID"],
                "Speaker Type": row["Speaker Type"], 
                "Class ID": row["Class ID"],
                "Term": row["Term"], 
                "Year": row["Year"],
                "Cohort": row["Cohort"], 
                "Module Number": row["Module Number"], 
                "Analysis Unit": row["Analysis Unit"]
            }
            locals()[f'{temp_dict_name}']=temp_dict # Dynamically renames dict to be speaker ID
            list_of_dicts.append(temp_dict)
    return list_of_dicts

def upload_extracted_data(current_directory, path_break, list_of_dicts):
    already_uploaded="error"
    if os.name == "linux-gnu":
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database.db')
    else: 
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database')
    try: 
        prior_list_of_dicts=database["List of Dicts"]
        initial_db_size=len(prior_list_of_dicts)
        for dict in list_of_dicts: 
            if type(dict) != type({}) or dict in prior_list_of_dicts: 
                continue
            else: 
                prior_list_of_dicts.append(dict)
        database['List of Dicts']=prior_list_of_dicts
        if len(database['List of Dicts']) == initial_db_size:
            already_uploaded=1
        else: 
            already_uploaded=0
    except: 
        database['List of Dicts']=list_of_dicts
        print("Returned as exception.")
    finally: 
        database.close()
    return already_uploaded

def download_master_database(current_directory, path_break): 
    if os.name == "linux-gnu":
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database.db')
    else: 
        database=shelve.open(f'{current_directory}{path_break}Master_Database{path_break}master_database')
    try: 
        downloaded_dicts=database['List of Dicts']
    finally: 
        database.close()

    master_csv_file_path=f'{current_directory}{path_break}Master_Database{path_break}master_data.csv'
    if os.path.exists(master_csv_file_path):
        os.remove(master_csv_file_path)
    Path(master_csv_file_path).touch()

    # Print sentences in csv
    field_names=["Speaker ID", "Speaker Type", "Class ID", "Term", "Year", "Cohort", "Module Number", "Analysis Unit"]
    with open(master_csv_file_path, 'w', newline='', encoding="utf-8") as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in downloaded_dicts:
            if len(dict)==8:
                writer.writerow(dict)