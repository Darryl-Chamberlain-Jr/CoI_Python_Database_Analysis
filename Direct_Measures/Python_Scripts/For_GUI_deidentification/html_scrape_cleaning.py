import re
import numpy
import random, string

from .deidentify import *

before_breaks_replacement_array=[
    {'Html': '\n', 'Replace with': ''},
    {'Html': '<strong>', 'Replace with': ''},
    {'Html': '</strong>', 'Replace with': ''}, 
    {'Html': '<em>', 'Replace with': ''},
    {'Html': '</em>', 'Replace with': ''}
]
after_breaks_replacement_array=[
    {'Html': '&nbsp;', 'Replace with': ' '}, 
    {'Html': '<div>', 'Replace with': ''},
    {'Html': '<div\sclass=.+>', 'Replace with': ''},
    {'Html': '<span\sclass=.+><span\sdata-offset-key.+>', 'Replace with': ''},
    {'Html': '<span\sdata-offset-key.+>', 'Replace with': ''},
    {'Html': '<span\sstyle=.+>', 'Replace with': ''},
    {'Html': '</div>', 'Replace with': ''},
    {'Html': '<img.+>', 'Replace with': '[image]'},
    {'Html': 'https://.+\s', 'Replace with': '[url]'},
    {'Html': '&amp;', 'Replace with': '&'},
    {'Html': '<script.+</script>', 'Replace with': ''},
    {'Html': '<ol>', 'Replace with': ''},
    {'Html': '</ol>', 'Replace with': ''},
    {'Html': '<ul>', 'Replace with': ''},
    {'Html': '</ul>', 'Replace with': ''},
    {'Html': '<p>', 'Replace with': ''}, # Special case when </p> is caught in a final script or image call.
    {'Html': '<li>', 'Replace with': ''}, # Special case 
    {'Html': '<sup>', 'Replace with': '^'}, 
    {'Html': '</sup>', 'Replace with': ''}
]
special_character_removal_array=[
    {'Replace': '\\n', 'With': ''},
    {'Replace': '\\\\:', 'With': ''},
]

def extract_equation(array):
    extract_equation_array=[]
    equation_regex='<img\sclass="equation_image".+?">'
    for sentence in array:
        if re.findall(equation_regex, sentence)!=[]:
            split_without_equation=re.split(equation_regex, sentence)
            raw_equation_array=re.findall(equation_regex, sentence)
            clean_equation_array=[]
            for raw_equation in raw_equation_array:
                # First try to extact the exact equation display
                try:
                    math_to_display=re.search('data-equation-content=".*?"', raw_equation).group()
                    cleaned_math=re.sub('data-equation-content="', '', math_to_display)
                    cleaned_math=re.sub('"', '', cleaned_math)
                    clean_equation_array.append(cleaned_math)
                # If an error occurs (such as not finding data-equation-content) substitute for a generic statement
                except:
                    clean_equation_array.append('[equation_image]')
            clean_sentence=split_without_equation.pop(0)
            while len(clean_equation_array)!=0:
                clean_sentence+=clean_equation_array.pop(0)
                clean_sentence+=split_without_equation.pop(0)
            extract_equation_array.append(clean_sentence)
        else:
            extract_equation_array.append(sentence)
    return extract_equation_array

def split_by_environment(array, env_html_sub, env_new_val, env_html_end):
    split_array=[]
    for entry in array:
        if re.findall(env_html_end, entry)!=[]:
            sentence_breaks=re.split(env_html_end, entry)
            for sentence in sentence_breaks:
                sentence=re.sub(env_html_sub, env_new_val, sentence)
                split_array.append(sentence)
        else:
            split_array.append(entry)
    return split_array

def split_sentences(old_entry):
    revised_entry=old_entry
    # Removes nan entries from splitting, returns an empty string
    if type(revised_entry) != type(''):
        return ['']
    try:
        for replacement_dict in before_breaks_replacement_array:
            revised_entry=re.sub(replacement_dict['Html'], replacement_dict['Replace with'], revised_entry)
    except:
        input(revised_entry)
    # Comb through arrays, splitting as necessary
    temp_array=extract_equation([revised_entry])
    temp_array=split_by_environment(temp_array, '<br>', '', '<br>')
    temp_array=split_by_environment(temp_array, '<a\sclass="instructure_file_link.*?>.*', '[file]', '</a>')
    temp_array=split_by_environment(temp_array, 'href=.*?>.*', '[url]', '<a')
    temp_array=split_by_environment(temp_array, '<span>', '', '</span>')
    #temp_array=split_by_environment(temp_array, '<div>', '', '</div>')
    temp_array=split_by_environment(temp_array, '<p.*?>', '', '</p>')
    temp_array=split_by_environment(temp_array, '<li>', '', '</li>')
    
    final_array=[]
    
    for entry in temp_array:
        # Skip nan entries
        if type(entry) != type(''):
            continue
        elif len(entry)>0:
            if entry[0]=='>' or entry[0]=='-':
                entry=entry[1:]
            final_entry=entry
            for replacement_dict in after_breaks_replacement_array:
                final_entry=re.sub(replacement_dict['Html'], replacement_dict['Replace with'], final_entry)
            # After cleaning, append to final array
            if type(final_entry) == type(''):
                final_entry=final_entry.strip()
            for special_character in special_character_removal_array:
                if special_character['Replace'] in final_entry:
                    final_entry=final_entry.replace(special_character['Replace'], special_character['With'])
            if len(final_entry)>0:
                final_array.append(final_entry)
    return final_array

