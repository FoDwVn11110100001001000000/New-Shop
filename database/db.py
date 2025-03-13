"""
This module contains classes for working with the database.
"""

from datetime import datetime
from collections import defaultdict

from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from aiogram.types import Message, CallbackQuery

from utils.logs import log
from database.models import User, SellLog, Reserve, Lots, timezone, session


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
        user.last_visit = datetime.now(timezone)
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
                last_visit= datetime.now(timezone)
            )
            self.session.add(new_user)
            log.info(
                f'ID: {telegram.telegram_id}| Username: '
                f'{telegram.username}| Added to the database'
                )
            self.session.commit()

    def topup_balance(self, new_balance: str) -> bool:
        """
        Adds money to user's balance.
        
        Args:
            new_balance (str): Amount of money to add to the balance.
        
        Returns:
            bool: True if the user was found and their balance was updated, False otherwise.
        """
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                user.balance += float(new_balance)
                self.session.commit()
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Changed balance to: {new_balance}'
                    )
                return True
            else:
                log.error('ID: {self.telegram_id}| Username: {self.username}| User not found')
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
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                balance = user.balance
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Balance: {balance}')
                return balance
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')

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


class SelllogDb:
    """
    Database class for handling sell logs.
    """
    def __init__(self, telegram_id: str, username: str, name: str) -> None:
        self.user = User
        self.session = session
        self.telegram_id = telegram_id
        self.username = username
        self.name = name

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
                    SellLog.telegram_id == self.telegram_id
                    ).scalar()
            log.info(f'ID: {self.telegram_id}| Username: {self.username}| Count: {count}')
            return str(count)

    def sell_log(self, folder_name: str, filename: str, price: float) -> None:
        """
        Adds a sell log to the database.A

        Args:
            folder_name (str): The type of the sell.
            filename (str): The name of the file that was sold.
            price (float): The price of the sell.
        """
        with self.session:
            sell_log = SellLog(
                telegram_id=self.telegram_id,
                time=datetime.now(timezone),
                name=self.name,
                username=self.username,
                type=folder_name,
                filename=filename,
                price= price
            )
            self.session.add(sell_log)
            self.session.commit()
            log.info(
                f'ID: {self.telegram_id}| Username: {self.username}| '
                f'Added sell log to the database'
                )

    def topup_log(self, folder_name: str, filename: str, price: float) -> None:
        """
        Adds a topup log to the database.

        Args:
            folder_name (str): The type of the topup.
            filename (str): The name of the file that was topped up.
            price (float): The price of the topup.
        """

        with self.session:   
            sell_log = SellLog(
                telegram_id=self.telegram_id,
                time=datetime.now(timezone),
                name=self.name,
                username=self.username,
                type=folder_name,
                filename=filename,
                price= price
            )
            self.session.add(sell_log)
            self.session.commit()
            log.info(f'ID: {self.telegram_id}| Username: {self.username}| Added topup log to the database')


