from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from variables.RUS import Strings as var
from utils.logs import log
from env import Config as config


class Keyboards:
    def subscribe_keyboard(self):
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add( 
            InlineKeyboardButton(var.ask_subscribe, url=config.channel_name),
            InlineKeyboardButton(var.check_subscribe, callback_data='check_subscribe')
        )
        return keyboard