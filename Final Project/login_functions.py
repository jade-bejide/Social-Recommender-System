from guizero import *

def ShowLoginScreen():
    app = App("Login in to 'Rate Movies!'", height=250, width=500)

    #check to see if the user is new or existing

    welcome = Text(app, text='Welcome to "Rate Movies!"')
    new_users = PushButton(app, command=lambda:initiateNewUser(app), text="New User")
    existing_users = PushButton(app, command=lambda:initiateExistingUser(app), text="Existing User")

    newUser = new_users.value
    app.display()

def LoginScreen():
    ShowLoginScreen()

    ShowHomePageWindow()

def initiateNewUser(window):
    ShowNewUserWindow()

    passwordHashed = hashPassword(password)
    user = Users(username, passwordHashed)

    '''INSERT INTO Users (username, password, loggedIn) VALUES (user.getUsername(), user.getPassword(), TRUE);'''

def createAccount(username, password, authenticate):
    usernames = '''SELECT username FROM users;'''

    if username not in usernames:
        validateUsername(username)
    else:
        ShowUsernameErrorWindow()

    validatePassword(password, authenticate)

def validateUsername(username):
    #usernames must be 5 characters or more

    if len(username) < 5:
        ShowUsernameLengthWindow()

    #usernames must not start with a special character

    elif username[0].isSpecialChar():
        ShowUsernameFirstCharWindow()

def validatePassword(password, passwordAgain):
    #check if passwords match
    if password != passwordAgain:
        ShowPasswordMatchErrorWindow()

    if len(password) < 10:
        ShowPasswordLengthErrorWindow()
    else:
        noNumber = 0
        noSpecialChar = 0
        noUpperChar = 0
        noLowerChar = 0

        #checks if the password begins with a letter

        if password[0].isNumeber() == True or password[0].isSpecialChar() == True:
            ShowFirstCharErrorWindow()
        else:

            for i in range(0 ,len(password)):
                #switch case statements to test the security
                if password[i].isNumber():
                    noNumber += 1
                elif password[i].isSpecialChar():
                    noSpecialChar += 1
                elif password[i].isUpperChar():
                    noUpperChar += 1
                elif password[i].isLowerChar():
                    noLowerChar += 1

                if password[i] == " ":
                    ShowNoSpacesErrorWindow()

def initiateExistingUser(window):
    details = ShowExisitingUserWindow()

    authenticateUser(details)
def authenticateUser(username, password):
    usernames = '''SELECT username FROM users;'''

    if username not in username:
        ShowNoSuchUserWindow()

    passwordMatch = '''SELECT password FROM users WHERE username=username;'''
    password = hashPassword(password)

    if password != passwordMatch:
        ShowIncorrectDetailsWindow()

def hashPassword(password):
    #converts password to decimal value

    decimalValue = 0
    for i in range(0, len(password)):
        decimalValue += ord(password[0])
        #converts decimal value to hexadecimal
        hashed = Hex(decimalValue)

    return hashed
