import sqlite3

conn = sqlite3.connect('system.db')
c = conn.cursor()

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

    def setRating(self, user, userRating):
        import conn, c
        c.execute('''INSERT INTO usersRatedTitles (userId, title, rating) VALUES ('{}', '{}', '{}')'''.format(user.getId(), self, userRating))
        conn.commit()

    def getRating(self, user):
        rating = c.execute('''SELECT rating FROM UserRatedTitles WHERE title = '{}' AND username = '{}';'''.format(self.getTitle(), user.getUsername()))
        conn.commit()

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
