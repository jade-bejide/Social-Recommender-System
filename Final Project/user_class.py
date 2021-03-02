##Methods to Add:
#setConnectsTo
#sortConnectsTo
#getConnectsTo

class Users(object):
    def __init__(self, username, password):
        self._userId = setUserId()
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
        return self._userId

    def getRecommendations(self):
        return self._recommendations

    def getRatedGenres(self):
        return self._ratedGenres

    def getRatedTitles(self):
        return self._ratedTitles

    def getGenreScores(self):
        return self._genreScores

    def getUsername(self):
        return self._username

    def getConnectsTo(self):
        return self._connectsTo

    def setConnectsTo(self, connection):
        self._connectsTo[self.getUsername()][connection[0]] = connection[1]

    def sortConnections(self):
        self._connectsTo[self.getUsername()] = sorted(self._connectsTo[self.getUsername()], key=self._connectsTo[self.getUsername()].get)
        
    def rate_titles(self, title):
        #show ratings window

        showRatingsWindow(self, title)

        if ratingQueue.isEmpty() == True:
            rating = False

    def followUser(self, user):
        #sets user to follow desired user
        self._followers.append(user)
        user.setFollower(self)
        '''INSERT INTO user_following (userId, user, user_follows) VALUES (self.getId(), getUsername(), user.getUsername());"'''

    def setFollower(self, user):
        #updates user's followers when they are followed

        user._followers.append(user)

        '''INSERT INTO user_followers (userId, user, user_followedBy) VALUES (self.getId(), self.getUsername());"'''
        
