from queue_class import *
#needed to perform linear algebra calculations
import numpy as np

class RecommenderSystem(TitlePriorityQueue):
    def __init__(self, maxsize):
        super.new(maxsize)

    def generateRecommendations(self, user):
        while hiddenTitles.isEmpty() == False:
            useenTitle = hiddenTitles.dequeue()
            unseenTitle_genres = unseenTitle.getGenres()
            predictedRating = 0

            for i in range(0, len(user.getGenreScores())):
                if user.getGenreScores()[i]['genre'] in unseenTitle_genres:
                    predictedRating += user.getGenreScores()[i]['averageRating']

            predictedRating = (predictedRating / len(unseenTitle_genres)) * 0.85

            if predictedRating >= 3:
                user.setRecommendations(unseenTitle)


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

    def saveRating(self, user, title, rating):
        title.setRating(user, rating)

        template = {"genre": None, "averageRating": 0, "timesRated": 0}

        titleGenres = title.getGenres()

        self.updateScores(user, titleGenres, title, template)
        self.saveMovieRatingToUser(user, title)

    def update_scores(user, ratedGenres, title, template):
        for i in range(0, len(ratedGenres)):
            if ratedGenres[i] in user.getRatedGenres():
                for j in range(0, len(user.getGenreScores())):
                    if user.getGenreScores()[j]["genre"] == ratedGenres[i]:
                        template["averageRating"] += title.getRating(user)
                        template["timesRated"] += 1

    def saveMovieRatingToUser(user, title):
        #saves user rating of title to database
        '''INSERT INTO UserRatedTitles (userId, title, rating) VALUES (user.getId(), title.getTitle(), title.getRating(user);'''
    
                       
