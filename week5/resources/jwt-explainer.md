# JWT — Explainer

---

## What Is a JWT?

A **JSON Web Token** is a compact, signed string that proves a user is who they claim to be — without the server needing to store any session data.

A JWT has 3 parts, separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyaWRlcl8xMjMiLCJyb2xlIjoicmlkZXIiLCJleHAiOjE3MTk0MDAwMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
└──────────── Header ────────────┘└────────────────── Payload ──────────────────┘└────────── Signature ──────────┘
```

---

## The 3 Parts

### 1. Header
```json
{ "alg": "HS256", "typ": "JWT" }
```
Specifies the signing algorithm.

### 2. Payload (Claims)
```json
{
  "sub": "rider_123",
  "role": "rider",
  "exp": 1719400000
}
```
- `sub` — subject (the user ID)
- `exp` — expiry time (Unix timestamp) — **always set this**
- You can add custom claims like `role` to distinguish riders from drivers

⚠️ **The payload is Base64-encoded, not encrypted.** Anyone can decode and read it. Never put passwords or sensitive data in a JWT payload.

### 3. Signature
```
HMACSHA256(base64(header) + "." + base64(payload), YOUR_SECRET_KEY)
```
This is what makes the token trustworthy. If anyone tampers with the header or payload, the signature won't match anymore, and verification fails.

---

## The Auth Flow

```
1. Rider sends username + password to POST /auth/login
                    │
                    ▼
2. Server verifies credentials against the database
                    │
                    ▼
3. Server creates a JWT containing {sub: user_id, role: "rider", exp: ...}
   and signs it with a secret key
                    │
                    ▼
4. Server returns: {"access_token": "eyJ...", "token_type": "bearer"}
                    │
                    ▼
5. Rider's app stores the token and sends it on every future request:
   Authorization: Bearer eyJ...
                    │
                    ▼
6. Server verifies the signature + checks `exp` hasn't passed
   → if valid: process the request
   → if invalid/expired: return 401 Unauthorized
```

---

## Python Implementation (FastAPI + python-jose)

```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = "your-secret-key-keep-this-safe"  # use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # {"sub": ..., "role": ..., "exp": ...}
    except JWTError:
        raise ValueError("Invalid or expired token")
```

---

## Protecting a Route in FastAPI

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return verify_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

@app.get("/rides/{ride_id}")
def get_ride(ride_id: str, current_user: dict = Depends(get_current_user)):
    # current_user = {"sub": "rider_123", "role": "rider", "exp": ...}
    ...
```

---

## Why JWTs Need an Expiry (`exp`)

Unlike server-side sessions, a JWT can't be easily "logged out" — the server doesn't track which tokens are active. A stolen JWT is valid until it expires.

**Mitigations:**
- Keep `exp` short (e.g. 15–60 minutes for access tokens)
- Use a **refresh token** (longer-lived, stored more securely) to issue new access tokens without re-entering credentials
- For true revocation, maintain a server-side blocklist of revoked token IDs (adds back some statefulness, but only for the rare revoke case)

---

## Role-Based Access in This Roadmap

Your ride-hailing API has two roles: `rider` and `driver`. Encode the role in the JWT payload and check it in your route handlers:

```python
def require_role(required_role: str):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return checker

@app.post("/drivers/location")
def update_location(current_user: dict = Depends(require_role("driver"))):
    ...
```
