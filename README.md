Instruction for Autograding
------

How to run:
1. modify score_pipe.py 

- line24:

```
download_dir = '/Users/shen/Downloads/' # the directory where the dropbox assignment folder located at.
```

Dropbox assignment was downloaded, should be a .zip file.

- line 34:

```
ddl = datetime.datetime(2018,ddl_mon,ddl_day,14) + datetime.timedelta(days=1) # 2018 and 14 should be modified.
```

This function helps determine whether submission is before deadline and convert the local PST time to UTC time. 

- line 79:

```
course_id = 1580035 # could be found in canvas url
token = '1018~*********' # Sangyu's token
```

2. run the following scripts in the utilites directory:

```
utilites$ python score_pipe.py ../submitted/ ../scores/ <new_grades> <assign_folder_name> 
          <download_folder> <assign_id> <month> <day> <hw_name>
```

- `new_grades`: True/False. For those students already have a grade, if they should be graded again this time
- `assign_folder_name`: assignment folder name, e.g., lab1_knn_lab
- `download_folder`: folder name of dropbox folder, e.g., Lab-KNN
- `assign_id`: canvas assignment id, found in canvas url, e.g., 6799280
- `month`: the deadline month info (local time -PST)
- `day`: the deadline day info (local time -PST)
- `hw_name`: the name of one homework in the assignment folder, e.g., knn_lab

3. Provide two further instructions:
   - `New Grading [yes/no]`: indicting whether students should be graded again if they have been graded last time
   - `Updating Score [yes/no]`: indicting whether the scores should be updated in Canvas


Additional Information
------
- Token could be generated: `account` -> `setting` -> `Approved Integrations`

- Course id and assignment id:
  - e.g.:https://lorem.instructure.com/courses/1580035/assignments/6799280
  - course id : 1580035
  - assignment id : 6799280

- short starting sample:
```
base_path = 'https://usfca.instructure.com/api'
url = base_path + '/v1/accounts/'
token = '1018~**'
header = {'Authorization': 'Bearer ' + token}
r = requests.get(url, headers = header)
print (r.status_code)
```

- useful link
  - [Canvas API : Getting Started](https://community.canvaslms.com/docs/DOC-14390-canvas-apis-getting-started-the-practical-ins-and-outs-gotchas-tips-and-tricks#jive_content_id_API_Calls_Made_Simple__Curtis_Rose)
  - [Canvas Course API : detailed info](https://canvas.instructure.com/doc/api/courses.html)
  - [Canva Live API](https://lorem.instructure.com/doc/api/live) (would be your canvas in api format)
  
  
