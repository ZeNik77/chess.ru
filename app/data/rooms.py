import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase):
    __tablename__ = 'rooms'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users = sqlalchemy.Column(sqlalchemy.Integer,
                              index=True, unique=False, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer,
                             index=True, unique=False, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    data = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=False, nullable=True)
