import random
import time

from app import app, render_template, connects
from flask import request, jsonify, make_response
from app.data.db_session import create_session
from app.data.__all_models import users, rooms
import hashlib

MAX_GAMES = 5
ROOM_IDS_RANGE = 10 ** 10
USER_IDS_RANGE = 10 ** 10

'''
rms = db_sess.query(rooms.Room).all()
        counter = 0
        for i in rms:
            k = eval(i.data)
            if account in k:
                counter += 1
        if counter < MAX_GAMES:
'''


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
            return res[0].id
    return False


@app.route('/')
@app.route('/index')
def index():
    return render_template('game.html')


@app.route('/room/new', methods=['GET', 'POST'])
def newroom():
    print(request.json)
    account = account_check(request)
    a = request.cookies.get('rooms_created', 0)
    if account:
        if a < MAX_GAMES:
            print('ok')
            room = rooms.Room()
            room.glob_id = id = random.randint(1, ROOM_IDS_RANGE)
            room.data = ''
            room.type = '1v1'
            room.users = 0
            db_sess.add(room)
            db_sess.commit()
            resp = make_response(id)
            resp.set_cookie("rooms_created", a + 1, max_age=60 * 60)

            @app.route(f'/room/{id}', methods=['GET'])
            def room():
                ...

            return resp
        else:
            print('not ok')
            return 'Too many rooms'
    else:
        return 'Session not found'


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
            try:
                new = users.User()
                new.glob_id = random.randint(1, USER_IDS_RANGE)
                new.email = mail
                new.name = username
                new.hashed_password = password
                db_sess.add(new)
                db_sess.commit()
            except:
                return 'server error'
            return 'Ok'
        else:
            return 'Failed'
    else:
        return render_template('signup.html')

@app.route('/leaderboard', methods=['POST', 'GET'])
def leaderboard():
    leaderboard_data = db_sess.query(users.User.name, users.User.rating).order_by(users.User.rating.desc()).all()
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)
