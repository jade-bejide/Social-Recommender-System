from guizero import *

def ShowHomePageWindow(user):
    app = App("Rate Movies!", height=250, width=500)

    welcome = Text(app, text="Welcome" + user.getUsername() + "!")

    setMoviesToRate = Combo(app, options=[5,10,15,20,25,30])

    app.display()

def ShowLoginScreen():
    app = App("Login in to 'Rate Movies!'", height=250, width=500)

    #check to see if the user is new or existing

    welcome = Text(app, text='Welcome to "Rate Movies!"')
    new_users = PushButton(app, command=lambda:initiateNewUser(app), text="New User")
    existing_users = PushButton(app, command=lambda:initiateExistingUser(app), text="Existing User")

    newUser = new_users.value
    app.display()

def ShowNewUserWindow(app):
    global Users
    newUserWindow = Window(app, title="Create an account")
    

    welcome_newUser = Text(newUserWindow, text="Create an account")
    username_label = Text(newUserWindow, text="Username: ")
    newUser_inputUsername = TextBox(newUserWindow)
    password_label = Text(newUserWindow, text="Password: ")
    newUser_inputPassword = TextBox(newUserWindow, hide_text=True)
    password2_label = Text(newUserWindow, text="Enter password again: ")
    newUser_inputPasswordAgain = TextBox(newUserWindow, hide_text=True)
    newUser_createAccount = PushButton(newUserWindow, text="Create Account", command=lambda:validateCreation(newUserWindow, app, newUser_inputUsername, newUser_inputPassword, newUser_inputPasswordAgain))
    
    user = Users(newUser_inputUsername, newUser_inputPassword)

def ShowExistingUserWindow(app):
    existingUserWindow = Window(app, title="Login into an existing account")

    welcome_existingUser = Text(existingUserWindow, text="Login to your account")
    username_label = Text(existingUserWindow, text="Username: ")
    existingUser_inputUsername = TextBox(existingUserWindow)
    password_label = Text(existingUserWindow, text="Password: ")
    existingUser_inputPassword = TextBox(existingUserWindow, hide_text=True)
    existingUser_createAccount = PushButton(existingUserWindow, text="Login", command=lambda:authenticateLogin(existingUserWindow, app, existingUser_inputUsername, existingUser_inputPassword))

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

    
