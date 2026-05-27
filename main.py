import serial # type: ignore
import time
from fastapi import FastAPI, Depends, Body # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlmodel import Session, select # type: ignore
from security import proteger_dado, revelar_dado # type: ignore

# --- IMPORTAÇÕES LOCAIS ---
from database import create_db_and_tables, get_session
from models import User, Script, SocialBattery, ChatRequest, BatteryRequest
from services import gerar_resposta_gpt, prever_sobrecarga_mmq, suavizar_texto_gpt, calcular_bateria_social_gpt

# ---------- CONFIGURAÇÕES DO APP ----------
app = FastAPI(title="Sereno Backend", version="0.6.0")

# CORS (Permite que o HTML converse com o Python de forma segura)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas do banco de dados ao iniciar
create_db_and_tables()

# ---------- CONFIGURAÇÃO DO HARDWARE (ARDUINO) ----------
# Tenta conectar com o Arduino pela porta USB
try:
    # IMPORTANTE: Mude 'COM3' para a porta que aparecer na sua IDE do Arduino (ex: COM4, COM5)
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2) # Pausa rápida para o Arduino sincronizar
    arduino_conectado = True
    print("✅ Arduino conectado com sucesso!")
except Exception as e:
    print(f"⚠️ Aviso: Arduino não encontrado. O sistema funcionará apenas de forma virtual. Detalhe: {e}")
    arduino_conectado = False

# ---------- VARIÁVEL GLOBAL (MEMÓRIA PREDITIVA) ----------
historico_usuario = []


# ---------- ROTAS DA API ----------

@app.get("/")
def home():
    return {"status": "Sereno Backend Online", "db": "Active", "arduino": arduino_conectado}

# Rota de IA (Chat Geral)
@app.post("/api/ia")
def chat_endpoint(payload: ChatRequest):
    # Passamos o payload.estilo como terceiro argumento para o serviço
    resposta = gerar_resposta_gpt(payload.texto, payload.imagem, payload.estilo)
    return {"resposta": resposta}

# Rota de IA (Tradutor de Polidez)
@app.post("/api/suavizar")
def endpoint_suavizar(payload: ChatRequest):
    resultado = suavizar_texto_gpt(payload.texto)
    return {"revisado": resultado}

# Rota de Cálculo Inteligente de Bateria + Previsão de Sobrecarga (MMQ)
@app.post("/api/bateria/calcular")
def calcular_energia_endpoint(payload: ChatRequest):
    global historico_usuario # Usa a lista global para lembrar das últimas pontuações
    
    nivel_calculado = calcular_bateria_social_gpt(payload.texto)
    
    # Adiciona ao histórico e mantém apenas os últimos 5 registros
    historico_usuario.append(nivel_calculado)
    if len(historico_usuario) > 5:
        historico_usuario.pop(0)
    
    # Calcula a previsão de queda usando a matemática de Mínimos Quadrados
    analise = prever_sobrecarga_mmq(historico_usuario)
    
    return {
        "nivel_estimado": nivel_calculado,
        "previsao": analise
    }

# Rota de Bateria Social Manual
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
    statement = select(SocialBattery).order_by(SocialBattery.timestamp.desc()).limit(10)
    results = session.exec(statement).all()
    return results

# Rotas de Scripts Sociais
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


# ---------- ROTA DO HARDWARE (NOVO) ----------
@app.post("/api/motor")
def controlar_motor(dados: dict = Body(...)):
    estado = dados.get("estado")
    
    if arduino_conectado:
        if estado == '1':
            arduino.write(b'1') # Envia comando de LIGAR para o Arduino
            return {"mensagem": "Motor ativado! Regulação tátil iniciada."}
        else:
            arduino.write(b'0') # Envia comando de DESLIGAR
            return {"mensagem": "Motor desativado!"}
    
    return {"erro": "Hardware físico não conectado. Conecte o Arduino no cabo USB."}


# ---------- INICIALIZAÇÃO ----------
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

from pydantic import BaseModel

# 1. Cria o modelo de dados para receber o plano
class Planejamento(BaseModel):
    bateria_atual: int
    atividades: str

# 2. Cria a nova rota de previsão
@app.post("/api/energia/prever")
def prever_energia(plan: Planejamento):
    # Prompt de sistema que transforma a IA em uma "Contadora de Energia e Recuperação"
    prompt = f"""
    Você é o Sereno, um assistente especialista em regulação sensorial e carga social.
    O usuário possui atualmente {plan.bateria_atual}% de bateria social.
    Ele planeja fazer as seguintes atividades hoje: "{plan.atividades}".
    
    Sua tarefa:
    1. Analise o impacto sensorial, cognitivo e social de CADA atividade.
    2. Atribua um "custo" em porcentagem (%) para cada uma.
    3. Subtraia os custos da bateria atual ({plan.bateria_atual}%).
    4. Veredito: O usuário conseguirá fazer tudo sem entrar em sobrecarga (bateria < 15%)? Diga o Saldo Final.
    5. Estimativa de Recuperação: Analise o tamanho do desgaste gerado por essas atividades e estime o tempo e o tipo de descanso necessários para recarregar a bateria gasta (ex: "45 minutos de isolamento acústico", "2 horas de hiperfoco", ou "Uma noite inteira de sono profundo").
    
    Formatação obrigatória: 
    - Seja amigável e direto.
    - Use bullet points para listar os custos das atividades.
    - Crie um título final chamado "⏳ Tempo de Recuperação Estimado" para destacar a sua previsão de recarga, sugerindo o uso de ferramentas do app (como o gerador de ruído marrom/ondas do mar ou respiração guiada) se a carga for alta.
    """
    
    try:
        # Reutilizamos a função já existente no seu services.py!
        resposta_texto = gerar_resposta_gpt(prompt, None)
        
        return {"analise": resposta_texto}
    except Exception as e:
        print(f"Erro real detectado na IA: {e}")
        return {"analise": "Erro ao processar o planejamento com a IA."}