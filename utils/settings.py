import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENCRYPT_KEY = os.getenv('ENCRYPT_KEY')
    VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')
    TENANT_NAME = os.getenv('TENANT_NAME')
    APP_ID = os.getenv('APP_ID')
    APP_SECRET = os.getenv('APP_SECRET')
    DEBUG = os.getenv('DEBUG')
