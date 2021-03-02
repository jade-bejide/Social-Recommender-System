from guizero import *
import sqlite3
import json
import urllib
import numpy as np
import requests
import random
from PIL import *
import sys

sys.setrecursionlimit(6400)

##12/02/21 To Do:
#Sort Queue based on rated titles

##16/02/21 To Do:
#Sort Queue based on rated titles after 10 titles have been rated

##21/02/21 To Do:
#Further research on binary heaps and priority queues to form my own code because the algorithm isn't working


conn = sqlite3.connect('system.db')

#Load in titles

#Based on IMDb's top 250 and top rated TV shows
imdbIDs = ['0805647', '0468569', '0167260', '0120737', '0133093', '0245429', '0110357', '0088763', '4154796',
           '4633694', '7286456', '8503618', '4154756', '2380307', '2096673', '0993846', '2024544', '1454029',
           '1201607', '0435761', '0892769', '0405159', '0266697', '0137523', '6751668', '1049413', '0910970'
           , '0395169', '0347149', '0266543', '0253474', '0317248', '0198781', '0211915', '0109830',
           '0110912','0108052','0097576','8579674','1950186','8613070','6966692', '1392190','2267998','0986264','0457430',
           '0434409','0096283','0088247','0086190','0083658','0080678', '4786824','8134470','0460681',
           '7569576','11794642','0413573','1190634','0944947','5171438','2442560','1520211','1844624','0386676',
           '10048342','8111088','0903747','0108778','0364845','4574334']


def setUpUnseenTitles():
    global system, imdbIDs, Movie, TVShow

    
    for item in imdbIDs:
        #scraps the data of the imdb
        currentTitle = requests.get("http://www.omdbapi.com/?i=tt" + item + "&apikey=8598b952")

        #Titles the user will rate
        currentTitle = currentTitle.text
        currentTitle = json.loads(currentTitle)
        currentTitle['Genre'] = currentTitle['Genre'].split(", ")

        #The title data is instaniated into an object based on if it is a movie or tv show (this has already been categorised by the API)

        if currentTitle['Type'] == "movie":

            titleobject = Movie(currentTitle['Poster'], currentTitle['Title'], currentTitle['Genre'], item)

        elif currentTitle['Type'] == "series":
            titleobject = TVShow(currentTitle['Poster'], currentTitle['Title'], currentTitle['Genre'], item)


        system.getUnseenQueue().enqueue(titleobject)    

##def setUpRatingQueue(amount):
##    #The value of the drop down menu is passed into the function to define the maxsize of the queue
##    global system, Movie, TVShow
##    amount = int(amount)
##    title_queue = TitlePriorityQueue(amount)
##
##    track= 0
##
##    while track < amount:
##        #Titles are enqueued from the unseen queue ready for the user to rate
##        title = system.getUnseenQueue().dequeue()
##        title_queue.enqueue(title)
##
##        track += 1
##
##    #the title queue object is passed back into the ratings window interface
##    return title_queue

