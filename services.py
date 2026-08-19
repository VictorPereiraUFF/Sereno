# services.py
import os
import re
import base64
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict
from dotenv import load_dotenv  # type: ignore # Biblioteca para ler o ficheiro .env
from google import genai
from google.genai import types

# 1. Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# 2. Configuração da Chave da API e do Cliente
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=CHAVE_GEMINI)

# Modelo atualizado para evitar o erro 404 encontrado anteriormente
MODELO_ATUAL = 'gemini-2.5-flash'

# ==========================================================
# PERSONA_SERENO — Núcleo de personalidade do assistente
# ==========================================================
PERSONA_SERENO = """
Você é o Sereno, um assistente de apoio sensorial e social para pessoas do Espectro Autista.

QUEM VOCÊ É:
- Calmo, literal e previsível. Você não improvisa tom: mantém a mesma voz sempre.
- Você valida sem minimizar. Prefira "isso faz sentido" a "não se preocupe" ou "vai ficar tudo bem".
- Você é direto e concreto. Evita floreios, metáforas vagas e entusiasmo forçado.
- Você fala como uma presença estável, não como uma celebridade animada. Sem excesso de emojis ou exclamações.
- Você respeita o tempo e o processamento da pessoa: frases curtas, uma ideia por vez, sem pressa.

LIMITES (sempre):
- Você não dá diagnósticos médicos nem se apresenta como terapia ou tratamento.
- Você não insiste em small talk nem faz perguntas desnecessárias quando a pessoa já disse o que precisa.
- Quando não tiver certeza, você diz isso com naturalidade, sem se desculpar em excesso.
""".strip()

# ==========================================================
# MÓDULO DE INTERAÇÃO COM GEMINI (CHAT E TRADUÇÃO)
# ==========================================================

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None, estilo: Optional[str] = None, bateria_atual: Optional[int] = None) -> str:
    """Processa texto e imagem usando o modelo Gemini mais recente."""
    if not CHAVE_GEMINI:
        return "Erro: Chave de API não configurada no ficheiro .env!"

    system_prompt = (
        PERSONA_SERENO + "\n\n"
        "TAREFA ATUAL (Assistente Geral):\n"
        "1. Se receber imagem, analise APENAS gatilhos sensoriais (luzes, padrões, bagunça).\n"
        "2. Se receber texto, sugira calma e estratégias sociais.\n"
    )

    if estilo == "detailed":
        system_prompt += "3. IMPORTANTE: O usuário prefere textos mais acolhedores, empáticos e explicativos. Desenvolva bem a resposta, sem perder a objetividade da persona.\n"
    else:
        system_prompt += "3. IMPORTANTE: O usuário prefere textos curtos, diretos ao ponto e estruturados em tópicos rápidos. Seja extremamente objetivo e evite excessos.\n"

    if bateria_atual is not None:
        if bateria_atual <= 20:
            system_prompt += (
                "4. ESTADO ATUAL: bateria social crítica (<=20%). Use frases ainda mais curtas, "
                "evite propor várias ações ao mesmo tempo, priorize validação e uma única sugestão de descanso. "
                "Não faça perguntas de acompanhamento."
            )
        elif bateria_atual <= 50:
            system_prompt += (
                "4. ESTADO ATUAL: bateria social moderada (21-50%). Mantenha o tom calmo e sugira no máximo "
                "uma ou duas ações leves, sem sobrecarregar."
            )
        else:
            system_prompt += (
                "4. ESTADO ATUAL: bateria social alta (>50%). Você pode manter o tom normal da persona, "
                "sem necessidade de cautela extra."
            )

    contents = []
    
    if imagem_b64:
        image_bytes = base64.b64decode(imagem_b64)
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
        )
    
    prompt_texto = texto if texto else "Analise esta imagem quanto a gatilhos sensoriais."
    contents.append(prompt_texto)

    try:
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text
    except Exception as e:
        print(f"Erro Gemini Chat: {e}")
        return "Não consegui processar isso agora. Pode tentar de novo em instantes."

def suavizar_texto_gpt(texto: str) -> str:
    """Reescreve textos diretos para torná-los polidos e empáticos."""
    if not CHAVE_GEMINI:
        return "Erro: Chave de API não configurada."

    system_prompt = (
        PERSONA_SERENO + "\n\n"
        "TAREFA ATUAL (Tradutor Social):\n"
        "Você recebe frases curtas, diretas ou 'secas' (comuns em neurodivergentes) e as reescreve "
        "de forma educada, empática e profissional para o mundo social neurotípico, mantendo o significado "
        "original — sem trair a intenção real da pessoa. "
        "Dê apenas a frase reescrita, sem explicações extras."
    )

    try:
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=f"Suavize esta frase: '{texto}'",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text
    except Exception as e:
        print(f"Erro Gemini Tradutor: {e}")
        return "Não consegui suavizar essa frase agora. Pode tentar de novo em instantes."


# ==========================================================
# MÓDULO TEMPORAL DE BATERIA SOCIAL E MMQ
# ==========================================================

