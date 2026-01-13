# models.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field # type: ignore
from pydantic import BaseModel # type: ignore

# --- Modelos do Banco de Dados ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Script(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    message: str

# --- Modelos de Requisição (API) ---
class ChatRequest(BaseModel):
    texto: str
    imagem: Optional[str] = None