#Users Class
class Users(object):
    def __init__(self, username, password):
        #self._userId = setUserId()
        self._username = username
        self._password = password
        self._recommendations = []
        self._followings = []
        self._followers = []
        self._ratedGenres = []
        self._ratedTitles = []
        self._genreScores = []
        self._connectsTo = {username: {}}

        #insert user into database

    def getId(self):
        global conn

        c = conn.cursor()

        userIdQuery = c.execute('''SELECT userId FROM users WHERE username = '{}';'''.format(self.getUsername()))

        rows = userIdQuery.fetchall()

        userId = rows[0][0]    
        conn.commit()
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

    def setGenreScores(self, score):
        self._genreScores.append(score)

    def getUsername(self):
        return self._username

    def getPassword(self):
        return self._password

    def getConnectsTo(self):
        return self._connectsTo

    def setConnectsTo(self, connection):
        self._connectsTo[self.getUsername()][connection[0]] = connection[1]

    def sortConnections(self):
        self._connectsTo[self.getUsername()] = sorted(self._connectsTo[self.getUsername()], key=self._connectsTo[self.getUsername()].get)
        
    def rate_titles(self, title):
        #show ratings window
        showRatingsWindow(self, title)

    def followUser(self, user):
        global conn
        #sets user to follow desired user
        self._followers.append(user)
        user.setFollower(self)
        '''INSERT INTO user_following (userId, user, user_follows) VALUES (self.getId(), getUsername(), user.getUsername());"'''

    def setFollower(self, user):
        global conn
        #updates user's followers when they are followed

        user._followers.append(user)

        '''INSERT INTO user_followers (userId, user, user_followedBy) VALUES (self.getId(), self.getUsername());"'''

    def setRecommendations(self, title, predictedRating):
        global conn

        
        #updates recommendations in program
        self._recommendations.append(title)

        #saves recommendations externally
        c = conn.cursor()

        unseenTitlesCheck = c.execute('''SELECT imdbId FROM unseenTitles WHERE userId = '{}';'''.format(self.getId()))
        conn.commit()

        #checks if the title is already in the database
        idCheck = []
        for item in unseenTitlesCheck:
            idCheck.append(item[0])

        print("Recommended IDs", idCheck)

        if title.getId() in idCheck:
            #updates unseen titles to include new values if so
            c.execute('''UPDATE unseenTitles SET predictedRating = '{}' AND recommended = TRUE WHERE imdbId = '{}' and userId = '{}';'''.format(predictedRating, title.getId(), self.getId()))
            conn.commit()
        else:
            #otherwise adds the record entry into the database
            c.execute('''INSERT INTO unseenTitles (userId, imdbId, predictedRating, recommended) VALUES ('{}', '{}', '{}', TRUE);'''.format(self.getId(), title.getId(), predictedRating))
            conn.commit()

        c.execute('''INSERT INTO recommendations (userId, imdbId) VALUES ('{}', '{}');'''.format(self.getId(), title.getId()))
        conn.commit()
        c.close()
        
#Titles Class

class Title(object):
    def __init__(self, coverImage, title, genres, imdbId):
        self._coverImage = coverImage
        self._title = title
        self._genres = genres
        self._imdbId = imdbId
        #score used for the priority queue to update (as a binary heap)
        self._priorityScore = 0


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
        global conn
        c = conn.cursor()
        c.execute('''INSERT INTO usersRatedTitles (userId, imdbId, rating) VALUES ('{}', '{}', '{}');'''.format(user.getId(), self.getId(), userRating))
        conn.commit()
        c.close()

    def getRating(self, user):
        global conn
        c = conn.cursor()
        ratingQuery = c.execute('''SELECT rating FROM usersRatedTitles WHERE imdbId = '{}' AND userId = '{}';'''.format(self.getId(), user.getId()))
        rows = ratingQuery.fetchall()
        rating = rows[0][0]
        conn.commit()
        c.close()
        
        return rating

class Movie(Title):
    def __init__(self, titleImage, titleName, genreList, imdbId, titleType = "Movie"):
        super().__init__(titleImage, titleName, genreList, imdbId)
        self._type = titleType

    def getType(self):
        return self._type

class TVShow(Title):
    def __init__(self, titleImage, titleName, genreList, imdbId, titleType = "TV Show"):
        super().__init__(titleImage, titleName, genreList, imdbId)
        self._type = titleType

    def getType(self):
        return self._type

