
import math
import os
import requests
import shutil
import statistics

import matplotlib.pyplot as plt
import pandas as pd
from   nbgrader.api import Gradebook, MissingEntry


class GradeUpdate():
    def __init__(self, course_id, assignment_id, key):
        
        url_string = ('https://lorem.instructure.com/api/v1/courses/{}/assignments/{}/submissions/')
        self.url = url_string.format(course_id, assignment_id)
        self.hd = {'Authorization': 'Bearer ' + key}
    
    def indv_grade_update(self, student_id, grade):
        """Update the score for a student"""
        
        update_url = self.url + student_id
        
        data = {'submission[posted_grade]':grade}
        
        requests.put(update_url, headers = self.hd, data = data)
        
        print ('successfully update grade of user %s ..' % student_id)
    
    def group_grade_update(self, grades_file_address):
        """Update the scores of a group of student from grades information (csv file)"""
        
        grades_df = pd.read_csv(grades_file_address)[['ID', 'score']]
        
        for i in range(len(grades_df)):
            
            id_score_pair = grades_df.iloc[i]
            
            if all(pd.notna(id_score_pair)): # ignore the students without id or score
                stud_id, score = str(int(id_score_pair[0])), id_score_pair[1]
                self.indv_grade_update(stud_id, score)
            else:
                print ('-- No student id for No. %d student' % (i+1))

def fetch_score(database_url, selected_assignment, grades_file, student_id, id_col):
    """Pull score from db and save into a csv"""

    with Gradebook(database_url) as gb:
        
        grades = []
        for assignment in gb.assignments:
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
    
    # Merge the score information with sis_id from df of student_id
    grades_info = pd.merge(grades, student_id, left_on='student', right_on=id_col, how='left')
    
    # Save the grades
    grades_info.to_csv(grades_file)
       
                
def print_summary(grades_file, score_path, folder_name):
    """Print out the summary of scores, details save in ../scores/ folder"""
    
    # Generate histogram
    score_df = pd.read_csv(grades_file)
    score_df['score'].hist()
    plt.title('Histogram for %s' % folder_name)
    plt.savefig(score_path+folder_name+'/hist.png')

    # Save scores
    with open(score_path+folder_name+'/summary.txt', "a") as f:
    
        f.write("\n---score summary---\n")
        f.write(f"min    : {min(score_df['score'])}")
        f.write(f"max    : {max(score_df['score'])}")
        f.write(f"median : {statistics.median(score_df['score'])}")
        f.write(f"std    : {statistics.stdev(score_df['score']):.2f}")
        f.close()
