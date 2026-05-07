from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
PROJECT_NAME = os.getenv("PROJECT_NAME", "HackMate")
REDIS_URL = os.getenv("REDIS_URL")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")