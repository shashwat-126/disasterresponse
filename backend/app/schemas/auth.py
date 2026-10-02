from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Self-service signup for citizens. Staff/admin accounts are still provisioned by an
    admin (via seed scripts or a future admin-only user-management endpoint) so that only
    verified personnel end up scoped to a department.
    """

    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
