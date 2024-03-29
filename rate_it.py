from guizero import *
import mysql.connector
import json
import urllib
import numpy as np
import math
import requests
import random
from PIL import *

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from mysqlconnection import getSystem

systemdb = getSystem()

c = systemdb.cursor(buffered=True)

#Based on IMDb's top 250 and top rated TV shows
imdbIDs = ['0805647', '0468569', '0167260', '0120737', '0133093', '0245429', '0110357', '0088763', '4154796',
           '4633694', '7286456', '8503618', '4154756', '2380307', '2096673', '0993846', '2024544', '1454029',
           '1201607', '0435761', '0892769', '0405159', '0266697', '0137523', '6751668', '1049413', '0910970'
           , '0395169', '0347149', '0266543', '0253474', '0317248', '0198781', '0211915', '0109830',
           '0110912','0108052','0097576','8579674','1950186','8613070','6966692', '1392190','2267998','0986264','0457430',
           '0434409','0096283','0088247','0086190','0083658','0080678', '4786824','8134470','0460681',
           '7569576','11794642','0413573','1190634','0944947','5171438','2442560','1520211','1844624','0386676',
           '10048342','8111088','0903747','0108778','0364845','4574334', '12361974', '9140560',  '9208876',  '5109280',
           '0770828',  '2948372', '9620292', '9770150', '6723592', '9698442', '0451279', '5363618', '0094898',
           '2395427', '9784798', '0068646', '12920838', '0448115', '1345836', '10288566', '6802400', '10813940']

#enables quick checking of updation of each window's state
windows = {
    'newUserWindow': 0,
    'existingUserWindow': 0,
    'ratingWindow': 0,
    'recommendationsWindow': 0,
    'profileWindow': 0,
    'followersWindow': 0,
    'followingsWindow': 0,
    'searchEngineWindow': 0,
    'resultsWindow':0,
    'instructionsWindow':0,
    'creditsWindow':0}

#checks theme color choice 0 - light theme, 1 - darkTheme
themeChoice = 0

#light and dark mode color palettes
lightThemeButtonColor = (28,254,251)
lightThemeBgColor = "white"
lightThemeComplBg = (3,168,229)
lightThemeTextColor = "black"

darkThemeButtonColor = (229,9,20)
darkThemeBgColor = (45,45,45)
darkThemeComplBg = (177,6,15)
darkThemeTextColor = "white"

def chooseTheme(choice):
    global themeChoice
    if choice == "Light Mode":
        themeChoice = 0
    if choice == "Dark Mode":
        themeChoice = 1

        
def colorWidget(widgetType):
    global themeChoice
    if themeChoice == 0:
        if widgetType == 'Combo':
            return lightThemeComplBg
        if widgetType == 'App' or widgetType == 'Window':
            return lightThemeBgColor
        if widgetType == 'Push Button':
            return lightThemeButtonColor
        if widgetType == 'Text':
            return lightThemeTextColor

    if themeChoice == 1:
        if widgetType == 'Combo':
            return darkThemeComplBg
        if widgetType == 'App' or widgetType == 'Window':
            return darkThemeBgColor
        if widgetType == 'Push Button':
            return darkThemeButtonColor
        if widgetType == 'Text':
            return darkThemeTextColor

   



def isWindowOpen(window):
    global windows
    
    if windows[window] == 1:
        #window is already open and therefore won't open another window
        return True
    else:
        #if not, the program will open the window, so this state is updated here
        windows[window] = 1
        return False

def closeWindow(windowname, windowobj):
    #informs the windows dictionary that the window
    #has been closed
    windows[windowname] = 0
    windowobj.destroy()

    #if the window to be closed is the searchEngine window, the searchResults variable
    #is set to zero to show that this is also closed as a result

    if windowobj == 'searchEngineWindow':
        searchResults = 0

