# main.py
import serial # type: ignore
import time
from datetime import datetime, timezone
from pydantic import BaseModel # type: ignore
from fastapi import FastAPI, Depends, Body # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlmodel import Session, select # type: ignore

# --- IMPORTAÇÕES LOCAIS E SERVICES ---
from database import create_db_and_tables, get_session
from models import Script, SocialBattery, ChatRequest, BatteryRequest, TriggerEvent
from services import (
    gerar_resposta_gpt, 
    suavizar_texto_gpt, 
    analisar_padroes_gatilhos,
    calcular_impacto_prompt_gpt,
    processar_interacao_bateria,
    prever_sobrecarga_mmq
)

# ---------- CONFIGURAÇÕES DO APP ----------
app = FastAPI(title="Sereno Backend", version="0.7.0")

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
try:
    # Mude 'COM3' para a porta do seu Arduino (ex: COM4, COM5)
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
    arduino_conectado = True
    print("✅ Arduino conectado com sucesso!")
except Exception as e:
    print(f"⚠️ Aviso: Arduino não encontrado. O sistema funcionará apenas de forma virtual. Detalhe: {e}")
    arduino_conectado = False

# ---------- ESTADO GLOBAL TEMPORAL (BATERIA E MMQ) ----------
bateria_atual_global = 100.0
timestamp_ultimo_prompt_global = datetime.now(timezone.utc)
timestamp_inicio_sessao = datetime.now(timezone.utc)
historico_mmq_temporal = []  # Armazena tuplas: (minutos_decorridos, bateria)


# ---------- MODELOS DE DADOS ADICIONAIS ----------
class Planejamento(BaseModel):
    bateria_atual: int
    atividades: str


# ---------- ROTAS DA API ----------

@app.get("/")
def home():
    return {"status": "Sereno Backend Online", "db": "Active", "arduino": arduino_conectado}

# Rota de IA (Chat Geral)
@app.post("/api/ia")
def chat_endpoint(payload: ChatRequest):
    resposta = gerar_resposta_gpt(payload.texto, payload.imagem, payload.estilo, payload.bateria_atual)
    return {"resposta": resposta}

# Rota de IA (Tradutor de Polidez)
@app.post("/api/suavizar")
def endpoint_suavizar(payload: ChatRequest):
    resultado = suavizar_texto_gpt(payload.texto)
    return {"revisado": resultado}

# Rota de Cálculo Inteligente de Bateria + Previsão de Sobrecarga (MMQ Temporal)
@app.post("/api/bateria/calcular")
def calcular_energia_endpoint(payload: ChatRequest):
    global bateria_atual_global, timestamp_ultimo_prompt_global, timestamp_inicio_sessao, historico_mmq_temporal
    
    # 1. Avalia o desgaste/ganho gerado pelo texto atual (-50 a +50)
    impacto = calcular_impacto_prompt_gpt(payload.texto)
    
    # 2. Processa a recuperação pelo tempo de descanso + o novo impacto
    resultado_bateria = processar_interacao_bateria(
        bateria_anterior=bateria_atual_global,
        timestamp_ultimo_prompt=timestamp_ultimo_prompt_global,
        impacto_prompt=impacto
    )
    
    # Atualiza o estado em memória
    bateria_atual_global = resultado_bateria["bateria_final"]
    timestamp_ultimo_prompt_global = resultado_bateria["timestamp"]
    
    # 3. Registra os minutos decorridos reais desde o início da sessão e o nível atual
    minutos_decorridos = (timestamp_ultimo_prompt_global - timestamp_inicio_sessao).total_seconds() / 60.0
    historico_mmq_temporal.append((minutos_decorridos, bateria_atual_global))
    
    # Mantém os últimos 5 registros de janela deslizante
    if len(historico_mmq_temporal) > 5:
        historico_mmq_temporal.pop(0)
    
    # 4. Executa a previsão MMQ com base na série temporal
    analise_mmq = prever_sobrecarga_mmq(historico_mmq_temporal)
    
    return {
        "nivel_estimado": int(bateria_atual_global),
        "previsao": analise_mmq
    }

