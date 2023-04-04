import hashlib
from app.data.__all_models import users, rooms
from app.data.db_session import create_session
db_sess = create_session()


def sha512(Password):
    HashedPassword = hashlib.sha512(Password.encode('utf-8')).hexdigest()
    return HashedPassword


def account_check(req):
    a = req.cookies.get('session', 0)

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