def getUser2Id(user2):
    global systemdb
    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT userId FROM users WHERE username='{}';'''.format(user2))
    user2Id = c.fetchall()
    user2Id = user2Id[0][0]


    c.close()

    return user2Id

def getUnseenTitles(user):
    global systemdb
    #Returns user's unseen titles from the database
    c = systemdb.cursor(buffered=True)
    unseenTitles_query = c.execute('''SELECT imdbId FROM unseenTitles WHERE userId='{}';'''.format(user.getId()))
    unseenTitles_query = c.fetchall()
    unseenTitles = []
    for row in unseenTitles_query:
        unseenTitles.append(row[0])

    c.close()

    return unseenTitles

def addTitleToQueue(dataset):
    global system
    #adds titles from a dataset of imdb id's
    #whether its the imdbIDs list or the unseen titles result
    #queried from the database to the recommender system's
    #priority queue
    for item in dataset:
        title = convertIdToTitleObject(item)
        if title not in system.getUnseenQueue().getDataset():
            system.getUnseenQueue().enqueue(title)

    
    

def convertIdToTitleObject(titleId):
    #ocurrs when a title imdb id is passed into a function rather than a title object (i.e. when the system uses collaborative filtering to generate recommendations)
    #scraps the data of the imdb
    title = requests.get("http://www.omdbapi.com/?i=tt" + titleId + "&apikey=8598b952")

    #Titles the user will rate
    title = title.text
    title = json.loads(title)
    title['Genre'] = title['Genre'].split(", ")

    #The title data is instaniated into an object based on if it is a movie or tv show (this has already been categorised by the API)

    if title['Type'] == "movie":

        titleobject = Title(title['Poster'], title['Title'], title['Genre'], titleId, "movie")

    elif title['Type'] == "series":
        titleobject = Title(title['Poster'], title['Title'], title['Genre'], titleId, "series")

    return titleobject

def setUpUnseenTitles(user):
    global imdbIDs, systemdb
    c = systemdb.cursor(buffered=True)

    #checks whether the user has rated titles before
    unseenTitles = getUnseenTitles(user)

    #if the user has rated titles before, the program loads in titles the user hasn't rated
    if unseenTitles != []:
        addTitleToQueue(unseenTitles)
    else:
        #else it loads in all tiles
        random.shuffle(imdbIDs)
        addTitleToQueue(imdbIDs)

    c.close()

   
def returnSimilarity(elem):
    return elem[1]

#Users Class
class Users(object):
    def __init__(self, username, password):
        self._username = username
        #Review whether storing the password is necessary
        self._password = password
        self._recommendations = []
        self._followings = []
        self._followers = []
        self._ratedGenres = []
        self._ratedTitles = []
        self._genreScores = {}
        #saves saved genre scores from database (needed when calculating nearest neighbours)
        self._genreScoresExternal = {}
        self._connectsTo = []

    def getId(self):
        global systemdb

        c = systemdb.cursor(buffered=True)
        #gets the user's id from the database, this is useful to quickly query other tables in the database as appropriate
        c.execute('''SELECT userId FROM users WHERE username = '{}';'''.format(self.getUsername()))
        systemdb.commit()
        rows = c.fetchall()

        userId = rows[0][0]    
        c.close()
        
        return userId

    def getRecommendations(self):
        return self._recommendations

    def getRatedGenres(self):
        return self._ratedGenres

    def setRatedGenres(self, genre):
        self._ratedGenres.append(genre)

    def getRatedTitles(self):
        return self._ratedTitles

    def getGenreScores(self):
        return self._genreScores

    def createGenreScoresExternal(self):
        #gets genre scores from database
        global systemdb
        c= systemdb.cursor(buffered=True)
        #creates the template for the genre scores
        template = {"genre": None, "averageRating": None, "timesRated": None}
        #queries user's genre rating data
        c.execute('''SELECT genre, averageRating, timesRated FROM ratingsMatrix WHERE userId = '{}';'''.format(self.getId()))
        systemdb.commit()
        genreScores_query = c.fetchall()
        
        for row in genreScores_query:
            #saves the data internally in the system during the user's log in session
            template["averageRating"] = row[1]
            template["timesRated"] = row[2]
            self.setGenreScoresExternal(row[0], template)
            template = {"averageRating": None, "timesRated": None}

        c.close()

    def getGenreScoresExternal(self):
        return self._genreScoresExternal
        

    def setGenreScores(self, genre, score):
        self._genreScores[genre] = score

    def setGenreScoresExternal(self, genre, score):
        self._genreScoresExternal[genre] = score

    def getUsername(self):
        return self._username

    def getPassword(self):
        return self._password

    def getConnections(self):
        return self._connectsTo

    def setConnectsTo(self, connection):
        self._connectsTo.append(connection)

        self._connectsTo.sort(reverse=True, key=returnSimilarity)

    def rate_titles(self, title):
        #show ratings window
        showRatingsWindow(self, title)

    def followUser(self, user):
        global systemdb, system
        #ignores empty results
        if user == None:
            pass
        else:
            #updates selected user's followers
            c = systemdb.cursor(buffered=True)
            #gets user to follow's id
            c.execute('''SELECT userId FROM users WHERE username='{}';'''.format(user))
            systemdb.commit()
            userToFollow_id = getUser2Id(user)
            c.execute('''SELECT * from userFollowings WHERE userId = '{}';'''.format(self.getId()))
            systemdb.commit()
            followingsQuery = c.fetchall()
            followers = []
            for row in followingsQuery:
                followers.append(row[0])
            if userToFollow_id not in followers:
                #inserts user into followings
                c.execute('''INSERT INTO userFollowings(userId, user_follows) VALUES ('{}', '{}');'''.format(self.getId(), userToFollow_id))
                systemdb.commit()
                #updates user to follow's followers
                c.execute('''INSERT INTO userFollowers(userId, user_followedBy) VALUES ('{}', '{}');'''.format(userToFollow_id, self.getId()))
                systemdb.commit()
            else:
                pass
                #the user already follows that user
            c.close()

            system.updateUsersSimilarity(self,user)

    def unfollowUser(self, user):
        global systemdb
        #ignores empty results
        if user == None:
            pass
        else:
            if user in self._followings:
                self._followings.remove(user)

            c = systemdb.cursor(buffered=True)
            #gets user to unfollow's id
            c.execute('''SELECT userId FROM users WHERE username='{}';'''.format(user))
            systemdb.commit()
            userToUnfollow_id = c.fetchall()
            userToUnfollow_id = row[0][0]

            #removes records from both the userFollowers and userFollowings tables in the database
            c.execute('''DELETE FROM userFollowings WHERE userId ='{}' AND user_follows='{}';'''.format(self.getId(), userToUnfollow_id))
            systemdb.commit()
            c.execute('''DELETE FROM userFollowers WHERE userId='{}' AND user_followedBy='{}';'''.format(userToUnfollow_id, self.getId()))
            systemdb.commit()

            c.close()

    #gets followings from external database to be copied into the user's followings attribute when the user logs into a new session
    def updateFollowings(self):
        global systemdb, system
        c = systemdb.cursor(buffered=True)
        c.execute('''SELECT users.username FROM users JOIN userFollowings WHERE users.userId=userFollowings.user_follows AND userFollowings.userId = '{}';'''.format(self.getId()))
        systemdb.commit()
        followings_query = c.fetchall()
        for row in followings_query:
            if row not in self.getFollowings():
                self._followings.append(row[0])
                #updates user similarity with their followings
            system.updateUsersSimilarity(self, row[0])

        c.close()

    def getFollowings(self):
        return self._followings

    def getFollowers(self):
        return self._followers
       
    def setRecommendations(self, title, predictedRating):
        global systemdb, system
        
        if isinstance(title, str) == True:
            title = convertIdToTitleObject(title)

        #updates recommendations in program
        self._recommendations.append(title)

        #saves recommendations externally
        c = systemdb.cursor(buffered=True)

        #checks if the title is already in the database
        unseenTitlesCheck = getUnseenTitles(self)
        
        if title.getId() in unseenTitlesCheck:
            #updates unseen titles to include new values if so
            c.execute('''UPDATE unseenTitles SET predictedRating = '{}' AND recommended = TRUE WHERE imdbId = '{}' and userId = '{}';'''.format(predictedRating, title.getId(), self.getId()))
            systemdb.commit()
        else:
            #otherwise adds the record entry into the database
            c.execute('''INSERT INTO unseenTitles (userId, imdbId, predictedRating, recommended) VALUES ('{}', '{}', '{}', TRUE);'''.format(self.getId(), title.getId(), predictedRating))
            systemdb.commit()
            
        c.execute('''INSERT INTO recommendations (userId, imdbId) VALUES ('{}', '{}');'''.format(self.getId(), title.getId()))
        systemdb.commit()
            
        c.close()

#Titles Class

class Title(object):
    def __init__(self, coverImage, title, genres, imdbId, titleType):
        self._coverImage = coverImage
        self._title = title
        self._genres = genres
        self._imdbId = imdbId
        #score used for the priority queue to update (as a binary heap)
        self._priorityScore = 0
        #differentiates movies from tv shows
        self._titleType = titleType

    def getTitleType(self):
        return self._titleType


    def getPriorityScore(self):
        return self._priorityScore

    def setPriorityScore(self, score):
        self._priorityScore = score

    def getGenres(self):
        return self._genres

    def getTitle(self):
        return self._title

    def getId(self):
        return self._imdbId

    def getcoverImage(self):
        return self._coverImage

    def setRating(self, user, userRating):
        global systemdb
        c = systemdb.cursor(buffered=True)
        #saves rated title into database
        c.execute('''INSERT INTO usersRatedTitles (userId, imdbId, rating) VALUES ('{}', '{}', '{}');'''.format(user.getId(), self.getId(), userRating))
        systemdb.commit()
        #when the title has been rated by the user, it is removed from the unseenTitles table in the database,
        #so that when the titles are next loaded into the system, the user does not rerate titles
        c.execute('''DELETE FROM unseenTitles where imdbId = '{}' AND userId = '{}';'''.format(self.getId(), user.getId()))
        systemdb.commit()
        c.close()

    def getRating(self, user):
        global systemdb
        #gets users rating of a title from the external database
        c = systemdb.cursor(buffered=True)
        c.execute('''SELECT rating FROM usersRatedTitles WHERE imdbId = '{}' AND userId = '{}';'''.format(self.getId(), user.getId()))
        systemdb.commit()
        rows = c.fetchall()
        rating = rows[0][0]
        c.close()
        
        return rating

#Queue Classes
class TitleQueue(object):
    #Operates as a linear queue
    def __init__(self, maxsize):
        self._usedPositions = 0
        self._maxsize = maxsize
        self._dataset = [None] * maxsize
        self._front = 0
        self._rear = 0


    def getUsedPositions(self):
        return self._usedPositions

    def getMaxsize(self):
        return self._maxsize

    def getFront(self):
        return self._front

    def getRear(self):
        return self._rear

    def getDataset(self):
        return self._dataset

    def incrementUsedPositions(self):
        self._usedPositions += 1

    def decrementUsedPositions(self):
        self._usedPositions -= 1

    def setFront(self):
        self._front += 1

    def isFull(self):
        if self._usedPositions == self._maxsize:
            return True

    def isEmpty(self):
        if self.getUsedPositions() == 0:
            return True
        else:
            return False

    def enqueue(self, data):
        if self.isFull() == True:
            return "Queue is full"

        if self._usedPositions > 0:
            self._rear += 1

        self._dataset[self._rear] = data
        self.incrementUsedPositions()

    def dequeue(self):
        data = None

        if self.isEmpty() == True:
            return "Queue is empty"

        data = self._dataset[self._front]
        if self._front == self._rear:
            self._front = 0
            self._rear = 0
            self._usedPositions = 0
        else:
            self._front += 1
            self.decrementUsedPositions()

        return data

class TitlePriorityQueue(TitleQueue):
    #Customised to operate as a priority queue with priority scores based on user's previous rating activity
    def __init__(self,maxsize):
        super().__init__(maxsize)

    def setPriorityScores(self, user):
    #goes through each item in the items left in the unseen queue
        score = 0
        #works similar to getting a predicted rating for each title, but instead it is used to get a priority score for each title in the system's priority queue to be sorted dynamically
        for i in range(self.getRear(), self.getFront(), -1):
            for j in range(0, len(self.getDataset()[i].getGenres())):
                    if self.getDataset()[i].getGenres()[j] in user.getRatedGenres():
                            score += user.getGenreScores()[self.getDataset()[i].getGenres()[j]]["averageRating"]

            

            #produces an average of that score (doesn't necessarily have to fit a scale of 1-5)
            score = round(score / len(self.getDataset()[i].getGenres()))
            #sets title's priority score
            self.getDataset()[i].setPriorityScore(score)

    def heapSort(self, user):
        #gets length of dataset - adjusted to demonstrate length of the queue
        n = self.getRear() - self.getFront()
        
        #creates arbitary scores for titles which have not yet been rated by the user based on user profile data
        self.setPriorityScores(user)

        #creates a maximum heap
        for i in range((n//2), self.getFront(), -1):
            self.heapify(self.getDataset(), n, i)

        #heap sorts elements, one by one
        for j in range(n, self.getFront(), -1):
            self.getDataset()[j], self.getDataset()[self.getFront()] = self.getDataset()[self.getFront()], self.getDataset()[j]
            self.heapify(self.getDataset(), j, self.getFront())

        #updates dataset into the main program
        #return self.getDataset()

    def heapify(self, dataset, n, index):
        #sets up heap, with largest element as the root
        largest = index
        left = (index * 2) + 1
        right = (index * 2) + 2
        #checks if the left child of the root exists and if its greater than the root
        if left < n and dataset[largest].getPriorityScore() < dataset[left].getPriorityScore():
            #dataset[largest], dataset[left] = dataset[left],dataset[largest]
            largest = left

        #checks if the right child of the root exists and if its greater than the root
        if right < n and dataset[largest].getPriorityScore() < dataset[right].getPriorityScore():
            #dataset[largest], dataset[right] = dataset[right], dataset[largest]
            largest = right

        #changes root if needed
        if largest != index:
            dataset[index], dataset[largest] = dataset[largest], dataset[index]


            #recursive call of function until fully sorted
            self.heapify(dataset, n, largest)


def getPriority(elem):
    return elem.getPriorityScore()

#Recommender System Class
class RecommenderSystem():
    def __init__(self):
        #queue to store titles that the user skipped when rating titles and any other titles the user is yet to rate on the system
        self._unseenQueue = TitlePriorityQueue(200)
        #keeps a track of how many titles the user has rated in one rating session
        self._rateTracker = 0

    def incrementRateTracker(self):
        self._rateTracker += 1

    def getRatingTracking(self):
        return self._rateTracker

    def resetRateTracker(self):
        self._rateTracker = 0


    def getUnseenQueue(self):
        return self._unseenQueue

    def createTitleObjects(self, dataset):
        for item in dataset:
            titleobject = convertIdToTitleObject(item)
            self.getUnseenQueue().enqueue(titleobject)

    def generateRecommendations(self, user):
        global systemdb



        #updates cosine similarity between user and their followings
        for following in user.getFollowings():
            self.updateUsersSimilarity(user, following)

        c = systemdb.cursor(buffered=True)

        c.execute('''SELECT genre FROM ratingsMatrix WHERE userId = '{}';'''.format(user.getId()))
        systemdb.commit()
        ratedGenres_query = c.fetchall()
        ratedGenres = []
        for row in ratedGenres_query:
            ratedGenres.append(row[0])

        #create a queue object of remaining titles
        for genre in user.getGenreScores():
            user.getGenreScores()[genre]["averageRating"] = user.getGenreScores()[genre]["averageRating"] / user.getGenreScores()[genre]["timesRated"]
            if genre in ratedGenres:
                c.execute('''UPDATE ratingsMatrix SET averageRating = '{}' WHERE userId = '{}' AND genre = '{}';'''.format(round(user.getGenreScores()[genre]["averageRating"], 2), user.getId(), genre))
                systemdb.commit()
                c.execute('''UPDATE ratingsMatrix SET timesRated = '{}' WHERE userId = '{}' AND genre = '{}';'''.format(round(user.getGenreScores()[genre]["timesRated"], 2), user.getId(), genre))
                systemdb.commit()
            else:
                c.execute('''INSERT INTO ratingsMatrix (userId, genre, averageRating, timesRated) VALUES ('{}', '{}', '{}', '{}');'''.format(user.getId(), genre, round(user.getGenreScores()[genre]["averageRating"], 2), user.getGenreScores()[genre]["timesRated"]))
                systemdb.commit()
        c.close()
            

        for j in range(system.getUnseenQueue().getFront(), system.getUnseenQueue().getRear()):
            title = system.getUnseenQueue().getDataset()[j]
            unseenTitle_genres = title.getGenres()
            predictedRating = 0

            for genre in user.getGenreScores():
                if genre in unseenTitle_genres:
                    predictedRating += user.getGenreScores()[genre]["averageRating"]

            predictedRating = round((predictedRating / len(unseenTitle_genres)),2)

            if predictedRating >= 3:
                user.setRecommendations(title, predictedRating)
            else:
                #27/02/21 - WISHLIST: REMOVE TITLE FROM RECOMMENDATION IF THE UPDATED PREDICTED RATING IS NOW LESS THAN THREE (Resolved 03/04/21)
                #If the title will not be recommended to the user
                c = systemdb.cursor(buffered=True)
                unseenTitlesCheck = getUnseenTitles(user)

                #if applicable, removes any titles that have a rating of less than 3 that were previously recommended from the
                #recommdendations table

                c.execute('''SELECT imdbId FROM recommendations WHERE imdbId = '{}' AND userId = '{}';'''.format(title.getId(), user.getId()))
                systemdb.commit()
                removeRecommendations = c.fetchall()

                
                if removeRecommendations != []:
                    titleToRemove = removeRecommendations[0][0]
                    c.execute('''DELETE FROM recommendations WHERE imdbId = '{}' AND userId = '{}';'''.format(titleToRemove, user.getId()))
                    systemdb.commit()
                    c.execute('''UPDATE unseenTitles SET recommended = FALSE WHERE imdbId = '{}' AND userId = '{}';'''.format(titleToRemove, user.getId()))
                    systemdb.commit()

                if title.getId() in unseenTitlesCheck:
                    c.execute('''UPDATE unseenTitles SET predictedRating = '{}' WHERE imdbId = '{}' AND userId = '{}';'''.format(predictedRating, title.getId(), user.getId()))
                    systemdb.commit()
                else:
                    c.execute('''INSERT INTO unseenTitles (userId, imdbId, predictedRating, recommended) VALUES ('{}', '{}', '{}', FALSE)'''.format(user.getId(), title.getId(), predictedRating))
                    systemdb.commit()
                c.close()

        if user.getFollowings() != []:
            self.integrateRecommendations(user)

    #user1 - object, user2 - string (username)
    def setUpVectors(self, user1, user2):
        global systemdb
        values_user1 = []
        values_user2 = []
        c = systemdb.cursor(buffered=True)
        #gets user2's id directly from database
        user2Id = getUser2Id(user2)
        #saves list of user2's rated genres
        c.execute('''SELECT genre FROM ratingsMatrix WHERE userId = '{}';'''.format(user2Id))
        systemdb.commit()
        user2_ratedGenres_query = c.fetchall()
        user2_ratedGenres = []
        for row in user2_ratedGenres_query:
            user2_ratedGenres.append(row[0])

        c.close()
        #prevents database locking from too many queries -
        #this will hopefully not be needed as much when switching to a multiuser remote SQL database
        c = systemdb.cursor(buffered=True)

        #creates 2 1xn (where n is the number of genres rated by user1) for user1 and user 2 -
        #the user's following, with the elements being the average
        #rating of that genre by both users respectively (or zero if user2 has not rated that genre)
        user1.createGenreScoresExternal()

        for genre in user1.getGenreScoresExternal():
            values_user1.append([user1.getGenreScoresExternal()[genre]["averageRating"]])
            if genre in user2_ratedGenres:
                c.execute('''SELECT averageRating FROM ratingsMatrix WHERE userId = '{}' AND
