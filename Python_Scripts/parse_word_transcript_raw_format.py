import shelve  # To interact with dictonaries
import os      # To determine os type
import csv     # To read csv files
import re
import glob
import time 
from pathlib import Path # Convert from docx to strings
from docx import Document
import subprocess

#from deidentify_sets import * # Use for deindentifying. May need to modify per set of transcripts.
special_period_set = [ [" p.", " p"], ["p.s.", "ps"], ["P.S.", "PS"], [" lbs.", " lbs"], [" n.d.", " nd"], [" oz.", " oz"], [" AHA!", " AHA"], ["i.e.", " ie"], ["e.g.", " eg"], ["Mr.", "Mr"], ["Mrs.", "Mrs"], ["Ms.", "Ms"], ["Dr.", "Dr"], ["U.S.", "US"], [" al.", " al"], [" vs.", " vs"], [" hr.", " hr"], [" hrs.", " hrs"], [" et.", " et"], [" etc.", " etc"], [" a.k.a.", " aka"], [" .pdf", " pdf"], [" .jpg", " jpg"], [" .png", " png"], [" :)", " [smile-emoji]."], ["J.R.", "JR"], ["Prof H.", "Prof Han"], [" .s.g.", " sg"], ["Mr. Dang", "Mr Dang"]]

# Remove trash from new download method
remove_trash_containing=["Reply Reply to Comment", "Manage Discussion Entry"]

# Detect trash date
def detect_trash(string):
    months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for month in months:
        if month in string and "2021" in string and ("am" in string or "pm" in string):
            string="skip line"
    for trash_phrase in remove_trash_containing:
        if trash_phrase in string: 
            string="skip line"
    return string 

