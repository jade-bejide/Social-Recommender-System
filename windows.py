from guizero import *
import json
import urllib
import requests
import mysql.connector
import random

import config
import mod
from objectclasses import *
from themeControllers import *


import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import mysqlconnection

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

def addToUnseenQueue(user, title, window, rateCapacity):
        #Enqueues title back to unseen queue
        config.system.getUnseenQueue().enqueue(title)

        #Updates number of rating tracker
        config.system.incrementRateTracker()
        temp = window.master
        window.destroy()

        #resolving wishlist to add a 'penalty' to the genre scores of genres included
        #in a title that has been skipped to inform the user that the user may be less
        #familiar/less likely to enjpy similar titles (useful to heap sorting in the
        #priority queue

        #use of -0.01 and negative sampling is used

        template = {"averageRating": 0, "timesRated": 0}
        config.system.updateScores(user, title.getGenres(), template, -0.01)

        #refreshes the window
        refreshWindow(temp, user, rateCapacity)
        

def saveRating(user, title, rating, window, rateCapacity):
    #updates the relevant titles and genre scores with the user's rating of the title
        config.system.incrementRateTracker()
        #Saves user rating to the database
        title.setRating(user, rating)

        template = {"genre": None, "averageRating": 0, "timesRated": 0}

        #What does this do? Resolved (it updates genre scores)
        
        config.system.updateScores(user, title.getGenres(), template, title.getRating(user))

        temp = window.master
        window.destroy()

        refreshWindow(temp, user, rateCapacity)
def refreshWindow(window, user, rateCapacity):
    #Loads the next title to be rated
    config.system.getUnseenQueue().heapSort(user)

    if config.system.getRatingTracking() >= int(rateCapacity) or config.system.getUnseenQueue().isEmpty() == True:
        #rating session is complete so the system resets its rating tracker
        config.system.resetRateTracker()
        #Recommendations loaded to database
        config.system.generateRecommendations(user)
    else:    
        showRatingsWindow(window, user, rateCapacity)

def showRatingsWindow(window, user, rateCapacity):
    global title_title, title_image, star_1, star_2, star_3, star_4, star_5
    #Builds the layout of the ratings window
    title = config.system.getUnseenQueue().dequeue()

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
    star_1 = PushButton(rateBox, image=star, command=lambda:saveRating(user, title, 1, ratingWindow, rateCapacity), align="left")
    star_2 = PushButton(rateBox, image=star, command=lambda:saveRating(user, title, 2, ratingWindow, rateCapacity), align="left")
    star_3 = PushButton(rateBox, image=star, command=lambda:saveRating(user, title, 3, ratingWindow, rateCapacity), align="left")
    star_4 = PushButton(rateBox, image=star, command=lambda:saveRating(user, title, 4, ratingWindow, rateCapacity), align="left")
    star_5 = PushButton(rateBox, image=star, command=lambda:saveRating(user, title, 5, ratingWindow, rateCapacity), align="left")
    unseenTitle_btn = PushButton(rateBox, text="Skip", command = lambda:addToUnseenQueue(user, title, ratingWindow, rateCapacity))
    unseenTitle_btn.bg = colorWidget('Push Button')
    star_1.resize(30,30)
    star_2.resize(30,30)
    star_3.resize(30,30)
    star_4.resize(30,30)
    star_5.resize(30,30)

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
    #displays the layout for the recommendations window
    global systemdb

    if len(user.getFollowings()) > 0:
        config.system.integrateRecommendations(user)
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
    ratingsButton = PushButton(buttonsBox, text="Start Rating", command=lambda:showRatingsWindow(app, user, setMoviesToRate.value), align="left")
    ratingsButton.bg = colorWidget('Push Button')
    profileButton = PushButton(buttonsBox, text="See Profile", command=lambda:ShowProfileWindow(app, user), align="left")
    profileButton.bg = colorWidget('Push Button')

    app.display()

def viewInstructions(window):
    #Displays the instruction menu
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
    #Displays the credits menu
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
            user = Users(username)
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
    #Authenticates existing user's log in attempt
    global systemdb
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
        user = Users(username)
        c = systemdb.cursor(buffered=True)
        #notifies the program that the user has logged into the system
        c.execute('''UPDATE users SET loggedIn = 1 WHERE username = '{}';'''.format(username))
        systemdb.commit()
        c.close()

        ShowHomePageWindow(user, window.master)

def setUpUnseenTitles(user):
    #Fills the priority queue with titles
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

def addTitleToQueue(dataset):
    #adds titles from a dataset of imdb id's
    #whether its the imdbIDs list or the unseen titles result
    #queried from the database to the recommender system's
    #priority queue
    for item in dataset:
        title = convertIdToTitleObject(item)
        if title not in config.system.getUnseenQueue().getDataset():
            config.system.getUnseenQueue().enqueue(title)

def convertIdToTitleObject(titleId):
    global Title
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
    
def hashPassword(password):
    #converts password to decimal value

    decimalValue = 0
    for i in range(0, len(password)):
        decimalValue += ord(password[0])
        #converts decimal value to hexadecimal
        hashed = hex(decimalValue)

    return hashed
