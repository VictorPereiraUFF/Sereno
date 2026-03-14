# services.py
import os
import re
import base64
from google import genai
from google.genai import types
from typing import Optional

# 1. Configuração da Chave da API
# COLE SUA CHAVE NOVA AQUI DENTRO DAS ASPAS E SALVE O ARQUIVO
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=CHAVE_GEMINI)

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None) -> str:
    """Processa texto e imagem usando Gemini 2.5 Flash."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_NOVA_AQUI_E_MANTENHA_SECRETA":
        return "Erro: Você esqueceu de colar a chave nova no código!"

    system_prompt = (
        "Você é o Sereno AI, focado em acessibilidade e regulação sensorial. "
        "1. Se receber imagem, analise APENAS gatilhos sensoriais (luzes, padrões, bagunça). "
        "2. Se receber texto, sugira calma e estratégias sociais. "
        "3. NÃO dê diagnósticos médicos. Seja breve."
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
        # MUDANÇA AQUI: Atualizado para o modelo mais recente (2.5)!
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text
    except Exception as e:
        erro_real = str(e)
        print(f"Erro Gemini Chat: {erro_real}")
        return f"🕵️‍♂️ Erro de Conexão com o Google: {erro_real}"

def suavizar_texto_gpt(texto: str) -> str:
    """Reescreve textos diretos para torná-los polidos usando Gemini."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_NOVA_AQUI_E_MANTENHA_SECRETA":
        return "Erro: Chave de API não configurada."

    system_prompt = (
        "Você é um especialista em comunicação social e etiqueta brasileira. "
        "Sua função é receber frases curtas, diretas ou 'secas' (comuns em neurodivergentes) "
        "e reescrevê-las de forma educada, empática e profissional, mantendo o significado original. "
        "Dê apenas a frase reescrita, sem explicações extras."
    )

    try:
        # MUDANÇA AQUI: Atualizado para o modelo mais recente (2.5)!
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Suavize esta frase: '{texto}'",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text
    except Exception as e:
        return f"🕵️‍♂️ Erro Gemini Tradutor: {str(e)}"

def calcular_bateria_social_gpt(texto: str) -> int:
    """Estima o nível de bateria social de 0 a 100 usando Gemini."""
    if CHAVE_GEMINI == "COLE_SUA_CHAVE_NOVA_AQUI_E_MANTENHA_SECRETA":
        return 50 

    system_prompt = (
        "Você é um analisador de energia social e sobrecarga cognitiva para pessoas neurodivergentes. "
        "Leia a intenção do usuário e estime o nível atual de disposição social dele em uma escala de 0 a 100. "
        "Responda APENAS com um número inteiro."
    )

    try:
        # MUDANÇA AQUI: Atualizado para o modelo mais recente (2.5)!
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Calcule a bateria para: '{texto}'",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            )
        )
        resultado = response.text.strip()
        numeros = re.findall(r'\d+', resultado)
        if numeros:
            return max(0, min(100, int(numeros[0])))
        return 50
    except Exception as e:
        print(f"Erro Gemini Bateria: {e}")
        return 50