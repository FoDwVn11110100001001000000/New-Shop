from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from keyboard.panels import Keyboards, TelegramChannelSubscription
from keyboard.keyboard_sender import KeyboardSender
from variables.RUS import Strings as var
from env import Config as config
from utils.logs import log
from database.db import UserDb


class Main:
    def __init__(self):
        self.bot = Bot(token=config.token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)

        self.keyboard = Keyboards()
        self.send_keyboard = KeyboardSender(bot=self.bot)
        self.user = UserDb()
        self.telegram_subs = TelegramChannelSubscription(bot=self.bot)

        self.register_handlers()

    def register_handlers(self):
        """
        Register all handlers for the bot.
        """
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_callback_query_handler(self.check_subscription, text='check_subscription')
        self.dp.register_callback_query_handler(self.main_menu, text='main_menu')

    async def start(self, message: Message, state: FSMContext):
        await state.finish()
        user_data = self.user.get_user(object=message)
        if not user_data:
            self.user.create_user(object=message)
        elif user_data and await self.telegram_subs.check_member(object=message):
            await self.main_menu(message, state)

        keyboard = self.keyboard.subscribe_keyboard()
        await self.send_keyboard.keyboard(
            object=message, 
            text=var.welcome, 
            keyboard=keyboard
            )

    async def check_subscription(self, callback: CallbackQuery, state: FSMContext):
        await state.finish()

        member_check = await self.telegram_subs.check_member(object=callback)
        if member_check:
            await self.main_menu(callback, state)
        else:
            await self.telegram_subs.alert_subscription(object=callback)
            await self.start(callback, state)

    async def main_menu(self, callback: CallbackQuery, state: FSMContext):
        print('MAIN MENU***')







    def run(self):
        log.info("Bot started")
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    bot_instance = Main()
    bot_instance.run()
