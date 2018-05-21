import os


### constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "gym.db")


### table names
SESSION_TABLE = "session"
EXERCISE_TABLE = "exercise"
SESSION_DETAILS_TABLE = "session_details"
INTENSITY_TABLE = "intensity"

