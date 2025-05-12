from faker import Faker
import random
from database.models import User, SellLog, Account, session

fake = Faker()

def populate_db():
    # Users
    users = []
    for _ in range(20):
        user = User(
            telegram_id=fake.unique.random_int(min=100000000, max=999999999),
            name=fake.name(),
            username=fake.user_name(),
            balance=round(random.uniform(10.0, 1000.0), 2),
            language=random.choice(['en', 'ru', 'es']),
            last_visit=fake.date_time_between(start_date='-30d', end_date='now'),
            is_ban=random.choice([False, False, False, True])
        )
        session.add(user)
        users.append(user)
    session.commit()

    # SellLogs
    for user in users:
        for _ in range(4):  # Генерация 4 записей для каждого пользователя
            sell_log = SellLog(
                telegram_id=user.telegram_id,
                name=user.name,
                username=user.username,
                type=random.choice(['PDF', 'IMG', 'DOC']),
                filename=fake.file_name(extension=random.choice(['pdf', 'jpg', 'doc'])),
                price=str(round(random.uniform(5.0, 100.0), 2)),
            )
            session.add(sell_log)

    # Accounts
    accounts = []
    for _ in range(20):
        account = Account(
            lot_type=random.choice(['type1', 'type2', 'type3']),
            lot_format=random.choice(['txt', 'logpass', 'txt']),
            filename = f"{fake.unique.slug()[:8]}.txt",
            txt=fake.unique.text(max_nb_chars=100),
            price=random.choice([1, 2]),
            added_by=fake.user_name()
        )
        session.add(account)
        accounts.append(account)

    session.commit()
    print("✅ Database populated successfully.")

def init_db():
    if not session.query(User).first():
        populate_db()

