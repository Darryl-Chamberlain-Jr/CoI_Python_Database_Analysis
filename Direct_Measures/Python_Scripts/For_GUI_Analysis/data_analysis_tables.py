import sys
import pandas
import numpy
import itertools
from progress.bar import ChargingBar
import os, shutil
import re
# Data Analysis

# Table: Student Presence Code Count
## Columns: M1, M2, M3, M4, M5, M6, M7, M8, M9, TOTAL
## Dicts: 
    # SOCIAL
        # Affective: EM, PL, H, SDI
        # Interactive: AK, IE, I, NE, EAG, EAP
        # Cohesive: GR, GS, V, SS
    # COGNITIVE
        # Triggering Event: P, CL
        # Exploration: A, IS, DV, LC, PN, OP
        # Integration: BO, CS, JH, SD, SA
        # Resolution: WU, TE, ATD
### Calculated by: 
    # Counting the number of times a code appears in a specific module for a specific classID/year/term/section. 
    # Use loops to create table for an entire classID/year/term

# Table: Student Presence Word Counts
## Columns: M1, M2, M3, M4, M5, M6, M7, M8, M9, TOTAL
## Dicts: 
    # SOCIAL
        # Affective: EM, PL, H, SDI
        # Interactive: AK, IE, I, NE, EAG, EAP
        # Cohesive: GR, GS, V, SS
    # COGNITIVE
        # Triggering Event: P, CL
        # Exploration: A, IS, DV, LC, PN, OP
        # Integration: BO, CS, JH, SD, SA
        # Resolution: WU, TE, ATD
### Calculated by: 
    # Summing the number of words each time a code appears in a specific module for a specific classID/year/term/section. 
    # Use loops to create table for an entire classID/year/term

# Table: Presence Density  
## Columns: M1, M2, M3, M4, M5, M6, M7, M8, M9, TOTAL
## Dicts: 
    # SOCIAL
        # Affective: EM, PL, H, SDI
        # Interactive: AK, IE, I, NE, EAG, EAP
        # Cohesive: GR, GS, V, SS
    # COGNITIVE
        # Triggering Event: P, CL
        # Exploration: A, IS, DV, LC, PN, OP
        # Integration: BO, CS, JH, SD, SA
        # Resolution: WU, TE, ATD
### Calculated by: 
    # 1000 times (student presence code count / total number of words for that module)
    # Sum all densities within each family.

# Table: Inter-rater Reliability expanded
# Columns (coder 1): EM, PL, H, SDI, AK, IE, I, NE, EAG, EAP, GR, GS, V, SS, P, CL, A, IS, DV, LC, PN, OP, BO, CS, JH, SD, SA, WU, TE, ATD
# Rows (coder 2): EM, PL, H, SDI, AK, IE, I, NE, EAG, EAP, GR, GS, V, SS, P, CL, A, IS, DV, LC, PN, OP, BO, CS, JH, SD, SA, WU, TE, ATD
### Calculated by: 
    # Counting the number of times coder 1 coded column AND coder 2 coded row.

# Table: Inter-rater Reliability condensed
# Columns (coder 1): AR, IR, CR, TE, E, I, R
# Rows (coder 2): AR, IR, CR, TE, E, I, R


### STATICS
# Student & Instructor Social Presences
Affective_Response_codes=["EM", "PL", "H", "SDI"]
Interactive_Response_codes=["AK", "IE", "I", "NE", "EAG", "EAP"]
Cohesive_Response_codes=["GR", "GS", "V", "SS"]
social_presence_codes=Affective_Response_codes+Interactive_Response_codes+Cohesive_Response_codes
# Student Cognitive Presenses
Triggering_Event_codes=["P", "CL"]
Exploration_codes=["A", "IS", "DV", "LC", "PN", "OP"]
Integration_codes=["BO", "CS", "JH", "SD", "SA"]
Resolution_codes=["WU", "TE", "ATD"]
cognitive_presence_codes=Triggering_Event_codes+Exploration_codes+Integration_codes+Resolution_codes
# Instructor Teaching Presences
Facilitating_Discourse_codes=["CNS", "ENC", "LE"]
Instructional_Design_codes=["ES", "EN", "ML"]
Direct_Instruction_codes=["Q", "ANS", "F", "TH", "BR", "RS", "M", "FB"]
teaching_presence_codes=Facilitating_Discourse_codes+Instructional_Design_codes+Direct_Instruction_codes
# All codes
all_code_list=social_presence_codes+cognitive_presence_codes+teaching_presence_codes
# Codes by category
social_cat=["Affective", "Interactive", "Cohesive"]
cognitive_cat=["Triggering", "Exploration", "Integration", "Resolution"]
teaching_cat=["Facilitating", "Design_of_Instruct", "Instruction"]
cat_code_list=social_cat+cognitive_cat+teaching_cat