genre = '{}';'''.format(user2Id, genre))
                systemdb.commit()
                genreRating_query = c.fetchall()
                genreRating = genreRating_query[0][0]
                values_user2.append([genreRating])
            else:
                values_user2.append([0])
        c.close()

        #using the python library numPy
        user1Vector = np.array(values_user1)
        user2Vector = np.array(values_user2)

        return user1Vector, user2Vector


    def dotProduct1byN(self, a, b):
        dotProduct = 0
        for i in range(0,len(a)):
            dotProduct += a[i][0] * b[i][0]

        return dotProduct
        

    def calcMagnitude(self, vector):
        vector_magnitude = 0
        for i in range(0, len(vector)):
            vector_magnitude += (vector[i][0]**2)

        return vector_magnitude

    def calcSimilarity(self, user1Vector, user2Vector, user1, user2):
        global systemdb

        #uses pre-built library to calculate the dot product of the vectors
        dotProduct = self.dotProduct1byN(user1Vector, user2Vector)

        #calculates the magnitude of both vectors
        user1Vector_magnitude = self.calcMagnitude(user1Vector)
        user2Vector_magnitude = self.calcMagnitude(user2Vector)

        #calculates cosine similarity
        if user1Vector_magnitude == 0 or user2Vector_magnitude == 0:
            cosineSimilarity = 0
        else:
            #the values should lie between 0 and 2pi (2pi is approximately 6.283185307) - result is in radians
            cosineSimilarity = math.acos(dotProduct / (user1Vector_magnitude * user2Vector_magnitude))

        c = systemdb.cursor(buffered=True)
        #gets user2's id directly from database
        c.execute('''SELECT userId FROM users WHERE username = '{}';'''.format(user2))
        systemdb.commit()
        user2Id = getUser2Id(user2)
        cosineSimilarity = round(cosineSimilarity, 3)
        c.execute('''UPDATE userFollowings SET cosineSimilarity = '{}' where userId = '{}' and user_follows = '{}';'''.format(cosineSimilarity, user1.getId(), user2Id))
        systemdb.commit()
        c.close()

        return cosineSimilarity

    def updateUsersSimilarity(self, user1, user2):
        #updates user's similarity adjacency list
        records = self.setUpVectors(user1, user2)
        user1.setConnectsTo([user2, self.calcSimilarity(records[0], records[1], user1, user2)])


    def integrateRecommendations(self, user):
        global systemdb

        c = systemdb.cursor(buffered=True)
        
        unseen_titles = getUnseenTitles(user)
               
        template = {"title": None, "predictedRating": 0}
        for title in unseen_titles:
            template["title"] = title
            
            #if rated, gets followings rating of titles that the user is yet to rate that its followings have rated
            c.execute('''SELECT usersRatedTitles.rating FROM usersRatedTitles JOIN userFollowings WHERE userFollowings.user_follows=usersRatedTitles.userId
        AND usersRatedTitles.imdbId = '{}' AND userFollowings.userId = '{}';'''.format(title, user.getId()))
            systemdb.commit()

            ratings_query = c.fetchall()
            if ratings_query != []:            
                #sums up all of these rating
                
                template["predictedRating"] += ratings_query[0][0]

                

                #takes an average
                template["predictedRating"] = round(template["predictedRating"]/len(user.getFollowings()), 2)
                #if predicted rating is more than 3 it is added to the user's recommendations
                if template["predictedRating"] >= 3:
                    user.setRecommendations(template["title"], template["predictedRating"])

            template = {"title": None, "predictedRating": 0}

        c.close()
                
                           
    def addToUnseenQueue(self, user, title, window, rateCapacity):
        global system
        #Enqueues title back to unseen queue
        self._unseenQueue.enqueue(title)

        #Updates number of rating tracker
        system.incrementRateTracker()
        temp = window.master
        window.destroy()

        #resolving wishlist to add a 'penalty' to the genre scores of genres included
        #in a title that has been skipped to inform the user that the user may be less
        #familiar/less likely to enjpy similar titles (useful to heap sorting in the
        #priority queue

        #use of -0.01 and negative sampling is used

        template = {"averageRating": 0, "timesRated": 0}
        self.updateScores(user, title.getGenres(), template, -0.01)

        #refreshes the window
        refreshWindow(temp, user, rateCapacity)
        

    def saveRating(self, user, title, rating, window, rateCapacity):
        global system
        
        system.incrementRateTracker()
        #Saves user rating to the database
        title.setRating(user, rating)

        template = {"genre": None, "averageRating": 0, "timesRated": 0}

        #What does this do? Resolved (it updates genre scores)
        
        self.updateScores(user, title.getGenres(), template, title.getRating(user))

        temp = window.master
        window.destroy()

        refreshWindow(temp, user, rateCapacity)

    def updateScores(self, user, ratedGenres, template, titleRating):
        for i in range(0, len(ratedGenres)):
            if ratedGenres[i] in user.getRatedGenres():
                for genre in user.getGenreScores():
                    if genre == ratedGenres[i]:
                        user.getGenreScores()[genre]["averageRating"] += titleRating
                        user.getGenreScores()[genre]["timesRated"] += 1
            else:
                template["averageRating"] = titleRating
                template["timesRated"] += 1
                user.setGenreScores(ratedGenres[i], template)
                user.setRatedGenres(ratedGenres[i])
                
            template = {"averageRating": 0, "timesRated": 0}

    
def refreshWindow(window, user, rateCapacity):
    global system

    system.getUnseenQueue().heapSort(user)

    if system.getRatingTracking() >= int(rateCapacity) or system.getUnseenQueue().isEmpty() == True:
        #rating session is complete so the system resets its rating tracker
        system.resetRateTracker()
        #Recommendations loaded to database
        system.generateRecommendations(user)
    else:    
        showRatingsWindow(window, user, rateCapacity)

def showRatingsWindow(window, user, rateCapacity):
    global system, title_title, title_image, star_1, star_2, star_3, star_4, star_5
    #Builds the layout of the ratings window
    title = system.getUnseenQueue().dequeue()

    ratingWindow = Window(window, title="Rating Movies", height=700, width=500, bg=colorWidget('Window'))
    ratingWindow.when_closed = lambda:closeWindow('ratingWindow', ratingWindow)

    rateBox = Box(ratingWindow, align="bottom")
    titleBox = Box(ratingWindow, align="top")


    coverImage_data = requests.get(title.getcoverImage()).content
    with open('coverImage.png', 'wb') as image:
        image.write(coverImage_data)

    title_title = Text(titleBox, text=title.getTitle(), color=colorWidget('Text'))
    title_image = Picture(titleBox, image='coverImage.png')
    title_image.resize(300, 446)

    #Remember to change these buttons to star icons at the end of primary development
    star = "staricon.png"
    star_1 = PushButton(rateBox, image=star, command=lambda:system.saveRating(user, title, 1, ratingWindow, rateCapacity), align="left")
    star_2 = PushButton(rateBox, image=star, command=lambda:system.saveRating(user, title, 2, ratingWindow, rateCapacity), align="left")
    star_3 = PushButton(rateBox, image=star, command=lambda:system.saveRating(user, title, 3, ratingWindow, rateCapacity), align="left")
    star_4 = PushButton(rateBox, image=star, command=lambda:system.saveRating(user, title, 4, ratingWindow, rateCapacity), align="left")
    star_5 = PushButton(rateBox, image=star, command=lambda:system.saveRating(user, title, 5, ratingWindow, rateCapacity), align="left")
    unseenTitle_btn = PushButton(rateBox, text="Skip", command = lambda:system.addToUnseenQueue(user, title, ratingWindow, rateCapacity))
    unseenTitle_btn.bg = colorWidget('Push Button')
    star_1.resize(30,30)
    star_2.resize(30,30)
    star_3.resize(30,30)
    star_4.resize(30,30)
    star_5.resize(30,30)
   
def initialiseRatingsWindow(window, user, rateCapacity):
    global system

    #current bug needs to be fixed, backtracking to previously working version
##    if isWindowOpen('ratingWindow') == True:
##        #window is already open
##        pass
##    else:
##        showRatingsWindow(window, user, rateCapacity)

    showRatingsWindow(window, user, rateCapacity)

    
def logOffUser(user, window):
    global systemdb
    c = systemdb.cursor(buffered=True)
    #informs the external database that the user has now logged off
    c.execute('''UPDATE users SET loggedIn = 0 WHERE username = '{}';'''.format(user.getUsername()))
    systemdb.commit()
    c.close()
    window.destroy()

def viewFollowers(user, window):
    global systemdb

    #checks if the followers window is already open
    if isWindowOpen('followersWindow') == True:
        pass
    else:
        followersWindow = Window(window, title=user.getUsername() + "'s followers", bg=colorWidget('Window'))
        followersWindow.when_closed = lambda:closeWindow('followersWindow', followersWindow)
        #grabs users followers from SQL database
        c = systemdb.cursor(buffered=True)
        followers = []
        
        c.execute('''SELECT userFollowers.user_followedBy, users.username FROM
    userFollowers JOIN users WHERE userFollowers.user_followedBy=users.userId AND userFollowers.userId = '{}';'''.format(user.getId()))
        systemdb.commit()

        followersQuery = c.fetchall()
        for row in followersQuery:
            if row[1] not in user.getFollowers():
                user.getFollowers().append(row[1])

        c.close()

        txt_followers = Text(followersWindow, text="Your Followers", color=colorWidget('Text'))
        followersList = ListBox(followersWindow, items=user.getFollowers())
        followersList.text_color = colorWidget('Text')

def viewFollowings(user, window):
    global systemdb
    #checks if the followings window is already open
    if isWindowOpen('followingsWindow') == True:
        pass
    else:
        followingsWindow = Window(window, title=user.getUsername() + "'s followings", bg=colorWidget('Window'))
        followingsWindow.when_closed = lambda:closeWindow('followingsWindow', followingsWindow)
        
        #grabs users followers from SQL database
        c = systemdb.cursor(buffered=True)
        followings = []

        c.execute('''SELECT userFollowings.user_follows, users.username FROM
    userFollowings JOIN users WHERE userFollowings.user_follows=users.userId AND userFollowings.userId='{}';'''.format(user.getId()))
        systemdb.commit()
        followingsQuery = c.fetchall()
        for row in followingsQuery:
            if row[1] not in user.getFollowings():
                user.getFollowings().append(row[1])

        c.close()

        txt_followings = Text(followingsWindow, text="Who You Follow", color=colorWidget('Text'))
        followersList = ListBox(followingsWindow, items=user.getFollowings())
        followersList.text_color = colorWidget('Text')

def refreshSearchResults(oldresults, newresults):
    #clears previous search results window
    for item in oldresults.items:
        oldresults.remove(item)

    for item in range(0, len(newresults)):
        oldresults.insert(item, newresults[item])

    return oldresults

    
def searchUser(window, user, searchValue):
    #usersList made global so that the variable remains running in memory
    global systemdb, searchResults, usersList
    #allows the user to search for other users on the database
    #12/03/21 - Wishlist - update this so that only one list box is present every time the user presses the 'search' button
    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT * FROM users WHERE username LIKE '%{}%' AND username <> '{}';'''.format(searchValue, user.getUsername()))
    systemdb.commit()
    searchQuery = c.fetchall()
    users = []
    for row in searchQuery:
        users.append(row[1])

    
    if isWindowOpen('resultsWindow') == True:
        refreshSearchResults(usersList, users)

    else:
        resultsWindow = Window(window, title="Search Results", bg=colorWidget('Window'))
        resultsWindow.when_closed = lambda:closeWindow('resultsWindow', resultsWindow)
        usersList = ListBox(resultsWindow, items=users)
        usersList.text_color = colorWidget('Text')
        searchResults = 1
        btn_follow = PushButton(resultsWindow, text="Follow", command=lambda:user.followUser(usersList.value))
        btn_follow.bg = colorWidget('Push Button')
        btn_unfollow = PushButton(resultsWindow, text="Unfollow", command=lambda:user.unfollowUser(usersList.value))
        btn_unfollow.bg = colorWidget('Push Button')
    