def calcular_impacto_prompt_gpt(texto: str) -> float:
    """
    Avalia a variação da bateria social (-30 a +20) gerada pelo prompt atual.
    """
    if not CHAVE_GEMINI:
        return -5.0 

    system_prompt = (
        "Você é um analisador de impacto emocional e sensorial. "
        "Avalie o texto do usuário e retorne um número decimal relativo ao impacto no nível de energia dele: "
        "Valores negativos para exaustão/estresse (ex: -20 para sobrecarga, -5 para leve cansaço) "
        "e positivos para momentos de descanso ou calma (ex: +10). "
        "Responda APENAS com o número. Exemplo: -15"
    )

    try:
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=f"Calcule o impacto na bateria para: '{texto}'",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            )
        )
        resultado = response.text.strip()
        numeros = re.findall(r'[-+]?\d*\.?\d+', resultado)
        if numeros:
            impacto = float(numeros[0])
            return max(-50.0, min(50.0, impacto))
        return -5.0
    except Exception as e:
        print(f"Erro Gemini Impacto: {e}")
        return -5.0


def calcular_recuperacao_passiva(
    bateria_anterior: float,
    timestamp_ultimo_prompt: datetime,
    tempo_recuperacao_minutos: float = 120.0,
    timestamp_atual: Optional[datetime] = None
) -> float:
    """Calcula o ganho de bateria por tempo de descanso passivo."""
    if timestamp_atual is None:
        timestamp_atual = datetime.now(timezone.utc)
        
    if timestamp_ultimo_prompt.tzinfo is None:
        timestamp_ultimo_prompt = timestamp_ultimo_prompt.replace(tzinfo=timezone.utc)

    delta_t_minutos = max(0.0, (timestamp_atual - timestamp_ultimo_prompt).total_seconds() / 60.0)

    if bateria_anterior >= 100.0 or tempo_recuperacao_minutos <= 0:
        return min(100.0, bateria_anterior)

    taxa_recuperacao = (100.0 - bateria_anterior) / tempo_recuperacao_minutos
    bateria_recuperada = bateria_anterior + (taxa_recuperacao * delta_t_minutos)
    return min(100.0, max(0.0, bateria_recuperada))


def processar_interacao_bateria(
    bateria_anterior: float,
    timestamp_ultimo_prompt: datetime,
    impacto_prompt: float,
    tempo_recuperacao_estimado: float = 120.0
) -> Dict[str, any]:
    """Aplica a recuperação passiva e o desgaste do novo prompt."""
    agora = datetime.now(timezone.utc)

    # 1. Recuperação por descanso acumulado
    bateria_base = calcular_recuperacao_passiva(
        bateria_anterior=bateria_anterior,
        timestamp_ultimo_prompt=timestamp_ultimo_prompt,
        tempo_recuperacao_minutos=tempo_recuperacao_estimado,
        timestamp_atual=agora
    )

    # 2. Impacto da nova interação
    bateria_final = min(100.0, max(0.0, bateria_base + impacto_prompt))

    return {
        "bateria_base_recuperada": round(bateria_base, 2),
        "bateria_final": round(bateria_final, 2),
        "timestamp": agora
    }


def prever_sobrecarga_mmq(historico_temporal: List[Tuple[float, float]]) -> Dict[str, any]:
    """
    Aplica MMQ sobre pontos (x_i, y_i) em minutos decorridos reais:
    x_i = minutos decorridos desde o primeiro registro
    y_i = nível de bateria
    """
    n = len(historico_temporal)
    if n < 3:
        return {"alerta": False, "m": 0.0, "mensagem": "Histórico insuficiente."}

    x = [ponto[0] for ponto in historico_temporal]
    y = [ponto[1] for ponto in historico_temporal]

    soma_x = sum(x)
    soma_y = sum(y)
    soma_xy = sum(xi * yi for xi, yi in zip(x, y))
    soma_x2 = sum(xi**2 for xi in x)

    denominador = (n * soma_x2) - (soma_x**2)
    if denominador == 0:
        return {"alerta": False, "m": 0.0, "mensagem": ""}

    # Inclinação m (% de energia perdida por minuto)
    m = ((n * soma_xy) - (soma_x * soma_y)) / denominador

    # Gatilho: perda acentuada por minuto de interação contínua
    if m <= -0.5:
        return {
            "alerta": True,
            "m": round(m, 3),
            "mensagem": "⚠️ Alerta: Queda rápida de energia detectada. Sugerimos pausa imediata."
        }
    
    return {"alerta": False, "m": round(m, 3), "mensagem": "Energia estável."}


# ==========================================================
# MÓDULO DE ANÁLISE DE GATILHOS
# ==========================================================

def analisar_padroes_gatilhos(historico_texto: str) -> str:
    if not CHAVE_GEMINI:
        return "Conexão com a IA indisponível."

    system_prompt = (
        PERSONA_SERENO + "\n\n"
        "TAREFA ATUAL (Diário de Gatilhos):\n"
        "Você recebe um log de eventos (luzes fortes, barulhos, quedas de bateria social) e explica, "
        "em 1 ou 2 parágrafos curtos, o que parece estar causando os maiores desgastes na energia da pessoa. "
        "Termine com uma sugestão prática baseada nos dados."
    )

    try:
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=f"Analise este histórico e encontre o padrão: {historico_texto}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
            )
        )
        return response.text
    except Exception as e:
        print(f"Erro Gemini Análise de Gatilhos: {e}")
        return "Não consegui analisar os padrões agora. Pode tentar de novo em instantes."