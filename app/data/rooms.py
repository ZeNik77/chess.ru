import datetime
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
                          unique=False, nullable=True)
    b = sqlalchemy.Column(sqlalchemy.Integer,
                          unique=False, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer,
                             index=True, unique=False, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    state = sqlalchemy.Column(sqlalchemy.String)
    data = sqlalchemy.Column(sqlalchemy.String,
                             index=True, unique=False, nullable=True)
