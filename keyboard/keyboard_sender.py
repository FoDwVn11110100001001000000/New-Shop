from aiogram import Bot
from aiogram.types import ParseMode, Message, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeEdited
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


async def send_keyboard(
        bot: Bot, 
        obj: Message|CallbackQuery, 
        text: str, 
        keyboard: InlineKeyboardMarkup|ReplyKeyboardMarkup,
        ):
    try:
        await bot.edit_message_text(
            chat_id = obj.chat.id,
            message_id=obj.message_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    except MessageCantBeEdited:
        await bot.send_message(
            chat_id=obj.chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    except AttributeError:
        await bot.send_message(
            chat_id=obj.chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )