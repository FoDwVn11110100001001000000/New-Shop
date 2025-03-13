"""
Module for sending keyboards to users.
"""

from aiogram import Bot
from aiogram.types import ParseMode, Message, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeEdited, MessageNotModified
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


class KeyboardSender:
    """
    Class for sending keyboards to users.
    """
    def __init__(self, bot: Bot ) -> None:
        self.bot = bot

    async def keyboard(
            self,
            obj: Message|CallbackQuery,
            text: str,
            keyboard: InlineKeyboardMarkup|ReplyKeyboardMarkup,
            ) -> None:
        """
        Sends or edits a message with a given keyboard.

        Depending on whether the object is a Message or CallbackQuery, this method
        attempts to either edit an existing message or send a new one with the provided
        text and keyboard markup. 

        Args:
            obj (Message|CallbackQuery): The Telegram object containing message data 
                or callback query.
            text (str): The text to be displayed in the message.
            keyboard (InlineKeyboardMarkup|ReplyKeyboardMarkup): The keyboard markup 
                to be attached to the message.

        Note:
            If the message can't be edited (e.g., it's not the last message in a chat),
            a new message is sent. If the message has not changed, no action is taken.
        """

        if isinstance(obj, Message):
            try:
                # Edit message object
                await self.bot.edit_message_text(
                    chat_id = obj.chat.id,
                    message_id=obj.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageCantBeEdited:
                # In case of message cant be edited because this message is not last in flow
                await self.bot.send_message(
                    chat_id=obj.chat.id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageNotModified:
                # In case of message not modified
                pass

        elif isinstance(obj, CallbackQuery):
            # Probably callback query
            try:
                await self.bot.edit_message_text(
                    chat_id = obj.message.chat.id,
                    message_id=obj.message.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageCantBeEdited:
                # In case of message cant be edited because this message is not last in flow
                await self.bot.send_message(
                    chat_id=obj.message.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageNotModified:
                # In case of message not modified
                pass
