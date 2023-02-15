nbgrader + Canvas
-------

This is a collection of utilities to help run nbgrader and then post student scores to Canvas. 

[nbgrader](https://github.com/jupyter/nbgrader) is a package for autograding Jupyter Notebooks. 

Canvas is a learning management system (LMS), aka a gradebook. Canvas has a high-quality API that allows for the programmatic updating of student grades.

Setup
------

- Generate Canvas API token:
  - https://lorem.instructure.com/profile/settings
  - `account` -> `setting` -> `Approved Integrations`  -> 'New Access Token'

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
python autograde.py 
```

Useful Links
------

- [Canvas API: Getting Started](https://community.canvaslms.com/docs/DOC-14390-canvas-apis-getting-started-the-practical-ins-and-outs-gotchas-tips-and-tricks#jive_content_id_API_Calls_Made_Simple__Curtis_Rose)
- [Canvas Course API: detailed info](https://canvas.instructure.com/doc/api/courses.html)
- The url to the what endpoints are available of your specific Canvas instance- https://lorem.instructure.com/doc/api/live
  