#Queue Classes
class TitleQueue(object):
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
    def __init__(self,maxsize):
        super().__init__(maxsize)

    def setPriorityScores(self, user):
    #goes through each item in the items left in the unseen queue
        score = 0
        #works similar to getting a predicted rating for each title, but instead it is used to get a priority score for each title in the system's priority queue to be sorted dynamically
        for i in range(self.getRear(), self.getFront(), -1):
            for j in range(0, len(self.getDataset()[i].getGenres())):
                for k in range(0, len(user.getRatedGenres())):
                    if self.getDataset()[i].getGenres()[j] == user.getRatedGenres()[k]:
                        for l in range(0, len(user.getGenreScores())):
                            if user.getGenreScores()[l]["genre"] == self.getDataset()[i].getGenres()[j]:
                                score += user.getGenreScores()[l]["averageRating"]

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
        self._unseenQueue = TitlePriorityQueue(100)


    def getUnseenQueue(self):
        return self._unseenQueue

    #Check this class

    def generateRecommendations(self, user):
        global conn
        #create a queue object of remaining titles
        for i in range(0, len(user.getGenreScores())):
            user.getGenreScores()[i]["averageRating"] = user.getGenreScores()[i]["averageRating"] / user.getGenreScores()[i]["timesRated"]

        for j in range(system.getUnseenQueue().getFront(), system.getUnseenQueue().getRear()):
            #unseenTitle = self.getUnseenQueue().dequeue()
            title = system.getUnseenQueue().getDataset()[j]
            unseenTitle_genres = title.getGenres()
            predictedRating = 0

            for i in range(0, len(user.getGenreScores())):
                if user.getGenreScores()[i]["genre"] in unseenTitle_genres:
                    predictedRating += user.getGenreScores()[i]["averageRating"]

            predictedRating = round(((predictedRating / len(unseenTitle_genres)) * 0.85),2)

            if predictedRating >= 3:
                user.setRecommendations(title, predictedRating)
            else:
                #If the title will not be recommended to the user
                c = conn.cursor()
                unseenTitlesCheck = c.execute('''SELECT imdbId FROM unseenTitles WHERE userID = '{}';'''.format(user.getId()))
                conn.commit()
                idCheck = []
                #Checks the there is no record entry for that title id already in the database (to avoid data redundancies)
                for item in unseenTitlesCheck:
                    idCheck.append(item[0])

                print("IDs", idCheck)
                if title.getId() in idCheck:
                    c.execute('''UPDATE unseenTitles SET predictedRating = '{}' WHERE imdbId = '{}' AND userId = '{}';'''.format(predictedRating, title.getId(), user.getId()))
                    conn.commit()
                else:
                    c.execute('''INSERT INTO unseenTitles (userId, imdbId, predictedRating, recommended) VALUES ('{}', '{}', '{}', FALSE)'''.format(user.getId(), title.getId(), predictedRating))
                    conn.commit()
                c.close()

    def setUpVectors(self, user1, user2):
        user1Vector = []
        user2Vector = []

        for i in range(0, len(user1.getRatedTitles())):
            if user1.getRatedTitles()[i] in user2.getRatedTitles():
                user1Vector.append([user1.getRatedTitles()[i], user1.getRatedTitles()[i].getRating(user1)])
                user2Vector.append([user1.getRatedTitles()[i], user1.getRatedTitles()[i].getRating(user2)])
            else:
                user1Vector.append([user1.getRatedTitles()[i], user1.getRatedTitles()[i].getRating(user1)])
                user2Vector.append([user1.getRatedTitles()[i], 0])

        return user1Vector, user2Vector

    def calcMagnitude(self, vector):
        vector_magnitude = 0
        for i in range(0, len(vector)):
            vector_magnitude += (vector[i][1]**2)

        return vector_magnitude

    def calcSimilarity(self, user1Vector, user2Vector):
        #uses pre-built library to calculate the dot product of the vectors
        dotProduct = dot(user1Vector, user2Vector)

        #calculates the magnitude of both vectors
        user1Vector_magnitude = self.calcMagnitude(user1Vector)
        user2Vector_magnitude = self.calcMagnitude(user2Vector)

        #calculates cosine similarity
        cosineSimilarity = dotProduct / (user1Vector_magnitude * user2Vector_magnitude)

        return cosineSimilarity

    def UpdateUsersSimilarity(self, user1, user2, similarity):
        #updates user's similarity adjacency list
        user1.setConnectsTo([user2, self.calcSimilarity(self.setUpVectors(user1, user2))])

        #sorts adjacency list by cosine similarity value to prioritise user's following by who is most similar

        user1.sortConnectsTo()

    def addToUnseenQueue(self, user, title, window, rateCapacity):
        global conn, rateTracker
        #Enqueues title back to unseen queue
        self._unseenQueue.enqueue(title)

        #Updates number of rating tracker
        rateTracker += 1
        temp = window.master
        window.destroy()

        if rateTracker >= int(rateCapacity):
            #generates recommendations automatically when needed
            system.generateRecommendations(user)
        else:
            #refreses the window
            refreshWindow(temp, user, rateCapacity)
        

    def saveRating(self, user, title, rating, window, rateCapacity):
        global rateTracker

        rateTracker += 1
        #Saves user rating to the database
        title.setRating(user, rating)
        
        #Saves user rating to the object (does nothing at the moment)
        self.saveMovieRatingToUser(user, title)

        template = {"genre": None, "averageRating": 0, "timesRated": 0}

        titleGenres = title.getGenres()

        #What does this do? Resolved (it updates genre scores)
        self.updateScores(user, titleGenres, title, template)

        temp = window.master
        window.destroy()

        refreshWindow(temp, user, rateCapacity)

    def updateScores(self, user, ratedGenres, title, template):
        #15/02/21 Logic error where rating is repeatedly added to dictionary due to for loop (Resolved)
        for i in range(0, len(ratedGenres)):
            if ratedGenres[i] in user.getRatedGenres():
                
                for j in range(0, len(user.getGenreScores())):
                    if user.getGenreScores()[j]["genre"] == ratedGenres[i]:
                        user.getGenreScores()[j]["averageRating"] += title.getRating(user)
                        user.getGenreScores()[j]["timesRated"] += 1
            else:
                template["genre"] = ratedGenres[i]
                template["averageRating"] = title.getRating(user)
                template["timesRated"] += 1
                user.setGenreScores(template)
                user.setRatedGenres(ratedGenres[i])
                
            template = {"genre": None, "averageRating": 0, "timesRated": 0}

    def saveMovieRatingToUser(self, user, title):
        pass
    
