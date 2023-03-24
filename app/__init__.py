from flask import Flask, render_template
from .data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("app/db/main.db")
from app import routes
