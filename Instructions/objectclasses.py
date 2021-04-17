import mysql.connector
from guizero import *
#from windows import *

import config
import mod

systemdb = mysql.connector.connect(
    host="sql11.freemysqlhosting.net",
    user="sql11399413",
    password="EQ2GCCEILe",
    database="sql11399413"
)

c = systemdb.cursor(buffered=True)

#Users Class
class Users(object):
    def __init__(self, username):
        self._username = username
        self._followings = []
        self._followers = []
        self._ratedGenres = []
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

    def getConnections(self):
        return self._connectsTo

    def setConnectsTo(self, connection):
        self._connectsTo.append(connection)

        self._connectsTo.sort(reverse=True, key=returnSimilarity)

    def followUser(self, user):
        global systemdb
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

            config.system.updateUsersSimilarity(self,user)

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
        global systemdb
        c = systemdb.cursor(buffered=True)
        c.execute('''SELECT users.username FROM users JOIN userFollowings WHERE users.userId=userFollowings.user_follows AND userFollowings.userId = '{}';'''.format(self.getId()))
        systemdb.commit()
        followings_query = c.fetchall()
        for row in followings_query:
            if row not in self.getFollowings():
                self._followings.append(row[0])
                #updates user similarity with their followings
            config.system.updateUsersSimilarity(self, row[0])

        c.close()

    def getFollowings(self):
        return self._followings

    def getFollowers(self):
        return self._followers
       
    def setRecommendations(self, title, predictedRating):
        global systemdb
        
        if isinstance(title, str) == True:
            title = convertIdToTitleObject(title)

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
            

        for j in range(self.getUnseenQueue().getFront(), self.getUnseenQueue().getRear()):
            title = self.getUnseenQueue().getDataset()[j]
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

def returnSimilarity(elem):
    return elem[1]