headers_without_modify=['Speaker ID', 'Speaker Type', 'Class ID', 'Term', 'Year', 'Cohort', 'Module Number', 'Analysis Unit', 'Analysis Unit Index']
static_headers=headers_without_modify+['Modify']
researcher_names=['Emily', 'Syaza', 'Abigail', 'Patrick', 'Amina', 'Qaisara', 'Andrea', 'Emma', 'Elizabeth'] # Update when adding researchers
database_header_array=static_headers+researcher_names

headers_to_str_dict={}
for key in headers_without_modify:
    headers_to_str_dict[key]='str'

### END STATICS

### DEFINITIONS for all tasks 
def define_mask(df, key, user_inputs):
    all_true_mask=numpy.repeat(True, len(df.index))
    if user_inputs[key]=='All':
        mask=all_true_mask
    elif user_inputs[key]=='Include Research Codes':
        pass # We don't want a mask for this statement
    else:
        mask=df[key]==user_inputs[key]
    return mask

def define_partial_dataframe(main_df, user_inputs):
    main_df=main_df.astype(headers_to_str_dict) # Convert all entries to strings

    speaker_mask=define_mask(main_df, 'Speaker Type', user_inputs)
    class_mask=define_mask(main_df, 'Class ID', user_inputs)
    term_mask=define_mask(main_df, 'Term', user_inputs)
    year_mask=define_mask(main_df, 'Year', user_inputs)
    cohort_mask=define_mask(main_df, 'Cohort', user_inputs)
    module_number_mask=define_mask(main_df, 'Module Number', user_inputs)
    final_partial_mask=speaker_mask & class_mask & term_mask & year_mask & cohort_mask & module_number_mask

    partial_df=main_df[final_partial_mask]
    return partial_df

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
    
def save_all_dfs_as_tables(file_name, overview_table, array_of_detailed_tables):
    writer = pandas.ExcelWriter(file_name, engine='xlsxwriter')
    # Write each dataframe to a different worksheet.
    overview_table.to_excel(writer, sheet_name='overview')
    for dict in array_of_detailed_tables:
        df_for_sheet=dict['Dataframe']
        df_for_sheet.to_excel(writer, sheet_name=dict['Sheet Name'])
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()


### DEFINITIONS for Task 1 - Create Progress Report
def progress_report(df):
    total_sentences=len(df)
    mask=~df.isnull()
    tf_mask=mask[researcher_names]
    sum_of_true_by_row=tf_mask.sum(axis=1)
    try:
        not_coded=sum_of_true_by_row.value_counts()[0]
    except:
        not_coded=0
    try:
        one_coded=sum_of_true_by_row.value_counts()[1]
    except:
        one_coded=0
    fully_coded=total_sentences-not_coded-one_coded
    try:
        progress_percent=round(float(100*(2*fully_coded+one_coded)/(2*total_sentences)), 1)
    except:
        progress_percent=0
    return [total_sentences, not_coded, one_coded, fully_coded, progress_percent]

def progress_report_statement(progress_report_values):
    total_sentences, not_coded, one_coded, fully_coded, progress_percent=progress_report_values
    string=f'Of {total_sentences} rows, {not_coded} have not been coded, {one_coded} have been coded by one researcher, and {fully_coded} have been coded by at least two researchers. Progress at {progress_percent}%.'
    return string

