import json
import random
import time
import hashlib
import flask_sock
from app import app, render_template
from flask import request, jsonify, make_response, redirect
from app.data.db_session import create_session
from app.data.__all_models import users, rooms
from app.socketproto import *
from app.funcs import *
from app.config import *

sock = flask_sock.Sock(app)

db_sess = create_session()

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
            room.state = 'lobby'
            room.cost = 10
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
            if 'logout' in request.form:
                user = db_sess.query(users.User).filter(users.User.glob_id == id).first()
                if user:
                    user.session = ''
                    db_sess.commit()
                    # print('\n\n\nhere\n\n\n')
                    return redirect('/login')
            else:
                return redirect('/edit_profile')
        else:
            user = db_sess.query(users.User.name, users.User.rating, users.User.about, users.User.email).filter(users.User.glob_id == id).first()
            # print(type(user))
            if len(user):
                # print('\n\n\n', dataxd, '\n\n\n')
                return render_template('profile.html', cur_user=user[0], rating=user[1], about=user[2], email=user[3]) 
            else:
                return "no data"
    else:
        return redirect('/signup')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    id = account_check(request)
    if id:
        user = db_sess.query(users.User).filter(users.User.glob_id == id).first()
        if request.method == 'POST':
            if 'confirm' in request.form:
                if user:
                    user.name = request.form['name']
                    user.about = request.form['de']
                    db_sess.commit()
                    return redirect('/profile')
                else:
                    return redirect('/profile')
            if 'cancel' in request.form:
                return redirect('/profile')
        print('\n\n\n', user.name, '\n\n\n')
        return render_template('edit_profile.html', cur_user=user.name, about=user.about, email=user.email, rating=user.rating)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', cur_user=get_username(request))

@app.route('/news', methods=['POST', 'GET'])
def news(request):
    # data = db_sess.query(news.New.title, news.New.description, news.New.date, news.New.topic, news.New.url).all()
    # return render_template('news.html', data=data, cur_user=get_username(request))
    return


# SOCKETS

@sock.route('/gamesock')
def handle(ws):
    db_sess2 = create_session()
    while True:
        data = ws.receive()
        result = socketdatacheck(data, request, db_sess2)
        # print(result)
        if result:
            ws.send(result)
        else:
            ...
            # ws.send('Something went wrong')
