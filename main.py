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
from database.db import UserDb, AccountDb, Telegram
from database.models import Base, engine
from populate_database import init_db
from utils.decorators import exception_handler
from utils.cache import RedisManager
from utils.states import StateManager, StateList


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
        self.account = AccountDb()
        self.redis = RedisManager()
        self.telegram = Telegram()

        self.register_handlers()

    def register_handlers(self) -> None:
        """
        Register all handlers for the bot.
        """
        self.dp.register_message_handler(self.start, commands=["start"])
        self.dp.register_callback_query_handler(self.check_subscription, text="check_subscription")
        self.dp.register_callback_query_handler(self.main_menu, text="main_menu")
        self.dp.register_callback_query_handler(self.lot_list, text="lot_list")
        self.dp.register_callback_query_handler(self.profile, text="profile")
        self.dp.register_callback_query_handler(self.support, text="support")
        self.dp.register_callback_query_handler(
            self.lot_prebuy_menu,
            lambda callback_query: callback_query.data.startswith("buy_")
            )
        self.dp.register_message_handler(self.handle_lot_input, state=StateList.LOT_MENU)
        self.dp.register_callback_query_handler(self.purchase, text="purchase", state=StateList.LOT_MENU)
        
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
        
        # Init Redis
        await self.redis.connect()

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
        
        text = f'***{var.available}***\n\n'

        account_stats = self.account.get_desription_main()
        print(f'***acc stats***{account_stats}')
        telegram_id = self.telegram.data(obj=callback).telegram_id

        for lot_type, price, quantity in account_stats:
            text += f"*{lot_type}* /// $*{price}* /// *{quantity}**{var.pcs}*\n"

        keyboard = self.keyboard.main_menu()
        await self.send_keyboard.keyboard(
            obj=callback,
            text=text,
            keyboard=keyboard
        )

    @exception_handler
    async def lot_list(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.finish()

        desc = [var.category]

        buttons = list()
        lot_type = self.account.get_lot_type()

        for lot_type in lot_type:
            buttons.append(lot_type)

        keyboard = self.keyboard.lot_menu(buttons)
        await self.send_keyboard.keyboard(
            obj=callback,
            text=desc,
            keyboard=keyboard
        )
    
    @exception_handler
    async def lot_prebuy_menu(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.finish()

        lot_type = callback.data.split('_')[-1]
        data = self.account.get_lot_details(lot_type=lot_type)

        desc = f'{lot_type}\n{var.price}{data[1]}\n{var.available}{data[2]}\n\n{var.lot_buy_desc}'

        keyboard = self.keyboard.one_button()
        await self.send_keyboard.keyboard(
            obj=callback,
            text=desc,
            keyboard=keyboard
        )
        manager = StateManager(state)
        await manager.set_state(StateList.LOT_MENU)
        await manager.set_data(key="lot_type", value=lot_type)
        await manager.set_data(key="available_quantity", value=data[2])

    @exception_handler
    async def handle_lot_input(self, message: Message, state: FSMContext):
        try:
            lot_quantity = int(message.text.strip())
        except ValueError:
            await message.answer(var.input_exception)
            await self.main_menu(message, state)
            return

        if lot_quantity > 20 or lot_quantity < 0:    
            await message.answer(var.input_quantity_exception)
            await self.main_menu(message, state)
            return

        manager = StateManager(state)
        lot_data = await manager.get_all_data()
        lot_type = lot_data.get("lot_type")
        lots = self.account.get_lot_texts_by_type(lot_type=lot_type, quantity=lot_quantity)

        telegram_id = self.telegram.data(obj=message).telegram_id
        await self.redis.reserve_lots(telegram_id=telegram_id, lots=lots)

        available_quantity = int(lot_data.get("available_quantity"))
        if available_quantity < lot_quantity:
            await message.answer(var.input_quantity_available)
            await self.main_menu(message, state)
            return
        
        lot_info = self.account.get_lot_details(lot_type)
        await manager.set_data(key="lot_quantity", value=lot_quantity)
        total_price = float(lot_info[1]) * lot_quantity
        await manager.set_data(key="lot_total_price", value=total_price)

        balance = self.user.get_balance()
        if balance < total_price:
            await message.answer(var.input_balance_exception)
            await self.main_menu(message, state)
            return

        desc = (
            f"{var.lot_list}: {lot_data.get('lot_type')}\n"
            f"{var.price}{lot_info[1]}\n"
            f"{var.quantity}{lot_quantity}\n"
            f"{var.total}{total_price}\n"
            f"{var.acc_balance}{balance}"
        )

        keyboard = self.keyboard.buy_menu()
        await self.send_keyboard.keyboard(
            obj=message,
            text=desc,
            keyboard=keyboard
        )   

    @exception_handler
    async def purchase(self, callback: CallbackQuery, state: FSMContext) -> None:
        manager = StateManager(state)
        lot_data = await manager.get_all_data()
        print(f'***{lot_data}***')

        desc = (
            f'{var.lot_list}: {lot_data.get("lot_type")}\n'
            f'{var.price}{lot_data.get("lot_total_price")} USDT\n'
            f'{var.quantity}{lot_data.get("lot_quantity")}\n'
        )

        keyboard = self.keyboard.one_button()
        await self.send_keyboard.keyboard(
            obj=callback,
            text=desc,
            keyboard=keyboard
        )



    @exception_handler
    async def profile(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.finish()
        print('profile')

    @exception_handler
    async def support(self, callback: CallbackQuery, state: FSMContext) -> None:
        await state.finish()
        print('support')




    @exception_handler
    def run(self):
        log.info("***Bot started***")
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    # Create and populate the database
    Base.metadata.create_all(engine)
    init_db()

    bot_instance = Main()
    bot_instance.run()
