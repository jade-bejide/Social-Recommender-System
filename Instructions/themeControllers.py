

#enables quick checking of updation of each window's state
windows = {
    'newUserWindow': 0,
    'existingUserWindow': 0,
    'ratingWindow': 0,
    'recommendationsWindow': 0,
    'profileWindow': 0,
    'followersWindow': 0,
    'followingsWindow': 0,
    'searchEngineWindow': 0,
    'resultsWindow':0,
    'instructionsWindow':0,
    'creditsWindow':0}

#checks theme color choice 0 - light theme, 1 - darkTheme
themeChoice = 0

#light and dark mode color palettes
lightThemeButtonColor = (28,254,251)
lightThemeBgColor = "white"
lightThemeComplBg = (3,168,229)
lightThemeTextColor = "black"

darkThemeButtonColor = (229,9,20)
darkThemeBgColor = (45,45,45)
darkThemeComplBg = (177,6,15)
darkThemeTextColor = "white"

def chooseTheme(choice):
    global themeChoice
    if choice == "Light Mode":
        themeChoice = 0
    if choice == "Dark Mode":
        themeChoice = 1

        
def colorWidget(widgetType):
    global themeChoice
    if themeChoice == 0:
        if widgetType == 'Combo':
            return lightThemeComplBg
        if widgetType == 'App' or widgetType == 'Window':
            return lightThemeBgColor
        if widgetType == 'Push Button':
            return lightThemeButtonColor
        if widgetType == 'Text':
            return lightThemeTextColor

    if themeChoice == 1:
        if widgetType == 'Combo':
            return darkThemeComplBg
        if widgetType == 'App' or widgetType == 'Window':
            return darkThemeBgColor
        if widgetType == 'Push Button':
            return darkThemeButtonColor
        if widgetType == 'Text':
            return darkThemeTextColor

   



def isWindowOpen(window):
    global windows
    
    if windows[window] == 1:
        #window is already open and therefore won't open another window
        return True
    else:
        #if not, the program will open the window, so this state is updated here
        windows[window] = 1
        return False

def closeWindow(windowname, windowobj):
    #informs the windows dictionary that the window
    #has been closed
    windows[windowname] = 0
    windowobj.destroy()

    #if the window to be closed is the searchEngine window, the searchResults variable
    #is set to zero to show that this is also closed as a result

    if windowobj == 'searchEngineWindow':
        searchResults = 0
