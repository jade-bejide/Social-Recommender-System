from mysqlconnection import getSystem

systemdb = getSystem()

c = systemdb.cursor(buffered=True)

###Users Table
##c.execute('''CREATE TABLE users (
##        userId INTEGER PRIMARY KEY AUTO_INCREMENT,
##        username TEXT NOT NULL,
##        password TEXT NOT NULL,
##        loggedIn BOOLEAN NOT NULL        
##    )''')
##systemdb.commit()
#Recommendations Table
c.execute('''CREATE TABLE recommendations (
    recommendationId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
)''')
systemdb.commit()
#Rating Matrix Table  
c.execute('''CREATE TABLE ratingsMatrix (
    ratingId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    genre TEXT NOT NULL,
    averageRating REAL,
    timesRated INTEGER,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
systemdb.commit()
#User Followers table
c.execute('''CREATE TABLE userFollowers (
    entryId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    user_followedBy INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_followedBy) REFERENCES users(userId)
    )''')

#User Followings table
c.execute('''CREATE TABLE userFollowings (
    entryId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    user_follows INTEGER NOT NULL,
    cosineSimilarity REAL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_follows) REFERENCES users(userId)
    )''')
systemdb.commit()
#Users rated table
c.execute('''CREATE TABLE usersRatedTitles (
    entryId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    rating INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
systemdb.commit()
#Unseen Titles table (store predictedRating)
c.execute('''CREATE TABLE unseenTitles (
    entryId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    predictedRating DECIMAL,
    recommended BOOLEAN,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
systemdb.commit()
#similarity table
c.execute('''CREATE TABLE similarity (
    entryId INTEGER PRIMARY KEY AUTO_INCREMENT,
    userId INTEGER NOT NULL,
    user_follows INTEGER NOT NULL,
    cosineSimilarity DECIMAL NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_follows) REFERENCES users(userId)
    )''')

systemdb.commit()

systemdb.close()