# Rota de Previsão de Energia para Planejamento de Atividades
@app.post("/api/energia/prever")
def prever_energia(plan: Planejamento):
    prompt = f"""
    Você é o Sereno, um assistente especialista em regulação sensorial e carga social.
    O usuário possui atualmente {plan.bateria_atual}% de bateria social.
    Ele planeja fazer as seguintes atividades hoje: "{plan.atividades}".
    
    Sua tarefa:
    1. Analise o impacto sensorial, cognitivo e social de CADA atividade.
    2. Atribua um "custo" em porcentagem (%) para cada uma.
    3. Subtraia os custos da bateria atual ({plan.bateria_atual}%).
    4. Veredito: O usuário conseguirá fazer tudo sem entrar em sobrecarga (bateria < 15%)? Diga o Saldo Final.
    5. Estimativa de Recuperação: Analise o tamanho do desgaste gerado por essas atividades e estime o tempo e o tipo de descanso necessários para recarregar a bateria gasta.
    
    Formatação obrigatória: 
    - Seja amigável e direto.
    - Use bullet points para listar os custos das atividades.
    - Crie um título final chamado "⏳ Tempo de Recuperação Estimado" para destacar a sua previsão de recarga.
    """
    
    try:
        resposta_texto = gerar_resposta_gpt(prompt, None)
        return {"analise": resposta_texto}
    except Exception as e:
        print(f"Erro no planejamento com IA: {e}")
        return {"analise": "Erro ao processar o planejamento com a IA."}

# Rota de Bateria Social Manual
@app.post("/api/battery")
def log_battery(payload: BatteryRequest, session: Session = Depends(get_session)):
    novo_registro = SocialBattery(level=payload.level)
    session.add(novo_registro)
    session.commit()
    
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
    return session.exec(statement).all()

# Rotas de Scripts Sociais
@app.get("/scripts")
def list_scripts(session: Session = Depends(get_session)):
    scripts = session.exec(select(Script)).all()
    return scripts if scripts else []

@app.post("/scripts")
def add_script(message: str = Body(..., embed=True), session: Session = Depends(get_session)):
    novo_script = Script(message=message)
    session.add(novo_script)
    session.commit()
    session.refresh(novo_script)
    return novo_script

@app.post("/events")
def log_event(payload: dict = Body(...), session: Session = Depends(get_session)):
    tipo = payload.get("type", "desconhecido")
    valor = payload.get("value", 0)
    
    novo_evento = TriggerEvent(tipo=tipo, valor=int(valor))
    session.add(novo_evento)
    session.commit()
    return {"status": "salvo no diario"}

# Retorna os últimos eventos para o HTML
@app.get("/api/triggers")
def get_triggers(session: Session = Depends(get_session)):
    statement = select(TriggerEvent).order_by(TriggerEvent.timestamp.desc()).limit(15)
    return session.exec(statement).all()

# Pede para a IA ler os eventos e achar o padrão
@app.post("/api/triggers/analyze")
def analyze_triggers(session: Session = Depends(get_session)):
    statement = select(TriggerEvent).order_by(TriggerEvent.timestamp.desc()).limit(20)
    eventos = session.exec(statement).all()
    
    if not eventos:
        return {"analise": "Ainda não há dados suficientes no seu diário para encontrar um padrão."}
    
    texto_historico = ", ".join([f"{e.tipo} (nível {e.valor}) às {e.timestamp.strftime('%H:%M')}" for e in eventos])
    analise = analisar_padroes_gatilhos(texto_historico)
    return {"analise": analise}

@app.post("/api/motor")
def controlar_motor(dados: dict = Body(...)):
    estado = dados.get("estado")
    
    if arduino_conectado:
        if estado == '1':
            arduino.write(b'1')
            return {"mensagem": "Motor ativado! Regulação tátil iniciada."}
        else:
            arduino.write(b'0')
            return {"mensagem": "Motor desativado!"}
    
    return {"erro": "Hardware físico não conectado. Conecte o Arduino no cabo USB."}


# ---------- INICIALIZAÇÃO ----------
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)