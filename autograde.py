"""
Automatically grade student's work in Jupyter Notebook using the nbgrader package.
After grading, automtically post the scores to Canvas (the Learning Management System).
"""

from   dataclasses import dataclass
import json
from   operator    import getitem 
import os
from   pathlib     import Path
from   pprint      import pprint
import shutil
import sys

from   nbgrader.apps import NbGraderAPI
import requests


@dataclass
class Assignment:
    """Specific assignment for a class"""
    course_name: str
    course_id: int 
    assignment_name: str
    assignment_id: int
    
# Set current variables
scores = {}
assignment = 1
post_to_canvas = True
grade_individual = False
# grade_individual = True; 
# user_id_to_grade = 6197818

# Setup Canvas API
# Token could be generated: `Account` -> `Settings` -> `Approved Integrations` -> 'New Access Token'
# https://lorem.instructure.com/profile/settings
token = ''


def get_file_names(assignment, grade_individual=False):
    path = Path('./')
    filenames = list(path.glob(f"canvas/{assignment.assignment_name}/*.ipynb"))
    if grade_individual:
        filenames = [filename for filename in filenames if str(user_id_to_grade) in str(filename)]
    
    return filenames

def grade_students(assignment, filenames):
    nbgrader = NbGraderAPI()
    print (f"Grading {assignment.assignment_name}…")
    for n, filename in enumerate(filenames, start=1):

        # Process filename
        canvas_name, user_id, unknown_num_2, login_id, *_ = filename.parts[-1].lower().split("_") # `*_` discards how student named file

        path_submitted = path / "submitted" / user_id / assignment.assignment_name
        if not os.path.exists(path_submitted):
            os.makedirs(path_submitted)

        # Move and rename 
        file_name_new = assignment.assignment_name+'.ipynb'
        shutil.copyfile(src=filename,
                        dst=path / "submitted" / user_id / assignment.assignment_name / file_name_new)
        
        # Autograde
        nbgrader_result = nbgrader.autograde(assignment_id=assignment.assignment_name, 
                                            student_id=user_id, 
                                            force=True,  
                                            create=True)

        if nbgrader_result['success'] == False:
            print(nbgrader_result['log'])
            sys.exit(1) 

        current_score = nbgrader.get_student_notebook_submissions(assignment_id=assignment.assignment_id, student_id=user_id)[0]['score']
        print(f"{n:> 4} out of {n_students} - Successfully graded score of {current_score:>2.0f} for {canvas_name.title()}")
        scores[canvas_name] = {'user_id':       user_id,
                            'current_score': current_score}

        # Move file for uploading back to canvas
        autograded_folder = 'autograded'
        to_upload = 'to_upload'

        filename_orginal = filename.parts[-1]
        current_path = Path(to_upload) / Path(assignment.assignment_name)
        if not os.path.exists(current_path):
            os.makedirs(current_path)

        shutil.copyfile(src=path / autograded_folder / user_id / assignment.assignment_name / file_name_new,
                        dst=path / to_upload / assignment.assignment_name / filename_orginal)

    # Sort scores 
    scores_sorted = dict(sorted(scores.items(),
                        key=lambda x: getitem(x[1], 'current_score'),
                        reverse=False # From low to high
                        ))

    # Log scores
    try:
        with open(f"{assignment.assignment_name}_scores.json", 'w') as fp:
            json.dump(scores_sorted, fp)
    except FileNotFoundError as err:
        print("Error: Need to create file:", str(err).split(" ")[-1])

    print("\nGrading done")
    pprint(scores_sorted)
    
    return scores

def post_scores(token, assignment, scores):
    """Post to Canvas via API"""

    for n, canvas_name in enumerate(scores, start=1):
        # gernal https://canvas.instructure.com/doc/api/index.html
        # docs - https://canvas.instructure.com/doc/api/submissions.html#Submission
        user_id = scores[canvas_name]['user_id']
        current_score = scores[canvas_name]['current_score']
        url = f"https://lorem.instructure.com/api/v1/courses/{course_id}/assignments/{assignment.assignment_id}/submissions/{user_id}"
        headers = {'Authorization': 'Bearer ' + token}
        data = {'submission[posted_grade]': current_score}

        try:
            r = requests.put(url=url, headers=headers, data=data)
            print(f"{n:> 4} out of {n_students} successfully posted to Canvas a score of {current_score:>2.0f} for {canvas_name.title()}")
        except requests.exceptions.HTTPError as err:
            print(err)
            print(f"Something wrong with call to Canvas for {canvas_name} / {user_id}")
            sys.exit(1)

if __name__ == '__main__':

    assignment = Assignment(course_name="Lorem",
                            course_id=1587402,
                            assignment_name="1_assignment_regression",
                            assignment_id=6886889
                            )
    print(assignment.assignment_name)

    filenames = get_file_names(assignment)
    
    scores = grade_students(assignment=assignment, 
                          filenames=filenames)
    
    if post_to_canvas:
        post_scores(token=token, assignment=assignment, scores=scores)
    else:
        print("Scores not posted to Canvas.")
