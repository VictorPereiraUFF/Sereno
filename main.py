# main.py
from fastapi import FastAPI, Depends, Body # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlmodel import Session, select # type: ignore

# --- IMPORTAÇÕES LOCAIS ---
# 1. Importamos o gerenciamento do banco
from database import create_db_and_tables, get_session
# 2. Importamos os modelos (tabelas e dados)
from models import User, Script, SocialBattery, ChatRequest, BatteryRequest
# 3. Importamos as funções de IA
from services import gerar_resposta_gpt, suavizar_texto_gpt

# ---------- CONFIGURAÇÕES DO APP ----------
app = FastAPI(title="Sereno Backend", version="0.5.0")

# CORS (Permite que o HTML converse com o Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas ao iniciar usando a função importada
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

# Rota de IA (Tradutor de Polidez)
@app.post("/api/suavizar")
def endpoint_suavizar(payload: ChatRequest):
    resultado = suavizar_texto_gpt(payload.texto)
    return {"revisado": resultado}

# Rota de Bateria Social
@app.post("/api/battery")
def log_battery(payload: BatteryRequest, session: Session = Depends(get_session)):
    novo_registro = SocialBattery(level=payload.level)
    session.add(novo_registro)
    session.commit()
    
    sugestao = ""
    if payload.level <= 20:
        sugestao = "Bateria crítica. Ativando recomendações de descanso."
    elif payload.level <= 50:
        sugestao = "Energia moderada. Considere pausas."
    else:
        sugestao = "Energia estável."

    return {"status": "saved", "message": sugestao}

# Rota para pegar histórico da bateria
@app.get("/api/battery/history")
def get_battery_history(session: Session = Depends(get_session)):
    # Requer importação do select no topo
    statement = select(SocialBattery).order_by(SocialBattery.timestamp.desc()).limit(10)
    results = session.exec(statement).all()
    return results

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

# ---------- INICIALIZAÇÃO ----------
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)