def openSearchEngine(user, window):
    global systemdb
    #checks if the window is already open
    if isWindowOpen('searchEngineWindow') == True:
        pass
    else:
        searchEngineWindow = Window(window, title="Follow/Unfollow a User", bg=colorWidget('Window'))
        searchEngineWindow.when_closed = lambda:closeWindow('searchEngineWindow', searchEngineWindow)
    
        #sets up environment to search for users

        lbl_followUser = Text(searchEngineWindow, text="Search for a user: ", color=colorWidget('Text'))
        userToFollow = TextBox(searchEngineWindow)
        userToFollow.text_color = colorWidget('Text')
        search_btn = PushButton(searchEngineWindow, text="Search", command=lambda:searchUser(searchEngineWindow, user, userToFollow.value))
        search_btn.bg = colorWidget('Push Button')

def ShowProfileWindow(window, user):
    global systemdb
    #queries database to log all of users followings to the system

    if isWindowOpen('profileWindow') == True:
        pass
    else:
        profileWindow = Window(window, title=user.getUsername() + "'s Profile", bg=colorWidget('Window'))
        profileWindow.when_closed = lambda:closeWindow('profileWindow', profileWindow)
    
    
        txt_username = Text(profileWindow, text=user.getUsername(), color=colorWidget('Text'))

        buttonsBox = Box(profileWindow)
        btn_followers = PushButton(buttonsBox, text="Followers", command=lambda:viewFollowers(user, profileWindow), align="left")
        btn_followers.bg = colorWidget('Push Button')
        btn_followings = PushButton(buttonsBox, text="Followings", command=lambda:viewFollowings(user, profileWindow), align="left")
        btn_followings.bg = colorWidget('Push Button')
        btn_followAUser = PushButton(buttonsBox, text="Find a User To Follow", command=lambda:openSearchEngine(user, profileWindow), align="bottom")
        btn_followAUser.bg = colorWidget('Push Button')

