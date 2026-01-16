# main.py
import os
from fastapi import FastAPI, Depends, Body # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlmodel import SQLModel, create_engine, Session, select # type: ignore

# --- IMPORTAÇÕES LOCAIS ---
# Certifique-se de que models.py está na mesma pasta
from models import User, Script, ChatRequest
from services import gerar_resposta_gpt, suavizar_texto_gpt

# ---------- CONFIGURAÇÕES ----------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sereno.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Sereno Backend", version="0.3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- BANCO DE DADOS ----------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

create_db_and_tables()

# ---------- ROTAS ----------

@app.get("/")
def home():
    return {"status": "Sereno Backend Online", "db": "Active"}

# Rota de IA (Chat Geral)
@app.post("/api/ia")
def chat_endpoint(payload: ChatRequest):
    resposta = gerar_resposta_gpt(payload.texto, payload.imagem)
    return {"resposta": resposta}

# Rota de IA (Tradutor de Polidez) - NOVO
@app.post("/api/suavizar")
def endpoint_suavizar(payload: ChatRequest):
    # Reutilizamos o modelo ChatRequest pois ele já tem o campo 'texto'
    resultado = suavizar_texto_gpt(payload.texto)
    return {"revisado": resultado}

# Rotas de Scripts
@app.get("/scripts")
def list_scripts(session: Session = Depends(get_session)):
    scripts = session.exec(select(Script)).all()
    if not scripts:
        return []
    return scripts

@app.post("/scripts")
def add_script(message: str = Body(..., embed=True), session: Session = Depends(get_session)):
    novo_script = Script(message=message)
    session.add(novo_script)
    session.commit()
    session.refresh(novo_script)
    return novo_script

@app.post("/events")
def log_event(payload: dict = Body(...)):
    print(f"Evento recebido: {payload}")
    return {"status": "logged"}

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)