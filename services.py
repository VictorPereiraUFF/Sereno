# services.py
import os
import re
import base64
from dotenv import load_dotenv  # type: ignore # Biblioteca para ler o ficheiro .env
from google import genai
from google.genai import types
from typing import Optional

# 1. Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# 2. Configuração da Chave da API e do Cliente
# A chave é lida de forma segura das variáveis de ambiente
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=CHAVE_GEMINI)

# Modelo atualizado para evitar o erro 404 encontrado anteriormente
MODELO_ATUAL = 'gemini-2.5-flash'

# ==========================================================
# PERSONA_SERENO — Núcleo de personalidade do assistente
# ==========================================================
# Este bloco define QUEM o Sereno é (caráter, tom, limites).
# Todas as funções que chamam a IA partem daqui e apenas
# ACRESCENTAM a instrução específica da tarefa (chat, tradução,
# análise de gatilhos, etc). Isso garante que a voz do assistente
# seja a mesma em qualquer parte do app.
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

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None, estilo: Optional[str] = None, bateria_atual: Optional[int] = None) -> str:
    """Processa texto e imagem usando o modelo Gemini mais recente."""
    if not CHAVE_GEMINI:
        return "Erro: Chave de API não configurada no ficheiro .env!"

    # Base do prompt = persona + regras específicas desta tarefa
    system_prompt = (
        PERSONA_SERENO + "\n\n"
        "TAREFA ATUAL (Assistente Geral):\n"
        "1. Se receber imagem, analise APENAS gatilhos sensoriais (luzes, padrões, bagunça).\n"
        "2. Se receber texto, sugira calma e estratégias sociais.\n"
    )

    # Injeção dinâmica de estilo baseada na escolha do usuário
    if estilo == "detailed":
        system_prompt += "3. IMPORTANTE: O usuário prefere textos mais acolhedores, empáticos e explicativos. Desenvolva bem a resposta, sem perder a objetividade da persona.\n"
    else:
        system_prompt += "3. IMPORTANTE: O usuário prefere textos curtos, diretos ao ponto e estruturados em tópicos rápidos. Seja extremamente objetivo e evite excessos.\n"

    # Adapta o tom ao nível atual de bateria social, quando informado
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
        # Detalhe técnico só vai para o log; o usuário recebe uma frase no tom do Sereno
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

def calcular_bateria_social_gpt(texto: str) -> int:
    """Estima o nível de bateria social de 0 a 100 com base no texto do utilizador."""
    if not CHAVE_GEMINI:
        return 50 

    system_prompt = (
        "Você é um analisador de energia social e sobrecarga cognitiva para pessoas neurodivergentes. "
        "Leia a intenção do usuário e estime o nível atual de disposição social dele em uma escala de 0 a 100. "
        "Responda APENAS com um número inteiro (ex: 25). Não escreva mais nada."
    )

    try:
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=f"Calcule a bateria para: '{texto}'",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            )
        )
        resultado = response.text.strip()
        
        # Extração de números para garantir que o retorno é um inteiro
        numeros = re.findall(r'\d+', resultado)
        if numeros:
            nivel = int(numeros[0])
            return max(0, min(100, nivel))
        return 50
    except Exception as e:
        print(f"Erro Gemini Bateria: {e}")
        return 50
    
def prever_sobrecarga_mmq(historico_bateria: list) -> dict:
    """
    Analisa a tendência da bateria social usando MMQ.
    Retorna True se detectar uma queda brusca (sobrecarga iminente).
    """
    n = len(historico_bateria)
    if n < 3:  # Necessário um histórico mínimo para prever tendência
        return {"alerta": False, "mensagem": ""}

    # x = tempo (índice), y = nível da bateria
    x = list(range(n))
    y = historico_bateria

    soma_x = sum(x)
    soma_y = sum(y)
    soma_xy = sum(xi * yi for xi, yi in zip(x, y))
    soma_x2 = sum(xi**2 for xi in x)

    denominador = (n * soma_x2) - (soma_x**2)
    if denominador == 0:
        return {"alerta": False, "mensagem": ""}

    # Cálculo da inclinação (m)
    m = ((n * soma_xy) - (soma_x * soma_y)) / denominador

    # Se m < -5, a bateria está a cair mais de 5% por interação
    if m <= -5.0:
        return {
            "alerta": True,
            "mensagem": "⚠️ Alerta: Queda rápida de energia detectada. Sugerimos pausa imediata."
        }
    
    return {"alerta": False, "mensagem": "Energia estável."}

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
                temperature=0.3, # Temperatura baixa para ser mais analítico e preciso
            )
        )
        return response.text
    except Exception as e:
        print(f"Erro Gemini Análise de Gatilhos: {e}")
        return "Não consegui analisar os padrões agora. Pode tentar de novo em instantes."