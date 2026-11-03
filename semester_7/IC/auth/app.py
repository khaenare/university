"""
Сервер авторизації (Flask + SQLite).

Зберігає користувачів і сесії в SQLite. Шлюз nginx перед кожним запитом
до Grafana/Prometheus викликає /auth/verify: якщо сесія дійсна — сервер
повертає 200 і логін/роль користувача, інакше 401 (шлюз перенаправляє на вхід).

Керування користувачами з командного рядка:
    python app.py add-user <логін> <пароль> [Viewer|Editor|Admin]
    python app.py delete-user <логін>
    python app.py list-users
"""
import argparse
import hashlib
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import Flask, Response, redirect, render_template_string, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from werkzeug.security import check_password_hash, generate_password_hash

SERVICE_NAME = "auth"
DB_PATH = os.getenv("AUTH_DB_PATH", "/data/auth.db")
SESSION_TTL = int(os.getenv("SESSION_TTL_SECONDS", str(8 * 3600)))
COOKIE_NAME = "ic_session"
ROLES = ("Viewer", "Editor", "Admin")
# Логін передається в Grafana HTTP-заголовком, тому лише ASCII-символи
USERNAME_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")
MIN_PASSWORD_LENGTH = 8
# Після стількох невдалих спроб за LOCKOUT_SECONDS вхід для пари логін+IP блокується
MAX_FAILED_LOGINS = 5
# ...а після стількох невдалих спроб з однієї IP (з будь-якими логінами) — для всієї IP
MAX_FAILED_PER_IP = 30
LOCKOUT_SECONDS = 5 * 60
# Скільки пар логін+IP пам'ятати одночасно (захист від переповнення пам'яті)
MAX_TRACKED_KEYS = 10_000


def check_credentials(username, password):
    """Повертає текст помилки, якщо логін або пароль не відповідають правилам."""
    if not USERNAME_RE.fullmatch(username or ""):
        return "логін: лише латинські літери, цифри та . _ - (до 64 символів)"
    if len(password or "") < MIN_PASSWORD_LENGTH:
        return f"пароль має містити щонайменше {MIN_PASSWORD_LENGTH} символів"
    return None


# ---------- Логи у форматі JSON ----------

class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            # ISO 8601 з часовим поясом, щоб не плутати з локальним часом у Grafana
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
log = logging.getLogger(SERVICE_NAME)
log.addHandler(handler)
log.setLevel(logging.INFO)