def term_table_by_cohort_and_module(partial_df, base_keys):
    # Counts by row for each module, then a total row
    speaker_type, class_id, term, year, list_of_cohorts = base_keys
    array_of_dicts=[]
    summary_dict={
        'Speaker Type': speaker_type, 
        'Class ID': class_id,
        'Term': term, 
        'Year': year,
        'Cohort': 'All',
        'Module Number': 'All'
    }
    for researcher in researcher_names:
        summary_dict[researcher]=0
        
    for cohort in list_of_cohorts:
        cohort_mask=partial_df['Cohort']==cohort
        cohort_df=partial_df[cohort_mask].copy()
        for module_number in range(1, 10):
            row_mask=cohort_df['Module Number']==str(module_number)
            module_df=cohort_df[row_mask]
            temp_dict={
                'Speaker Type': speaker_type, 
                'Class ID': class_id,
                'Term': term, 
                'Year': year,
                'Cohort': cohort,
                'Module Number': module_number
            }
            for researcher in researcher_names:
                temp_dict[researcher]=module_df[researcher].count()
                # Create statistics for each row from progress report
                total_sentences, not_coded, one_coded, fully_coded, progress_percent=progress_report(module_df)
                temp_dict['Total Lines']=total_sentences
                temp_dict['Not Coded']=not_coded
                temp_dict['One Coded']=one_coded
                temp_dict['Fully Coded']=fully_coded
                temp_dict['Progress %']=progress_percent
                # Running count for summary dict
                #summary_dict[researcher]+=module_df[researcher].count()
            array_of_dicts.append(temp_dict)
    
    term_df=pandas.DataFrame.from_dict(array_of_dicts)
    # Define summary row column values
    for researcher in researcher_names:
        summary_dict[researcher]=term_df[researcher].sum()
    for statistic in ['Total Lines', 'Not Coded', 'One Coded', 'Fully Coded']:
        summary_dict[statistic]=term_df[statistic].sum()
    if summary_dict['Total Lines'] == 0:
        summary_dict['Progress %'] = 0
    else:
        summary_dict['Progress %']=round(100*(2*summary_dict['Fully Coded']+summary_dict['One Coded'])/(2*summary_dict['Total Lines']), 1)    
    # Add summary row at end of table
    summary_row=pandas.DataFrame([summary_dict])
    final_df=pandas.concat([term_df, summary_row], ignore_index=True)
    return final_df
    
def term_table_overview(df):
    # Counts by row for each term with a progress column
    # rows:
    AUG21_MATH_row={
        'Class ID': 'MATH',
        'Term': 'AUG', 
        'Year': '2021',
        'Cohort Set': list(range(1, 8))
    }
    AUG21_PHY_row={
        'Class ID': 'PHY',
        'Term': 'AUG', 
        'Year': '2021',
        'Cohort Set': list(range(1, 6))
    }
    AUG22_MATH_row={
        'Class ID': 'MATH',
        'Term': 'AUG', 
        'Year': '2022',
        'Cohort Set': list(range(1, 6))
    }
    AUG22_PHY_row={
        'Class ID': 'PHY',
        'Term': 'AUG', 
        'Year': '2022',
        'Cohort Set': list(range(1, 6))
    }
    SEP21_MATH_row={
        'Class ID': 'MATH',
        'Term': 'SEP', 
        'Year': '2021',
        'Cohort Set': list(range(1, 6))
    }
    SEP21_PHY_row={
        'Class ID': 'PHY',
        'Term': 'SEP', 
        'Year': '2021',
        'Cohort Set': list(range(1, 5))
    }
    summary_df=pandas.DataFrame()
    array_of_detailed_dfs=[]
    
    list_of_row_dicts=[AUG21_MATH_row, AUG21_PHY_row, AUG22_MATH_row, AUG22_PHY_row, SEP21_MATH_row, SEP21_PHY_row]
    bar=ChargingBar('Summary row calc: ', max=len(list_of_row_dicts))
    for row_dict in list_of_row_dicts:
        # Finish off row_dict so it can be used as user_inputs
        row_dict['Cohort']='All'
        row_dict['Module Number']='All'
        row_dict['Include Researcher Codes']='Yes'
        for speaker_type in ['Student', 'Instructor']:
            row_dict['Speaker Type']=speaker_type
            # Get partial database
            partial_df=define_partial_dataframe(df, row_dict) 
            # Get related detailed table
            base_keys=[speaker_type, 
                       row_dict['Class ID'], 
                       row_dict['Term'], 
                       row_dict['Year'], 
                       [str(i) for i in row_dict['Cohort Set']]
            ]
            IRR_table_full=organize_progress_report_df(term_table_by_cohort_and_module(partial_df, base_keys))
            # Save detailed table for sheet
            sheet_name=f"{row_dict['Term']}{row_dict['Year']}_{row_dict['Class ID']}_{speaker_type}"
            array_of_detailed_dfs.append({'Sheet Name': sheet_name, 'Dataframe': IRR_table_full})
            # Extract summary line
            summary_row=IRR_table_full.iloc[-1:].copy()
            # Add progress_report values
            total_sentences, not_coded, one_coded, fully_coded, progress_percent=progress_report(partial_df)
            # Modify last row of IRR_table_full, depreciated
            #IRR_table_full.loc[-1, 'Total Lines']=total_sentences
            #IRR_table_full.loc[-1, 'Not Coded']=not_coded
            #IRR_table_full.loc[-1, 'One Coded']=one_coded
            #IRR_table_full.loc[-1, 'Fully Coded']=fully_coded
            #IRR_table_full.loc[-1, 'Progress %']=progress_percent
            summary_row['Total Lines']=total_sentences
            summary_row['Not Coded']=not_coded
            summary_row['One Coded']=one_coded
            summary_row['Fully Coded']=fully_coded
            summary_row['Progress %']=progress_percent
            summary_df=pandas.concat([summary_df, summary_row], ignore_index=True)
        bar.next()
    bar.finish()
    sum_these_cols=researcher_names+['Total Lines', 'Not Coded', 'One Coded', 'Fully Coded']
    col_sum_df=summary_df.sum(numeric_only=True).to_frame().T # Convert sum by col series to dataframe
