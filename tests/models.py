import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    full_name = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    address = relationship("Address", uselist=False, backref="user")


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    description = Column(Text, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