def clean_file(document, deidentify_student_names, deidentify_instructor_names): 
    # Extract text from document into array of paragraphs
    full_text=[] 
    for para in document.paragraphs:
        full_text.append(para.text)
    # Remove excess line breaks from each paragraph.
    clean_text=[]
    for entry in full_text:
        entry.lstrip()
        entry.rstrip()
        no_break_entry=entry.replace('\n', '')
        clean_entry=no_break_entry.replace('.  ', '. ')
        if len(entry)>0:
            clean_text.append(clean_entry)
    # Ensure there are spaces after special endings
    special_endings=["?", "!", "]", ",", ")", ":"]
    special_endings_with_space=["? ", "! ", "] ", ", ", ") ", ": "]
    special_endings_index=0
    while special_endings_index<6:
        if special_endings[special_endings_index] in clean_text and special_endings_with_space[special_endings_index] not in clean_text:
            clean_text.replace(special_endings[special_endings_index], special_endings_with_space[special_endings_index])
        special_endings_index+=1
    # Convert paragraphs in clean_text into individual sentences.
    first_parse=[]
    second_parse=[]
    fully_parsed=[]
    for sentence in clean_text:
        # Before sentence split by period, remove special uses of period that do not indicate end of sentence. 
        for special_period_case_pair in special_period_set:
            sentence = sentence.replace(str(special_period_case_pair[0]), str(special_period_case_pair[1]))
        # Before spliting by period, protect numbers with decimal expansions and remove emails/urls.
        check_for_numbers_separated=sentence.split()
        removing_decimals=""
        for string in check_for_numbers_separated:
            if '@' in string:
                string='[email]'
            elif '.edu' in string:
                string='[url]'
            elif '.com' in string:
                string='[url]'
            elif '.net' in string: 
                string='[url]'
            elif '.org' in string:
                string='[url]'
            elif '.jpg' in string: 
                string='[image]'
            elif '.png' in string: 
                string='[image]'
            # First checkes that there are numbers to both sides. Otherwise makes a space between the period so the split works.
            elif any(char.isdigit() for char in string):
                check_if_error=string.split('.')
                if len(check_if_error)>1:
                    # Second entry is empty if a number is the end of a sentence, like "Module 2." We want to treat these as ends of sentences and leave the period.
                    if len(check_if_error[1])==0:
                        string=f"{check_if_error[0]}."
                    # Else if there are numbers on either side of the period, we replace the period with DECIMALPOINT.
                    elif all(any(char.isdigit() for char in small_string) for small_string in check_if_error):
                        string=string.replace('.', 'DECIMALPOINT')
                    # Otherwise this is a number in the sentence that doesn't need to be modified.
                    else:
                        fixed_no_space=""
                        for piece in check_if_error:
                            fixed_no_space+=f'{piece} '
                        string=fixed_no_space
            removing_decimals+=f'{string} '       
        # Split by period
        parsed=removing_decimals.split('.')
        # Add decimals back after spliting out periods.
        adding_back_decimals=[]
        for string in parsed:
            if any(char.isdigit() for char in string):
                string=string.replace('DECIMALPOINT', '.')
            adding_back_decimals.append(string)
        parsed=adding_back_decimals
        # 
        for entry in parsed:
            # Strips any whitespace from beginning or ending of a sentence. 
            stripped_entry=entry.strip()
            # Removes new trash sentences introduced from new raw transcription generation method.
            stripped_entry=detect_trash(stripped_entry)
            # Continues cleaning process on nonempty, non-trash lines. 
            if len(stripped_entry)>0 and stripped_entry != "skip line":
                # Checks if the last entry is a special ending. If not, it adds a period that is not there.
                if stripped_entry[-1] not in special_endings:
                    # Add period back to end of sentence
                    stripped_entry+="."
                # Replace special characters
                # Uncomment when trying to determine special characters to decode
                ###
                #encoding=stripped_entry.encode("utf-8")
                #print(encoding)
                ###
                stripped_entry=stripped_entry.replace(b'\xce\xbc'.decode('utf-8'), 'mu')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x9c'.decode('utf-8'), '\"')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x9d'.decode('utf-8'), '\"')
                stripped_entry=stripped_entry.replace(b'\xe2\x88\x92'.decode('utf-8'), '-')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x93'.decode('utf-8'), '--')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x94'.decode('utf-8'), '---')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x98'.decode('utf-8'), '\'')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\x99'.decode('utf-8'), '\'')
                stripped_entry=stripped_entry.replace(b'\xe2\x96\xb3'.decode('utf-8'), ' [delta] ')
                stripped_entry=stripped_entry.replace(b'\xce\x94'.decode('utf-8'), ' [delta] ')
                stripped_entry=stripped_entry.replace(b'\xe2\x89\x88'.decode('utf-8'), ' [approximately] ')
                stripped_entry=stripped_entry.replace(b'\xe2\x80\xa6'.decode('utf-8'), '')
                stripped_entry=stripped_entry.replace(b'\xc3\x97'.decode('utf-8'), ' x ')
                stripped_entry=stripped_entry.replace(b'\xc2\xb2'.decode('utf-8'), '^2')
                ### END REPLACE SPECIAL CHARACTERS
                ###
                # Checks for the new comment phrase "Collapse Subdiscussion [name]". Removes it for just the name of the speaker if it appears.
                if "Collapse Subdiscussion" in stripped_entry:
                    stripped_entry=stripped_entry.replace("Collapse Subdiscussion ", "SPEAKER ") #Uses "SPEAKER " to break and tag sentences later.
                # Deidentify student names ONLY IF they are not the declaration of speaker
                else: 
                    for student_name in deidentify_student_names:
                        stripped_entry = stripped_entry.replace(str(student_name), "[name]")
                    for instructor_name in deidentify_instructor_names:
                        stripped_entry = stripped_entry.replace(str(instructor_name[0]), "[instructor]")
                    stripped_entry = stripped_entry.replace("[name] [name]", "[name]")
                # Split special case where punctuation occures within quotations - STILL NEEDS TO BE ADDED
                # Add entry to list of fully_parsed sentences
                first_parse.append(stripped_entry)
    # Previous break only split by periods. This splits sentences by "!"
    for semi_cleaned_sentence in first_parse:
        semi_parsed = semi_cleaned_sentence.split('!')
        for sentence in semi_parsed:
            revised_sentence=""
            stripped_sentence=sentence.strip()
            if len(stripped_sentence)>0:
                if stripped_sentence[-1] not in ["?", ".", "]", ",", ")", ":"]:
                    # Add ! back to end of sentence
                    stripped_sentence+="!"
                revised_sentence+=f"{stripped_sentence} "
            second_parse.append(revised_sentence)
    # Previous break only split by periods and "!". This splits sentences by "?"
    for semi_cleaned_sentence in second_parse:
        semi_parsed = semi_cleaned_sentence.split('?')
        for sentence in semi_parsed:
            revised_sentence=""
            stripped_sentence=sentence.strip()
            if len(stripped_sentence)>0:
                if stripped_sentence[-1] not in ["!", ".", "]", ",", ")", ":"]:
                    # Add ? back to end of sentence
                    stripped_sentence+="?"
                revised_sentence+=f"{stripped_sentence} "
            fully_parsed.append(stripped_sentence)
        clean_text_again=[]
    # Strips away additional spaces and breaks, just in case. Also removes empty sentences from array.
    for entry in fully_parsed:
        entry.strip()
        no_break_entry=entry.replace('\n', '')
        clean_entry=no_break_entry.replace('. ', '.')
        if len(clean_entry)>0 and clean_entry != " ":
            clean_text_again.append(clean_entry)
    return clean_text_again

