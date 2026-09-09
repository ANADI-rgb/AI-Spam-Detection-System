import json
import os


# --------------------------------------------------
# Users File
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_FILE = os.path.join(
    BASE_DIR,
    "users.json"
)


# --------------------------------------------------
# Load Users
# --------------------------------------------------

def load_users():

    if not os.path.exists(USER_FILE):
        return {}

    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return {}


# --------------------------------------------------
# Save Users
# --------------------------------------------------

def save_users(users):

    try:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(
                users,
                f,
                indent=4
            )

        return True

    except OSError:
        return False


# --------------------------------------------------
# Register User
# --------------------------------------------------

def register_user(username, password):

    users = load_users()

    if username in users:
        return False

    users[username] = {
        "password": password
    }

    return save_users(users)


# --------------------------------------------------
# Validate User
# --------------------------------------------------

def validate_user(username, password):

    users = load_users()

    if (
        username in users
        and users[username]["password"] == password
    ):
        return True

    return False


# --------------------------------------------------
# Reset Password
# --------------------------------------------------

def reset_password(username, new_password):

    users = load_users()

    if username not in users:
        return False

    users[username]["password"] = new_password

    return save_users(users)