# ---------- Робота з SQLite ----------

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'Viewer',
                created_at    REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at REAL NOT NULL
            );
        """)
        # Перший адміністратор береться зі змінних оточення — лише для порожньої БД,
        # щоб видалений адміністратор не з'являвся знову зі старим паролем з .env
        admin, password = os.getenv("ADMIN_USERNAME"), os.getenv("ADMIN_PASSWORD")
        no_users = conn.execute("SELECT count(*) FROM users").fetchone()[0] == 0
        if admin and password and no_users:
            problem = check_credentials(admin, password)
            if problem:
                raise ValueError(f"ADMIN_USERNAME/ADMIN_PASSWORD: {problem}")
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, 'Admin', ?)",
                (admin, generate_password_hash(password), time.time()),
            )
            log.info("Створено адміністратора", extra={"fields": {"username": admin}})


def hash_token(token):
    # У БД зберігається лише хеш токена сесії, а не сам токен
    return hashlib.sha256(token.encode()).hexdigest()


def current_user():
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    with db() as conn:
        return conn.execute(
            "SELECT u.username, u.role FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token_hash = ? AND s.expires_at > ?",
            (hash_token(token), time.time()),
        ).fetchone()


def count_active_sessions():
    with db() as conn:
        return conn.execute("SELECT count(*) FROM sessions WHERE expires_at > ?",
                            (time.time(),)).fetchone()[0]


# ---------- Захист від підбору пароля ----------

# Ключі: ("user", логін, IP) — спроби входу; ("ip", IP) — невдалі спроби з IP.
# Значення — час спроб; порядок ключів — від найдавніше змінених.
_attempts = {}
_attempts_lock = threading.Lock()
# Хеш для неіснуючих логінів: перевірка пароля триває однаково довго,
# тож за часом відповіді не можна дізнатися, чи існує користувач
DUMMY_PASSWORD_HASH = generate_password_hash(secrets.token_urlsafe(16))


def _recent(key, now):
    return [t for t in _attempts.get(key, []) if t > now - LOCKOUT_SECONDS]


def _store(key, times, now):
    _attempts.pop(key, None)
    _attempts[key] = times  # ключ переходить у кінець словника
    if len(_attempts) > MAX_TRACKED_KEYS:
        # Спершу забуваємо записи, строк яких минув; найдавніші активні —
        # лише якщо цього не досить (захист від переповнення пам'яті)
        for old in [k for k, ts in _attempts.items() if ts[-1] <= now - LOCKOUT_SECONDS]:
            del _attempts[old]
        for old in list(_attempts)[: max(0, len(_attempts) - MAX_TRACKED_KEYS)]:
            del _attempts[old]


def begin_attempt(username, ip):
    """Атомарно перевіряє ліміти і зараховує спробу. False — вхід заблоковано."""
    now = time.time()
    user_key = ("user", username, ip)
    with _attempts_lock:
        user_attempts = _recent(user_key, now)
        if (len(user_attempts) >= MAX_FAILED_LOGINS
                or len(_recent(("ip", ip), now)) >= MAX_FAILED_PER_IP):
            return False
        _store(user_key, user_attempts + [now], now)
        return True


def register_failure(ip):
    """Зараховує невдалу спробу для IP (ліміт на перебір багатьох логінів)."""
    now = time.time()
    with _attempts_lock:
        _store(("ip", ip), _recent(("ip", ip), now) + [now], now)


def reset_failures(username, ip):
    with _attempts_lock:
        _attempts.pop(("user", username, ip), None)


def log_username(username, known):
    # Невідомий «логін» може бути паролем, введеним не в те поле, тож у лог його не пишемо
    return username if known else "<невідомий>"


def user_exists(username):
    with db() as conn:
        return conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone() is not None


# ---------- Метрики для Prometheus ----------

LOGIN_ATTEMPTS = Counter("auth_login_attempts", "Спроби входу", ["result"])
VERIFY_REQUESTS = Counter("auth_verify_requests", "Перевірки доступу від шлюзу", ["result"])
ACTIVE_SESSIONS = Gauge("auth_active_sessions", "Кількість активних сесій")
ACTIVE_SESSIONS.set_function(count_active_sessions)
# Лічильники стартують з нуля, щоб increase() у Prometheus враховував і першу подію
for result in ("success", "failure", "blocked"):
    LOGIN_ATTEMPTS.labels(result)
for result in ("allowed", "denied"):
    VERIFY_REQUESTS.labels(result)


# ---------- HTTP ----------

app = Flask(__name__)

LOGIN_PAGE = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Вхід — Моніторинг СУБД</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center;
           background: #111217; color: #e6e6e6; font-family: system-ui, sans-serif; }
    form { width: min(340px, 90vw); padding: 32px; border-radius: 10px;
           background: #1c1d24; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
    h1 { margin: 0 0 4px; font-size: 22px; }
    p { margin: 0 0 24px; color: #9a9aa5; font-size: 14px; }
    label { display: block; margin: 14px 0 6px; font-size: 14px; }
    input { box-sizing: border-box; width: 100%; padding: 10px; border-radius: 6px;
            border: 1px solid #34353f; background: #111217; color: inherit; font-size: 15px; }
    button { width: 100%; margin-top: 22px; padding: 11px; border: 0; border-radius: 6px;
             background: #3d71d9; color: #fff; font-size: 15px; cursor: pointer; }
    .error { margin-top: 16px; padding: 10px; border-radius: 6px;
             background: #4a1d22; color: #ffb3ba; font-size: 14px; }
  </style>
</head>
<body>
  <form method="post" action="/auth/login">
    <h1>Моніторинг СУБД</h1>
    <p>Доступ лише для авторизованих користувачів</p>
    <input type="hidden" name="next" value="{{ next }}">
    <label for="username">Логін</label>
    <input id="username" name="username" autocomplete="username" required autofocus>
    <label for="password">Пароль</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Увійти</button>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
  </form>
</body>
</html>"""


def safe_next(url):
    # Дозволяємо перенаправлення лише на внутрішні шляхи (захист від open redirect)
    return url if url and url.startswith("/") and not url.startswith("//") else "/"


def client_ip():
    return request.headers.get("X-Real-IP", request.remote_addr)


@app.get("/auth/login")
def login_form():
    next_url = safe_next(request.args.get("next"))
    if current_user():
        return redirect(next_url)
    return render_template_string(LOGIN_PAGE, error=None, next=next_url)