#### Opens csv and extracts rows as array of dicts ####
def extract_deidentified_data(dir, path_break, identified_names_csv):
    list_of_dicts=[]
    with open(f'{dir}{path_break}Identifable_Data{path_break}{identified_names_csv}', newline='', encoding='utf-8-sig') as csv_identified:
        reader = csv.DictReader(csv_identified)
        for row in reader: 
            temp_dict_name=row["Speaker ID"]
            temp_dict={
                "Speaker Name": row["Speaker"],
                "Speaker ID": row["Speaker ID"],
                "Speaker Type": row["Speaker Type"], 
                "Class ID": row["Class ID"],
                "Term": row["Term"], 
                "Year": row["Year"],
                "Cohort": row["Cohort"]
            }
            locals()[f'{temp_dict_name}']=temp_dict # Dynamically renames dict to be speaker ID
            list_of_dicts.append(temp_dict)
    return list_of_dicts

#### Takes array of dicts and adds them to database ####
def upload_extracted_data(dir, path_break, list_of_dicts):
    path_to_ident_database=f'{dir}{path_break}Identifable_Data{path_break}deidentify_dynamic'
    if os.path.exists(f'{path_to_ident_database}.db'): # Deletes db if already created to remove overlap.
        os.remove(f'{path_to_ident_database}.db')
    if os.name == "linux-gnu":
        database=shelve.open(f'{path_to_ident_database}.db')
    else: 
        database=shelve.open(path_to_ident_database)
    try: 
        database['List of Dicts']=list_of_dicts
    except: 
        print("\n\nAn error occured when loading the database.\n")
    finally: 
        database.close()


### Dynamically define deidentified sets to use ###
# Structure: 
    # Take input from user to determine Class ID, Term, Cohort
    # Define 5 arrays based on the inputs: 
        #1   encode_student_names          Used to replace full name at start of post with speaker code
        #2   deidentify_student_names      Used to replace all other mentions of student name within the document with [name]
        #3   encode_instructor_names       Used to replace full name at start of post with speaker code
        #4   deidentify_instructor_names   Used to replace all other mentions of instructor name with their speaker code
        #5   list_of_instructor_IDs        Used when sorting dictonaries 
def arrays_for_deidentification(dir, path_break, class_ID, term, year, cohort): 
    #Inititalize target arrays
    encode_student_names=[]
    deidentify_student_names=[]
    encode_instructor_names=[]
    deidentify_instructor_names=[]
    list_of_instructor_IDs=[]

    path_to_ident_database=f'{dir}{path_break}Identifable_Data{path_break}deidentify_dynamic'
    if os.name == "linux-gnu":
        database=shelve.open(f'{path_to_ident_database}.db')
    else: 
        database=shelve.open(path_to_ident_database)
    try: 
        for each_speaker_ID in database['List of Dicts']: 
            temp_dict=each_speaker_ID
            if temp_dict["Class ID"]==class_ID and temp_dict["Term"]==term and temp_dict["Year"]==year and temp_dict["Cohort"]==cohort: 
                if temp_dict["Speaker Type"]=="Student":
                    encode_student_names.append([temp_dict["Speaker Name"], temp_dict["Speaker ID"]])
                    for part_of_name in temp_dict["Speaker Name"].split():
                        deidentify_student_names.append(part_of_name)
                else: 
                    encode_instructor_names.append([temp_dict["Speaker Name"], temp_dict["Speaker ID"]])
                    deidentify_instructor_names.append([temp_dict["Speaker Name"].split()[1], temp_dict["Speaker ID"]])
                    list_of_instructor_IDs.append(temp_dict["Speaker ID"])
    finally: 
        database.close()
    
    return [encode_student_names, deidentify_student_names, encode_instructor_names, deidentify_instructor_names, list_of_instructor_IDs]

