from pydantic import BaseModel, EmailStr
from enum import Enum

# Role validation with Enum (Allows only specific values)
class RoleValues(str, Enum):
    user = "user"
    admin = "admin"

# Schema for user creation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleValues 

# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str