class ReserveDb:
    """
    Database class for handling reservations.
    """
    def __init__(self, telegram_id: str, username: str) -> None:
        self.user = User
        self.session = session
        self.telegram_id = telegram_id
        self.username = username

    def is_file_reserved(self, file_path: str) -> bool:
        """
        Checks if a file is reserved.
        Args:
            file_path (str): The path to the file to be checked.
        Returns:
            bool: True if the file is reserved, False otherwise.
        """
        with self.session:
            try:
                check_reserve = self.session.query(Reserve).filter(
                    Reserve.file_path == file_path).count() > 0
                return check_reserve

            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in reserve check.| Path: {file_path}| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in reserve check.| Path: {file_path}| Exception: {e}'
                    )

    def add_reservation(
            self,
            file_path: str,
            category: str,
            filename: str,
            reserve_time_end: datetime
        ) -> bool:
        """
        Adds a reservation to the database.

        Args:
            file_path (str): The path to the file to be reserved.
            category (str): The category of the file to be reserved.
            filename (str): The name of the file to be reserved.
            reserve_time_end (datetime): The time when the reservation should end.

        Returns:
            bool: True if the reservation was successfully added, False otherwise.
        """
        with self.session:
            try:
                reservation = Reserve(
                    telegram_id=self.telegram_id,
                    username=self.username,
                    file_path=file_path,
                    category=category,
                    filename=filename,
                    reserve_time_end=reserve_time_end
                )
                self.session.add(reservation)
                self.session.commit()
                return True
            except IntegrityError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'There is already a reservation on this file| Exception: {e}'
                    f'| Path: {file_path}'
                    )
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in adding reservations.| Exception: {e}| Path: {file_path}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in adding reservations.| Exception: {e}| Path: {file_path}'
                    )

    def check_reservation(self) -> tuple[str, dict]:
        """
        Retrieves and summarizes the reservation data for a user.

        Queries the database for reservations associated with the current user,
        identified by their Telegram ID. If reservations are found, counts the
        number of files reserved in each category and returns this data as a
        formatted string and a dictionary. Logs the count and details. If no
        reservations are found, returns zero and an empty dictionary.

        Returns:
            tuple[str, dict]: A tuple containing a formatted string summarizing
            the reservation counts by category and a dictionary with the categories 
            as keys and their respective counts as values.
        """

        with self.session:
            try:
                user_reservations = self.session.query(Reserve).filter_by(
                    telegram_id=self.telegram_id).all()
                if user_reservations:
                    # Словарь для хранения количества файлов каждого типа покупки
                    files_count_by_category = defaultdict(int)
                    # Считаем количество каждого типа
                    for res in user_reservations:
                        files_count_by_category[res.category] += 1
                    # Формируем текст с количеством файлов по типам
                    count_info = "\n".join(
                        [f"✔*{category}* : *{count}*" for category, count 
                         in files_count_by_category.items()]
                        )
                    log.info(
                        f'ID: {self.telegram_id}| Username: {self.username}| '
                        f'Count: {count_info}| Files: {files_count_by_category}'
                        )
                    return count_info, dict(files_count_by_category)
                else:
                    return 0, dict()
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in checking reservation.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in checking reservation.| Exception: {e}'
                    )

    def get_file_paths_by_telegram_id(self) -> list[str]|None:
        """
        Retrieves a list of file paths for reservations associated with the given Telegram ID.

        Returns:
            list[str]|None: A list of file paths if reservations are found, else None.
        """
        with self.session:
            try:
                # Querying the database
                user_reservations = self.session.query(Reserve).filter_by(
                    telegram_id=self.telegram_id
                    ).all()
                # Extracting file paths
                file_paths = [reservation.file_path for reservation in user_reservations]
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'File paths: {file_paths}'
                    )
                return file_paths
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting file paths.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting file paths.| Exception: {e}'
                    )

    def delete_reservation_by_file_path(self, file_path: str) -> bool:
        """
        Deletes a reservation from the database based on the provided file path.

        Args:
            file_path (str): The path to the file whose reservation should be deleted.

        Returns:
            bool: True if the reservation was successfully deleted, False otherwise.
        """
        with self.session:
            try:
                # Ищем запись в таблице Reserve по file_path
                reservation_to_delete = self.session.query(Reserve).filter_by(
                    file_path=file_path
                    ).first()
                if reservation_to_delete:
                    # Если запись найдена, удаляем её из сессии и подтверждаем изменения
                    self.session.delete(reservation_to_delete)
                    self.session.commit()
                    log.info(
                        f'ID: {self.telegram_id}| Username: {self.username}| '
                        f'Deleted reservation by file path: {file_path}'
                        )
                    return True
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in deleting reservation by file path.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in deleting reservation by file path.| Exception: {e}'
                    )
            return False

    def delete_expired_reservations(self) -> None:
        """
        Deletes all expired reservations from the database.

        This method queries the Reserve table for all records with a reserve_time_end
        value less than the current time and deletes them from the session. The changes
        are then committed to the database.

        If an error occurs during the deletion process, it is logged with ERROR level.
        """
        with self.session:
            try:
                current_time = datetime.now(timezone)
                expired_reservations = self.session.query(Reserve).filter(
                    Reserve.reserve_time_end < current_time
                    ).all()
                for reservation in expired_reservations:
                    self.session.delete(reservation)
                self.session.commit()
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Deleted expired reservations'
                    )
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in deleting expired reservations.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in deleting expired reservations.| Exception: {e}'
                    )

    def get_reserve_items_count(self)-> dict:
        """
        Returns a dictionary with category names as keys and their respective counts as values.

        The method queries the Reserve table for all records and counts the number of records
        for each category. The result is returned as a dictionary.

        If an error occurs during the query or counting process, it is logged with ERROR level.
        """
        with self.session:
            try:
                reserve_items = self.session.query(Reserve).all()
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting reserve items count.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting reserve items count.| Exception: {e}'
                    )
            if not reserve_items:
                return {}

            category_counts = {}
            for item in reserve_items:
                category = item.category
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            log.info(
                f'ID: {self.telegram_id}| Username: {self.username}| '
                f'Category counts: {category_counts}'
                )
            return category_counts

    def clear_reserve_by_telegram_id(self) -> None:
        """
        Deletes all reserve items associated with the user identified by the provided Telegram ID.
        The method queries the Reserve table for all 
        records with the provided Telegram ID and deletes them.
        If an error occurs during the deletion process, it is logged with ERROR level.
        """
        with self.session:
            try:
                self.session.query(Reserve).filter(Reserve.telegram_id == self.telegram_id).delete()
                self.session.commit()
                log.info(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Deleted reserve items'
                    )
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in clearing reserve items.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in clearing reserve items.| Exception: {e}'
                    )

    def get_users_stats(self) -> str|None:
        """
        Retrieves and formats user statistics, including balance and purchase history.

        Retrieves the user's balance and the 20 most recent purchases.
        Formats the retrieved data into a string and logs it with INFO level.
        Returns the formatted string.
        If an error occurs during the retrieval or formatting process, 
        it is logged with ERROR level.
        """
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
                purchases = self.session.query(SellLog).filter_by(
                    telegram_id=self.telegram_id
                    ).order_by(desc(SellLog.time)).limit(20).all()

                stats_str = f"👤 User: {user.name} - {user.telegram_id}\n"
                stats_str += f"💰 Balance: {user.balance}\n\n"

                for purchase in purchases:
                    formatted_time = purchase.time.strftime('%d-%m-%Y %H:%M:%S')
                    stats_str += (
                        f"⏳ Time: {formatted_time}\n✏️ Type: {purchase.type},\n📄" 
                        f" Filename: {purchase.filename},\n💲 Price: {purchase.price}\n\n"
                        )
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Stats: {stats_str}')
                return stats_str
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting users stats.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting users stats.| Exception: {e}'
                    )


class LotsDb:
    """
    Class for working with lots in the database.
    """
    def __init__(self, telegram_id: str, username: str) -> None:
        self.session = session
        self.telegram_id = telegram_id
        self.username = username

    def get_all_lots(self) -> list:
        """
        Retrieves all lots from the database.

        Queries the database for all lots and returns them as a list of Lots objects.
        If an error occurs during the retrieval process, it is logged with ERROR level.

        Returns:
            list: A list of Lots objects.
        """
        with self.session:
            try:
                lots = self.session.query(Lots).all()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Getting all lots')
                return lots
            except SQLAlchemyError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting all lots.| Exception: {e}'
                    )
            except AttributeError as e:
                log.error(
                    f'ID: {self.telegram_id}| Username: {self.username}| '
                    f'Error in getting all lots.| Exception: {e}'
                    )
