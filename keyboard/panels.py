from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from variables.RUS import Strings as var
from utils.logs import log
from env import Config as config


class Keyboards:
    def subscribe_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add( 
            InlineKeyboardButton(var.ask_subscribe, url=config.channel_url),
            InlineKeyboardButton(var.check_subscribe, callback_data='check_subscription')
        )
        return keyboard
    

class TelegramChannelSubscription:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.admin_list = config.admins
        self.workers_list = config.workers
    
    async def check_member(self, object: CallbackQuery) -> bool:
        user = await self.bot.get_chat_member(chat_id=config.channel_id, 
                                user_id=object.from_user.id)
        if user.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    
    async def alert_subscription(self, object: CallbackQuery) -> None:
        await self.bot.answer_callback_query(
            callback_query_id=object.id,
            text=var.not_subscribed,
            show_alert=True
        )
        