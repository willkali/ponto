# config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('192.168.1.14', 'postgresql://postgres:reboot3@localhost/cadastro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