#    col_sum_df['Progress %']=round(float(100*(2*col_sum_df['Fully Coded']+col_sum_df['One Coded'])/(2*col_sum_df['Total Lines'])), 1)
    col_sum_df['Progress %']=round(100*(2*col_sum_df['Fully Coded']+col_sum_df['One Coded'])/(2*col_sum_df['Total Lines']), 1)
    summary_df=organize_progress_report_df(pandas.concat([summary_df, col_sum_df], ignore_index=True))
    for col_name in sum_these_cols:
        summary_df=summary_df.astype({col_name: 'int'})
    return [summary_df, array_of_detailed_dfs]

def organize_progress_report_df(df):
    base_headers=['Speaker Type', 'Class ID', 'Term', 'Year', 'Cohort', 'Module Number']
    stat_headers=['Total Lines', 'Not Coded', 'One Coded', 'Fully Coded', 'Progress %']
    organized_headers=base_headers+researcher_names+stat_headers
    organized_df=df[organized_headers]
    return organized_df

### DEFINITIONS for Task 2 - IRR Report
def convert_to_category(code):
    # Student & Instructor Social Presences
    if code in Affective_Response_codes:
        cat_code="Affective"
    elif code in Interactive_Response_codes:
        cat_code="Interactive"
    elif code in Cohesive_Response_codes:
        cat_code="Cohesive"
    # Student Cognitive Presenses
    elif code in Triggering_Event_codes:
        cat_code="Triggering"
    elif code in Exploration_codes:
        cat_code="Exploration"
    elif code in Integration_codes:
        cat_code="Integration"
    elif code in Resolution_codes:
        cat_code="Resolution"
    # Instructor Teaching Presences
    elif code in Facilitating_Discourse_codes:
        cat_code="Facilitating"
    elif code in Instructional_Design_codes:
        cat_code="Design_of_Instruct"
    elif code in Direct_Instruction_codes:
        cat_code="Instruction"
    else:
        cat_code=code # Used for INDEX 
        #raise Exception("Unexpected code when trying to convert to category of code.")
    return cat_code

