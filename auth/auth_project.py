from database import get_db
from sqlalchemy.orm import Session
import auth.models
from fastapi import APIRouter, Depends, HTTPException, status
import os
import jwt
from datetime import datetime, timedelta, timezone
from auth.schemas import UserCreate, UserLogin
from auth.utils import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


router = APIRouter( prefix="/api/v1/auth" )
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({ "exp": expire })
    encode_jwt = jwt.encode( to_encode, JWT_SECRET, algorithm=ALGORITHM )
    return encode_jwt

@router.post("/signup")
def register_user(user:UserCreate, db:Session=Depends(get_db)):
    existing_user = db.query(auth.models.User).filter(auth.models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    #HASH PASSWORD
    hashed_pass = hash_password(user.password)

    new_user = auth.models.User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_pass,
        role = user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return { "id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role }


@router.post("/login")
def login(form_data:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
    user = db.query(auth.models.User).filter(auth.models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")
    
    token_data = { "sub": user.username, "role": user.role }
    token = create_access_token(token_data)
    return { 'access_token':token, "token_type": "bearer" }


def get_current_user(token:str=Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode( token, JWT_SECRET, algorithms=[ALGORITHM] )
        username:str = payload.get("sub")
        role:str = payload.get("role")
        if username is None or role is None:
            raise credential_exception
        
    except jwt.ExpiredSignatureError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired",
                            headers={"WWW-Authenticate": "Bearer"})
    except jwt.InvalidTokenError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token",
                            headers={"WWW-Authenticate": "Bearer"})
    
    return { "username": username, "role":role }

@router.get("/protected")
def protected_route(current_user:dict=Depends(get_current_user)):
    return { "message": f"Hello, {current_user['username']}, you accessed a protected route" }

def require_roles(allowed_roles:list[str]):
    def role_checker(current_user:dict=Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission")
        
        return current_user
    return role_checker

@router.get("/profile")
def profile(current_user:dict=Depends(require_roles([ "user", "admin" ]))):
    return { "message": f"Profile of {current_user['username']} ({current_user['role']})" }

@router.get("/user/dashboard")
def user_dashboard( current_user:dict=Depends(require_roles(["user"])) ):
    return { "message": "Welcome User" }

@router.get("/admin/dashboard")
def admin_dashboard( current_user:dict=Depends(require_roles(["admin"])) ):
    return { "message": "Welcome Admin" }