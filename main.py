from fastapi import FastAPI
from app.config import PROJECT_NAME
from app.models import User,Profile

app = FastAPI(title=PROJECT_NAME)

@app.get("/")
def home():
  return {"message": f"{PROJECT_NAME} is alive"}

@app.get('/health')
def health():
  return {"status" : "Ok",
          "Project": PROJECT_NAME}
@app.get('/about')
def about():
  return {"project": PROJECT_NAME,
          "version": "0.3.0",
          "description": "Hackathon team formation platform"
          }