def goForward(position, recommendationWindow, recommendation, recommendationImage, recommendations):
    global clickForward, clickBackward
    #clears the recommendation window for the next recommendation
    recommendation.destroy()
    recommendationImage.destroy()
    clickForward.destroy()
    clickBackward.destroy()
    
    position += 1
    togglePosition(position, recommendationWindow, recommendations)

def goBackward(position, recommendationWindow, recommendation, recommendationImage, recommendations):
    global clickForward, clickBackward
    #clears the recommendation window and goes back to the previous recommendation
    recommendation.destroy()
    recommendationImage.destroy()
    clickForward.destroy()
    clickBackward.destroy()
    
    position -= 1
    togglePosition(position, recommendationWindow, recommendations)

def togglePosition(position, recommendationsWindow, recommendations):
    global clickForward, clickBackward

    #if the position pointer points to a region outside of the recommendation list's index, the position loops to the opposite side of the list
    if position == -1:
        position = len(recommendations) -1
    if position == len(recommendations):
        position = 0

    #displays the recommendation

    title = recommendations[position]
    coverImage_data = requests.get(title.getcoverImage()).content

    with open('recommendation_coverImage.png', 'wb') as recommendedTitle:
        recommendedTitle.write(coverImage_data)

    recommendation = Text(recommendationsWindow, text=title.getTitle(), color=colorWidget('Text'))
    recommendationImage = Picture(recommendationsWindow, image='recommendation_coverImage.png')
    recommendationImage.resize(300, 446)

    leftButton = "leftarrow.png"
    rightButton = "rightarrow.png"
    clickForward = PushButton(recommendationsWindow, image=rightButton, command=lambda:goForward(position, recommendationsWindow, recommendation, recommendationImage, recommendations), align="right")
    clickForward.resize(20,20)
    clickForward.bg = colorWidget('Push Button')
    clickBackward = PushButton(recommendationsWindow, image=leftButton, command=lambda:goBackward(position, recommendationsWindow, recommendation, recommendationImage, recommendations), align="left")
    clickBackward.resize(20,20)
    clickBackward.bg = colorWidget('Push Button')

