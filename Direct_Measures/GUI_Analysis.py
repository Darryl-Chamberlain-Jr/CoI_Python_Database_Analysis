#GUI_Analysis

# Structure: 
    # Modifying analysis database
        # Create initial analysis database
        # Add to analysis database
        # Download analysis database
        # Change sentences in exisiting database
    # Analysis of data
        # Presence Densities
        # IRR
    # Analysis of researchers
        # Hours worked
        # Coding speed


from sys import path_importer_cache
import glob
import os, shutil
import openpyxl

from Python_Scripts.For_GUI_Analysis.data_analysis_tables import *

### NECESSARY STATICS THAT SHOULD NOT BE CHANGED ###
base_dir=os.getcwd()
if os.name == 'nt':
    path_break='\\'
else:
    path_break='/'

### GLOBAL VARIABLES ###
path_to_main_database=f'{base_dir}{path_break}Main_Database{path_break}main_database.xlsx'

while True: 
    task=input('\nType the number of the task you would like to complete: \n (1) Create Progress Report \n (2) Create IRR Table \n (3) Presence Density Report \n (0) Exit. \n\nTask: ')

    if task=='0':
        break 

    elif task=='1':
        print('\nReading main database into system.')
        main_df=pandas.read_excel(path_to_main_database, index_col=[0])
        overview_table, array_of_detailed_tables=term_table_overview(main_df)
        progress_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}code_table_progress.xlsx'
        save_all_dfs_as_tables(progress_file_name, overview_table, array_of_detailed_tables)

    elif task=='2':
        print('\nReading main database into system.')
        main_df=pandas.read_excel(path_to_main_database, index_col=[0])

        IRR_table_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}IRR{path_break}IRR_table.xlsx'
        IRR_archive_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}IRR{path_break}Archive'

        IRR_df, IRR_full_breakdown_df_array, IRR_cat_breakdown_df_array=IRR_table(main_df)
        IRR_df.to_excel(IRR_table_file_name)

        IRR_full_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}IRR{path_break}IRR_full_detailed_report.xlsx'
        IRR_cat_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}IRR{path_break}IRR_cat_detailed_report.xlsx'

        save_all_dfs_as_tables(IRR_full_file_name, IRR_df, IRR_full_breakdown_df_array)
        save_all_dfs_as_tables(IRR_cat_file_name, IRR_df, IRR_cat_breakdown_df_array)

    elif task=='3':
        print('\nReading main database into system.')
        main_df=pandas.read_excel(path_to_main_database, index_col=[0])

        # Types of df to analyze
        dict_of_student_dfs = {
            'student_df': main_df[main_df['Speaker Type'] == 'Student'], # all students
            'student_math_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'MATH')], # all math students
            'student_math_aug21_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'MATH') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2021)], # all math aug 21 students
            'student_math_aug22_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'MATH') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2022)], # all math aug 22 students
            'student_phy_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'PHY')], # all phy students
            'student_phy_aug21_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'PHY') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2021)], # all phy aug 21 students
            'student_phy_aug22_df': main_df[(main_df['Speaker Type'] == 'Student') & (main_df['Class ID'] == 'PHY') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2022)], # all phy aug 22 students
        }
        dict_of_instructor_dfs = {
            'instructor_df': main_df[main_df['Speaker Type'] == 'Instructor'], # all instructors
            'instructor_math_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'MATH')], # all math instructors
            'instructor_math_aug21_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'MATH') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2021)], # all math aug 21 instructors
            'instructor_math_aug22_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'MATH') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2022)], # all math aug 22 instructors
            'instructor_phy_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'PHY')], # all phy students
            'instructor_phy_aug21_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'PHY') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2021)], # all phy aug 21 instructors
            'instructor_phy_aug22_df': main_df[(main_df['Speaker Type'] == 'Instructor') & (main_df['Class ID'] == 'PHY') & (main_df['Term'] == 'AUG') & (main_df['Year'] == 2022)], # all phy aug 22 instructors
        }

        print('Creating Full Density Table from Student Data. Please wait...')
        CD_full_df_student_file_name = f'{base_dir}{path_break}Data_Analysis{path_break}Density{path_break}full_density_table_student.xlsx'
        if os.path.exists(CD_full_df_student_file_name):
            os.remove(CD_full_df_student_file_name)

        # for each df, create a full density table and save as an excel sheet to the same workbook
        for student_dict_key in dict_of_student_dfs.keys(): 
            temp_df = compile_density_df(dict_of_student_dfs[student_dict_key], 'full')
            if os.path.exists(CD_full_df_student_file_name):
                with pandas.ExcelWriter(CD_full_df_student_file_name, engine='openpyxl', mode='a') as writer:
                    temp_df.to_excel(writer, sheet_name=student_dict_key)
            else:
                temp_df.to_excel(CD_full_df_student_file_name, sheet_name=student_dict_key)
        density_comparison_table(CD_full_df_student_file_name, all_code_list)
    
        print('Creating Full Density Table from Instructor Data. Please wait...')
        CD_full_df_instructor_file_name = f'{base_dir}{path_break}Data_Analysis{path_break}Density{path_break}full_density_table_instructor.xlsx'
        # for each df, create a full density table and save as an excel sheet to the same workbook
        if os.path.exists(CD_full_df_instructor_file_name):
            os.remove(CD_full_df_instructor_file_name)

        for instructor_dict_key in dict_of_instructor_dfs.keys(): 
            temp_df = compile_density_df(dict_of_instructor_dfs[instructor_dict_key], 'full')
            if os.path.exists(CD_full_df_instructor_file_name):
                with pandas.ExcelWriter(CD_full_df_instructor_file_name, engine='openpyxl', mode='a') as writer:
                    temp_df.to_excel(writer, sheet_name=instructor_dict_key)
            else:
                temp_df.to_excel(CD_full_df_instructor_file_name, sheet_name=instructor_dict_key)
        density_comparison_table(CD_full_df_instructor_file_name, all_code_list)

        print('Creating Categorical Density Table from Student Data. Please wait...')
        CD_category_df_student_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}Density{path_break}category_density_table_student.xlsx'
        # for each df, create a full density table and save as an excel sheet to the same workbook
        if os.path.exists(CD_category_df_student_file_name):
            os.remove(CD_category_df_student_file_name)

        for student_dict_key in dict_of_student_dfs.keys(): 
            temp_df = compile_density_df(dict_of_student_dfs[student_dict_key], 'cat')
            if os.path.exists(CD_category_df_student_file_name):
                with pandas.ExcelWriter(CD_category_df_student_file_name, engine='openpyxl', mode='a') as writer:
                    temp_df.to_excel(writer, sheet_name=student_dict_key)
            else:
                temp_df.to_excel(CD_category_df_student_file_name, sheet_name=student_dict_key)
        density_comparison_table(CD_category_df_student_file_name, cat_code_list)

        print('Creating Categorical Density Table from Instructor Data. Please wait...')
        CD_category_df_instructor_file_name=f'{base_dir}{path_break}Data_Analysis{path_break}Density{path_break}category_density_table_instructor.xlsx'
        # for each df, create a full density table and save as an excel sheet to the same workbook
        if os.path.exists(CD_category_df_instructor_file_name):
            os.remove(CD_category_df_instructor_file_name)

        for instructor_dict_key in dict_of_instructor_dfs.keys(): 
            temp_df = compile_density_df(dict_of_instructor_dfs[instructor_dict_key], 'cat')
            if os.path.exists(CD_category_df_instructor_file_name):
                with pandas.ExcelWriter(CD_category_df_instructor_file_name, engine='openpyxl', mode='a') as writer:
                    temp_df.to_excel(writer, sheet_name=instructor_dict_key)
            else:
                temp_df.to_excel(CD_category_df_instructor_file_name, sheet_name=instructor_dict_key)
        density_comparison_table(CD_category_df_instructor_file_name, cat_code_list)




