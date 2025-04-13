"""
This module contains classes for working with the database.
"""

from datetime import datetime
from pytz import timezone
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, Text, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from env import Config as config


tz = timezone(config.timezone)

engine = create_engine(config.database_url)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    name = Column(String)
    username = Column(String, index=True)
    balance = Column(Float)
    language = Column(String)
    last_visit = Column(DateTime)
    is_ban = Column(Boolean, default=False)

    # Relationships
    sell_logs = relationship("SellLog", back_populates="user")

class SellLog(Base):
    __tablename__ = 'sell_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, default=lambda: datetime.now(tz))
    telegram_id = Column(BigInteger, ForeignKey('users.telegram_id'), index=True)
    name = Column(String)
    username = Column(String)
    type = Column(String)
    filename = Column(String)
    price = Column(String)

    # Relationships
    user = relationship("User", back_populates="sell_logs")


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_type = Column(String, index=True)
    lot_format = Column(String)
    txt = Column(Text, unique=True)
    price = Column(Float)
    added_by = Column(String, index=True)


# Base.metadata.create_all(engine)
