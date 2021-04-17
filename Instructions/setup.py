from cx_Freeze import setup, Executable

base = None

executables = [Executable("main.py", base=base)]

includefiles = ["leftarrow.png", "rightarrow.png", "staricon.png", "themeControllers.py", "config.py", "mod.py", "windows.py",
                "objectclasses.py"]
includes = []
packages = ["idna", "guizero", "mysql.connector", "json", "urllib", "numpy",
            "math", "requests", "random", "PIL", "sys", "tkinter"]

options = {
    'build_exe': {
        'packages':packages,
        'includes': includes,
        'include_files': includefiles
        },
}

setup(
    name = "Social Recommender System",
    options = options,
    version = "0.0.1",
    author = "Jadesola Bejide",
    description = "Rate movies and TV shows and follow other users to get recommendations",
    executables = executables
)
