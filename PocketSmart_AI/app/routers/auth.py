from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.db_models import User
from ..models.schemas import (
    LoginRequest,
    RegisterRequest,
    UserOut,
)
from ..services.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    tags=["authentication"]
)


def set_cookie(
    response: Response,
    token: str,
):

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400,
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):

    email = payload.email.lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail=(
                "An account with this email "
                "already exists"
            ),
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(
            payload.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=UserOut,
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    user = db.scalar(
        select(User).where(
            User.email == payload.email.lower()
        )
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user)

    set_cookie(
        response,
        access_token,
    )

    return user


@router.post("/token")
def token(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    user = db.scalar(
        select(User).where(
            User.email == payload.email.lower()
        )
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user)

    set_cookie(
        response,
        access_token,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out"
    }


@router.get(
    "/session-info",
    response_model=UserOut,
)
def session_info(
    user: User = Depends(get_current_user),
):

    return user


@router.get("/session-data")
def session_data(
    request: Request,
    user: User = Depends(get_current_user),
):

    return {
        "logged_in": True,
        "user_id": user.id,
        "email": user.email,
        "path": request.url.path,
    }
