from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from passlib.apps import custom_app_context as password_context

import sys


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password_hash = Column(String(64))
    email = Column(String(250), index=True, unique=True, nullable=False)
    picture = Column(String(250))

    # Encrypt pw with SHA256
    def hash_password(self, password):
        self.password_hash = password_context.hash(password)

    # Check pws and return a boolean
    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)


class Language(Base):
    __tablename__ = "language"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, nullable=False, unique=True)
    # ForeignKey
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    # JSON serialization
    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    translation = Column(String(250))
    notes = Column(String(1000))
    is_learned = Column(Boolean, default=False)
    # ForeignKey
    language_id = Column(Integer, ForeignKey("language.id"))
    language = relationship(Language)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    # JSON serialization
    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "translation": self.translation,
            "notes": self.notes,
            "is_learned": self.is_learned,
            "language": self.language.name,
            "user": self.user.username
        }


engine = create_engine("sqlite:///morewords.db")

Base.metadata.create_all(engine)
