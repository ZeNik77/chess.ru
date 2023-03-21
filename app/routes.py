from app import app, render_template, connects
from flask import request, jsonify


@app.route('/')
@app.route('/index')
def index():
    return render_template('game.html')


@app.route('/room/new', methods=['POST'])
def newroom():
    print(request.json, request.cookies.get('accounthash', 0))
    return connects.newroom(request)
