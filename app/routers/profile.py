from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas.profile import FullUserResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileResponse,ProfileUpdate




router = APIRouter(prefix="/profile",tags=["Profile"])

@router.get("/",response_model=FullUserResponse)
def get_profile(
  current_user : User = Depends(get_current_user),
  db : Session = Depends(get_db)
):
  profile = db.query(Profile).filter(Profile.user_id==current_user.id).first ()
  if not profile:
    raise HTTPException(
      status_code= status.HTTP_404_NOT_FOUND,
      detail = "Profile not found"
    )
  return{
    "id":current_user.id,
    "email":current_user.email,
    "username":current_user.username,
    "is_active":current_user.is_active,
    "profile":profile
  }

@router.put('/',response_model=ProfileResponse)
def update_profile(
  data:ProfileUpdate,
  current_user:User = Depends(get_current_user),
  db : Session = Depends(get_db)
):
  profile = db.query(Profile).filter(Profile.user_id==current_user.id).first()
  if not profile:
    raise HTTPException(
      status_code= status.HTTP_404_NOT_FOUND,
      detail="Profile not found"
    )
  update_data = data.model_dump(exclude_unset=True)
  for field,value in update_data.items():
    setattr(profile,field,value)
  
  profile.profile_completeness = calculate_completeness(profile)

  db.commit()
  db.refresh(profile)

  return profile

def calculate_completeness(profile:Profile)->float:
  fields = [
    profile.bio,
    profile.skills,
    profile.github_url,
    profile.linkedin_url
  ]
  filled = sum( 1 for f in fields if f )
  return round(filled/len(fields),2)
