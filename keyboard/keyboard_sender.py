from aiogram import Bot
from aiogram.types import ParseMode, Message, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeEdited, MessageNotModified
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


class KeyboardSender:
    def __init__(self, bot: Bot ) -> None:
        self.bot = bot

    async def keyboard(
            self,
            object: Message|CallbackQuery,
            text: str, 
            keyboard: InlineKeyboardMarkup|ReplyKeyboardMarkup,
            ) -> None:
        if isinstance(object, Message):
            try:
                # Edit message object
                await self.bot.edit_message_text(
                    chat_id = object.chat.id,
                    message_id=object.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageCantBeEdited:
                # In case of message cant be edited because this message is not last in flow
                await self.bot.send_message(
                    chat_id=object.chat.id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageNotModified:
                # In case of message not modified
                pass

        elif isinstance(object, CallbackQuery):
            # Probably callback query        
            try:
                await self.bot.edit_message_text(
                    chat_id = object.message.chat.id,
                    message_id=object.message.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageCantBeEdited:
                # In case of message cant be edited because this message is not last in flow
                await self.bot.send_message(
                    chat_id=object.message.message_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except MessageNotModified:
                # In case of message not modified
                pass