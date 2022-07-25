#View Database

# LIST OF IMPORTS
import shelve  # To interact with dictonaries
import os      # To determine os type

if os.name == "nt":
    path_break="\\"
else:
    path_break="/"
temp_dir = os.getcwd() # If using Windows, the path names are defined with \ rather than /. 
current_directory=temp_dir.replace(f"{path_break}Python_Scripts", "")
path_to_master_database=f'{current_directory}{path_break}Master_Database{path_break}master_database'
if os.path.exists(f'{path_to_master_database}.db')==False:
    print("\n\nMaster Database does not exist.\n\n")
else: 
    if os.name == "linux-gnu":
        database=shelve.open(f'{path_to_master_database}.db')
    else: 
        database=shelve.open(path_to_master_database)
    try: 
        number_of_dicts=0
        for each_speaker_ID in database['List of Dicts']: 
            if type(each_speaker_ID) == type({}):
                for key in each_speaker_ID.keys():
                    to_print=each_speaker_ID[f'{key}']
                    print(f'{to_print}')
                print('\n')
                number_of_dicts+=1
    except Exception as e: 
        print(e)
        print("Database is empty. Try uploading data first.")
    finally: 
        print(f'Size of database: {number_of_dicts}')
        database.close()