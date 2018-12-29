#!/usr/bin/env python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from passlib.apps import custom_app_context as pwd_context
import random, string

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(250), nullable=False, index=True, unique=True)
    id = Column(Integer, primary_key=True)
    description = Column(String(1500))
    category_name = Column(Integer, ForeignKey('category.name'))
    category = relationship("Category", back_populates='items')
    created_user_id = Column(Integer, ForeignKey('user.id'))
    created_user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category': self.category_name
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    items = relationship("Item", back_populates='category')

    @property
    def serialize(self):
        """Return Category data in easily serializeable format
            including data from items under category"""
        return {
            'name': self.name,
            'id': self.id,
            'items': [i.serialize for i in self.items]
        }

    @property
    def serializeWithoutItems(self):
        """Return Category data in easily serializeable format
            without information about items under category"""
        return {
            'name': self.name,
            'id': self.id,
        }


engine = create_engine('sqlite:///categoryapp.db')
Base.metadata.create_all(engine)
