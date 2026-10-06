from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app import auth, captcha

app = FastAPI(title="ДЭ 2026 API", version="1.0.0",
              description="Информационная система для демонстрационного экзамена")


class LoginIn(BaseModel):
    username: str
    password: str
    sid: str
    order: list[int]


# ── API ─────────────────────────────────────────
@app.get("/api/captcha/new")
def cap_new():
    return captcha.new_captcha()


@app.post("/api/auth/login")
def login(data: LoginIn):
    if not captcha.check_captcha(data.sid, data.order):
        return JSONResponse({"ok": False, "message": "Капча не пройдена"}, 400)
    u, err = auth.login(data.username, data.password)
    if err == "blocked":
        return JSONResponse({"ok": False, "message": "Вы заблокированы. Обратитесь к администратору"}, 403)
    if err:
        return JSONResponse({"ok": False,
            "message": "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные"}, 401)
    return {"ok": True, "message": "Вы успешно авторизовались",
            "token": auth.make_token(u), "role": u.role}


@app.get("/api/admin/users")
def list_users(token: str):
    me = auth.current(token)
    if not me or me.role != "admin":
        return JSONResponse({"ok": False, "message": "Нет доступа"}, 403)
    return [{"username": u.username, "role": u.role, "blocked": u.blocked}
            for u in auth.users.values()]


@app.post("/api/admin/add")
def add_user(data: LoginIn, token: str):
    me = auth.current(token)
    if not me or me.role != "admin":
        return JSONResponse({"ok": False, "message": "Нет доступа"}, 403)
    ok, msg = auth.add_user(data.username, data.password)
    return JSONResponse({"ok": ok, "message": msg}, 400 if not ok else 200)


@app.post("/api/admin/block")
def block_user(username: str, value: bool, token: str):
    me = auth.current(token)
    if not me or me.role != "admin":
        return JSONResponse({"ok": False, "message": "Нет доступа"}, 403)
    ok, msg = auth.set_blocked(username, value)
    return {"ok": ok, "message": msg}


# ── HTML ────────────────────────────────────────
LOGIN_PAGE = """<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<title>Вход</title><style>
body{font-family:sans-serif;background:#2a5298;display:flex;justify-content:center;
     align-items:center;min-height:100vh;margin:0}
.card{background:#fff;padding:30px;border-radius:14px;width:360px;
      box-shadow:0 10px 40px rgba(0,0,0,.3)}
h2{margin:0 0 20px;color:#2a5298}
input{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ccc;
      border-radius:8px;box-sizing:border-box;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:6px;margin-bottom:14px}
.piece{aspect-ratio:1;border-radius:8px;cursor:pointer;display:flex;
       align-items:center;justify-content:center;color:#fff;font-size:32px;
       font-weight:bold;border:3px solid transparent}
.piece.sel{border-color:#2a5298}
button{width:100%;padding:11px;background:#2a5298;color:#fff;border:0;
       border-radius:8px;font-size:15px;cursor:pointer}
button:hover{background:#1e3c72}
.msg{margin-top:10px;padding:8px;border-radius:6px;font-size:13px;text-align:center}
.err{background:#fee;color:#c0392b}.ok{background:#e8f8f5;color:#0e7c5a}
</style></head><body>
<div class="card">
<h2>Вход в систему</h2>
<input id="u" placeholder="Логин">
<input id="p" type="password" placeholder="Пароль">
<div class="grid" id="cap"></div>
<button onclick="go()">Войти</button>
<div id="m" class="msg"></div>
</div>
<script>
let sid, order=[], sel=null;
const COLORS=['#ff6b6b','#feca57','#48dbfb','#1dd1a1'];
const SYMS=['1','2','3','4'];

async function load(){
  const r = await fetch('/api/captcha/new'); const d = await r.json();
  sid = d.sid; order = d.shuffled; sel = null; draw();
}
function draw(){
  const c = document.getElementById('cap'); c.innerHTML='';
  order.forEach((v,i)=>{
    const d = document.createElement('div');
    d.className = 'piece' + (sel===i?' sel':'');
    d.style.background = COLORS[v];
    d.textContent = SYMS[v];
    d.onclick = ()=>click(i);
    c.appendChild(d);
  });
}
function click(i){
  if(sel===null){ sel=i; draw(); return; }
  if(sel===i){ sel=null; draw(); return; }
  [order[sel], order[i]] = [order[i], order[sel]];
  sel=null; draw();
}
async function go(){
  const u=document.getElementById('u').value.trim();
  const p=document.getElementById('p').value;
  if(!u || !p){ msg('Заполните все поля','err'); return; }
  const r = await fetch('/api/auth/login',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:u,password:p,sid,order})});
  const d = await r.json();
  msg(d.message, d.ok?'ok':'err');
  if(d.ok){
    localStorage.setItem('token',d.token);
    localStorage.setItem('role',d.role);
    setTimeout(()=>location.href = d.role==='admin'?'/admin':'/',800);
  } else load();
}
function msg(t,c){ const m=document.getElementById('m'); m.textContent=t; m.className='msg '+c; }
load();
</script></body></html>"""


ADMIN_PAGE = """<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<title>Админ</title><style>
body{font-family:sans-serif;background:#f0f2f8;padding:40px;margin:0}
.box{max-width:700px;margin:auto;background:#fff;padding:30px;border-radius:14px;
     box-shadow:0 5px 20px rgba(0,0,0,.1)}
h2{color:#2a5298}
table{width:100%;border-collapse:collapse;margin:16px 0}
th,td{padding:10px;border-bottom:1px solid #eee;text-align:left;font-size:14px}
th{background:#f5f6fa}
input,select{padding:8px;border:1px solid #ccc;border-radius:6px;margin-right:6px}
button{padding:6px 12px;border:0;border-radius:6px;cursor:pointer;font-size:13px}
.b{background:#c0392b;color:#fff}.g{background:#1dd1a1;color:#fff}
.p{background:#2a5298;color:#fff;padding:8px 16px}
</style></head><body>
<div class="box">
<h2>Панель администратора</h2>
<div>
<input id="nu" placeholder="Логин">
<input id="np" type="password" placeholder="Пароль">
<button class="p" onclick="add()">Добавить</button>
</div>
<div id="m" style="margin:10px 0;color:#2a5298"></div>
<table><thead><tr><th>Логин</th><th>Роль</th><th>Статус</th><th></th></tr></thead>
<tbody id="rows"></tbody></table>
<a href="/">Выйти</a>
</div>
<script>
const t = localStorage.getItem('token');
async function load(){
  const r = await fetch('/api/admin/users?token='+t);
  const d = await r.json();
  const tb = document.getElementById('rows'); tb.innerHTML='';
  d.forEach(u=>{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${u.username}</td><td>${u.role}</td>
      <td>${u.blocked?'Заблокирован':'Активен'}</td>
      <td><button class="${u.blocked?'g':'b'}" onclick="bl('${u.username}',${!u.blocked})">
        ${u.blocked?'Разблокировать':'Блокировать'}</button></td>`;
    tb.appendChild(tr);
  });
}
async function add(){
  const u=document.getElementById('nu').value;
  const p=document.getElementById('np').value;
  const r=await fetch('/api/admin/add?token='+t,{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:u,password:p,sid:'',order:[]})});
  const d=await r.json();
  document.getElementById('m').textContent=d.message;
  if(d.ok){document.getElementById('nu').value='';document.getElementById('np').value='';load();}
}
async function bl(name,val){
  await fetch(`/api/admin/block?username=${name}&value=${val}&token=${t}`,{method:'POST'});
  load();
}
load();
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return LOGIN_PAGE

@app.get("/admin", response_class=HTMLResponse)
def admin():
    return ADMIN_PAGE