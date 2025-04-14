"""
Main module for the Telegram bot. Initializes the bot, sets up the necessary
components for bot operation, including the bot itself, storage, dispatcher,
keyboards, user database, and channel subscription checks. Also registers the
handlers for bot commands and callbacks.
"""

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
from database.models import Base, engine
from populate_database import init_db
from utils.decorators import exception_handler


class Main:
    """
    Initializes the main bot components and sets up the necessary instances
    for bot operation, including the bot itself, storage, dispatcher, keyboards,
    user database, and channel subscription checks. Also registers the handlers
    for bot commands and callbacks.
    """

    def __init__(self) -> None:
        self.bot = Bot(token=config.token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)

        self.keyboard = Keyboards()
        self.send_keyboard = KeyboardSender(bot=self.bot)
        self.user = UserDb()
        self.telegram_subs = TelegramChannelSubscription(bot=self.bot)

        self.register_handlers()

    def register_handlers(self) -> None:
        """
        Register all handlers for the bot.
        """
        self.dp.register_message_handler(self.start, commands=["start"])
        self.dp.register_callback_query_handler(self.check_subscription, text="check_subscription")
        self.dp.register_callback_query_handler(self.main_menu, text="main_menu")
        
    @exception_handler
    async def start(self, message: Message, state: FSMContext) -> None:
        """
        Handles the /start command for the Telegram bot. Finishes the current state,
        retrieves user data from the database, and creates a new user if not found.
        If the user is already in the database and subscribed to the channel, navigates
        to the main menu. Otherwise, sends a welcome message with a subscription
        keyboard to prompt the user to subscribe to the channel.

        Args:
            message (Message): The message object containing info about the user and the command.
            state (FSMContext): The FSM context for maintaining the state of the bot.
        """
        await state.finish()

        user_data = self.user.get_user(obj=message)
        if not user_data:
            self.user.create_user(obj=message)
        elif user_data and await self.telegram_subs.check_member(obj=message):
            await self.main_menu(message, state)
            return

        keyboard = self.keyboard.subscribe_keyboard()
        await self.send_keyboard.keyboard(obj=message, text=var.welcome, keyboard=keyboard)

    @exception_handler
    async def check_subscription(self, callback: CallbackQuery, state: FSMContext) -> None:
        """
        Handles the callback query for the 'check_subscription' button.
        Checks if the user is subscribed to the channel and if so, navigates
        to the main menu. Otherwise, prompts the user with a message and
        returns to the start state.
        """
        await state.finish()

        member_check = await self.telegram_subs.check_member(obj=callback)
        if member_check:
            await self.main_menu(callback, state)
        else:
            await self.telegram_subs.alert_subscription(obj=callback)
            await self.start(callback, state)

    @exception_handler
    async def main_menu(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.finish()
        
        keyboard = self.keyboard.main_menu()
        await self.send_keyboard.keyboard(
            obj=callback,
            text=var.available,
            keyboard=keyboard
        )










    @exception_handler
    def run(self):
        log.info("Bot started")
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    # Create and populate the database
    Base.metadata.create_all(engine)
    init_db()

    bot_instance = Main()
    bot_instance.run()
