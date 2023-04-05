import json
import random
import time
import hashlib
import flask_sock
from app import app, render_template
from flask import request, jsonify, make_response, redirect
from app.data.db_session import create_session
from app.data.__all_models import users, rooms

sock = flask_sock.Sock(app)
MAX_GAMES = 9999
ROOM_IDS_RANGE = 10 ** 10
USER_IDS_RANGE = 10 ** 10
db_sess = create_session()


# FUNCTIONS

def sha512(Password):
    HashedPassword = hashlib.sha512(Password.encode('utf-8')).hexdigest()
    return HashedPassword


def account_check(req):
    a = request.cookies.get('session', 0)

    if a:
        res = db_sess.query(users.User).filter(users.User.session == a).all()
        if len(res) == 1:
            return res[0].glob_id
    return False


def get_username(request):
    id = account_check(request)
    username = db_sess.query(users.User.name).filter(users.User.glob_id == id).first()
    if username:
        return username[0]
    else:
        return ''


def get_orientation(request):
    account = account_check(request)


# ERROR HANDLERS
...


# ROUTES
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', cur_user=get_username(request))


@app.route('/game')
def game():
    id = request.values.get('id', 0)
    account = account_check(request)
    if id and account:
        room = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == id).all()
        if room:
            room = room[0]
            if room.w == account or room.b == account:
                ...
            elif not room.w:
                room.w = account
            elif not room.b:
                room.b = account
            else:
                return redirect('/')

            db_sess.commit()
        else:
            return redirect('/')
    elif not account:
        return redirect('/login')
    else:
        return redirect('/')
    return render_template('game.html', cur_user=get_username(request))


@app.route('/newroom', methods=['GET'])
def newroom():
    account = account_check(request)
    a = int(request.cookies.get('rooms_created', 0))
    if account:
        if a < MAX_GAMES:
            room = rooms.Room()
            room.glob_id = id = random.randint(1, ROOM_IDS_RANGE)
            room.data = 'start'
            room.type = '1v1'
            room.users = '{}'
            db_sess.add(room)
            db_sess.commit()
            cnt = json.dumps({'id': id})
            resp = make_response(cnt)
            resp.set_cookie("rooms_created", value=str(a + 1), max_age=60 * 60)
            return resp
        else:
            return 'Too many rooms'
    else:
        return 'Session not found'


@app.route('/login', methods=['POST', 'GET'])
def login():
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
        return render_template('login.html', cur_user=get_username(request))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.is_json:
        username = request.json['name']
        mail = request.json['mail']
        password = request.json['pass']
        usrs = db_sess.query(users.User).filter(users.User.email == mail or users.User.name == username).all()
        if len(usrs) == 0:
            try:
                new = users.User()
                new.glob_id = random.randint(1, USER_IDS_RANGE)
                new.email = mail
                new.rating = 0
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
        return render_template('signup.html', cur_user=get_username(request))


@app.route('/leaderboard', methods=['POST', 'GET'])
def leaderboard():
    leaderboard_data = db_sess.query(users.User.name, users.User.rating).order_by(users.User.rating.desc()).all()
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data, cur_user=get_username(request))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    id = account_check(request)
    if id:
        if request.method == 'POST':            
            user = db_sess.query(users.User).filter(users.User.glob_id==id).first()
            if user:
                user.session = ''
                db_sess.commit()
                print('\n\n\nhere\n\n\n')
                return redirect('/login')
        else:
            dataxd = db_sess.query(users.User.name, users.User.rating).filter(users.User.glob_id == id).first()
            print(type(dataxd))
            if len(dataxd):
                #print('\n\n\n', dataxd, '\n\n\n')
                return render_template('profile.html', data=dataxd, cur_user=get_username(request))
            else:
                return "no data"
    else:
        return redirect('/signup')


# SOCKETS

@sock.route('/gamesock')
def handle(ws):
    account = account_check(request)
    data = ws.receive()
    if data == 'null':
        print('closing')
        ws.close()
    else:
        print(data)
        room = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == data).all()[0]
        # w_us = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == int(room.w)).first()
        # b_us = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == int(room.b)).first()
        jdt = {"fen": room.data, "orientation": "white" if room.w == account else "black"}

        ws.send(jdt)
        print('STARTED', data)
        print(jdt)
        while True:
            data = ws.receive(timeout=0.01)
            if not data:
                continue
            if data.count('/') == 7:
                room.data = data
                db_sess.commit()
            elif data == 'draw':
                ...
            elif data == 'checkmate':
                ...
            print(data)
            jdt = {"fen": room.data, "orientation": "white" if room.w == account else "black"}
            ws.send(jdt)


@app.route('/news', methods=['POST', 'GET'])
def news(request):
    # data = db_sess.query(news.New.title, news.New.description, news.New.date, news.New.topic, news.New.url).all()
    # return render_template('news.html', data=data, cur_user=get_username(request))
    return