### Deidentify data, save data as array of dicts, and write dicts to csv ###
def run_deidentification(dir, path_break, file_name, class_ID, term, year, cohort, module_number): 
    list_of_dicts = extract_deidentified_data(dir, path_break, "Deident_Key.csv")
    upload_extracted_data(dir, path_break, list_of_dicts)
    encode_student_names, deidentify_student_names, encode_instructor_names, deidentify_instructor_names, list_of_instructor_IDs = arrays_for_deidentification(dir, path_break, class_ID, term, year, cohort)
    to_strip=f'{dir}{path_break}Word_Documents_To_Deidentify{path_break}'
    create_csv_file=file_name.replace(to_strip, '') # Strips directory naming
    document = Document(f'{file_name}.docx')
    cleaned_sentences=clean_file(document, deidentify_student_names, deidentify_instructor_names)

    # Find SPEAKER and create blanks
    final_cleaning=[]
    initial_list_of_IDs=[]
    index_to_remove_after_speaker=0
    speaker_real_name="" 
    for sentence in cleaned_sentences:
        # If "SPEAKER" is in the sentence, define this as the new speaker's name.
        if "SPEAKER" in sentence:
            speaker_real_name=sentence.replace("SPEAKER ", "")
            index_to_remove_after_speaker=1
        # Skips line after SPEAKER declaration as this is the student name in the raw data and not part of their post.
        elif index_to_remove_after_speaker==1:
            index_to_remove_after_speaker=0 # resets index for skip
        # Add the speaker name to the list of IDs and the sentence to the final cleaning
        else:
            if sentence != '\".' and sentence != '\"?' and sentence != '\"!' and sentence != "":
                final_cleaning.append(sentence)
                initial_list_of_IDs.append(speaker_real_name)
    # Deidentify speakers
    list_of_IDs=[]
    for name_in_list in initial_list_of_IDs: 
        found_name=0
        # Encode instructor names
        for instructor_name in encode_instructor_names:
            if instructor_name[0] in name_in_list:
                list_of_IDs.append(instructor_name[1])
                found_name=1
        for student_name_encode in encode_student_names:
            if student_name_encode[0] in name_in_list:
                list_of_IDs.append(student_name_encode[1])
                found_name=1
        if found_name==0:
            list_of_IDs.append(name_in_list)
    # Create a dictonary for each sentence that can later be used to tag with code.
    list_of_dicts=[]
    for index in range(0, len(final_cleaning)):
        temp_dict={}
        temp_dict["Analysis Unit"]=final_cleaning[index]
        if final_cleaning[index]=="":
            temp_dict["Speaker ID"]=""
        else:
            temp_dict["Speaker ID"]=list_of_IDs[index]
        if list_of_IDs[index] in list_of_instructor_IDs:
            temp_dict["Speaker Type"]="Instructor"
        else:
            temp_dict["Speaker Type"]="Student"
        temp_dict["Class ID"]=class_ID
        temp_dict["Term"]=term
        temp_dict["Year"]=year
        temp_dict["Cohort"]=cohort
        temp_dict["Module Number"]=module_number
        list_of_dicts.append(temp_dict)

    # Create csv file
    csv_file_path=f'{dir}{path_break}Deidentified_CSV_Files{path_break}{create_csv_file}.csv'
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    Path(csv_file_path).touch()

    # Print sentences in csv
    field_names=["Speaker ID", "Speaker Type", "Class ID", "Term", "Year", "Cohort", "Module Number", "Analysis Unit"]
    with open(csv_file_path, 'w', newline='', encoding="utf-8") as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in list_of_dicts:
            writer.writerow(dict)