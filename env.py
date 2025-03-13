"""
Module for storing environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Class for storing environment variables.
    """
    token = os.getenv('BOT_TOKEN')
    channel_name = os.getenv('CHANNEL_NAME')
    channel_url = os.getenv('CHANNEL_URL')
    database_url = os.environ.get('DATABASE_URL')
    timezone = os.environ.get('TIMEZONE')
    channel_id = os.environ.get('CHANNEL_ID')
    admins = os.environ.get('ADMINS')
    workers = os.environ.get('WORKERS')