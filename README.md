Using nbgrader with Canvas
-------

[Nbgrader](https://github.com/jupyter/nbgrader) a package for autograding grading Jupyter notebooks. Canvas is a learning management system (LMS), aka a gradebook. Canvas has a high-quality API which allow for the programmatic updating of student grades.

This repo is a collection of utilities to help run nbgrader and then pipeline the output into Canvas. 


Setup
------

- Token could be generated in Canvas: `account` -> `setting` -> `Approved Integrations`

- Find course id and assignment id:
  - Navigate to the specific assignment on your Canvas page - https://lorem.instructure.com/courses/1580035/assignments/6799280
  - Course id : 1580035
  - Assignment id : 6799280

- Code sample to get you started:

```python
import requests

base_path = 'https://lorem.instructure.com/api'
url = base_path + '/v1/accounts/'
token = '1018~**'
header = {'Authorization': 'Bearer ' + token}
r = requests.get(url, headers = header)
print(r.status_code)
```

Autograding Steps
------

1. Modify score_pipe.py 

  - line24: `  download_dir = '~/Downloads/' # the directory where the dropbox assignment folder located at.`

  - line 34: `ddl = datetime.datetime(2018,ddl_mon,ddl_day,14) + datetime.timedelta(days=1) # 2018 and 14 should be modified.` This function helps determine whether submission is before deadline and convert the local PST time to UTC time. 

2. Run the following scripts:

  ```bash
  python score_pipe.py ../submitted/ ../scores/ <new_grades> <assign_folder_name> 
          <download_folder> <assign_id> <month> <day> <hw_name>
  ```

  - `new_grades`: True/False. For those students already have a grade, if they should be graded again this time
  - `assign_folder_name`: assignment folder name, e.g., lab1_knn_lab
  - `download_folder`: folder name of dropbox folder, e.g., Lab-KNN
  - `assign_id`: canvas assignment id, found in canvas url, e.g., 6799280
  - `month`: the deadline month info (local time -PST)
  - `day`: the deadline day info (local time -PST)
  - `hw_name`: the name of one homework in the assignment folder, e.g., knn_lab

3. Provide two additional instructions:
  
  - `New Grading [yes/no]`: indicting whether students should be graded again if they have been graded last time
  - `Updating Score [yes/no]`: indicting whether the scores should be updated in Canvas


Useful Links
------

- [Canvas API : Getting Started](https://community.canvaslms.com/docs/DOC-14390-canvas-apis-getting-started-the-practical-ins-and-outs-gotchas-tips-and-tricks#jive_content_id_API_Calls_Made_Simple__Curtis_Rose)
- [Canvas Course API : detailed info](https://canvas.instructure.com/doc/api/courses.html)
- https://lorem.instructure.com/doc/api/live is your canvas in api format.
  