def auto_deidentify(df):
    # Create deident lists of names from columns
    # Complete multiple passes of deident with lists
    # Return modified df

    # Set to remove duplicates, then back to list
    student_names = list(set(df['Sortable Name'].tolist()))
    student_names = [name for name in student_names if str(name) != 'nan']
    instructor_names = list(set(df['Instructor'].tolist()))
    instructor_names = [name for name in instructor_names if str(name) != 'nan']

    # Remove instructor names from student list
    for instructor in instructor_names:
        try:
            student_names.remove(instructor)
        except:
            pass
    
    split_student_names = []
    for student in student_names:
        split_list_s = student.split(',')
        for split_student in split_list_s:
            split_student_names.append(split_student.strip())
    split_student_names = list(set(split_student_names))

    split_instructor_names = []
    for instructor in instructor_names:
        split_list_i = instructor.split(',')
        for split_instructor in split_list_i:
            split_instructor_names.append(split_instructor.strip())
    split_instructor_names = list(set(split_instructor_names))

    #df['Deidentifed Discussion Data'] = df['Deidentifed Discussion Data'].fillna('')

    df['Analysis Unit'] = df['Analysis Unit'].astype('str')
    
    for split_i_name in split_instructor_names:
        df['Analysis Unit'] = df['Analysis Unit'].str.replace(split_i_name, '[instructor]')
    
    for split_s_name in split_student_names:
        df['Analysis Unit'] = df['Analysis Unit'].str.replace(split_s_name, '[name]')

    df['Analysis Unit'] = df['Analysis Unit'].str.replace('[instructor] [instructor] [instructor]', '[instructor]')
    df['Analysis Unit'] = df['Analysis Unit'].str.replace('[instructor] [instructor]', '[instructor]')

    df['Analysis Unit'] = df['Analysis Unit'].str.replace('[name] [name] [name]', '[name]')
    df['Analysis Unit'] = df['Analysis Unit'].str.replace('[name] [name]', '[name]')
    df['Analysis Unit'] = df['Analysis Unit'].str.replace('[name][name]', '[name]')

    return df

def validate_df(raw_df):
    validated_df=raw_df.copy()
    validated_df = validated_df.reset_index(drop=True)
    all_analysis_index_blank = False
    try:
        analysis_index_list = [str(x) for x in list(validated_df['Analysis Unit Index'].unique())]
        if analysis_index_list == ['nan']:
            all_analysis_index_blank = True
    except:
        all_analysis_index_blank = True
    blank_data = {}
    for key in list(validated_df.columns):
        blank_data[key] = ''
    previous_row_values=pandas.Series(data=blank_data, index=['blank'])

    if 'Parent Discussion Entry Id' in list(validated_df.columns):
        validated_df['Parent Discussion Entry Id'] = validated_df['Parent Discussion Entry Id'].fillna(0)

    for index, row in validated_df.iterrows(): 
        if index > 0:
            previous_row_values=validated_df.iloc[index-1]     
        for key in list(validated_df.columns):
            if (pandas.isnull(row[key]) or row[key]=='nan') and key=='Analysis Unit Index' and all_analysis_index_blank == False: # Researcher added a row without defining values
                if index == 0:
                    new_unit_index = 0
                else:
                    new_unit_index=previous_row_values[key]+1000
                validated_df.loc[index, key]=new_unit_index
            elif (pandas.isnull(row[key]) or row[key]=='nan') and key=='Analysis Unit' and 'Modify' in list(validated_df.columns): # Replace blank Analysis with Modify, delete Modify
                validated_df.loc[index, key]=row['Modify']
                validated_df.loc[index, 'Modify']=numpy.NaN
            elif key == 'Modify' or key in researcher_names:
                pass
            elif pandas.isnull(row[key])==True:
                validated_df.loc[index, key]=previous_row_values[key] # Copies previous row value 
    
    return validated_df

### DEFS FOR converted_df
def speaker_type_func(row):
    if row['Sortable Name'] == row['Instructor']:
        return 'Instructor'
    else:
        return 'Student'