def IRR_table_full(df, coder_1, coder_2):
    array_of_IRR_dicts=[]
    for row_code in all_code_list:
        temp_dict={
            "INDEX": row_code
        }
        for column_code in all_code_list:
            combo_mask=(df[coder_1]==row_code) & (df[coder_2]==column_code)
            cell_count=len(df[combo_mask])
            temp_dict[column_code]=cell_count
        array_of_IRR_dicts.append(temp_dict)
    IRR_df=pandas.DataFrame.from_dict(array_of_IRR_dicts)
    IRR_df['Row Sum']=IRR_df.sum(axis=1, numeric_only=True) # Sum by row
    col_sum_df=IRR_df.sum(numeric_only=True).to_frame().T # Convert sum by col series to dataframe
    col_sum_df['INDEX']='Col Sum' # Define 'INDEX' key
    final_IRR_df=pandas.merge(IRR_df, col_sum_df, how='outer') 
    return final_IRR_df

def IRR_table_cat(df, coder_1, coder_2):
    cat_df=pandas.DataFrame()
    for name in researcher_names:
        cat_df[name]=df[name].apply(convert_to_category)
    array_of_IRR_dicts=[]
    for row_code in cat_code_list:
        temp_dict={
            "INDEX": row_code
        }
        for column_code in cat_code_list:
            combo_mask=(cat_df[coder_1]==row_code) & (cat_df[coder_2]==column_code)
            cell_count=len(cat_df[combo_mask])
            temp_dict[column_code]=cell_count
        array_of_IRR_dicts.append(temp_dict)
    IRR_df=pandas.DataFrame.from_dict(array_of_IRR_dicts)
    IRR_df['Row Sum']=IRR_df.sum(axis=1, numeric_only=True) # Sum by row
    col_sum_df=IRR_df.sum(numeric_only=True).to_frame().T # Convert sum by col series to dataframe
    col_sum_df['INDEX']='Col Sum' # Define 'INDEX' key
    final_IRR_df=pandas.merge(IRR_df, col_sum_df, how='outer') 
    return final_IRR_df

def calculate_kappa(IRR_table, keys):
    total_c1_dict={} 
    total_c1_intermediate=IRR_table['Row Sum'].T # Total coder_1 is transpose of last column
    for index in range(0, len(keys)): # Load intermediate with label
        key=keys[index]
        total_c1_dict[key]=total_c1_intermediate[index]
    total_c1=pandas.Series(total_c1_dict)
    
    total_c2=IRR_table.loc[IRR_table['INDEX']=='Col Sum'] # Total coder_2 is last row
    full_total=total_c1.sum()
    
    agreement_series=pandas.Series({}, index=[0], dtype=float)
    by_chance_series=pandas.Series({}, index=[0], dtype=float)
    
    for key in keys:
        agreement_row=IRR_table.loc[IRR_table['INDEX']==key]
        agreement_series=pandas.concat([agreement_series, agreement_row[key]])
        by_chance_series=pandas.concat([by_chance_series, pandas.Series(total_c1[key]*total_c2[key]/full_total, index=[0], dtype=float)])
    
    total_agreement=float(agreement_series.sum())
    total_by_chance=float(by_chance_series.sum())
    
    kappa_num=float(total_agreement - total_by_chance)
    kappa_denom=float(full_total - total_by_chance)
    if kappa_denom==0:
        kappa=numpy.NaN
    else:
        kappa=round(float(kappa_num/kappa_denom), 3)
    
    return [full_total, kappa]

