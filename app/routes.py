import time

from app import app, render_template, connects
from flask import request, jsonify, make_response
from app.data.db_session import create_session
from app.data.__all_models import users
import hashlib


def sha512(Password):
    HashedPassword = hashlib.sha512(Password.encode('utf-8')).hexdigest()
    return HashedPassword


db_sess = create_session()
'''
test = users.User()
test.name = 'xdeshnik'
test.email = 'aye@mail.ru'
db_sess.add(test)
db_sess.commit()
'''


def account_check(req):
    a = request.cookies.get('session', 0)
    if a:
        res = db_sess.query(users.User).filter(users.User.session == a).all()
        if len(res) == 1:
            return True
    return False


@app.route('/')
@app.route('/index')
def index():
    return render_template('game.html')


@app.route('/room/new', methods=['POST'])
def newroom():
    print(request.json)
    if account_check(request):
        return connects.newroom(request)
    else:
        return 'Session not found', 418


@app.route('/login', methods=['POST', 'GET'])
def login():
    print(account_check(request))
    if request.is_json:
        username = request.json.get('name', 0)
        password = request.json.get('pass', 0)
        res = db_sess.query(users.User).filter(
            users.User.name == username and users.User.hashed_password == password).all()
        if res:
            user = res[0]
            session = sha512(user.hashed_password + str(time.time()))
            user.session = session
            db_sess.commit()
            res = make_response(session)
            res.set_cookie("session", session, max_age=60 * 60 * 24 * 365 * 2)
            return res
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.is_json:
        username = request.json['name']
        mail = request.json['mail']
        password = request.json['pass']
        usrs = db_sess.query(users.User).filter(users.User.email == mail or users.User.name == username).all()
        if len(usrs) == 0:
            print('ok')
            new = users.User()
            new.email = mail
            new.name = username
            new.hashed_password = password
            db_sess.add(new)
            db_sess.commit()
            return 'Ok'
        else:
            return 'Failed'
    else:
        return render_template('signup.html')
