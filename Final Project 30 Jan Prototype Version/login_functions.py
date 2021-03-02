from guizero import *
from user_class import *
import sqlite3

conn = sqlite3.connect('system.db')
c = conn.cursor()

def ShowRecommendationsWindow():
    pass

def ShowProfileWindow():
    pass

def logOffUser(user, window):
    global c, conn
    c.execute('''UPDATE users SET loggedIn = 0 WHERE username = "{}"'''.format(user.getUsername()))
    conn.commit()

    window.destroy()


    
def ShowHomePageWindow(user, window):
    window.destroy()
    app = App("Rate Movies!", height=250, width=350)

    welcome = Text(app, text="Welcome " + user.getUsername() + "!")

    setToRate_lbl = Text(app, text="Number of titles to rate:")

    setMoviesToRate = Combo(app, options=[5,10,15,20,25,30])

    buttonsBox = Box(app, height=100, width=500)
    recommendationsButton = PushButton(buttonsBox, text="Recommended Titles", command=ShowRecommendationsWindow(), align="left")
    ratingsButton = PushButton(buttonsBox, text="Start Rating", command=lambda:user.rate_titles(setMoviesToRate.value), align="left")
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


    return user, window.master

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

    print(createAccount)


def ShowExistingUserWindow(app):
    existingUserWindow = Window(app, title="Login into an existing account")

    welcome_existingUser = Text(existingUserWindow, text="Login to your account")
    username_label = Text(existingUserWindow, text="Username: ")
    existingUser_inputUsername = TextBox(existingUserWindow)
    password_label = Text(existingUserWindow, text="Password: ")
    existingUser_inputPassword = TextBox(existingUserWindow)
    existingUser_createAccount = PushButton(existingUserWindow, text="Login", command=lambda:authenticateUser(existingUser_inputUsername.value, existingUser_inputPassword.value, existingUserWindow))

    return existingUser_createAccount.value

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
    global c, conn, Users
    usernames = c.execute('''SELECT username FROM users;''')
    conn.commit()
    usernames_list = []
    for row in usernames:
        usernames_list.append(row[0])
        
    if username not in usernames_list:
        if validateUsername(username, window) == True and validatePassword(password, authenticate, window) == True:
            passwordHashed = hashPassword(password)
            #user = Users(username, passwordHashed)

            c.execute('''INSERT INTO users (username, password, loggedIn) VALUES('{}', '{}', TRUE);'''.format(username, passwordHashed))
            conn.commit()
            #print(user, window)
            user = Users(username, passwordHashed)
            return user, window.master
            
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
    global conn, c, Users
    usernames = c.execute('''SELECT username FROM users;''')
    conn.commit()

    usernames_list = []

    for row in c:
        usernames_list.append(row[0])

    if username not in usernames_list:
        ShowNoSuchUserWindow(window)
        return False

    c.execute('''SELECT password FROM users WHERE username=username;''')
    conn.commit()
    for row in c:
        passwordMatch = row[0]
        
    password = hashPassword(password)

    if password != passwordMatch:
        ShowIncorrectDetailsWindow(window)
    else:
        user = Users(username, password)
        c.execute('''UPDATE users SET loggedIn = 1 WHERE username = '{}';'''.format(user.getUsername()))
        conn.commit()
        return user, window.master

def hashPassword(password):
    #converts password to decimal value

    decimalValue = 0
    for i in range(0, len(password)):
        decimalValue += ord(password[0])
        #converts decimal value to hexadecimal
        hashed = hex(decimalValue)

    return hashed
