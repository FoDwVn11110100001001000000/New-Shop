import pytz

from datetime import datetime
from collections import defaultdict

from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from utils.logs import log
from database.models import User, SellLog, Reserve, Lots, timezone


class UserDb:
    def __init__(self, session: sessionmaker, telegram_id: str, username: str, name: str) -> None:
        self.user = User
        self.session = session
        self.telegram_id = telegram_id
        self.username = username
        self.name = name

    def user_availability(self) -> bool:
        """
        Checks if user is in the database. If user is found, refreshes last visit parameter.

        Returns:
            bool: True if user is in the database, False if not.
        """
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                # Refresh last visit parameter
                user.last_visit = datetime.now(timezone)
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Was already in the database. Last visit refreshed')
                return True
            else:
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| User not found')
                return False
    
    def add_user(self, language: str) -> None:
        with self.session:
            new_user = User(
                telegram_id= self.telegram_id,
                name= self.name,
                username= self.username,
                balance= 0,
                language= language,
                last_visit= datetime.now(timezone)
            )
            self.session.add(new_user)
            log.info(f"ID: {self.telegram_id}| Username: {self.username}| Added to the database")
            self.session.commit()

    def topup_balance(self, new_balance: str) -> bool:
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                user.balance += float(new_balance)
                self.session.commit()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Changed balance to: {new_balance}')
                return True
            else:
                log.error('ID: {self.telegram_id}| Username: {self.username}| User not found')
                return False

    def get_balance(self) -> str|None:
        with self.session:
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                balance = user.balance
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Balance: {balance}')
                return balance
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')

    def change_user_language(self, new_language: str) -> bool:
        with self.session:  
            user = self.session.query(User).filter(User.telegram_id == self.telegram_id).first()
            if user:
                user.language = new_language
                self.session.commit()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Changed language in the database')
                return True
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')
                return False

    def get_user_language(self) -> str|None:
        with self.session: 
            user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
            if user:
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Getting language: {user.language}')
                return user.language
            else:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| User not found')
                return None


    def get_banned_users(self) -> list:
        with self.session:
            banned_users = self.session.query(User).filter(User.is_ban == True).all()
            if banned_users:
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Banned users: {banned_users}')
                return [f"ID: {user.telegram_id} - User: {user.username}" for user in banned_users]
            else:
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| No users are banned')
                return "No users are banned"

    def set_user_ban(self, telegram_id: str) -> bool:
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    user.is_ban = True
                    self.session.commit()
                    log.info(f'ID: {self.telegram_id}| Username: {self.username}| User {telegram_id} was banned')
                    return True
                return False
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in banning user {telegram_id}.| Exception: {e}')

    def set_user_unban(self, telegram_id: str) -> bool:
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    user.is_ban = False
                    self.session.commit()
                    log.info(f'ID: {self.telegram_id}| Username: {self.username}| User {telegram_id} was unbanned')
                    return True
                return False
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in unbanning user {telegram_id}.| Exception: {e}')

    def check_ban(self, telegram_id: str) -> bool:
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    return user.is_ban
                return False
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in checking ban status of user {telegram_id}.| Exception: {e}')


