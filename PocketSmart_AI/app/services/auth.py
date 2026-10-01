import hashlib
import hmac
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models.db_models import User


ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 24


def hash_password(
    password: str,
) -> str:

    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        310_000,
    )

    return (
        "pbkdf2_sha256$310000$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:

    try:

        scheme, rounds, salt_hex, digest_hex = (
            encoded.split("$")
        )

        if scheme != "pbkdf2_sha256":
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            int(rounds),
        )

        return hmac.compare_digest(
            digest.hex(),
            digest_hex,
        )

    except (
        ValueError,
        TypeError,
    ):

        return False


def create_access_token(
    user: User,
) -> str:

    settings = get_settings()

    now = datetime.now(
        timezone.utc
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "iat": now,
        "exp": (
            now
            + timedelta(
                hours=TOKEN_EXPIRE_HOURS
            )
        ),
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def get_token_from_request(
    request: Request,
) -> str | None:

    authorization = request.headers.get(
        "Authorization",
        "",
    )

    if authorization.lower().startswith(
        "bearer "
    ):

        return authorization[7:].strip()

    return request.cookies.get(
        "access_token"
    )


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    token = get_token_from_request(
        request
    )

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:

        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],
        )

        user_id = int(
            payload["sub"]
        )

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = db.get(
        User,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
