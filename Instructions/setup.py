from cx_Freeze import setup, Executable

base = None

executables = [Executable("finalproject.py", base=base)]

packages = ["idna", "guizero", "mysql.connector", "json", "urllib", "numpy",
            "math", "requests", "random", "PIL", "sys"]

options = {
    'build_exe': {
        'packages':packages,
        },
}

setup(
    name = "<Social Recommender System>",
    options = options,
    version = "0.0.1",
    description = "Rate movies and TV shows and follow other users to get recommendations",
    executables = executables
)
