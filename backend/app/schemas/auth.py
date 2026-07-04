from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str | None = None
