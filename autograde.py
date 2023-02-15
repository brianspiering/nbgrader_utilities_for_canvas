"""
Move student submissions around

# Examply
python score_students.py ../submitted/ ../scores/ <assign_name> <dropbox_name> <assign_id> <month> <day> <assignment_name>
"""

import os
import shutil
import subprocess
import statistics

import matplotlib.pyplot as plt
import pandas as pd

from fetching import *
from make_folders import *


def main():

    #############################################
    #Place the submissions into the right folder#
    #############################################

    sub_path = sys.argv[1] # example: ../submitted/
    score_path = sys.argv[2] # example: ../scores/
    #run = sys.argv[3] # example: True
    folder_name = sys.argv[3] # example: knn_lab
    dropbox_file_name = sys.argv[4] # example: Lab-KNN
    assignment_id = sys.argv[5] # example: 6805538
    ddl_mon = int(sys.argv[6]) # example: 11
    ddl_day = int(sys.argv[7]) # example: 4
    assignment_name = sys.argv[8] # assignment_name


    download_dir = '/Users/lorem/Downloads/' # the folder where submission.zip was downloaded to.
    
    unzip = 'unzip -d ' + download_dir + dropbox_file_name + ' ' + download_dir + dropbox_file_name + '.zip'

    os.system(unzip)

    origin_folder = download_dir + dropbox_file_name + '/'

    # convert the downloaded file modification time to UTC
    ddl = datetime.datetime(2018,ddl_mon,ddl_day,14) + datetime.timedelta(days=1)

    # create assignment folder for each student
    assignment_folder(sub_path, folder_name) 

    # create score folder to store grades info
    scores_folder(score_path, folder_name)  

    # move submissions to the assignment folder
    place_submission(origin_folder, sub_path, folder_name, assignment_name, score_path, ddl) 

    # delete the unzip folder
    shutil.rmtree(origin_folder)

    print ('Place Submission Done .. ')


    ###########
    #autograde#
    ###########

    assignment_dir = '../'  #the address where db locates in, e.g.: "/Users/shen/Desktop/USF/assignments"
    empty_sample_add = '../submitted/bspiering/knn_lab/knn_lab.ipynb' #an empty submission
    autograded_path = '../autograded/'

    # make sure every folder has a file
    put_file(sub_path, folder_name, empty_sample_add)

    run_new_file = input('New Grading [yes/no]:')

    if run_new_file == 'True':
        print ('New grading .. ')
    # if had been graded, delete previous grading info for new grading

    
    new_files(autograded_path, folder_name, run_new_file)

    # change the working directory into the address where db locates for autograding
    os.chdir(assignment_dir) 
 
    # call 'nbgrader autograde <assignment_name>'
    subprocess.call(["nbgrader", "autograde", folder_name])

    print ('%s Grade Done .. '% folder_name)


    ##########################
    #summary and upload score#
    ##########################

    # change the working directory back to utilities/
    # os.chdir(assignment_dir+'utilities')
    os.chdir('utilities')

    file_name = 'grades.csv' # grades info file name
    db_url = 'sqlite:///../gradebook.db' # db address
    course_id = 1580035 # could be found on canvas url
    token = 'lorem' 
    grades_file = score_path + folder_name +'/' + file_name # grades info file address

    # fetch the student info dataframe
    student_id = pd.read_csv('students_raw.csv').drop([0])
    student_id = student_id[['ID', 'SIS User ID', 'SIS Login ID']]
    id_col = 'SIS Login ID'

    # pull score from db
    fetch_score(db_url, folder_name, grades_file, student_id, id_col) 

    # generate score summary
    summary(grades_file, score_path, folder_name)

    # call canvas api to update score
    update = input('Updating Score [yes/no]:')
    if update == 'yes':
        updating = GradeUpdate(course_id, assignment_id, token)
        updating.group_grade_update(grades_file)
    print ('Upload Done .. ')

if __name__ == '__main__':
    main()