def IRR_table(main_df):
    array_of_researcher_combos=list(itertools.combinations(researcher_names, 2)) # All unique combos of researchers
    array_of_IRR_dicts=[]
    IRR_full_breakdown_df_array=[]
    IRR_cat_breakdown_df_array=[]
    bar=ChargingBar('Coder pairs: ', max=len(array_of_researcher_combos))
    for pair_of_coders in array_of_researcher_combos:
        coder_1=pair_of_coders[0]
        coder_2=pair_of_coders[1]
        IRR_full_df=IRR_table_full(main_df, coder_1, coder_2)
        IRR_cat_df=IRR_table_cat(main_df, coder_1, coder_2)
        number_of_codes, full_IRR_kappa=calculate_kappa(IRR_full_df, all_code_list)
        number_of_codes, cat_IRR_kappa=calculate_kappa(IRR_cat_df, cat_code_list)
        temp_dict={
            'Coder_1': coder_1,
            'Coder_2': coder_2,
            '# of Codes': number_of_codes,
            'Full_IRR': full_IRR_kappa, 
            'Cat_IRR': cat_IRR_kappa
        }
        array_of_IRR_dicts.append(temp_dict)
        # Save detailed IRR_table_full and IRR_table_cat
        IRR_full_sheet_name=f'full_{coder_1}_{coder_2}'
        IRR_cat_sheet_name=f'cat_{coder_1}_{coder_2}'
        IRR_full_breakdown_df_array.append({'Sheet Name': IRR_full_sheet_name, 'Dataframe': IRR_full_df})
        IRR_cat_breakdown_df_array.append({'Sheet Name': IRR_cat_sheet_name, 'Dataframe': IRR_cat_df})
        bar.next()
    bar.finish()
    IRR_by_pair_df=pandas.DataFrame.from_dict(array_of_IRR_dicts)
    return [IRR_by_pair_df, IRR_full_breakdown_df_array, IRR_cat_breakdown_df_array]

### DEFINITIONS for Task 3 - Density Report
def extract_first_code(code_string):
    all_codes = code_string.split(',')
    return all_codes[0]

def extract_second_code(code_string):
    all_codes = code_string.split(',')
    if len(all_codes) == 1:
        return all_codes[0]
    else:
        return all_codes[1]
    
def define_sentence_length(list_of_substrings):
    if type(list_of_substrings) != type([]): # Returns 0 for nan values, which str.split() returns for empty cells
        return 0
    else:
        return len(list_of_substrings)

def calculate_full_density_df(partial_df, partial_df_label):
    raw_df = partial_df.copy()
    raw_df['Word Count'] = raw_df['Analysis Unit'].str.split().map(define_sentence_length) 
    raw_df['All Codes'] = raw_df[researcher_names].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)
    coded_df = raw_df[raw_df['All Codes'] != ''].copy()

    #coded_df.loc[:, 'first_code_full'] = coded_df['All Codes'].map(extract_first_code)
    #coded_df.loc[:, 'second_code_full'] = coded_df['All Codes'].map(extract_second_code)
    coded_df['first_code_full'] = coded_df['All Codes'].apply(extract_first_code)
    coded_df['second_code_full'] = coded_df['All Codes'].apply(extract_second_code)
    analysis_df = coded_df[['first_code_full', 'second_code_full', 'Word Count']].copy()

    # MAKE A DF 
        # Index labeled as code
        # Cols as 
            # f'{partial_df_label} Text Units'
            # f'{partial_df_label} Word Count'
            # f'{partial_df_label} PD'

    list_of_partial_dfs = []

    for code in all_code_list:
        density_dict = {}
        # Count total number of codes in first column, if error count is 0
        try:
            first_code_count = analysis_df['first_code_full'].value_counts()[code]
        except:
            first_code_count = 0
        
        # Count total number of codes in second column, if error count is 0
        try:
            second_code_count = analysis_df['second_code_full'].value_counts()[code]
        except:
            second_code_count = 0
        
        # Count the number of times the two column codes match
        try: 
            coded_same_mask = analysis_df['first_code_full' == code] & analysis_df['first_code_full' == code]
            overcounting_code = len(analysis_df[coded_same_mask])
        except: 
            overcounting_code = 0

        total_count = first_code_count + second_code_count - overcounting_code

        if analysis_df['Word Count'].sum() == 0:
            density = 0
        else:
            density = round(1000 * total_count/analysis_df['Word Count'].sum(), 2)

        density_dict[f'M{partial_df_label} Text Units'] = total_count

        # Reduce df to instances where either first_code_full or second_code_full are code, then sum
        partial_word_count_mask = (analysis_df['first_code_full'] == code) | (analysis_df['second_code_full'] == code)
        partial_word_count_df = analysis_df[partial_word_count_mask].copy()
        density_dict[f'M{partial_df_label} Word Count'] = partial_word_count_df['Word Count'].sum()
        
        density_dict[f'M{partial_df_label} Density'] = density
        density_df = pandas.DataFrame(density_dict, index=[code])

        list_of_partial_dfs.append(density_df)
    
    full_df = pandas.concat(list_of_partial_dfs)
    
    return full_df

