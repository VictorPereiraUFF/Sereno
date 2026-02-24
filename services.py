# services.py
import os
import re
import google.generativeai as genai # type: ignore
from typing import Optional

# 1. Configuração da Chave da API do Google Gemini
# Coloque sua chave aqui dentro das aspas, ex: "AIzaSy..."
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY", "COLE_SUA_CHAVE_AQUI")
genai.configure(api_key=CHAVE_GEMINI)

# 2. Funções (Mantivemos os nomes originais para não quebrar o main.py)

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None) -> str:
    """Processa texto e imagem usando Gemini 1.5 Flash."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_AQUI":
        return "Erro: Você esqueceu de colocar sua chave do Gemini no arquivo services.py!"

    system_prompt = (
        "Você é o Sereno AI, focado em acessibilidade e regulação sensorial. "
        "1. Se receber imagem, analise APENAS gatilhos sensoriais (luzes, padrões, bagunça). "
        "2. Se receber texto, sugira calma e estratégias sociais. "
        "3. NÃO dê diagnósticos médicos. Seja breve."
    )

    # Prepara o conteúdo (Texto + Imagem se houver)
    contents = []
    if imagem_b64:
        contents.append({
            "mime_type": "image/jpeg",
            "data": imagem_b64
        })
    
    prompt_texto = texto if texto else "Analise esta imagem quanto a gatilhos sensoriais."
    contents.append(prompt_texto)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"Erro Gemini Chat: {e}")
        return "Tive uma dificuldade técnica para processar isso agora."

def suavizar_texto_gpt(texto: str) -> str:
    """Reescreve textos diretos para torná-los polidos usando Gemini."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_AQUI":
        return "Erro: Chave de API não configurada."

    system_prompt = (
        "Você é um especialista em comunicação social e etiqueta brasileira. "
        "Sua função é receber frases curtas, diretas ou 'secas' (comuns em neurodivergentes) "
        "e reescrevê-las de forma educada, empática e profissional, mantendo o significado original. "
        "Dê apenas a frase reescrita, sem explicações extras."
    )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        response = model.generate_content(f"Suavize esta frase: '{texto}'")
        return response.text
    except Exception as e:
        print(f"Erro Gemini Tradutor: {e}")
        return "Não consegui suavizar o texto agora."

def calcular_bateria_social_gpt(texto: str) -> int:
    """Estima o nível de bateria social de 0 a 100 usando Gemini."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_AQUI":
        return 50 

    system_prompt = (
        "Você é um analisador de energia social e sobrecarga cognitiva para pessoas neurodivergentes. "
        "Leia a intenção do usuário e estime o nível atual de disposição social dele em uma escala de 0 a 100. "
        "- 0 a 30 (Baixa): Textos diretos demais, irritados, relatando cansaço, aversão a barulho ou vontade de isolamento. "
        "- 40 a 60 (Média): Textos neutros, conversas do dia a dia, dúvidas simples. "
        "- 70 a 100 (Alta): Textos empolgados, longos, amigáveis ou buscando interação proativa. "
        "Responda APENAS com um número inteiro (ex: 25). Não escreva mais nada."
    )

    try:
        # Configura a temperatura baixa para respostas matemáticas mais diretas
        config = genai.GenerationConfig(temperature=0.2)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt, generation_config=config)
        
        response = model.generate_content(f"Calcule a bateria para: '{texto}'")
        resultado = response.text.strip()
        
        # Extrai apenas os números da resposta
        numeros = re.findall(r'\d+', resultado)
        if numeros:
            nivel = int(numeros[0])
            return max(0, min(100, nivel))
        return 50
    except Exception as e:
        print(f"Erro Gemini Bateria: {e}")
        return 50