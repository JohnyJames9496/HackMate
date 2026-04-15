from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import UserSignup, UserLogin
from app.utils.password import hash_password, verify_password
from app.utils.jwt_handler import create_access_token

def signup_user(data: UserSignup, db: Session):
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    new_user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)
    db.commit()

    token = create_access_token({"user_id": str(new_user.id)})

    return {"access_token": token, "token_type": "bearer", "user": new_user}


def login_user(data: UserLogin, db: Session):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    token = create_access_token({"user_id": str(user.id)})

    return {"access_token": token, "token_type": "bearer", "user": user}