def save_html_scrape_df_as_xlsx(encode_relations_dict, dict_file_properties, raw_df):
    # Workflow
        # Apply cleaning function to raw html row
        # Apply splitting function to raw html row, as single array of sentences
        # Rename columns with compatible column names
        # Explode single array of sentence column
        # Rename columns for main dataframe
    html_scrape_df=raw_df.copy()
    html_scrape_df = validate_df(html_scrape_df)
    if 'Analysis Unit' not in list(html_scrape_df.columns):
        html_scrape_df['Analysis Unit']=html_scrape_df['Raw Discussion Data'].apply(split_sentences)
    else:
        html_scrape_df['Analysis Unit']=html_scrape_df['Analysis Unit'].apply(split_sentences)
    html_scrape_df=html_scrape_df.explode('Analysis Unit')
    html_scrape_df['Analysis Unit']=html_scrape_df['Analysis Unit'].apply(clean_array_of_sentences, args=(encode_relations_dict['Unitized Student Names'], encode_relations_dict['Unitized Instructor Names']))
    html_scrape_df=html_scrape_df.explode('Analysis Unit')
    if 'Sortable Name' in html_scrape_df.columns:
        html_scrape_df = auto_deidentify(html_scrape_df)
    html_scrape_df['Analysis Unit Index'] = numpy.array(range(0, len(html_scrape_df)))

    converted_df = html_scrape_df.copy()

    # Conversion of columns:
        # 'Speaker Type'
            # If 'Instructor' == 'Sortable Name', Speaker Type is Instructor. otherwise Student
    if 'Speaker Type' not in list(converted_df.columns):
        converted_df['Speaker Type'] = converted_df.apply(speaker_type_func, axis=1)
        # 'Class ID'
            # Convert 'Code' entry 'MATH 111' to 'MATH'
            # Convert 'Code' entry 'PHYS 102' to 'PHYS' 
                # extract first 4 characters
    if 'Class ID' not in list(converted_df.columns):
        converted_df['Class ID'] = converted_df['Code'].apply(lambda x: x[:3])
        # 'Term' and 'Year'
            # 'Month of Start At' to 'Term' as first 4 characters
            # 'Month of Start At' to 'Year' as last 4 characters
    if 'Month of Start At' in list(converted_df.columns):
        converted_df['Term'] = converted_df['Month of Start At'].apply(lambda x: x[:3])
        converted_df['Year'] = converted_df['Month of Start At'].apply(lambda x: x[-4:])
        # 'Cohort'
            # Rename 'Section'
    if 'Cohort' not in list(converted_df.columns):
        converted_df['Cohort'] = converted_df['Section']
        # 'Module Number'
            # Eigth character of 'Title'
    if 'Module Number' not in list(converted_df.columns):
        converted_df['Module Number'] = converted_df['Title'].apply(lambda x: x[8-1])
        # 'Analysis Unit'
            # As cleaned above
        # 'Analysis Unit Index'
            # As cleaned above
        # 'Modify'
            # Blank
    if 'Modify' not in list(converted_df.columns):
        converted_df['Modify'] = ''
        # 'Researchers'
            # Blank
    for researcher_name in researcher_names:
        if researcher_name not in list(converted_df.columns):
            converted_df[researcher_name] = ''
        # 'Speaker ID' 
            # Import Deident_Key
            # Convert names in 'Sortable Names' to 'Speaker ID' using index
            # If name not found, add it to Deident_Key
            # Save new Deident_Key
    deident_df_path = f'{base_dir}{path_break}Identifiable_Data{path_break}Deident_Key.xlsx'
    deident_df = pandas.read_excel(deident_df_path)

    if 'Sortable Name' in list(html_scrape_df.columns):
        # Check that all names are included in deident_df
        for name in html_scrape_df['Sortable Name'].unique():
            try: 
                temp_var = deident_df.loc[name]
            except:
                name_list = name.split(', ')
                unique_ID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                while unique_ID in deident_df['Speaker ID'].unique():
                    unique_ID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                name_index_first_match = converted_df.index[converted_df['Sortable Name'] == name].tolist()[0]
                temp_dict = {
                    'Speaker Name': f'{name_list[1]} {name_list[0]}',
                    'Speaker ID': unique_ID,
                    'Speaker Type': converted_df.loc[name_index_first_match]['Speaker Type'], 
                    'Class ID': converted_df.loc[name_index_first_match]['Class ID'], 
                    'Term': converted_df.loc[name_index_first_match]['Term'],
                    'Year': converted_df.loc[name_index_first_match]['Year'], 
                    'Cohort': converted_df.loc[name_index_first_match]['Cohort']
                }
                temp_series = pandas.Series(temp_dict)
                deident_df.loc[name] = temp_series
        deident_df.to_excel(deident_df_path)

        converted_df['Speaker ID'] = converted_df['Sortable Name'].apply(lambda x: x.replace(x, deident_df.loc[x]['Speaker ID']))
    
    converted_df = converted_df[database_header_array]
    converted_df = converted_df.reset_index(drop=True)
    final_df = validate_df(converted_df)
    
    final_df_path=f'{base_dir}{path_break}Deidentified_xlsx_Files{path_break}{dict_file_properties["File Name"]}_deidentified.xlsx'
    if os.path.exists(final_df_path):
        os.remove(final_df_path)
    final_df.to_excel(final_df_path)