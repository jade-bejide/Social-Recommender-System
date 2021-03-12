import sqlite3

##conn = sqlite3.connect(':memory:')

conn = sqlite3.connect('system.db')

#cursor to execute sql
c = conn.cursor()

#later to add ratingId and recommendationId as foreign key

#Users Table
c.execute('''CREATE TABLE users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        loggedIn BOOLEAN NOT NULL        
    )''')
conn.commit()
#Recommendations Table
c.execute('''CREATE TABLE recommendations (
    recommendationId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
)''')
conn.commit()
#Rating Matrix Table  
c.execute('''CREATE TABLE ratingsMatrix (
    ratingId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    genre TEXT NOT NULL,
    averageRating REAL,
    timesRated INTEGER,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
conn.commit()
#User Followers table
c.execute('''CREATE TABLE userFollowers (
    entryId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    user_followedBy INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_followedBy) REFERENCES users(userId)
    )''')

#User Followings table
c.execute('''CREATE TABLE userFollowings (
    entryId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    user_follows INTEGER NOT NULL,
    cosineSimilarity REAL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_follows) REFERENCES users(userId)
    )''')
conn.commit()
#Users rated table
c.execute('''CREATE TABLE usersRatedTitles (
    entryId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    rating INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
conn.commit()
#Unseen Titles table (store predictedRating)
c.execute('''CREATE TABLE unseenTitles (
    entryId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    imdbId TEXT NOT NULL,
    predictedRating DECIMAL,
    recommended BOOLEAN,
    FOREIGN KEY (userId) REFERENCES users(userId)
    )''')
conn.commit()
#similarity table
c.execute('''CREATE TABLE similarity (
    entryId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    user_follows INTEGER NOT NULL,
    cosineSimilarity DECIMAL NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId),
    FOREIGN KEY (user_follows) REFERENCES users(userId)
    )''')

conn.commit()

conn.close()