def ShowRecommendationsWindow(window, user):
    global systemdb, system

    if len(user.getFollowings()) > 0:
        system.integrateRecommendations(user)
    recommendationsWindow = Window(window, title="Recommendations", height=700, width=500, bg=colorWidget('App'))

    recommendations = []

    c = systemdb.cursor(buffered=True)
    #Grabs all imdb ids from unseenTitles table in database
    c.execute('''SELECT imdbId FROM recommendations WHERE userId = '{}';'''.format(user.getId()))
    systemdb.commit()
    recommendationsQuery = c.fetchall()
    for row in recommendationsQuery:
        titleobject = convertIdToTitleObject(row[0])
        recommendations.append(titleobject)

    #if there are no recommendations, the window displays a 'rate more titles' message - prevents program crashing
    if len(recommendations) == 0:
        errorMessage = Text(recommendationsWindow, text="You currently do not have any recommendations.\nRate more movies to generate recommendations or follow some users.", color=colorWidget('Text'))

    else:
        position = 0
        togglePosition(position, recommendationsWindow, recommendations)
    
def ShowHomePageWindow(user, window):
    #Sets up the layout for the home page window
    window.destroy()
    user.updateFollowings()
    setUpUnseenTitles(user)
    app = App("Rate Movies!", height=250, width=350, bg=colorWidget('App'))
    app.when_closed=lambda:logOffUser(user, app)

    welcome = Text(app, text="Welcome " + user.getUsername() + "!", color=colorWidget('Text'))

    setToRate_lbl = Text(app, text="Number of titles to rate:", color=colorWidget('Text'))

    setMoviesToRate = Combo(app, options=[5,10,15,20,25,30])
    setMoviesToRate.bg = colorWidget('Combo')

    buttonsBox = Box(app, height=100, width=500)
    #use of lambda function to prevent the button function accidently running automatically
    #Use of align left to group together horizontally, in order
    recommendationsButton = PushButton(buttonsBox, text="Recommended Titles", command=lambda:ShowRecommendationsWindow(app, user), align="left")
    recommendationsButton.bg = colorWidget('Push Button')
    ratingsButton = PushButton(buttonsBox, text="Start Rating", command=lambda:initialiseRatingsWindow(app, user, setMoviesToRate.value), align="left")
    ratingsButton.bg = colorWidget('Push Button')
    profileButton = PushButton(buttonsBox, text="See Profile", command=lambda:ShowProfileWindow(app, user), align="left")
    profileButton.bg = colorWidget('Push Button')

    app.display()

