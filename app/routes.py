from app import app, render_template, connects
from flask import request, jsonify


def account_check(req):
    a = request.cookies.get('session', 0)
    if a:
        return True
    else:
        return False


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
    print(request.data)
    if request.is_json:
        username = request.json.get('name', 0)
        password = request.json.get('pass', 0)
        print(username, password)
        return 'xd'
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = request.json['name']
    password = request.json['pass']
