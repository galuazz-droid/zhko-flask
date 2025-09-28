# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'zhko-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///zhko.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
