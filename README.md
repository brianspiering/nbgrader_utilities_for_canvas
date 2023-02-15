nbgrader + Canvas
-------

This is a collection of utilities to help run nbgrader and then post student scores to Canvas. 

[nbgrader](https://github.com/jupyter/nbgrader) is a package for autograding Jupyter Notebooks. 

Canvas is a learning management system (LMS), aka a gradebook. Canvas has a high-quality API that allows for the programmatic updating of student grades.

Autograding Steps
------

1. Create local folders.
2. Autograde student submissions with nbgrader.
3. Post student scores to Canvas via the API.


Setup
------

- Generate Canvas API token: `account` -> `setting` -> `Approved Integrations`

- Find course id and assignment id:
  - Navigate to the specific assignment on your Canvas page - https://lorem.instructure.com/courses/1580035/assignments/6799280
  - Course id: 1580035
  - Assignment id: 6799280

- Sample Canvas API code to get you started:

```python
import requests

base_path = 'https://lorem.instructure.com/api'
url = base_path + '/v1/accounts/'
token = '1018~**'
header = {'Authorization': 'Bearer ' + token}
r = requests.get(url, headers = header)
print(r.status_code)
```

Example
------

```bash
python autograde.py ../submitted/ ../scores/ <assign_folder_name> <download_folder> <assign_id> <month> <day> <hw_name>
```

- `assign_folder_name`: assignment folder name, e.g., lab1_knn_lab
- `download_folder`: folder name of dropbox folder, e.g., Lab-KNN
- `assign_id`: canvas assignment id, found in canvas url, e.g., 6799280
- `month`: the deadline month info (local time -PST)
- `day`: the deadline day info (local time -PST)
- `hw_name`: the name of one homework in the assignment folder, e.g., knn_lab

Useful Links
------

- [Canvas API: Getting Started](https://community.canvaslms.com/docs/DOC-14390-canvas-apis-getting-started-the-practical-ins-and-outs-gotchas-tips-and-tricks#jive_content_id_API_Calls_Made_Simple__Curtis_Rose)
- [Canvas Course API: detailed info](https://canvas.instructure.com/doc/api/courses.html)
- The url to the what endpoints are available of your specific Canvas instance- https://lorem.instructure.com/doc/api/live
  