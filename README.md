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
* If you don't have github, or want to give formal feedback please do so following this <a href="https://docs.google.com/forms/d/1iWBEcv1yjr3HPctsqrla5k1L70qd_UQ8Wy-wMskHpQ0/edit" target="_blank">link</a>

### Things To Note

* Due to the current limitations in accessing the IMDb database, titles are scrapped manually to the software rather than updated automatically, this means that -for now- there are a limited number of titles available to rate but this will hopefully be rectified/updated regularly in the future
* This software is built using Python, therefore it may be slower than compiled software. Nevertheless, there is a 30 second guarantee of which, results will be loaded within 30 seconds. If they don't, feel free to report this!

### Installing the software

1. Download the folder 'Instructions'
2. Install <a href="https://pypi.org/project/cx-Freeze/">cx-Freeze</a>
3. Open your command line and direct to the installed folder
4. Run 'python3 setup.py build' (This may take several seconds)
5. Open the installed folder in File Explorer
6. Open Build
7. Open the folder in build (labelled 'exe.' + the platform your workstation users)
8. Open the executable program in the file


## Technologies
* Python
* MySQL

### Notable Third Party Modules 
* <a href="http://www.omdbapi.com/">OMDb (Open Movie Database) API</a> 
