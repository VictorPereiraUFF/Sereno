# models.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field # type: ignore
from pydantic import BaseModel # type: ignore

# Tabela de Usuários (Base)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Tabela de Scripts
class Script(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    message: str

# Tabela de Bateria Social (NOVO)
class SocialBattery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: int # 0 a 100
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- Schemas de Comunicação (Pydantic) ---
# Usados para receber dados do Frontend (JSON)

class ChatRequest(BaseModel):
    texto: str
    imagem: Optional[str] = None

class BatteryRequest(BaseModel):
    level: int

class ChatRequest(BaseModel):
    texto: str
    imagem: Optional[str] = None
    estilo: Optional[str] = None
    bateria_atual: Optional[int] = None  # Nível da bateria social no momento do envio (0-100)

class TriggerEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str # Ex: 'luz_alta', 'som_alto', 'queda_bateria'
    valor: int # Nível do gatilho (ex: 85% de brilho)
    timestamp: datetime = Field(default_factory=datetime.utcnow)