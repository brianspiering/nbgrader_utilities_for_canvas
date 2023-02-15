"""nbgrader has very specific requirements for file folder hierachary.
These functions are helpful in meeting those requirements.
"""

import collections
import datetime
import pathlib
import os
import re
import sys
import shutil

import pandas as pd

def assignment_folder(sub_path, folder_name):
    """Create the folder for each student for the assignment"""

    students_raw = pd.read_csv("students_raw.csv")
    students_raw = students_raw.drop([0])
    sis_ids = students_raw['SIS Login ID'].tolist()

    # Remove odd hash value
    sis_ids = [sis_id for sis_id in sis_ids if len(sis_id) < 40] 
    sis_ids.append('lorem')

    for sis_id in sis_ids:
        student_dir = sub_path + sis_id
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)

        # Assignment level directory  
        assignment_dir = student_dir+'/'+folder_name
        if not os.path.exists(student_dir+'/'+folder_name):
            os.makedirs(assignment_dir)

def scores_folder(score_path, folder_name):
    """Generate a new folder to store score information, ../scores/"""
    
    score_dir = score_path+folder_name
    if not os.path.exists(score_dir):
        os.makedirs(score_dir)

def place_submission(origin_folder, sub_path, folder_name, assignment_name, score_path, ddl, record_ref='sis_id.txt'):
    """Move the submissions from download folder to the right folders, 
    also make record of the ids without submission."""

    files = os.listdir(origin_folder) # read the file names from the download folder
    multiple_sub = collections.defaultdict(int) # dict for the sake of version update
    ddl_unix = (ddl - datetime.datetime(1970,1,1)).total_seconds()

    # make the file to record no submission
    with open(score_path+folder_name+'/summary.txt', 'w+') as f:
        ref_list = open(record_ref, 'r').read().split(',') # list of student id
        f.write('No submission:\n')
    
    # move the submitted file from download folder to the student's assignment folder
    # correct format - 'John John - jony2_labname.ipynb'
    for f in files:
        if f.endswith('ipynb'):
            student_file = f.split(' - ', 1)[-1]
            student = student_file.split('_',1)[0].lower()
            edition = re.search(r'\((.*?)\)',student_file) # version id
            
            if edition:
                num = int(edition.group(1))
            else:
                num = 0


            if num >= multiple_sub[student] and os.path.getmtime(origin_folder+f) <= ddl_unix:
                multiple_sub[student] = num
                new_folder = sub_path + student + '/' + folder_name + '/' + assignment_name + '.ipynb'
                try:
                    shutil.move(origin_folder+f, new_folder)
    
                    try:
                        ref_list.remove(student) # delete the student id of those submitted from list 
                    except ValueError:
                        pass
                    
                except (RuntimeError, TypeError, NameError, FileNotFoundError):
                    pass 
            else:
                continue

    # record the no submission
    with open(score_path+folder_name+'/summary.txt', 'a') as f:
        f.write('\n'.join(ref_list))