def refreshWindow(window, user, rateCapacity):
    global system, rateTracker

    system.getUnseenQueue().heapSort(user)

    if rateTracker >= int(rateCapacity):
        #Recommendations loaded to database
        system.generateRecommendations(user)
    else:    
        showRatingsWindow(window, user, rateCapacity)

def showRatingsWindow(window, user, rateCapacity):
    global system, title_title, title_image, star_1, star_2, star_3, star_4, star_5

    #title = system.getUnseenQueue.dequeue()

    title = system.getUnseenQueue().dequeue()

    ratingWindow = Window(window, title="Rating Movies", height=700, width=500)

    rateBox = Box(ratingWindow, align="bottom")
    titleBox = Box(ratingWindow, align="top")


    coverImage_data = requests.get(title.getcoverImage()).content
    with open('coverImage.png', 'wb') as image:
        image.write(coverImage_data)

    title_title = Text(titleBox, text=title.getTitle())
    title_image = Picture(titleBox, image='coverImage.png')
    title_image.resize(300, 446)

    star_1 = PushButton(rateBox, text="1", command=lambda:system.saveRating(user, title, 1, ratingWindow, rateCapacity))
    star_2 = PushButton(rateBox, text="2", command=lambda:system.saveRating(user, title, 2, ratingWindow, rateCapacity))
    star_3 = PushButton(rateBox, text="3", command=lambda:system.saveRating(user, title, 3, ratingWindow, rateCapacity))
    star_4 = PushButton(rateBox, text="4", command=lambda:system.saveRating(user, title, 4, ratingWindow, rateCapacity))
    star_5 = PushButton(rateBox, text="5", command=lambda:system.saveRating(user, title, 5, ratingWindow, rateCapacity))
    unseenTitle_btn = PushButton(rateBox, text="Skip", command = lambda:system.addToUnseenQueue(user, title, ratingWindow, rateCapacity))
   
def initialiseRatingsWindow(window, user, rateCapacity):
    #needs to be fixed to meet testing requirements of test id 6
    global system, rateTracker

    rateTracker = 0

    if rateTracker <= int(rateCapacity):
        showRatingsWindow(window, user, rateCapacity)
    elif rateTracker > int(rateCapacity):
        system.generateRecommendations(user)

    #change to be more OOP friendly later

    #assumes those titles have already been rated
    

    numRatings = 0

    
