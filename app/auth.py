import hashlib, secrets
from dataclasses import dataclass

@dataclass
class User:
    username: str
    password_hash: str
    role: str = "user"
    blocked: bool = False
    fails: int = 0

def h(p): return hashlib.sha256(p.encode()).hexdigest()

users = {
    "admin": User("admin", h("admin123"), "admin"),
    "user":  User("user",  h("user123")),
}
tokens = {}

def login(username, password):
    u = users.get(username)
    if not u: return None, "not_found"
    if u.blocked: return None, "blocked"
    if u.password_hash != h(password):
        u.fails += 1
        if u.fails >= 3: u.blocked = True
        return None, "blocked" if u.blocked else "invalid"
    u.fails = 0
    return u, None

def make_token(u):
    t = secrets.token_urlsafe(16)
    tokens[t] = u.username
    return t

def current(token):
    return users.get(tokens.get(token, ""))

def add_user(name, pwd, role="user"):
    if name in users: return False, "Пользователь уже существует"
    users[name] = User(name, h(pwd), role)
    return True, "Пользователь добавлен"

def set_blocked(name, blocked):
    if name not in users: return False, "Не найден"
    users[name].blocked = blocked
    if not blocked: users[name].fails = 0
    return True, "Обновлено"