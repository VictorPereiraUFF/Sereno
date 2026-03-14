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

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None) -> str:
    """Processa texto e imagem usando o modelo Gemini mais recente."""
    if not CHAVE_GEMINI:
        return "Erro: Chave de API não configurada no ficheiro .env!"

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
        response = client.models.generate_content(
            model=MODELO_ATUAL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text
    except Exception as e:
        # Retorna o erro real para facilitar a depuração, se necessário
        print(f"Erro Gemini Chat: {e}")
        return f"Tive uma dificuldade técnica para processar isso agora. Detalhe: {str(e)}"

def suavizar_texto_gpt(texto: str) -> str:
    """Reescreve textos diretos para torná-los polidos e empáticos."""
    if not CHAVE_GEMINI:
        return "Erro: Chave de API não configurada."

    system_prompt = (
        "Você é um especialista em comunicação social e etiqueta brasileira. "
        "Sua função é receber frases curtas, diretas ou 'secas' (comuns em neurodivergentes) "
        "e reescrevê-las de forma educada, empática e profissional, mantendo o significado original. "
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
        return "Não consegui suavizar o texto agora."

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