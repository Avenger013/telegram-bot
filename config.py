import os
from dotenv import load_dotenv

load_dotenv('.env')

TOKEN = os.getenv('TOKEN')

SQLALCHEMY_URL = os.getenv('SQLALCHEMY_URL')

