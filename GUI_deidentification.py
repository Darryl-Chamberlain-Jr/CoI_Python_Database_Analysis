import time
import glob
import os 
dir=os.getcwd()
if os.name == "nt":
    path_break="\\"
else:
    path_break="/"

docx_files=[]
for file in glob.glob(f'{dir}{path_break}Word_Documents_To_Deidentify{path_break}*.docx'):
        docx_files.append(file)

def check_file_naming_convention(file_name):
    if "MATH" in file_name or "PHY" in file_name: 
        if "MATH" in file_name:
            class_ID="MATH"
        else: 
            class_ID="PHY"
    else: 
        class_ID="Unknown"
    if "AUG" in file_name or "SEPT" in file_name: 
        if "AUG" in file_name:
            term="AUG"
        else:
            term="SEPT"
    else: 
        term="Unknown"
    if "2021" in file_name or "2022" in file_name: 
        if "2021" in file_name:
            year="2021"
        else: 
            year="2022"
    else: 
        year="Unknown"
    cohort="Unknown"
    for section_number in ["1", "2", "3", "4", "5", "6", "7"]:
        if f"SECTION {section_number}" in file_name: 
            cohort=section_number
    module_number="Unknown"
    for module in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        if f"M{module}" in file_name:
            module_number=module
    return [class_ID, term, year, cohort, module_number]

for file in docx_files: 
    file_name=file.replace('.docx', '') # remove ".docx" from name

    class_ID, term, year, cohort, module_number = check_file_naming_convention(file_name)

    print(f"\nWelcome! Beginning to deidentify file \n\n{file_name}\n\n")
    check_unknown_index=0
    for string in [class_ID, term, year, cohort, module_number]:
        if string=="Unknown":
            print(f"Some values are unknown based on the file naming convention. Please input the following:\n")
            class_ID=input("Class ID (MATH, PHY) : ")
            term=input("Term (AUG, SEPT) : ")
            year=input("Year (2021, 2022) : ")
            cohort=input("Cohort (1, 2, 3, 4, 5, 6, 7) : ")
            module_number=input("Module Number (1, 2, 3, 4, 5, 6, 7, 8, 9) : ")
            break 
        else: 
            check_unknown_index+=1
    if check_unknown_index==5:
        confirm=input(f"Based on file naming convention, the following information was extracted. Confirm the information to continue (Y/N).\n\n Class ID: {class_ID} \n Term: {term} \n Year: {year} \n Cohort: {cohort} \n Module Number: {module_number} \n\n")
        if confirm=="Yes" or confirm=="Y" or confirm == "y" or confirm == "yes":
            print(f"Confirmed! Beginning to deidentify file \n\n{file_name}\n\n")
            time.sleep(1)
        else:
            print(f"\nUnderstood! Deidentifying the file \n\n{file_name}\n\n Please input the following:\n")
            class_ID=input("Class ID (MATH, PHY) : ")
            term=input("Term (AUG, SEPT) : ")
            year=input("Year (2021, 2022) : ")
            cohort=input("Cohort (1, 2, 3, 4, 5, 6, 7) : ")
            module_number=input("Module Number (1, 2, 3, 4, 5, 6, 7, 8, 9) : ")

    from Python_Scripts.parse_word_transcript_raw_format import *
    try: 
        run_deidentification(dir, path_break, file_name, class_ID, term, year, cohort, module_number)
        print("\nCompleted! Be sure to check csv files for irregularities.\n\n")
    except Exception as e: 
        print(e)
        print("\n\n Be sure that the prompt from the discussion has been deleted and all hyperlinks have been removed.")
