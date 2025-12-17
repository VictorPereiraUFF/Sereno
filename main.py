# main.py
import os
import logging
import base64
from typing import Optional, List
from datetime import datetime, timedelta

# FastAPI & Pydantic
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Body, Request # type: ignore
from fastapi.responses import JSONResponse, StreamingResponse # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore

# Banco de Dados & Segurança
from sqlmodel import SQLModel, Field, create_engine, Session, select # type: ignore
from passlib.hash import bcrypt # type: ignore
from jose import jwt, JWTError # type: ignore

# IA
from openai import OpenAI # type: ignore

# ---------- CONFIGURAÇÕES ----------
SECRET_KEY = os.getenv("SERENO_SECRET", "super-secret-key-change-me")
ALGORITHM = "HS256"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sereno.db")

# Configuração OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Banco de Dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Sereno Backend", version="0.2.0")

# CORS (Permite que o frontend acesse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELOS DE DADOS (DB) ----------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Script(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    message: str
    
# Cria tabelas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

create_db_and_tables()

# ---------- LÓGICA DE IA (MULTIMODAL) ----------
class ChatRequest(BaseModel):
    texto: str
    imagem: Optional[str] = None  # Base64 string

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None) -> str:
    """Processa texto e imagem usando GPT-4o-mini."""
    if not client.api_key:
        return "Erro: Chave de API não configurada no servidor."

    system_prompt = (
        "Você é o Sereno AI, focado em acessibilidade e regulação sensorial. "
        "1. Se receber imagem, analise APENAS gatilhos sensoriais (luzes, padrões, bagunça). "
        "2. Se receber texto/áudio, sugira calma e estratégias sociais. "
        "3. NÃO dê diagnósticos médicos. Seja breve."
    )

    user_content = []
    text_content = texto if texto else "Analise esta imagem quanto a gatilhos sensoriais."
    user_content.append({"type": "text", "text": text_content})

    if imagem_b64:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{imagem_b64}"}
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return "Tive uma dificuldade técnica para processar isso agora."

# ---------- ROTAS ----------

@app.get("/")
def home():
    return {"status": "Sereno Backend Online", "db": "Active"}

# Rota de IA (Pública para protótipo, mas pronta para receber Auth)
@app.post("/api/ia")
def chat_endpoint(payload: ChatRequest):
    resposta = gerar_resposta_gpt(payload.texto, payload.imagem)
    return {"resposta": resposta}

# Rota de Scripts (Exemplo de persistência)
@app.get("/scripts")
def list_scripts(session: Session = Depends(get_session)):
    # Retorna scripts do DB ou padrões se vazio
    scripts = session.exec(select(Script)).all()
    if not scripts:
        return [
            {"message": "Preciso de um minuto."},
            {"message": "O barulho está alto."}
        ]
    return scripts

@app.post("/scripts")
def add_script(message: str = Body(..., embed=True), session: Session = Depends(get_session)):
    # Salva no banco de dados SQLite
    novo_script = Script(message=message)
    session.add(novo_script)
    session.commit()
    session.refresh(novo_script)
    return novo_script

# Rota de Logs de Sensores (Simulação de IoT)
@app.post("/events")
def log_event(payload: dict = Body(...)):
    # Aqui você salvaria no banco 'Event' se quisesse histórico
    print(f"Evento recebido: {payload}")
    return {"status": "logged"}

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)