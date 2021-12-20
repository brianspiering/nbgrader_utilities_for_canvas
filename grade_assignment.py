
import json
from operator import getitem 
import os
from pathlib import Path
from pprint import pprint
import shutil
import sys

from nbgrader.apps import NbGraderAPI
import requests

assignment = 4
post_to_canvas = False
grade_individual = False
# grade_individual = True; user_id_to_grade = 6197818

# Define assignment parameters
if   assignment == 1:
    # Assignment #1
    assignment_id = 6886889 # https://lorem.instructure.com/courses/1587402/assignments/6886889
    assignment_name = "1_assignment_regression"
elif assignment == 2:
    # Assignment #2
    assignment_id = 6888950 # https://lorem.instructure.com/courses/1587402/assignments/6888950
    assignment_name = "2_assignment_binary_classification"
elif assignment == 3:
    # Assignment #3
    assignment_id = 6890335 # https://lorem.instructure.com/courses/1587402/assignments/6888950
    assignment_name = "3_assignment_mutliclass_classification" 
elif assignment == 4:
    # Assignment #4
    assignment_id = 6891827 # https://lorem.instructure.com/courses/1587402/assignments/6891827
    assignment_name = "4_assignment_feature_engineering" 
elif assignment == 5:
    # Assignment #5
    assignment_id = 6892527 # https://lorem.instructure.com/courses/1587402/assignments/6892527
    assignment_name = "5_assignment_clustering" 

print (f"Grading {assignment_name} …")

# Define filenames
path = Path('./')
filenames = list(path.glob(f"canvas/{assignment_name}/*.ipynb"))
if grade_individual:
    filenames = [filename for filename in filenames if str(user_id_to_grade) in str(filename)]
n_students = len(filenames)

# Define course parameters
course_id = 1587402 # https://lorem.instructure.com/courses/1587402

# Canvas API token
# Token could be generated: `Account` -> `Settings` -> `Approved Integrations` -> 'New Access Token'
# https://lorem.instructure.com/profile/settings
token = ''
nbgrader = NbGraderAPI()

scores = {}

for n, filename in enumerate(filenames, start=1):

    # Process filename
    canvas_name, user_id, unknown_num_2, login_id, *_ = filename.parts[-1].lower().split("_") # `*_` discards how student named file

    path_submitted = path / "submitted" / user_id / assignment_name
    if not os.path.exists(path_submitted):
        os.makedirs(path_submitted)

    # Move and rename 
    file_name_new = assignment_name+'.ipynb'
    shutil.copyfile(src=filename,
                    dst=path / "submitted" / user_id / assignment_name / file_name_new)
    
    # Autograde
    nbgrader_result = nbgrader.autograde(assignment_id=assignment_name, 
                                         student_id=user_id, 
                                         force=True,  
                                         create=True)

    if nbgrader_result['success'] == False:
        print(nbgrader_result['log'])
        sys.exit(1) 

    current_score = nbgrader.get_student_notebook_submissions(assignment_id=assignment_name,                                                      student_id=user_id)[0]['score']

    print(f"{n:> 4} out of {n_students} - Successfully graded score of {current_score:>2.0f} for {canvas_name.title()}")
    scores[canvas_name] = {'user_id':       user_id,
                           'current_score': current_score}

    # Move file for uploading back to canvas
    autograded_folder = 'autograded'
    to_upload = 'to_upload'

    filename_orginal = filename.parts[-1]
    current_path = Path(to_upload) / Path(assignment_name)
    if not os.path.exists(current_path):
        os.makedirs(current_path)

    shutil.copyfile(src=path / autograded_folder / user_id / assignment_name / file_name_new,
                    dst=path / to_upload / assignment_name / filename_orginal)

# Sort scores from low to high
scores_sorted = dict(sorted(scores.items(),
                    key=lambda x: getitem(x[1], 'current_score'),
                    reverse=False))
# Log scores
if len(scores_sorted) > 80: # Only log if most individuals are graded
    with open(f"scores/{assignment_name}_scores.json", 'w') as fp:
        json.dump(scores_sorted, fp)

print("\nGrading done")
pprint(scores_sorted)

# Post to Canvas via API

if post_to_canvas:
    input("""WARNING: double check grades are muted! \n
             Press return to continue:""")

    for n, canvas_name in enumerate(scores, start=1):
        # gernal https://canvas.instructure.com/doc/api/index.html
        # docs - https://canvas.instructure.com/doc/api/submissions.html#Submission
        user_id = scores[canvas_name]['user_id']
        current_score = scores[canvas_name]['current_score']
        url = f"https://lorem.instructure.com/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
        headers = {'Authorization': 'Bearer ' + token}
        data = {'submission[posted_grade]': current_score}

        try:
            r = requests.put(url=url, headers=headers, data=data)
            print(f"{n:> 4} out of {n_students} successfully posted to Canvas a score of {current_score:>2.0f} for {canvas_name.title()}")
        except requests.exceptions.HTTPError as err:
            print(err)
            print(f"Something wrong with call to Canvas for {canvas_name} / {user_id}")
            sys.exit(1)
else:
    print("Scores not posted to Canvas.")