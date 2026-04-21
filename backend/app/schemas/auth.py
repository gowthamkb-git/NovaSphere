from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AuthUser(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser
