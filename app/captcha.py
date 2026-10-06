"""Капча: сборка картинки 2x2 из фрагментов."""
import random, secrets

_storage = {}
PIECES = ["1.png", "2.png", "3.png", "4.png"]


def new_captcha():
    sid = secrets.token_urlsafe(8)
    shuf = PIECES[:]
    while shuf == PIECES:
        random.shuffle(shuf)
    _storage[sid] = PIECES[:]
    return {"sid": sid, "shuffled": shuf}


def check_captcha(sid, user_order):
    return _storage.pop(sid, None) == user_order