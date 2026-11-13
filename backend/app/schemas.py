from pydantic import BaseModel, Field
# EmailStr requires email-validator; use constrained string to keep dependencies lean.
from typing import Any

class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=10, max_length=128)
    organization: str = Field(default="personal", min_length=2, max_length=120)

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChatIn(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=12)

class ToolProposalIn(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = {}

class ApprovalDecisionIn(BaseModel):
    decision: str
    reason: str = ""

class MemoryIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