@app.post("/auth/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    next_url = safe_next(request.form.get("next"))
    ip = client_ip()

    if not begin_attempt(username, ip):
        LOGIN_ATTEMPTS.labels("blocked").inc()
        log.warning("Вхід тимчасово заблоковано після невдалих спроб",
                    extra={"fields": {"username": log_username(username, user_exists(username)),
                                      "ip": ip}})
        page = render_template_string(
            LOGIN_PAGE, next=next_url,
            error=f"Забагато невдалих спроб. Спробуйте через {LOCKOUT_SECONDS // 60} хв")
        return page, 429

    with db() as conn:
        user = conn.execute("SELECT id, password_hash FROM users WHERE username = ?",
                            (username,)).fetchone()
        password_ok = check_password_hash(
            user["password_hash"] if user else DUMMY_PASSWORD_HASH, password)
        if user is None or not password_ok:
            register_failure(ip)
            LOGIN_ATTEMPTS.labels("failure").inc()
            log.warning("Невдала спроба входу",
                        extra={"fields": {"username": log_username(username, user is not None),
                                          "ip": ip}})
            page = render_template_string(LOGIN_PAGE, error="Невірний логін або пароль", next=next_url)
            return page, 401

        token = secrets.token_urlsafe(32)
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
        conn.execute("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                     (hash_token(token), user["id"], time.time() + SESSION_TTL))

    reset_failures(username, ip)
    LOGIN_ATTEMPTS.labels("success").inc()
    log.info("Успішний вхід", extra={"fields": {"username": username, "ip": ip}})
    response = redirect(next_url)
    response.set_cookie(COOKIE_NAME, token, max_age=SESSION_TTL, httponly=True, samesite="Lax")
    return response


@app.get("/auth/verify")
def verify():
    """Викликається шлюзом nginx (auth_request) перед кожним запитом до системи."""
    user = current_user()
    if user is None:
        VERIFY_REQUESTS.labels("denied").inc()
        log.info("Доступ без авторизації відхилено",
                 extra={"fields": {"uri": request.headers.get("X-Original-URI"), "ip": client_ip()}})
        return "", 401
    VERIFY_REQUESTS.labels("allowed").inc()
    return "", 200, {"X-Auth-User": user["username"], "X-Auth-Role": user["role"]}


@app.get("/auth/logout")
def logout():
    user = current_user()
    token = request.cookies.get(COOKIE_NAME)
    if token:
        with db() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
    if user:
        log.info("Вихід із системи", extra={"fields": {"username": user["username"]}})
    response = redirect("/auth/login")
    response.delete_cookie(COOKIE_NAME)
    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


init_db()


# ---------- Керування користувачами з командного рядка ----------

def cli():
    parser = argparse.ArgumentParser(description="Керування користувачами сервера авторизації")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add-user", help="додати користувача (або змінити пароль/роль)")
    add.add_argument("username")
    add.add_argument("password")
    add.add_argument("role", nargs="?", choices=ROLES,
                     help="новому користувачу — Viewer за замовчуванням; існуючому — без змін")
    delete = sub.add_parser("delete-user", help="видалити користувача")
    delete.add_argument("username")
    sub.add_parser("list-users", help="список користувачів")
    args = parser.parse_args()

    if args.command == "add-user":
        problem = check_credentials(args.username, args.password)
        if problem:
            parser.error(problem)

    with db() as conn:
        if args.command == "add-user":
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(username) DO UPDATE SET "
                "password_hash = excluded.password_hash, role = COALESCE(?, role)",
                (args.username, generate_password_hash(args.password),
                 args.role or "Viewer", time.time(), args.role),
            )
            # Після зміни пароля всі старі сесії користувача перестають діяти
            revoked = conn.execute(
                "DELETE FROM sessions WHERE user_id = (SELECT id FROM users WHERE username = ?)",
                (args.username,),
            ).rowcount
            role = conn.execute("SELECT role FROM users WHERE username = ?",
                                (args.username,)).fetchone()[0]
            print(f"Користувача {args.username} ({role}) збережено"
                  + (f", завершено сесій: {revoked}" if revoked else ""))
        elif args.command == "delete-user":
            deleted = conn.execute("DELETE FROM users WHERE username = ?", (args.username,)).rowcount
            print(f"Видалено: {args.username}" if deleted else f"Користувача {args.username} не знайдено")
        else:
            for row in conn.execute("SELECT username, role, datetime(created_at, 'unixepoch') "
                                    "FROM users ORDER BY id"):
                print(f"{row[0]:<20} {row[1]:<8} {row[2]}")


if __name__ == "__main__":
    cli()
