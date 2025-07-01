import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 5))

settings = Settings()