def viewInstructions(window):
    instructions_text = '''Welcome to Rate It!\n \n A Social Recommender System that lets you customise which users can help influence what you are recommended.
\n \n Colour Theme (Light or Dark Mode) \n \n You can choose the color theme for this application from the menu bar and this will be updated for all other windows.\n \nRating Titles\n
You can set how many titles you wish to rate in one session in the home page window.\n Titles can be rated on a scale of 1-5 from left to right.
If you haven't seen the title before, you can press the skip button.\n \n Viewing Recommendations\n
When viewing recommendations you can view all recommendations\n based on what you have rated and what your top followings have rated.
\n \nFollowing Other Users\nIn the 'See Profile' window you can view your existing followers and followings. You can open the search engine to
find other users on the system and follow/unfollow them.'''
    if isWindowOpen('instructionsWindow') == False:
        instructionsWindow = Window(window, title="Instructions", bg=colorWidget('Window'), height=500, width=900)
        instructionsWindow.when_closed = lambda:closeWindow('instructionsWindow', instructionsWindow)
        instructions = Text(instructionsWindow, text=instructions_text, color=colorWidget('Text'))

def viewCredits(window):
    credits_text = '''Developer: Jadesola Bejide\n \n Github: www.github.com/jade-bejide \n \n Title Data Source: IMDb database (via the OMDb API)'''
    if isWindowOpen('creditsWindow') == False:
        creditsWindow = Window(window, title="Credits", bg=colorWidget('Window'))
        creditsWindow.when_closed = lambda:closeWindow('creditsWindow', creditsWindow)
        credits_text = Text(creditsWindow, text=credits_text, color=colorWidget('Text'))
        

def ShowLoginScreen():
    #sets up the layout for the log in screen
    app = App("Login in to 'Rate Movies!'", height=250, width=300, bg=colorWidget('App'))

    #menu window so that users can view instructions
    menubar = MenuBar(app, toplevel=["Instructions", "Credits", "Theme"],
                      options=[
                    
                      [["View Instructions", lambda:viewInstructions(app)]],
                      [["Show Credits", lambda:viewCredits(app)]],
                      [["Light Mode", lambda:chooseTheme('Light Mode')], ["Dark Mode", lambda:chooseTheme('Dark Mode')]]
                      ])

    menubar.bg = colorWidget('Combo')

    #check to see if the user is new or existing

    welcome = Text(app, text='Welcome to "Rate Movies!"', color=colorWidget('Text'))
    new_users = PushButton(app, command=lambda:ShowNewUserWindow(app), text="New User")
    new_users.bg = colorWidget('Push Button')
    existing_users = PushButton(app, command=lambda:ShowExistingUserWindow(app), text="Existing User")
    existing_users.bg = colorWidget('Push Button')
    
    app.display()

def ShowNewUserWindow(app):
    global Users
    #checks if the window is already open
    if isWindowOpen('newUserWindow') == False:

        newUserWindow = Window(app, title="Create an account", bg=colorWidget('App'))
        newUserWindow.when_closed = lambda:closeWindow('newUserWindow', newUserWindow)
        #sets up the layout for the new user window
        
        

        welcome_newUser = Text(newUserWindow, text="Create an account", color=colorWidget('Text'))
        username_label = Text(newUserWindow, text="Username: ", color=colorWidget('Text'))
        newUser_inputUsername = TextBox(newUserWindow)
        newUser_inputUsername.text_color = colorWidget('Text')
        password_label = Text(newUserWindow, text="Password: ", color=colorWidget('Text'))
        newUser_inputPassword = TextBox(newUserWindow, hide_text=True)
        newUser_inputPassword.text_color = colorWidget('Text')
        password2_label = Text(newUserWindow, text="Enter password again: ", color=colorWidget('Text'))
        newUser_inputPasswordAgain = TextBox(newUserWindow, hide_text=True)
        newUser_inputPasswordAgain.text_color = colorWidget('Text')
        newUser_createAccount = PushButton(newUserWindow, text="Create Account", command=lambda:createAccount(newUser_inputUsername.value, newUser_inputPassword.value, newUser_inputPasswordAgain.value, newUserWindow))
        newUser_createAccount.bg = colorWidget('Push Button')

