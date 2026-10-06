import random, secrets

_storage = {}   # sid -> правильный порядок

def new_captcha():
    sid = secrets.token_urlsafe(8)
    order = [0, 1, 2, 3]
    shuf = order[:]
    while shuf == order:
        random.shuffle(shuf)
    _storage[sid] = order
    return {"sid": sid, "shuffled": shuf}

def check_captcha(sid, user_order):
    return _storage.pop(sid, None) == user_order