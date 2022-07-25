from Python_Scripts.upload_to_master import *
import glob
import os

current_directory = os.getcwd() # If using Windows, the path names are defined with \ rather than /. 
if os.name == "nt":
    path_break="\\"
else:
    path_break="/"
path_to_master_database=f'{current_directory}{path_break}Master_Database{path_break}master_database.db'

while True:
    task=input("\nType the number of the task you would like to complete: \n (1) Upload all csv files to master database. \n (2) Download master database. \n (3) Delete old master database in preparation for new one.\n\n")
    if task=="1": 
        number_of_files_uploaded=0
        number_of_files_processed=0
        for file_name in glob.glob(f"{current_directory}{path_break}Deidentified_CSV_Files{path_break}*.csv"):
            if file_name=="master_data.csv": continue 
            else: 
                list_of_dicts=extract_deidentified_data(file_name)
                already_uploaded=upload_extracted_data(current_directory, path_break, list_of_dicts)
                clean_file_name=file_name.replace(f"{current_directory}{path_break}Deidentified_CSV_Files{path_break}", "")
                if already_uploaded==0:
                    print(f"File {clean_file_name} has been uploaded.")
                    number_of_files_uploaded+=1
                elif already_uploaded==1: 
                    print(f"File {clean_file_name} has been uploaded previously. Data was not added to master database.")
                else: 
                    print(f'There was an error uploading file {clean_file_name}.')
                number_of_files_processed+=1
        if number_of_files_uploaded==0: 
            follow_up_task=input("\nAll files have been previously uploaded to the master database. Would you still like to download the database now? (Y/N) \n\n")
        elif number_of_files_uploaded==1:
            follow_up_task=input(f"\n{number_of_files_processed} file has been uploaded to database. Would you like to download the new database now? (Y/N) \n\n")
        else: 
            follow_up_task=input(f"\n{number_of_files_processed} files have been uploaded to database. Would you like to download the new database now? (Y/N) \n\n")
        if follow_up_task=="Y" or follow_up_task=="y" or follow_up_task=="Yes" or follow_up_task=="yes":
            download_master_database(current_directory, path_break)
            print("\nDatabase has been downloaded as a csv file. Enjoy your day!\n\n")
            break 
        elif follow_up_task=="N" or follow_up_task=="n" or follow_up_task=="No" or follow_up_task=="no":
            print("\nUnderstood. Enjoy your day!\n\n")
            break 
        else: 
            print("\nAn invalid command was entered. Exiting now...\n\n")
    elif task=="2":
        empty_check=check_if_database_empty()
        if os.path.exists(path_to_master_database)==False:
            print("\nMaster database does not exist. Please create a database first.\n")
            break
        elif empty_check==1:
            print("\nMaster database is empty. Please load data first.\n")
            break
        else: 
            download_master_database(current_directory, path_break)
            break
    elif task=="3":
        if os.path.exists(path_to_master_database)==False:
            print("\nNo master database exists to be deleted.\n")
            break
        else: 
            warning=input("\nAre you sure you want to delete? Recovering the old database will be difficult. \n\n Y/N \n\n")
            if warning=="Y" or warning=="y" or warning=="Yes" or warning=="yes":
                os.remove(path_to_master_database)
                break
            else: 
                break
    else: 
        print("\nPlease input a valid command.\n")