def ShowExistingUserWindow(app):
    #checks if the window is already open
    if isWindowOpen('existingUserWindow') == True:
        pass
    else:
        existingUserWindow = Window(app, title="Login into an existing account", bg=colorWidget('App'))
        existingUserWindow.when_closed = lambda:closeWindow('existingUserWindow', existingUserWindow)
        #sets up the layout for the existing user window
        

        welcome_existingUser = Text(existingUserWindow, text="Login to your account", color=colorWidget('Text'))
        username_label = Text(existingUserWindow, text="Username: ", color=colorWidget('Text'))
        existingUser_inputUsername = TextBox(existingUserWindow)
        existingUser_inputUsername.text_color = colorWidget('Text')
        password_label = Text(existingUserWindow, text="Password: ", color=colorWidget('Text'))
        existingUser_inputPassword = TextBox(existingUserWindow, hide_text=True)
        existingUser_inputPassword.text_color = colorWidget('Text')
        existingUser_LogIn = PushButton(existingUserWindow, text="Login", command=lambda:authenticateUser(existingUser_inputUsername.value, existingUser_inputPassword.value, existingUserWindow))
        existingUser_LogIn.bg = colorWidget('Push Button')

#Password and Username authentication subroutines
def ShowInsufficientPasswordWindow(window):
    insufficientDetails= Text(window, text="Password is insufficient", color=colorWidget('Text'))
    
def ShowUsernameErrorWindow(window):
    usernameError = Text(window, text="Username is already taken.", color=colorWidget('Text'))

def ShowUsernameLengthWindow(window):
    usernameLengthError = Text(window, text="Usernames must be 5 characters or more.", color=colorWidget('Text'))

def ShowUsernameFirstCharWindow(window):
    usernameFirstCharError = Text(window, text="Usernames must begin with a letter.", color=colorWidget('Text'))

def ShowPasswordMatchErrorWindow(window):
    passwordMatchError = Text(window, text="Password do not match!", color=colorWidget('Text'))

def ShowFirstCharErrorWindow(window):
    firstCharError = Text(window, text="Passwords must begin with a letter.", color=colorWidget('Text'))

def ShowNoSpacesErrorWindow(window):
    spacesError = Text(window, text="Passwords should not contain spaces.", color=colorWidget('Text'))

def ShowPasswordLengthErrorWindow(window):
    passwordLengthError = Text(window, text="Passwords must be 10 characters or more.", color=colorWidget('Text'))

def ShowNoSuchUserWindow(window):
    noSuchUserError = Text(window, text="No such user exists in the database.", color=colorWidget('Text'))

def ShowIncorrectDetailsWindow(window):
    #later expand to create a cap on how many times a user can attempt to log in before their account is locked
    incorrectDetailsError = Text(window, text="Incorrect Password details!", color=colorWidget('Text'))

def createAccount(username, password, authenticate, window):
    #creates an account for a new user, instatiating an object for the user's current log in session as well as recording
    #their details in the external database
    global systemdb, Users
    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT username FROM users;''')
    systemdb.commit()
    usernames = c.fetchall()
    usernames_list = []
    for row in usernames:
        usernames_list.append(row[0])
    c.close()
        
    if username not in usernames_list:
        if validateUsername(username, window) == True and validatePassword(password, authenticate, window) == True:
            passwordHashed = hashPassword(password)
            #user = Users(username, passwordHashed)
            c = systemdb.cursor(buffered=True)
            c.execute('''INSERT INTO users (username, password, loggedIn) VALUES('{}', '{}', TRUE);'''.format(username, passwordHashed))
            systemdb.commit()
            c.close()
            user = Users(username, passwordHashed)
            ShowHomePageWindow(user, window.master)
            
    else:
        ShowUsernameErrorWindow(window)

def validateUsername(username, window):
    #usernames must be 5 characters or more

    if len(username) < 5:
        ShowUsernameLengthWindow(window)

    #usernames must not start with a special character

    elif username[0].isalnum() == False or username[0].isdigit() == True:
        ShowUsernameFirstCharWindow(window)

    else:
        return True

def validatePassword(password, passwordAgain, window):
    #check if passwords match
    if password != passwordAgain:
        ShowPasswordMatchErrorWindow(window)
        return False

    if len(password) < 10:
        ShowPasswordLengthErrorWindow(window)
    else:
        noNumber = 0
        noSpecialChar = 0
        noUpperChar = 0
        noLowerChar = 0

        #checks if the password begins with a letter

        if password[0].isdigit() == True or password[0].isalnum() == False:
            ShowFirstCharErrorWindow(window)
        else:

            for i in range(0 ,len(password)):
                #switch case statements to test the security
                if password[i].isdigit():
                    noNumber += 1
                elif password[i].isalnum() == False:
                    noSpecialChar += 1
                elif password[i].isupper():
                    noUpperChar += 1
                elif password[i].islower():
                    noLowerChar += 1

                elif password[i].isspace() or password[i] == " ":
                    ShowNoSpacesErrorWindow(window)
                    return False

            if noNumber < 1 or noSpecialChar < 1 or noUpperChar < 1 or noLowerChar < 1:
                ShowInsufficientPasswordWindow(window)
            else:
                return True

def authenticateUser(username, password, window):
    global systemdb, Users
    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT username FROM users;''')
    systemdb.commit()
    
    usernames_list = []
    usernames = c.fetchall()
    for row in usernames:
        
        usernames_list.append(row[0])

    c.close()

    #checks if such a user exists in the database
    if username not in usernames_list:
        ShowNoSuchUserWindow(window)
        return False

    c = systemdb.cursor(buffered=True)
    c.execute('''SELECT password FROM users WHERE username='{}';'''.format(username))
    systemdb.commit()
    passwordMatch_query = c.fetchall()
    passwordMatch = passwordMatch_query[0][0]

    c.close()
    #hash look up for the password
    password = hashPassword(password)

    #authenticates the user's password
    if password != passwordMatch:
        ShowIncorrectDetailsWindow(window)
    else:
        user = Users(username, password)
        c = systemdb.cursor(buffered=True)
        #notifies the program that the user has logged into the system
        c.execute('''UPDATE users SET loggedIn = 1 WHERE username = '{}';'''.format(username))
        systemdb.commit()
        c.close()

        ShowHomePageWindow(user, window.master)

def hashPassword(password):
    #converts password to decimal value

    decimalValue = 0
    for i in range(0, len(password)):
        decimalValue += ord(password[0])
        #converts decimal value to hexadecimal
        hashed = hex(decimalValue)

    return hashed


#Main Program
system = RecommenderSystem()
ShowLoginScreen()
