from fastapi import FastAPI
from app.config import PROJECT_NAME

app = FastAPI(title=PROJECT_NAME)

@app.get("/")
def home():
  return {"message": "HackMate is alive"}

@app.get('/health')
def health():
  return {"status" : "Ok",
          "Project": "HackMate"}
@app.get('/about')
def about():
  return {"project": "HackMate",
          "version": "0.1.0",
          "description": "Hackathon team formation platform"
          }
