from fastapi import FastAPI
from typing import Optional
from dotenv import load_dotenv
from project import router as project_router
from auth.auth_project import router as auth_router

load_dotenv()

app = FastAPI()

import create_table
import auth.auth_create_table

@app.get("/health-check")
def check_health():
    return { "status":"ok" }

@app.get("/get/{name}")
def check_health(name: str, age: Optional[int] = None ):
    return { "status":"ok", "message":  f"My name is {name} and I am {age} years old" if age else f"My name is {name}" }

app.include_router(project_router)
app.include_router(auth_router)













