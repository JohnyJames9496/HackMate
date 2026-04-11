from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
  return {"message": "HackMate is alive"}

@app.get('/health')
def health():
  return {"status" : "Ok",
          "Project": "HackMate"}