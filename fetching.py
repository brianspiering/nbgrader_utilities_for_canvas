import pandas as pd
from nbgrader.api import Gradebook, MissingEntry
import math
import requests
import shutil
import os
import statistics
import matplotlib.pyplot as plt


def put_file(sub_pat, folder_name, empty_sample_add):

    """
    Make sure every folder has a file. If no submission, copy an empty submission.
    """
    
    folders = os.listdir(sub_pat)

    for folder in folders:
        if not folder.startswith('.'): # ignore the .DS_store file
            if len(os.listdir(sub_pat+folder+'/'+folder_name) ) == 0: # find the empty folder
                n_path = sub_pat+folder+'/'+folder_name + '/' + folder_name + '.ipynb' 
                shutil.copy2(empty_sample_add, n_path)


def new_files(path, folder_name, run):
    """
    Delete previous submitted/graded versions
    """
    if run == 'yes': # identify to delete or not

        if os.path.exists(path): # if path doesn't exist, no need to delete
        # path = '../autograded/'
            folders = os.listdir(path)

            # delete the previous graded information
            for folder in folders:

                try:
                    shutil.rmtree(path+folder+'/'+folder_name)
                except (FileNotFoundError, NotADirectoryError):
                    pass
            





def fetch_score(database_url, selected_assignment, grades_file, student_id, id_col):
    """
    Pull score from db and save into a csv
    """

    with Gradebook(database_url) as gb:
        
        grades = []
        
        for assignment in gb.assignments:
            # only pull scores of the selected assignment
            if assignment.name == selected_assignment:

                for student in gb.students:
                    score ={}
                    score['max_score'] = assignment.max_score
                    score['student'] = student.id
                    score['assignment'] = assignment.name
                    
                    try:
                        submission = gb.find_submission(assignment.name, student.id)
                    except MissingEntry: 
                        score['score'] = 0.0
                    else:
                        score['score'] = submission.score

                    grades.append(score)

    # Create a pandas dataframe with our score information, and save it to disk
    grades = pd.DataFrame(grades)
    
    # merge the score information with sis_id from df of student_id
    grades_info = pd.merge(grades, student_id, left_on='student', right_on=id_col, how='left')
    
    # save the grades
    grades_info.to_csv(grades_file)
    

class GradeUpdate(object):
    def __init__(self, course_id, assignment_id, key):
        url_string = ('https://lorem.instructure.com/api/v1/courses/{}/assignments/{}/submissions/')
        self.url = url_string.format(course_id, assignment_id)
        self.hd = {'Authorization': 'Bearer ' + key}
    
    def indv_grade_update(self, student_id, grade):
        """
        Update the score for a student
        """
        
        update_url = self.url + student_id
        
        data = {'submission[posted_grade]':grade}
        
        requests.put(update_url, headers = self.hd, data = data)
        
        print ('successfully update grade of user %s ..' % student_id)
    
    def group_grade_update(self, grades_file_address):
        """
        Update the scores of a group of student from grades information (csv file)
        """
        
        grades_df = pd.read_csv(grades_file_address)[['ID', 'score']]
        
        for i in range(len(grades_df)):
            
            id_score_pair = grades_df.iloc[i]
            
            if all(pd.notna(id_score_pair)): # ignore the students without id or score
                stud_id, score = str(int(id_score_pair[0])), id_score_pair[1]
                self.indv_grade_update(stud_id, score)
            else:
                print ('-- No student id for No. %d student' % (i+1))
          
                 


def summary(grades_file, score_path, folder_name):
    """
    Print out the summary of scores, details save in ../scores/ folder
    """
    
    # generate histogram
    score_df = pd.read_csv(grades_file)
    score_df['score'].hist()
    plt.title('Histogram for %s' % folder_name)
    plt.savefig(score_path+folder_name+'/hist.png')

    # print score stat in summary.txt
    with open(score_path+folder_name+'/summary.txt', "a") as f:
    
        f.write('\n')
        f.write('---score summary---\n')
        f.write('min    : ' +  str(min(score_df['score']))+'\n' )
        f.write('max    : '+ str(max(score_df['score']))+'\n')
        f.write('median : '+ str(statistics.median(score_df['score']))+'\n')
        f.write('std    : '+str(round(statistics.stdev(score_df['score']),2)))
        f.close()