def compile_density_df(main_df, full_or_cat):
    copied_df = main_df.copy()
    list_of_dfs = []

    for module_number in range(1, 10):
        partial_df = copied_df[copied_df['Module Number']==module_number].copy()
        if full_or_cat == 'full':
            partial_density_df = calculate_full_density_df(partial_df, module_number)
        else:
            partial_density_df = calculate_category_density_df(partial_df, module_number)
        list_of_dfs.append(partial_density_df)
    
    if full_or_cat == 'full':
        total_density_df = calculate_full_density_df(copied_df, 'Total')
    else:
        total_density_df = calculate_category_density_df(copied_df, 'Total')
    list_of_dfs.append(total_density_df)

    return pandas.concat(list_of_dfs, axis=1)

def calculate_category_density_df(partial_df, partial_df_label):
    raw_df = partial_df.copy()
    raw_df['Word Count'] = raw_df['Analysis Unit'].str.split().map(define_sentence_length)
    raw_df['All Codes'] = raw_df[researcher_names].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)
    coded_df = raw_df[raw_df['All Codes'] != ''].copy()

    coded_df['first_code_cat'] = coded_df['All Codes'].apply(extract_first_code)
    coded_df['first_code_cat'] = coded_df['first_code_cat'].apply(convert_to_category)

    coded_df['second_code_cat'] = coded_df['All Codes'].apply(extract_second_code)
    coded_df['second_code_cat'] = coded_df['second_code_cat'].apply(convert_to_category)

    analysis_df = coded_df[['first_code_cat', 'second_code_cat', 'Word Count']].copy()

    list_of_partial_dfs = []

    for code in cat_code_list:
        density_dict = {}
        # Count total number of codes in first column, if error count is 0
        try:
            first_code_count = analysis_df['first_code_cat'].value_counts()[code]
        except:
            first_code_count = 0
        
        # Count total number of codes in second column, if error count is 0
        try:
            second_code_count = analysis_df['second_code_cat'].value_counts()[code]
        except:
            second_code_count = 0
        
        # Count the number of times the two column codes match
        try: 
            coded_same_mask = analysis_df['first_code_cat' == code] & analysis_df['first_code_cat' == code]
            overcounting_code = len(analysis_df[coded_same_mask])
        except: 
            overcounting_code = 0

        total_count = first_code_count + second_code_count - overcounting_code

        if analysis_df['Word Count'].sum() == 0:
            density = 0
        else:
            density = round(1000 * total_count/analysis_df['Word Count'].sum(), 2)

        # Reduce df to instances where either first_code_cat or second_code_cat are code, then sum
        partial_word_count_mask = (analysis_df['first_code_cat'] == code) | (analysis_df['second_code_cat'] == code)
        partial_word_count_df = analysis_df[partial_word_count_mask]
        density_dict[f'M{partial_df_label} Word Count'] = partial_word_count_df['Word Count'].sum()
        
        density_dict[f'M{partial_df_label} Density'] = density
        density_df = pandas.DataFrame(density_dict, index=[code])

        list_of_partial_dfs.append(density_df)
    
    full_df = pandas.concat(list_of_partial_dfs)
    
    return full_df

def density_comparison_table(file_name, index_names):
    # Creates a 'Total' comparison, where each sheet is a row
    df = pandas.ExcelFile(file_name)
    list_of_sheet_names = df.sheet_names
    list_of_rows = []
    list_of_col_names = []
    for sheet_name in list_of_sheet_names:
        temp_df = df.parse(sheet_name)
        temp_col_name = re.sub('student_', '', sheet_name)
        list_of_col_names.append(temp_col_name)
        temp_series = temp_df['MTotal Density']
        list_of_rows.append(temp_series)
    comparison_df = pandas.DataFrame(list_of_rows).T
    comparison_df['index'] = index_names
    comparison_df.set_index('index', inplace=True)
    comparison_df = comparison_df.set_axis(list_of_col_names, axis=1)
    with pandas.ExcelWriter(file_name, engine='openpyxl', mode='a') as writer:
        comparison_df.to_excel(writer, sheet_name='total_comparisons')
    