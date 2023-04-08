import json
from app.config import *
from app.data import rooms
from app.data.db_session import create_session
from app.funcs import *


def socketdatacheck(data, request, db_sess):
    lobbyflg = 0
    if not data:
        return False
    # print(data)
    data = json.loads(data)
    type = data['type']
    room_id = int(data['roomid'])
    color = data.get('color', None)
    fen = data.get('fen', None)
    wintype = data.get('wintype', None)
    room = db_sess.query(rooms.Room).filter(rooms.Room.glob_id == room_id).all()
    if not room:
        if DEBUG:
            print('room not found')
        return False
    else:
        room = room[0]
    id = account_check(request)
    w_user = db_sess.query(users.User).filter(users.User.glob_id == room.w).all()
    if not w_user:
        if DEBUG:
            print('white user not found')
        w_user = None
    w_user = w_user[0] if w_user else None
    b_user = db_sess.query(users.User).filter(users.User.glob_id == room.b).all()
    if not b_user:
        if DEBUG:
            print('black user not found')
        b_user = None
    b_user = b_user[0] if b_user else None
    if type == 'JOIN':
        flg_in = 1 if room.w == id or room.b == id else 0
        if not flg_in:
            if not room.w:
                room.w = id
            elif not room.b:
                room.b = id
            else:
                return 'OK'
        if room.w and room.b:
            room.state = 'game'
        db_sess.commit()
        return 'OK'
    elif type == 'UPDATE':
        if not fen:
            if DEBUG:
                print('Fen value has not been set')
            return False
        room.data = fen
        db_sess.commit()
        state = room.state
        pack = {'type': 'GET', 'fen': room.data, 'orientation': 'black' if room.b == id else 'white',
                'state': state, 'perms': 'player' if room.w == id or room.b == id else 'observer'}
        return json.dumps(pack)
    elif type == 'GET':
        state = room.state
        pack = {'type': 'GET', 'fen': room.data, 'orientation': 'black' if room.b == id else 'white',
                'state': state,
                'perms': 'player' if (room.w == id and room.w) or (room.b == id and room.b) else 'observer'}
        return json.dumps(pack)
    elif type == 'END' and room.state != 'end':
        if not w_user or not b_user:
            return False
        if not wintype:
            if DEBUG:
                print('endtype value has not been set')
            return False
        if wintype == 'win':
            winner = data.get('winner', None)
            room.state = 'end'
            if winner == 'w':
                w_user.rating += room.cost
            elif winner == 'b':
                b_user.rating += room.cost
            else:
                if DEBUG:
                    print('invalid winner value')
                db_sess.commit()
                return False
            db_sess.commit()
            return 'OK'
        elif wintype == 'draw':
            w_user.rating += room.cost // 2
            b_user.rating += room.cost // 2
            db_sess.commit()
        else:
            if DEBUG:
                print('invalid wintype')
            return False
    else:
        if DEBUG:
            print("Invalid request type")
        return False
