"""
Module for creating keyboard panels.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram import Bot
from variables.RUS import Strings as var
from env import Config as config


class Keyboards:
    """
    Class for creating keyboard panels.
    """
    def subscribe_keyboard(self) -> InlineKeyboardMarkup:
        """
        Method for creating a keyboard with buttons to subscribe to a telegram channel.

        Returns:
            InlineKeyboardMarkup: A keyboard with two buttons: one for subscribing to a channel
            and another for checking if the user is subscribed to the channel.
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add( 
            InlineKeyboardButton(var.ask_subscribe, url=config.channel_url),
            InlineKeyboardButton(var.check_subscribe, callback_data='check_subscription')
        )
        return keyboard

    def main_menu(self) -> InlineKeyboardMarkup:
        """
        Method for creating a keyboard with buttons to navigate to the main menu.

        Returns:
            InlineKeyboardMarkup: A keyboard with one button: the main menu.
        """
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add( 
            InlineKeyboardButton(var.lot_list, callback_data='lot_list'),
            InlineKeyboardButton(var.profile, callback_data='profile'),
            InlineKeyboardButton(var.support, callback_data='support')
        )
        return keyboard

    def lot_menu(self, buttons_list: list[str]) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for button in buttons_list:
            keyboard.add(
                InlineKeyboardButton(button, callback_data=f'buy_{button}'))
        return keyboard

class TelegramChannelSubscription:
    """
    Class for checking if a user is subscribed to a Telegram channel.
    """
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.admin_list = config.admins
        self.workers_list = config.workers

    async def check_member(self, obj: CallbackQuery) -> bool:
        """
        Method for checking if a user is subscribed to a Telegram channel.

        Args:
            object (CallbackQuery): The CallbackQuery object from the Telegram update.

        Returns:
            bool: True if the user is subscribed to the channel, False otherwise.
        """

        user = await self.bot.get_chat_member(chat_id=config.channel_id,
                                user_id=obj.from_user.id)
        if user.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False

    async def alert_subscription(self, obj: CallbackQuery) -> None:
        """
        Method for sending an alert to the user if the 
        user is not subscribed to the Telegram channel.
        Args:
            object (CallbackQuery): The CallbackQuery object from the Telegram update.
        """
        await self.bot.answer_callback_query(
            callback_query_id=obj.id,
            text=var.not_subscribed,
            show_alert=True
        )
