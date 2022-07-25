# CoI_Python_Database_Analysis

 Analysis of Community of Inquiry data using Python
 
Currently, there are two main python scripts to deidentify, clean, and restructure for analysis. 

## GUI_deidentification.py
The purpose of this script is to remove identifcation from students, clean files (e.g., remove excess lines from pdf -> word conversion), and put data in a csv file for later analysis. <br><br>

To use this script, you will need to: 
1. **Prepare the *Deident_Key.csv* for your data and place in the *Identifable_Data* folder.** <br>
This file has 7 columns: <br>
-**Speaker:** True name of the person who said the sentence.
-**Speaker ID:** Pseudonym of the person who said the sentence.
-**Speaker Type:** Student or Instructor. Our analysis uses different codes for types of speakers and so we needed a column to sort this information. 
-**Class ID:** Course name. We currently are analyzing different courses and use MATH and PHY to denote these differences. 
-**Term:** Semester the course is run. ERAU runs new terms every month (terms overlap with others) and so our terms are classified by month. This could be FALL, SPRING, SUMMER for traditional universities. 
-**Year:** Year the course is run. 
-**Cohort:** Also known as the section for the course. For ease of reference, we have numbered our sections within each course. 
*An example file can be found in the Identifable_Data folder.* <br>
2. **Prepare the Word documents and place in the *Word_Documents_To_Deidentify* folder.** <br> 
We use the following process to prepare our Word documents: 
-Open up the Canvas sections of the courses I want to pull transcripts from and navigate to the module discussion I want to pull.
-Click the Chrome add-in button for [Print Friendly](https://www.printfriendly.com/).
-Click “PDF” from the top menu bar, then click the green “download” button once it is done loading.
-Open the PDF from its location using Adobe. 
-In Adobe, I click “File” –> “Export To” -> “Microsoft Word” -> “Word Document”. <br>
We use the following naming convention for saving Word files: <br>
*CLASS_ID* *TERM* *YEAR* - SECTION *#* - M*#* Transcript.csv <br> 
Example: MATH111 AUG 2021 - SECTION 2 - M1 Transcript.csv<br>
**CAUTION: Sometimes there is a conversion problem. I do not know how to resolve this. But this works 95\% of the time.**<br>
3. **Open a Terminal in the folder and run *python3 GUI_deidentification.py* **


## GUI_master_files.py
The purpose of this script is to collect the deidentified csv files into a single repository/csv file. <br><br>

To use this script, you will need to: 
1. **Open a Terminal in the folder and run *python3 GUI_master_files.py* **

Follow the on-screen instructions to either: 
1. Upload all csv files to a master database. 
2. Download master database as a csv file. 
3. Delete old master database in preparation for a new one.

## Future Steps
-Analyzing data quantitatively by calling a loaded database. 