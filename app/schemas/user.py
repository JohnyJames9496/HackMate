from pydantic import BaseModel,EmailStr,field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserSignup(BaseModel):
  email: EmailStr
  username:str
  password:str

  @field_validator('username')
  @classmethod
  def username_valid(cls,v):
    if len(v) < 3:
      raise ValueError('Username must be at least 3 characters long')
    if len(v) > 100:
      raise ValueError('Username must be less than 100 characters long')
    if not v.isalnum():
      raise ValueError('Username must be alphanumeric')
    return v.lower()


  @field_validator('password')
  @classmethod
  def password_valid(cls,v):
    if len(v) < 8:
      raise ValueError('Password must be at least 8 characters long')
    return v
  
class UserLogin(BaseModel):
  email: EmailStr
  password:str

class UserResponse(BaseModel):
  id : UUID
  email:str
  username:str
  is_active:bool
  created_at:datetime

  model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
  access_token:str
  token_type:str = "bearer"
  user:UserResponse
