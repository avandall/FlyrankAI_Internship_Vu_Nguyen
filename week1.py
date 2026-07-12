from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to my FlyrankAI!"}

@app.get("/status")
def get_status():
    return {"status": "healthy", "version": "1.0.0"}