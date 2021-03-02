class Title(object):
    def __init__(self, coverImage, title, genres):
        self._coverImage = coverImage
        self._title = title
        self._genres = genres

    def getGenres(self):
        return self._genres

    def getTitle(self):
        return self._title

    def getcoverImage(self):
        return self._coverImage

    def setRating(user, userRating):
        '''UPDATE UserRatedTitles SET rating = userRating WHERE username = user.getUsername();'''

    def getRating(self, user):
        rating = '''SELECT rating FROM UserRatedTitles WHERE title = self.getTitle() AND username = user.getUsername();'''

class Movie(Title):
    def __init__(self, titleImage, titleName, genreList, titleType = "Movie"):
        super().__init__(titleImage, titleName, genreList)
        self._type = titleType

    def getType(self):
        return self._type

class TVShow(Title):
    def __init__(self, titleImage, titleName, genreList, titleType = "TV Show"):
        super().__init__(titleImage, titleName, genreList)
        self._type = titleType

    def getType(self):
        return self._type