def logOffUser(user, window):
    global conn
    c = conn.cursor()
    c.execute('''UPDATE users SET loggedIn = 0 WHERE username = "{}"'''.format(user.getUsername()))
    conn.commit()
    c.close()
    window.destroy()

def ShowProfileWindow():
    pass

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

    recommendation = Text(recommendationsWindow, text=title.getTitle())
    recommendationImage = Picture(recommendationsWindow, image='recommendation_coverImage.png')
    recommendationImage.resize(300, 446)

    clickForward = PushButton(recommendationsWindow, text="Next", command=lambda:goForward(position, recommendationsWindow, recommendation, recommendationImage, recommendations), align="right")
    clickBackward = PushButton(recommendationsWindow, text="Back", command=lambda:goBackward(position, recommendationsWindow, recommendation, recommendationImage, recommendations), align="left")

def ShowRecommendationsWindow(window, user):
    global conn
    recommendationsWindow = Window(window, title="Recommendations", height=700, width=500)

    recommendations = []

    c = conn.cursor()
    #Grabs all imdb ids from unseenTitles table in database
    recommendationsQuery = c.execute('''SELECT imdbId FROM recommendations WHERE userId = '{}';'''.format(user.getId()))
    conn.commit()

    for row in recommendationsQuery:
        title = row[0]
                #scraps the data of the imdb
        titleObject = requests.get("http://www.omdbapi.com/?i=tt" + title + "&apikey=8598b952")

        #splits the attributes of the title object
        titleObject = titleObject.text
        titleObject = json.loads(titleObject)
        titleObject['Genre'] = titleObject['Genre'].split(", ")

        #The title data is instaniated into an object based on if it is a movie or tv show (this has already been categorised by the API)

        if titleObject['Type'] == "movie":

            titleobject = Movie(titleObject['Poster'], titleObject['Title'], titleObject['Genre'], title)

        elif titleObject['Type'] == "series":
            titleobject = TVShow(titleObject['Poster'], titleObject['Title'], titleObject['Genre'], title)

        recommendations.append(titleobject)

    #if there are no recommendations, the window displays a 'rate more titles' message - prevents program crashing
    if len(recommendations) == 0:
        errorMessage = Text(recommendationsWindow, text="You currently do not have any recommendations.\nRate more movies to generate recommendations or follow some users.")

    else:
        position = 0
        togglePosition(position, recommendationsWindow, recommendations)
    
def ShowHomePageWindow(user, window):
    window.destroy()
    app = App("Rate Movies!", height=250, width=350)

    welcome = Text(app, text="Welcome " + user.getUsername() + "!")

    setToRate_lbl = Text(app, text="Number of titles to rate:")

    setMoviesToRate = Combo(app, options=[5,10,15,20,25,30])

    buttonsBox = Box(app, height=100, width=500)
    recommendationsButton = PushButton(buttonsBox, text="Recommended Titles", command=lambda:ShowRecommendationsWindow(app, user), align="left")
    ratingsButton = PushButton(buttonsBox, text="Start Rating", command=lambda:initialiseRatingsWindow(app, user, setMoviesToRate.value), align="left")
    profileButton = PushButton(buttonsBox, text="See Profile", command=ShowProfileWindow(), align="right")

    app.on_close(lambda:logOffUser(user, app))
    app.display()
    

def ShowLoginScreen():
    app = App("Login in to 'Rate Movies!'", height=250, width=300)

    #check to see if the user is new or existing

    welcome = Text(app, text='Welcome to "Rate Movies!"')
    new_users = PushButton(app, command=lambda:ShowNewUserWindow(app), text="New User")
    existing_users = PushButton(app, command=lambda:ShowExistingUserWindow(app), text="Existing User")

    app.display()

