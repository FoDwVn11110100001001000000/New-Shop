from aiogram.types import Message
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from keyboard.panels import Keyboards
from keyboard.keyboard_sender import send_keyboard
from variables.RUS import Strings as var
from env import Config as config
from utils.logs import log


class Main:
    def __init__(self):
        self.bot = Bot(token=config.token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)

        self.keyboard = Keyboards()

        self.register_handlers()

    def register_handlers(self):
        """
        Register all handlers for the bot.
        """
        self.dp.register_message_handler(self.start, commands=['start'])

    async def start(self, message: Message, state: FSMContext):
        await state.finish()
        keyboard = self.keyboard.subscribe_keyboard()
        await send_keyboard(self.bot, message, var.welcome, keyboard)

    def run(self):
        log.info("Bot started")
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    bot_instance = Main()
    bot_instance.run()
