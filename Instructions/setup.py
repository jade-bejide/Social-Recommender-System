from cx_Freeze import setup, Executable

base = None

executables = [Executable("rate_it.py", base=base)]

packages = ["idna", "guizero", "mysql.connector", "json", "urllib", "numpy",
            "math", "requests", "random", "PIL", "sys", "tkinter"]

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
