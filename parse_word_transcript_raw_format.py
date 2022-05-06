# Command to run:
    # cd ..\Transcript_Cleaning
    # .\parse_word_transcript.py  

# Only leave spaces between new instructors, not between each instructor post. 

# This file is meant to take a docx file in the same directory and parse it sentence by sentence into a csv file.
import os
import csv
import re
import glob
from pathlib import Path # Convert from docx to strings
from docx import Document
from deidentify_sets import * # Use for deindentifying. May need to modify per set of transcripts.
from parse_and_clean_sentences import * # Clean sentences separately from special formatting in the rest of this py file
import subprocess

docx_files=[]
for file in glob.glob("*.docx"):
    docx_files.append(file)
for file in docx_files: 
    file_name=file.replace('.docx', '') # remove ".docx" from name
    create_csv_file=file_name

    document = Document(file)
    cleaned_sentences=clean_file(document)

    # Find SPEAKER and create blanks
    final_cleaning=[]
    initial_list_of_IDs=[]
    index_to_remove_after_speaker=0
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
    list_of_student_dicts=[]
    list_of_instructor_dicts=[]
    for index in range(0, len(final_cleaning)):
        temp_dict={}
        temp_dict["Analysis Unit"]=final_cleaning[index]
        if final_cleaning[index]=="":
            temp_dict["Speaker ID"]=""
        else:
            temp_dict["Speaker ID"]=list_of_IDs[index]
        if list_of_IDs[index] in list_of_instructor_IDs:
            list_of_instructor_dicts.append(temp_dict)
        else:
            list_of_student_dicts.append(temp_dict)

    # Create csv file
    current_directory = os.getcwd()
    # If using Windows, the path names are defined with \ rather than /. 
    if os.name == "nt":
        path_break="\\"
    else:
        path_break="/"
    Path(str(current_directory) + str(path_break) + str(create_csv_file) + ' - students' + '.csv').touch()
    Path(str(current_directory) + str(path_break) + str(create_csv_file) + ' - instructor' + '.csv').touch()

    # Print sentences in csv
    field_names=["Speaker ID", "Analysis Unit"]
    with open(str(current_directory) + str(path_break) + str(create_csv_file) + ' - students' + '.csv', 'w', newline='', encoding="utf-8") as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in list_of_student_dicts:
            writer.writerow(dict)
    
    # Print sentences in csv
    field_names=["Speaker ID", "Analysis Unit"]
    with open(str(current_directory) + str(path_break) + str(create_csv_file) + ' - instructor' + '.csv', 'w', newline='', encoding="utf-8") as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for dict in list_of_instructor_dicts:
            writer.writerow(dict)