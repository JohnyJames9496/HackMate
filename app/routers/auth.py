from fastapi import APIRouter,Depends
from app.schemas.user import TokenResponse,UserSignup,UserLogin
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.auth_service import signup_user,login_user



router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post('/signup',response_model = TokenResponse)
def signup(data:UserSignup,db:Session = Depends(get_db)):
  return signup_user(data,db)

@router.post("/login",response_model=TokenResponse)
def login(data:UserLogin,db:Session = Depends(get_db)):
  return login_user(data,db)
