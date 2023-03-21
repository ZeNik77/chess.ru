from flask import Flask, render_template
from .data import db_session
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
from app import routes
db_session.global_init("app/db/main.db")
