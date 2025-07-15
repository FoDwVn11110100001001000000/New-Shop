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
    redis_host = os.environ.get('REDIS_HOST')
    redis_port = os.environ.get('REDIS_PORT')
    redis_expire = os.environ.get('REDIS_EXPIRE')
    testnet = os.environ.get('TESTNET')
    pay_currency = os.environ.get('PAY_CURRENCY')
    invoice_counter = os.environ.get('INVOICE_COUNTER')
    crypto_pay_token = os.environ.get('CRYPTO_PAY')
    my_id = os.environ.get('MY_ID')
