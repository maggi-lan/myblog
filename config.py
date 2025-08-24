import os

class Config:
    # if there is no env variable called SECRET_KEY, 'you-will-never-guess' will be assigned
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"