def ShowNewUserWindow(app):
    global Users
    newUserWindow = Window(app, title="Create an account")
    

    welcome_newUser = Text(newUserWindow, text="Create an account")
    username_label = Text(newUserWindow, text="Username: ")
    newUser_inputUsername = TextBox(newUserWindow)
    password_label = Text(newUserWindow, text="Password: ")
    newUser_inputPassword = TextBox(newUserWindow)
    password2_label = Text(newUserWindow, text="Enter password again: ")
    newUser_inputPasswordAgain = TextBox(newUserWindow)
    newUser_createAccount = PushButton(newUserWindow, text="Create Account", command=lambda:createAccount(newUser_inputUsername.value, newUser_inputPassword.value, newUser_inputPasswordAgain.value, newUserWindow))

def ShowExistingUserWindow(app):
    existingUserWindow = Window(app, title="Login into an existing account")

    welcome_existingUser = Text(existingUserWindow, text="Login to your account")
    username_label = Text(existingUserWindow, text="Username: ")
    existingUser_inputUsername = TextBox(existingUserWindow)
    password_label = Text(existingUserWindow, text="Password: ")
    existingUser_inputPassword = TextBox(existingUserWindow)
    existingUser_createAccount = PushButton(existingUserWindow, text="Login", command=lambda:authenticateUser(existingUser_inputUsername.value, existingUser_inputPassword.value, existingUserWindow))

def ShowInsufficientPasswordWindow(window):
    insufficientDetails= Text(window, text="Password is insufficient")
    
def ShowUsernameErrorWindow(window):
    usernameError = Text(window, text="Username is already taken.")

def ShowUsernameLengthWindow(window):
    usernameLengthError = Text(window, text="Usernames must be 5 characters or more.")

def ShowUsernameFirstCharWindow(window):
    usernameFirstCharError = Text(window, text="Usernames must begin with a letter.")

def ShowPasswordMatchErrorWindow(window):
    passwordMatchError = Text(window, text="Password do not match!")

def ShowFirstCharErrorWindow(window):
    firstCharError = Text(window, text="Passwords must begin with a letter.")

def ShowNoSpacesErrorWindow(window):
    spacesError = Text(window, text="Passwords should not contain spaces.")

def ShowPasswordLengthErrorWindow(window):
    passwordLengthError = Text(window, text="Passwords must be 10 characters or more.")

def ShowNoSuchUserWindow(window):
    noSuchUserError = Text(window, text="No such user exists in the database.")

def ShowIncorrectDetailsWindow(window):
    #later expand to create a cap on how many times a user can attempt to log in before their account is locked
    incorrectDetailsError = Text(window, text="Incorrect Password details!")

def createAccount(username, password, authenticate, window):
    global conn, Users
    c = conn.cursor()
    usernames = c.execute('''SELECT username FROM users;''')
    conn.commit()
    usernames_list = []
    for row in usernames:
        usernames_list.append(row[0])
    c.close()
        
    if username not in usernames_list:
        if validateUsername(username, window) == True and validatePassword(password, authenticate, window) == True:
            passwordHashed = hashPassword(password)
            #user = Users(username, passwordHashed)
            c = conn.cursor()
            c.execute('''INSERT INTO users (username, password, loggedIn) VALUES('{}', '{}', TRUE);'''.format(username, passwordHashed))
            conn.commit()
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
    global conn, Users
    c = conn.cursor()
    usernames = c.execute('''SELECT username FROM users;''')
    conn.commit()
    
    usernames_list = []

    for row in c:
        usernames_list.append(row[0])

    c.close()

    if username not in usernames_list:
        ShowNoSuchUserWindow(window)
        return False

    c = conn.cursor()
    c.execute('''SELECT password FROM users WHERE username=username;''')
    conn.commit()
    for row in c:
        passwordMatch = row[0]

    c.close()
    password = hashPassword(password)

    if password != passwordMatch:
        ShowIncorrectDetailsWindow(window)
    else:
        user = Users(username, password)
        c = conn.cursor()
        c.execute('''UPDATE users SET loggedIn = 1 WHERE username = '{}';'''.format(user.getUsername()))
        conn.commit()
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

setUpUnseenTitles()

ShowLoginScreen()
