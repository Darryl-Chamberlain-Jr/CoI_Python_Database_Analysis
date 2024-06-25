# Upload deidentified data to master database

import os # os is needed to define directory python script is being run in and determining os type to ensure path discovery breaks are correct.
import shelve # shelve is needed for interacting with database (.db) files.
from pathlib import Path # To touch files within python
import csv # Needed to read from csv file
import time
import chardet # Detects characters in csv file
from datetime import datetime, timedelta

def detect_encoding_type(file_name):
    with open(f'{file_name}', 'rb') as raw_data:
        detect=chardet.detect(raw_data.read(10000))
    encoding_type=detect["encoding"]
    if encoding_type=="ascii":
        encoding_type="utf-8"
    return encoding_type
def clean_withdrawal_date(raw_date):
    sliced_date=raw_date[:9]
    split_date=sliced_date.split("-")
    day=int(split_date[0])
    array_months_strings=[["JAN", 1], ["FEB", 2], ["MAR", 3], ["APR", 4], ["MAY", 5], ["JUN", 6], ["JUL", 7], ["AUG", 8], ["SEP", 9], ["OCT", 10], ["NOV", 11], ["DEC", 12]]
    for month_string in array_months_strings:
        if month_string[0]==split_date[1]:
            month=month_string[1]
            break
    year=int(f'20{split_date[2]}')
    python_date=datetime(year, month, day)
    return python_date
def clean_term_end_or_mid_date(raw_date): 
    if raw_date=="":
        python_date=""
    else:
        array_months_strings=[["Jan", 1], ["Feb", 2], ["Mar", 3], ["Apr", 4], ["May", 5], ["Jun", 6], ["Jul", 7], ["Aug", 8], ["Sep", 9], ["Oct", 10], ["Nov", 11], ["Dec", 12]]
        day=int(raw_date[5:7])
        for month_string in array_months_strings:
            if month_string[0]==raw_date[:3]:
                month=month_string[1]
                break 
        year=int(raw_date[8:])
        python_date=datetime(year, month, day)
    return python_date
def extract_deidentified_data(file_name):
    list_of_dicts=[]
    #index=0
    encoding_type=detect_encoding_type(file_name)
    with open(f'{file_name}', newline='', encoding=encoding_type) as csv_identified:
        reader = csv.DictReader(csv_identified)
        for row in reader: 
            #temp_dict_name=row["ERAUID"]
            temp_dict={
                "ERAUID": row["ERAUID"],
                "Withdrawal Date": clean_withdrawal_date(row["SUBMIT_TIMESTAMP"]),
                "Primary Reason": row["PRIMARYREASON"],
                "Comments": row["COMMENTS"], 
                "Course Code": [row["COURSECODE1"], row["COURSECODE2"], row["COURSECODE3"], row["COURSECODE4"], row["COURSECODE5"], row["COURSECODE6"], row["COURSECODE7"], row["COURSECODE8"], row["COURSECODE9"]], 
                "Course Title": [row["COURSETITLE1"], row["COURSETITLE2"], row["COURSETITLE3"], row["COURSETITLE4"], row["COURSETITLE5"], row["COURSETITLE6"], row["COURSETITLE7"], row["COURSETITLE8"], row["COURSETITLE9"]], 
                "Term End Date": [
                    clean_term_end_or_mid_date(row["TERMENDDATE1"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE2"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE3"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE4"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE5"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE6"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE7"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE8"]), 
                    clean_term_end_or_mid_date(row["TERMENDDATE9"])
                    ], 
                "Term Midpoint Date": [
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE1"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE2"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE3"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE4"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE5"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE6"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE7"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE8"]), 
                    clean_term_end_or_mid_date(row["TERMMIDDOINTDATE9"])
                    ]
            }
            raw_course_codes=temp_dict["Course Code"]
            raw_course_titles=temp_dict["Course Title"]
            raw_end_dates=temp_dict["Term End Date"]
            raw_midpoint_dates=temp_dict["Term Midpoint Date"]
            for array in [raw_course_codes, raw_course_titles, raw_end_dates, raw_midpoint_dates]:
                while "" in array:
                    array.remove("")
            # Term midpoints don't always populate, so this line forces blank arrays
            while len(raw_midpoint_dates)<len(raw_course_codes):
                raw_midpoint_dates.append("")
            temp_index=0
            for temp_index in range(0, len(raw_course_codes)-1):
                new_temp_dict={
                    "ERAUID": temp_dict["ERAUID"],
                    "Withdrawal Date": temp_dict["Withdrawal Date"],
                    "Primary Reason": temp_dict["Primary Reason"], 
                    "Comments": temp_dict["Comments"],
                    "Course Code": raw_course_codes[temp_index], 
                    "Course Title": raw_course_titles[temp_index], 
                    "Term End Date": raw_end_dates[temp_index], 
                    "Term Midpoint Date": raw_midpoint_dates[temp_index]
                }
                #locals()[f'{temp_dict_name}p{index}']=new_temp_dict # Dynamically renames dict 
                #index+=1
                temp_index+=1
                list_of_dicts.append(new_temp_dict)
    wanted_dicts=remove_unwanted_courses(list_of_dicts)
    legit_withdrawals, early_withdrawals=remove_early_withdrawals(wanted_dicts)
    return [legit_withdrawals, early_withdrawals]
def print_withdrawal_data(current_directory, path_break, list_of_withdrawal_dicts, legit_or_not): 
    if legit_or_not==1:
        withdrawal_data_path=f'{current_directory}{path_break}Withdrawal_Data{path_break}withdrawal_data.csv'
    else: 
        withdrawal_data_path=f'{current_directory}{path_break}Withdrawal_Data{path_break}early_withdrawal_data.csv'
    if os.path.exists(withdrawal_data_path):
        os.remove(withdrawal_data_path)
    Path(withdrawal_data_path).touch()
    # Print sentences in csv
    field_names=["ERAUID", "Withdrawal Date", "Primary Reason", "Comments", "Course Code", "Course Title", "Term End Date", "Term Midpoint Date"] 
    encoding_type=detect_encoding_type(withdrawal_data_path)
    with open(withdrawal_data_path, 'w', newline='', encoding=encoding_type) as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in list_of_withdrawal_dicts:
            writer.writerow(dict)
def remove_unwanted_courses(list_of_dicts): 
    wanted_dicts=[]
    wanted_courses=["PHYS  102", "PHYS  123", "PHYS  150", 
                    "CSCI  109", "CSCI  123", 
                    "ENGR  101", "ENGR  115", 
                    "ESCI  201", 
                    "MATH  106", "MATH  111"]
    for dict in list_of_dicts:
        if dict["Course Code"] in wanted_courses:
            wanted_dicts.append(dict)
    return wanted_dicts
def remove_early_withdrawals(list_of_dicts): 
    legit_withdrawals=[]
    early_withdrawals=[]
    for dict in list_of_dicts: 
        if dict["Term End Date"]-timedelta(days=62) < dict["Withdrawal Date"]:
            legit_withdrawals.append(dict)
        else:
            early_withdrawals.append(dict)
    return [legit_withdrawals, early_withdrawals]