class SelllogDb:
    def __init__(self, session: sessionmaker, telegram_id: str, username: str, name: str) -> None:
        self.user = User
        self.session = session
        self.telegram_id = telegram_id
        self.username = username
        self.name = name

    def count_rows(self) -> str:
        with self.session:
            count = self.session.query(func.count(SellLog.id)).filter(SellLog.telegram_id == self.telegram_id).scalar()
            log.info(f'ID: {self.telegram_id}| Username: {self.username}| Count: {count}')
            return str(count)

    def sell_log(self, folder_name: str, filename: str, price: float) -> None:
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
            log.info(f'ID: {self.telegram_id}| Username: {self.username}| Added sell log to the database')

    def topup_log(self, folder_name: str, filename: str, price: float) -> None:
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
    def __init__(self, session: sessionmaker, telegram_id: str, username: str) -> None:
        self.user = User
        self.session = session
        self.telegram_id = telegram_id
        self.username = username

    def is_file_reserved(self, file_path: str) -> bool:
        with self.session: 
            try: 
                check_reserve = self.session.query(Reserve).filter(Reserve.file_path == file_path).count() > 0
                return check_reserve
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in reserve check.| Path: {file_path}| Exception: {e}')

    def delete_expired_reservations(self) -> None:
        with self.session:
            try:
                current_time_utc = datetime.now(timezone)
                self.session.query(Reserve).filter(Reserve.reserve_time_end < current_time_utc).delete(synchronize_session=False)
                self.session.commit()
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in deleting expired reservations.| Exception: {e}')

    def add_reservation(self, file_path: str, category: str, filename: str, reserve_time_end: datetime) -> bool:
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
            except IntegrityError:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| There is already a reservation on this file| Path: {file_path}')
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in adding reservation.| Path: {file_path}| Exception: {e}')
            return False

    def check_reservation(self) -> tuple[str, dict]:
        with self.session:
            try:
                user_reservations = self.session.query(Reserve).filter_by(telegram_id=self.telegram_id).all()
                if user_reservations:
                    # Словарь для хранения количества файлов каждого типа покупки
                    files_count_by_category = defaultdict(int)
                    # Считаем количество каждого типа
                    for res in user_reservations:
                        files_count_by_category[res.category] += 1
                    # Формируем текст с количеством файлов по типам
                    count_info = "\n".join([f"✔*{category}* : *{count}*" for category, count in files_count_by_category.items()])
                    log.info(f'ID: {self.telegram_id}| Username: {self.username}| Count: {count_info}| Files: {files_count_by_category}')
                    return count_info, dict(files_count_by_category)
                else:
                    return 0, dict()
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in checking reservation.| Exception: {e}')

    def get_file_paths_by_telegram_id(self) -> list[str]|None:
        with self.session: 
            try:
                # Получаем все записи из таблицы Reserve, где telegram_id равен заданному значению
                user_reservations = self.session.query(Reserve).filter_by(telegram_id=self.telegram_id).all()
                # Извлекаем file_path из каждой записи
                file_paths = [reservation.file_path for reservation in user_reservations]
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| File paths: {file_paths}')
                return file_paths
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in getting file paths.| Exception: {e}')

    def delete_reservation_by_file_path(self, file_path: str) -> bool:
        with self.session:
            try:
                # Ищем запись в таблице Reserve по file_path
                reservation_to_delete = self.session.query(Reserve).filter_by(file_path=file_path).first()
                if reservation_to_delete:
                    # Если запись найдена, удаляем её из сессии и подтверждаем изменения
                    self.session.delete(reservation_to_delete)
                    self.session.commit()
                    log.info(f'ID: {self.telegram_id}| Username: {self.username}| Deleted reservation by file path: {file_path}')
                    return True
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in deleting reservation by file path.| Exception: {e}')
            return False

    def delete_expired_reservations(self) -> None:
        with self.session:
            try:
                current_time = datetime.now(timezone)
                expired_reservations = self.session.query(Reserve).filter(Reserve.reserve_time_end < current_time).all()
                for reservation in expired_reservations:
                    self.session.delete(reservation)
                self.session.commit()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Deleted expired reservations')
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in deleting expired reservations.| Exception: {e}')

    def get_reserve_items_count(self)-> dict:
        with self.session:
            try:
                reserve_items = self.session.query(Reserve).all()
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in getting reserve items count.| Exception: {e}')
            if not reserve_items:
                return {}
            
            category_counts = {}
            for item in reserve_items:
                category = item.category
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            log.info(f'ID: {self.telegram_id}| Username: {self.username}| Category counts: {category_counts}')
            return category_counts

    def clear_reserve_by_telegram_id(self) -> None:
        with self.session:
            try:
                self.session.query(Reserve).filter(Reserve.telegram_id == self.telegram_id).delete()
                self.session.commit()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Deleted reserve items')
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in clearing reserve items.| Exception: {e}')

    def get_users_stats(self) -> str|None:
        with self.session:
            try:
                user = self.session.query(User).filter_by(telegram_id=self.telegram_id).first()
                purchases = self.session.query(SellLog).filter_by(telegram_id=self.telegram_id).order_by(desc(SellLog.time)).limit(20).all()

                stats_str = f"👤 User: {user.name} - {user.telegram_id}\n"
                stats_str += f"💰 Balance: {user.balance}\n\n"
                
                for purchase in purchases:
                    formatted_time = purchase.time.strftime('%d-%m-%Y %H:%M:%S')
                    stats_str += f"⏳ Time: {formatted_time}\n✏️ Type: {purchase.type},\n📄 Filename: {purchase.filename},\n💲 Price: {purchase.price}\n\n"
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Stats: {stats_str}')
                return stats_str
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in getting users stats.| Exception: {e}')


class LotsDb:
    def __init__(self, session: sessionmaker, telegram_id: str, username: str) -> None:
        self.session = session
        self.telegram_id = telegram_id

    def get_all_lots(self) -> list:
        with self.session:
            try:
                lots = self.session.query(Lots).all()
                log.info(f'ID: {self.telegram_id}| Username: {self.username}| Getting all lots')
                return lots
            except Exception as e:
                log.error(f'ID: {self.telegram_id}| Username: {self.username}| Error in getting all lots.| Exception: {e}')