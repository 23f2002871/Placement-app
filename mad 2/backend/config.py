import os

# Getting the current directory path to store the sqlite db
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Basic config variables required for Flask and JWT
    SECRET_KEY = 'my_secret_key_for_flask'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'placement.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'my_secret_key_for_jwt_tokens'