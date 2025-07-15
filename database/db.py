"""
This module contains classes for working with the database.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from aiogram.types import Message, CallbackQuery
from utils.logs import log
from database.models import User, SellLog, Account,tz, session


class Telegram:
    """
    Class for storing necessary parameters from Message or CallbackQuery object.
    """
    def data(self, obj: Message|CallbackQuery) -> "Telegram":
        """
        Sets the necessary parameters from Message or CallbackQuery object.
        Either sets Message or CallbackQuery parameters, depending on the type of the object.
        Returns self.
        """
        if isinstance(obj, CallbackQuery):
            self.telegram_id = obj.message.chat.id
            self.message_id = obj.message.message_id
            self.username = obj.message.chat.username
            self.name = obj.message.chat.first_name
        elif isinstance(obj, Message):
            self.telegram_id = obj.chat.id
            self.message_id = obj.message_id
            self.username = obj.chat.username
            self.name = obj.chat.first_name
        return self


class UserDb(Telegram):
    """
    Class for working with the database.
    """
    def __init__(self) -> None:
        self.user = User
        self.session = session
        self.telegram = Telegram()

    def refresh_user(self, user: User, obj: Message|CallbackQuery) -> None:
        """
        Refreshes the last visit parameter of the user in the database.
        Checks the username and changes it if it is different from the one in the database.
        """
        telegram = self.telegram.data(obj)
        # Refresh last visit parameter
        user.last_visit = datetime.now(tz)
        log.info(
            f"ID: {telegram.telegram_id} | Username: {telegram.username} "
            f"Changed username in the database. Old: {user.username}"
        )
        # Check username. If it is different, change it
        if user.username != telegram.username:
            log.info(
                f'ID: {telegram.telegram_id}| Username: {telegram.username}| '
                f'Changed username in the database. Old: {user.username}'
                )
            user.username = self.username

    def get_user(self, obj: Message|CallbackQuery) -> dict|None:
        """
        Retrieves user data from the database.

        Checks if the user is already in the database. If the user is found, refreshes
        the last visit parameter and returns user data in a dictionary. If the user
        is not found, returns an empty dictionary.

        Args:
            obj (Message|CallbackQuery): Telegram object with user data

        Returns:
            dict|None: User data if found, else None
        """
        telegram = self.telegram.data(obj)

        with self.session:
            user = self.session.query(User).filter_by(telegram_id=telegram.telegram_id).first()
            if user:
                self.refresh_user(user=user, obj=obj)

                data = {
                    'name': user.name,
                    'username': user.username,
                    'balance': user.balance,
                    'language': user.language,
                    'is_ban': user.is_ban
                }
                log.info(
                    f'ID: {telegram.telegram_id}| Username: {telegram.username}| '
                    f'Data: {data}| Was already in the database'
                    )
                return data

            else:
                log.info(
                    f'ID: {telegram.telegram_id}| '
                    f'Username: {telegram.username}| User not found'
                    )
                return {}

    def create_user(self, obj: Message|CallbackQuery, language: str = 'RUS') -> None:
        """
        Creates a new user in the database.
        
        Args:
            obj (Message|CallbackQuery): Telegram object with user data
            language (str, optional): User language. Defaults to 'RUS'.
        """
        telegram = self.telegram.data(obj)

        with self.session:
            new_user = User(
                telegram_id= telegram.telegram_id,
                name= telegram.name,
                username= telegram.username,
                balance= 0,
                language= language,
                last_visit= datetime.now(tz)
            )
            self.session.add(new_user)
            log.info(
                f'ID: {telegram.telegram_id}| Username: '
                f'{telegram.username}| Added to the database'
                )
            self.session.commit()

    def topup_balance(self, obj: Message|CallbackQuery, topup_quantity: float) -> bool:
        """
        Adds money to user's balance.
        
        Args:
            new_balance (str): Amount of money to add to the balance.
        
        Returns:
            bool: True if the user was found and their balance was updated, False otherwise.
        """
        telegram = self.telegram.data(obj)

        with self.session:
            user = self.session.query(User).filter_by(telegram_id=telegram.telegram_id).first()
            if user:
                user.balance += Decimal(str(topup_quantity))
                self.session.commit()
                log.info(
                    f'ID: {telegram.telegram_id}| Username: {telegram.username}| '
                    f'Top up balance to {topup_quantity}'
                    )
                return True
            else:
                log.error(f'ID: {telegram.telegram_id}| Username: {telegram.username}| User not found')
                return False

    def get_balance(self) -> str|None:
        """
        Retrieves user's balance.
        
        Args:
            None
        
        Returns:
            str|None: User's balance if found, else None
        """
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram.telegram_id).first()
            if user:
                balance = user.balance
                log.info(
                    f'ID: {self.telegram.telegram_id}| '
                    f'Username: {self.telegram.username}| Balance: {balance}'
                )
                return balance
            else:
                log.error(
                    f'ID: {self.telegram.telegram_id}| '
                    f'Username: {self.telegram.username}| User not found'
                )

    def change_user_language(self, new_language: str) -> bool:
        """
        Changes user's language.

        Args:
            new_language (str): New user language.

        Returns:
            bool: True if the user was found and their language was updated, False otherwise.
        """
        with self.session:
            user = self.session.query(User).filter(User.telegram_id == self.telegram_id).first()
            if user:
                user.language = new_language
                self.session.commit()
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Changed language in the database'
                    )
                return True
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')
                return False

    def get_user_language(self) -> str|None:
        """
        Retrieves user's language.
        
        Args:
            None
        
        Returns:
            str|None: User's language if found, else None
        """
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Getting language: {user.language}'
                    )
                return user.language
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')
                return None


    def get_banned_users(self) -> list:
        """
        Retrieves a list of banned users from the database.

        Returns:
            list: A list of strings with the format "ID: <telegram_id> - User: <username>"
            for each banned user. If no users are banned, returns "No users are banned".
        """

        with self.session:
            banned_users = self.session.query(User).filter(User.is_ban is True).all()
            if banned_users:
                log.info(
                    f'ID: {self.telegram_id}| Username: '
                    f'{self.username}| Banned users: {banned_users}'
                    )
                return [f"ID: {user.telegram_id} - User: {user.username}" for user in banned_users]
            else:
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| No users are banned')
                return "No users are banned"

    def set_user_ban(self, telegram_id: str) -> bool:
        """
        Bans a user with the specified Telegram ID.

        Args:
            telegram_id (str): Telegram ID of the user to be banned.

        Returns:
            bool: True if the user was found and banned, False otherwise.
        """
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    user.is_ban = True
                    self.session.commit()
                    log.info(
                        f'ID: {self.telegram_id}| Username: {self.username}| '
                        f'User {telegram_id} was banned'
                        )
                    return True
                return False
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Database error while banning user {telegram_id}: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Attribute error while banning user {telegram_id}: {e}'
                    )

    def set_user_unban(self, telegram_id: str) -> bool:
        """
        Unbans a user with the specified Telegram ID.

        Args:
            telegram_id (str): Telegram ID of the user to be unbanned.

        Returns:
            bool: True if the user was found and unbanned, False otherwise.
        """
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    user.is_ban = False
                    self.session.commit()
                    log.info(
                        f'ID: {self.telegram_id}| Username: {self.username}| '
                        f'User {telegram_id} was unbanned'
                        )
                    return True
                return False
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Database error while unbanning user {telegram_id}: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Attribute error while unbanning user {telegram_id}: {e}'
                    )

    def check_ban(self, telegram_id: str) -> bool:
        """
        Checks if a user with the specified Telegram ID is banned.

        Args:
            telegram_id (str): Telegram ID of the user to be checked.

        Returns:
            bool: True if the user is banned, False otherwise.
        """
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    return user.is_ban
                return False
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in checking ban status of user {telegram_id}: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in checking ban status of user {telegram_id}: {e}'
                    )

    def get_balance_and_registration(
            self, obj: Message|CallbackQuery) -> tuple[float | None, datetime | None]:
        """
        Retrieves user's balance and registration date from the database.

        Args:
            obj (Message|CallbackQuery): Telegram object with user data

        Returns:
            tuple[float | None, datetime | None]: 
            A tuple containing the user's balance and registration date
            if the user was found, else (None, None)
        """
        telegram_id = self.telegram.data(obj).telegram_id

        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    purchase_count = len(user.sell_logs)
                    log.info(
                        f'ID: {telegram_id}| Username: {user.username}| '
                        f'Balance: {user.balance}, Registration: {user.registration_date}, '
                        f'Purchases: {purchase_count}'
                    )
                    return {
                        'balance': user.balance,
                        'registration_date': user.registration_date,
                        'purchases': purchase_count
                    }
                return None, None
            except SQLAlchemyError as e:
                log.error(
                    f"Error in getting balance and registration date for user: {telegram_id}: {e}"
                )
                return None, None


class SelllogDb:
    """
    Database class for handling sell logs.
    """
    def __init__(self) -> None:
        self.user = User
        self.session = session
        self.telegram = Telegram()

    def count_rows(self) -> str:
        """
        Counts the number of rows in the sell log for the given user.

        Returns:
            str: The number of rows in the sell log.
        """
        with self.session:
            count = self.session.query(
                func.count(SellLog.id)
                ).filter(
                    SellLog.telegram_id == self.telegram.telegram_id
                    ).scalar()
            log.info(f'ID: {self.telegram.telegram_id}| Username: {self.telegram.username}| Count: {count}')
            return str(count)

    def sell_log(
            self,
            folder_name: str,
            filename: str,
            price: float,
            content: str,
            obj: Message|CallbackQuery
        ) -> None:
        """
        Adds a sell log to the database.A

        Args:
            folder_name (str): The type of the sell.
            filename (str): The name of the file that was sold.
            price (float): The price of the sell.
        """
        telegram = self.telegram.data(obj)

        with self.session:
            sell_log = SellLog(
                telegram_id=telegram.telegram_id,
                time=datetime.now(tz),
                name=telegram.name,
                username=telegram.username,
                type=folder_name,
                filename=filename,
                content=content,
                price= price
            )
            self.session.add(sell_log)
            self.session.commit()
            log.info(
                f'ID: {telegram.telegram_id}| Username: {telegram.username}| '
                f'Added sell log to the database'
                )

    def topup_log(self, folder_name: str, filename: str, price: float, obj: Message|CallbackQuery) -> None:
        """
        Adds a topup log to the database.

        Args:
            folder_name (str): The type of the topup.
            filename (str): The name of the file that was topped up.
            price (float): The price of the topup.
        """
        telegram = self.telegram.data(obj)

        with self.session:
            sell_log = SellLog(
                telegram_id=telegram.telegram_id,
                time=datetime.now(tz),
                name=telegram.name,
                username=telegram.username,
                type=folder_name,
                filename=filename,
                price= price
            )
            self.session.add(sell_log)
            self.session.commit()
            log.info(
                f'ID: {telegram.telegram_id}| '
                f'Username: {telegram.username}| Added topup log to the database'
            )


class AccountDb(Telegram):
    """
    Database class for handling accounts.
    """
    def __init__(self) -> None:
        self.user = User
        self.session = session
        self.telegram = Telegram()

    def get_description_main(self) -> list[tuple[str, float, int]]:
        """
        Gets a description of the main menu.

        Returns:
            list[tuple[str, float, int]]: A list of tuples containing the type of the lot,
                its price and the quantity of such lots.
        """
        with self.session:
            results = (
                session.query(
                    Account.lot_type,
                    Account.price,
                    func.count(Account.id).label("quantity")
                )
                .group_by(Account.lot_type, Account.price)
                .order_by(Account.lot_type)
                .all()
            )
        return results

    def get_lot_type(self) -> list[tuple[str]]:
        """
        Gets a description of the main menu.

        Returns:
            list[tuple[str, float, int]]: A list of tuples containing the type of the lot,
                its price and the quantity of such lots.
        """
        with self.session:
            results = (
                self.session.query(Account.lot_type)
                .distinct()
                .order_by(Account.lot_type)
                .all()
            )
            return [row[0] for row in results]

    def get_lot_info(self, lot_type: str) -> list[tuple[float, int]]:
        """
        Retrieves price and quantity information for a specific lot type.

        Args:
            lot_type (str): The type of the lot for which information is to be retrieved.

        Returns:
            list[tuple[float, int]]: A list of tuples where each tuple contains the price
            of the lot and the quantity available at that price.
        """
        with session:
            results = (
                session.query(
                    Account.price,
                    func.count(Account.id).label("quantity")
                )
                .filter(Account.lot_type == lot_type)
                .group_by(Account.price)
                .order_by(Account.price)
                .all()
            )
        return results

    def get_lot_details(self, lot_type: str) -> tuple[str, float, int]:        
        """
        Retrieves the details of a specific lot type.

        Args:
            lot_type (str): The type of the lot for which details are to be retrieved.

        Returns:
            tuple[str, float, int]: A tuple containing the type of the lot, 
            its price, and the quantity available for that price.
        """
        with session:
            result = (
                session.query(
                    Account.lot_type,
                    Account.price,
                    func.count(Account.id).label("quantity")
                )
                .filter(Account.lot_type == lot_type)
                .group_by(Account.lot_type, Account.price)
                .order_by(Account.price)
                .first()
            )
        return result

    def get_lots_by_type(self, lot_type: str, quantity: int) -> list[Account]:
        """
        Retrieves a list of Account objects for a specified lot type and quantity.

        Args:
            lot_type (str): The type of the lot to filter by.
            quantity (int): The maximum number of lots to retrieve.

        Returns:
            list[Account]: A list of Account objects matching the specified lot type, 
            limited to the specified quantity, and ordered by price.
        """
        with session:
            result = (
                session.query(Account)
                .filter(Account.lot_type == lot_type)
                .order_by(Account.price)
                .limit(quantity)
                .all()
            )
        return result

    def get_lot_texts_by_type(self, lot_type: str, quantity: int) -> list[dict[str, str]]:
        """
        Retrieves a list of dictionaries, where each dictionary contains the type of the lot
        as the key and the text of the lot as the value, for a specified lot type and quantity.

        Args:
            lot_type (str): The type of the lot to filter by.
            quantity (int): The maximum number of lots to retrieve.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing the type of the lot as the
            key and the text of the lot as the value, limited to the specified quantity, and
            ordered by price.
        """
        with session:
            lots = (
                session.query(Account)
                .filter(Account.lot_type == lot_type)
                .order_by(Account.price)
                .limit(quantity)
                .all()
            )
            return [{'filename': lot.filename ,lot.lot_type: lot.txt} for lot in lots]

    def delete_by_filename(self, filename: str) -> None:
        """
        Deletes an account from the database by filename.
        Args:
            filename (str): The filename of the account to delete.
        """
        with self.session:
            self.session.query(Account).filter(
                Account.filename == filename
            ).delete(synchronize_session=False)
            self.session.commit()
