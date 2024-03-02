import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///zycurrency.db'
    URL_DOMAIN_WITH_PROTOCOL = 'http://127.0.0.1:5000'

    GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"

    FAST_FOREX_API_URL="https://api.fastforex.io"
    FAST_FOREX_API_KEY=os.getenv("FAST_FOREX_API_KEY")

    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    CELERY_TASK_IGNORE_RESULT = False