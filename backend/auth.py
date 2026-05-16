import os, time, sqlite3, secrets, urllib.request, urllib.error, json
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.environ.get("JWT_SECRET", "change-me-in-production-please")
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days
RESET_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
APP_URL        = os.environ.get("APP_URL", "https://marathon-predictor.netlify.app")

bearer_scheme = HTTPBearer(auto_error=False)

DB_PATH = os.environ.get("DB_PATH", "/data/marathon.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_users_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at INTEGER NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        email = payload["email"]
        return {"id": user_id, "email": email}
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def create_reset_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_db()
    try:
        # Invalidate any existing unused tokens for this user
        conn.execute(
            "UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND used = 0",
            (user_id,)
        )
        conn.execute(
            "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, int(time.time()) + RESET_TOKEN_EXPIRE_SECONDS)
        )
        conn.commit()
    finally:
        conn.close()
    return token

def send_reset_email(to_email: str, token: str):
    reset_url = f"{APP_URL}?token={token}"
    payload = {
        "from": "Marathon Predictor <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Reset your Marathon Predictor password",
        "text": f"""Hi,

You requested a password reset for your Marathon Time Predictor account.

Click the link below to set a new password (valid for 1 hour):

{reset_url}

If you didn't request this, you can safely ignore this email.

— Marathon Time Predictor
""",
        "html": f"""
<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
  <h2 style="color:#f97316">🏃 Marathon Time Predictor</h2>
  <p>You requested a password reset.</p>
  <p>Click the button below to set a new password. This link is valid for <strong>1 hour</strong>.</p>
  <a href="{reset_url}"
     style="display:inline-block;margin:16px 0;padding:12px 24px;background:#f97316;color:#fff;border-radius:8px;text-decoration:none;font-weight:bold">
    Reset Password
  </a>
  <p style="color:#888;font-size:13px">If you didn't request this, you can safely ignore this email.</p>
</div>
"""
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def validate_reset_token(token: str):
    """Returns user row if token is valid, raises HTTPException otherwise."""
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT prt.user_id, prt.expires_at, prt.used, u.email
               FROM password_reset_tokens prt
               JOIN users u ON u.id = prt.user_id
               WHERE prt.token = ?""",
            (token,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Invalid reset link")
        if row["used"]:
            raise HTTPException(status_code=400, detail="Reset link has already been used")
        if int(time.time()) > row["expires_at"]:
            raise HTTPException(status_code=400, detail="Reset link has expired")
        return dict(row)
    finally:
        conn.close()

def apply_reset_token(token: str, new_password: str):
    """Validates token, updates password, marks token used."""
    user = validate_reset_token(token)
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hash_password(new_password), user["user_id"])
        )
        conn.execute(
            "UPDATE password_reset_tokens SET used = 1 WHERE token = ?",
            (token,)
        )
        conn.commit()
        return user
    finally:
        conn.close()
