import os

class Config(object):
    DEBUG = os.getenv("FLASK_DEBUG")
    TESTING = os.getenv("FLASK_ENV")
    SECRET_KEY = os.getenv("SECRET_KEY")
    UPLOAD_FOLDER = './uploads'
    TEMPLATE_FOLDER = './app/templates'
