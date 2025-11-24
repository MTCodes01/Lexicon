from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    is_owner: bool = False

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None