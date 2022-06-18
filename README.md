# Social-Recommender-System

## Reforming Streaming Services Customer Experience

### What's the Problem?
Streaming and video entertainment platforms (such as YouTube, Netflix, Amazon Prime etc) use a range of recommendation algorithms to optimise user's browsing experience. However, the problem with these techniques is that they sometimes fail to consider the demand for customising who a user wishes to include as part of collaborative filtering techniques to produce recommendations regardless of how similar they are with other users available on a system.

### Problem Solution
Most people like to get movie or television show recommendations through word-of-mouth/face-to-face/any other communication channel. This project will automate this process. It aims to evaluate whether a user's ability to customise their nearest neighbours by allowing users to follow other users on the system will increase recommendation satisfaction. A user's followings who are most similar to that user will have the most significant influence on that user's recommendations

#### Summarised Aims

* Increase Recommendations Satisfaction
* Allows users to customise the extent to which other user's data influences their own recommendation by allowing users to 'follow' other users on the system.

### How Can I Get Involved?

* Want to be a beta tester? Feel free to report any issues, and add comments in the discussions section.
* You will need a personal computer/laptop that has constant Internet Access
* You will need <a href="https://www.python.org/downloads/">Python3</a> installed

### Things To Note

* Due to the current limitations in accessing the IMDb database, titles are scrapped manually to the software rather than updated automatically, this means that -for now- there are a limited number of titles available to rate but this will hopefully be rectified/updated regularly in the future
* This software is built using Python, therefore it may be slower than compiled software. Nevertheless, there is a 30 second guarantee of which, results will be loaded within 30 seconds. If they don't, feel free to report this!

### To Do

To use this project please create the file ```mysqlconnection.py``` and structure it as follows

```python
import mysql.connector

system = mysql.connector.connect(
    host="host_uri",
    user="user",
    password="password",
    database="databasename"
)

def getSystem():
    return system
```

### Installing the software

1. Install the libraries <a href="https://pypi.org/project/guizero/">GuiZero</a>, <a href="https://pypi.org/project/mysql-connector-python/">MySQL Connector</a>, <a href="https://pypi.org/project/Pillow/">Pillow</a>, <a href="https://pypi.org/project/numpy/">Numpy</a>, <a href="https://pypi.org/project/requests/">Requests</a>
2. Install <a href="https://pypi.org/project/cx-Freeze/">cx-Freeze</a>
3. Open your command line and direct to the installed project
4. Run 'python3 setup.py build' (This may take several seconds)
5. Open the installed folder in File Explorer
6. Open Build
7. Open the folder in build (labelled 'exe.' + the platform your workstation uses)
8. Open the executable program in the file


## Technologies
* Python
* MySQL

### Notable Third Party Modules 
* <a href="http://www.omdbapi.com/">OMDb (Open Movie Database) API</a> 
