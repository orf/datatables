from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
import datetime
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


engine=create_engine('sqlite://', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)