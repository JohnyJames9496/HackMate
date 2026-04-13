from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
  users = db.query(User).all()
  print("Database connection successful. Users:")
  print(f"Total users: {len(users)}")
except Exception as e:
  print("Database connection failed:", e)
finally:
  db.close()