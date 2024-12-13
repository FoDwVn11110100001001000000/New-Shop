import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    token = os.getenv('BOT_TOKEN')
    channel_name = os.getenv('CHANNEL_NAME')