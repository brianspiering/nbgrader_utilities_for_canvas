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

canvas_api_token = os.getenv("CANVAS_API_TOKEN")
course_name = "lorem"
course_id   = 1587402
assignment_name = "1_assignment_regression"
assignment_id   = 6886889
post_to_canvas = False


def get_user_ids(assignment):
    "Get uers ids from submitted files. Also, cleanup filenames for nbgrader."
    path = Path('./')
    filenames = list(path.glob(f"canvas/{assignment.assignment_name}/*.ipynb"))
    user_ids = []
    for n, filename in enumerate(filenames, start=1):
        
        # Process filename
        canvas_name, user_id, unknown_num_2, login_id, *_ = filename.parts[-1].lower().split("_") # `*_` discards how student named file
        user_ids.append(user_id)
        
        path_submitted = path / "submitted" / user_id / assignment.assignment_name
        if not os.path.exists(path_submitted):
            os.makedirs(path_submitted)

        # Move and rename 
        file_name_new = assignment.assignment_name+'.ipynb'
        shutil.copyfile(src=filename,
                        dst=path / "submitted" / user_id / assignment.assignment_name / file_name_new)
        
    return user_ids

def grade_students(assignment, user_ids):
    nbgrader = NbGraderAPI()
    scores = {}
    print (f"Grading {assignment.assignment_name} …\n")
    for n, userid in enumerate(user_ids, start=1):

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

    # Sort scores 
    scores_sorted = dict(sorted(scores.items(),
                        key=lambda x: getitem(x[1], 'current_score'),
                        reverse=False # From low to high
                        ))

    # Log scores
    if scores_sorted:
        with open(f"{assignment.assignment_name}_scores.json", 'w') as fp:
            json.dump(scores_sorted, fp)
        print("Student scores:")
        pprint(scores_sorted)
    else:
        print("There are no scores. Double check that is correct.")

    print("\nGrading done")
    
    return scores

def post_scores(assignment, scores, token):
    """Post to Canvas via API
    general: https://canvas.instructure.com/doc/api/index.html
    docs: https://canvas.instructure.com/doc/api/submissions.html#Submission
    """

    for n, student_name_on_canvas in enumerate(scores, start=1):
        user_id = scores[student_name_on_canvas]['user_id']
        current_score = scores[student_name_on_canvas]['current_score']
        url = f"https://lorem.instructure.com/api/v1/courses/{assignment.course_id}/assignments/{assignment.assignment_id}/submissions/{user_id}"
        headers = {'Authorization': 'Bearer ' + token}
        data = {'submission[posted_grade]': current_score}

        try:
            r = requests.put(url=url, headers=headers, data=data)
            print(f"{n:> 4} out of {n_students} successfully posted to Canvas a score of {current_score:>2.0f} for {student_name_on_canvas.title()}")
        except requests.exceptions.HTTPError as err:
            print(err)
            print(f"Something wrong with call to Canvas for {student_name_on_canvas} / {user_id}")
            sys.exit(1)

@dataclass
class Assignment:
    """Current assignment metadata"""
    course_name: str
    course_id:   int 
    assignment_name: str
    assignment_id:   int

if __name__ == '__main__':

    assignment = Assignment(course_name=course_name,
                            course_id=course_id,
                            assignment_name=assignment_name,
                            assignment_id=assignment_id,
                            )

    user_ids = get_user_ids(assignment=assignment)
    
    scores = grade_students(assignment=assignment, user_ids=user_ids)
    
    if post_to_canvas:
        post_scores(assignment=assignment, scores=scores, token=canvas_api_token)
    else:
        print("Scores not posted to Canvas.")
