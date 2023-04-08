import datetime
import time

import sqlalchemy
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase):
    __tablename__ = 'rooms'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    glob_id = sqlalchemy.Column(sqlalchemy.Integer,
                                unique=True)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    w = sqlalchemy.Column(sqlalchemy.Integer,
                          unique=False, nullable=True, default=0)
    b = sqlalchemy.Column(sqlalchemy.Integer,
                          unique=False, nullable=True, default=0)
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    started_time = sqlalchemy.Column(sqlalchemy.Integer,
                                     default=time.time())
    state = sqlalchemy.Column(sqlalchemy.String)
    wtimer = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    btimer = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    type = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    data = sqlalchemy.Column(sqlalchemy.String,
                             index=True, unique=False, nullable=True)
