import pytz

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from env import Config as config


timezone = pytz.timezone(config.timezone)

engine = create_engine(config.database_url)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True)
    name = Column(String)
    username = Column(String)
    balance = Column(Float)
    language = Column(String)
    last_visit = Column(DateTime)
    is_ban = Column(Boolean, default=False)

class SellLog(Base):
    __tablename__ = 'sell list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, default=datetime.now(timezone))
    telegram_id = Column(BigInteger)
    name = Column(String)
    username = Column(String)
    type = Column(String)
    filename = Column(String)
    price = Column(String)

class Reserve(Base):
    __tablename__ = 'reserve'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger)
    username = Column(String)
    file_path = Column(String)
    category = Column(String)
    filename = Column(String, unique=True)
    reserve_time_end = Column(DateTime)

class Lots(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_type = Column(String)
    txt = Column(Text, unique=True)
    added_by = Column(String)

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_type = Column(String) # Header
    price = Column(Float)
    lot_format = Column(String) # txt or logpass


Base.metadata.create_all(engine)


