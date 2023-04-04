import json
from app.config import *
from app.data import rooms
from app.data.db_session import create_session
from app.funcs import *

db_sess = create_session()


def socketdatacheck(data, request):
    if not data:
        return False
    print(data)
    data = json.loads(data)
    type = data['type']
    room_id = int(data['roomid'])
    color = data.get('color', None)
    fen = data.get('fen', None)
    endtype = data.get('endtype', None)
    room = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == room_id).all()
    if not room:
        if DEBUG:
            print('room not found')
        return False
    else:
        room = room[0]
    w_user = db_sess.query(users.User).filter(users.User.glob_id == room.w).all()
    if not w_user:
        if DEBUG:
            print('white user not found')
        return False
    w_user = w_user[0]
    b_user = db_sess.query(users.User).filter(users.User.glob_id == room.b).all()
    if not b_user:
        if DEBUG:
            print('black user not found')
        return False
    b_user = b_user[0]
    id = account_check(request)
    if type == 'JOIN':
        if room.w == id or room.b == id:
            if DEBUG:
                print('user already in room')
            return 'OK'
        if color == None:
            if not room.w:
                room.w = id
            elif not room.b:
                room.b = id
            else:
                if DEBUG:
                    print('all colors busy')
                return False
        elif color == 'w':
            room.w = id
        elif color == 'b':
            room.b = id
        else:
            if DEBUG:
                print('invalid color value')
            return False
        db_sess.commit()
        return 'OK'
    elif type == 'UPDATE':
        if not fen:
            if DEBUG:
                print('Fen value has not been set')
            return False
        room.data = fen
        db_sess.commit()
        return 'OK'
    elif type == 'GET':
        pack = {'type': 'GET', 'fen': room.data, 'orientation': 'white' if room.w == id else 'black'}
        return json.dumps(pack)
    elif type == 'END':
        if not endtype:
            if DEBUG:
                print('endtype value has not been set')
            return False
        if endtype == 'win':
            winner = data.get('winner', None)
            if winner == 'w':
                w_user.rate += room.cost
            elif winner == 'b':
                b_user.rate += room.cost
            else:
                if DEBUG:
                    print('invalid winner value')
                return False
            db_sess.commit()
            return 'OK'
    else:
        if DEBUG:
            print("Invalid request type")
        return False
