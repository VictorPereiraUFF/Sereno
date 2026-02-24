# services.py
import os
import re
from openai import OpenAI
from typing import Optional

# Configuração
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_resposta_gpt(texto: str, imagem_b64: Optional[str] = None) -> str:
    """Processa texto e imagem usando GPT-4o-mini."""
    if not client.api_key:
        return "Erro: Chave de API (OPENAI_API_KEY) não configurada."

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

def suavizar_texto_gpt(texto: str) -> str:
    """Reescreve textos diretos para torná-los polidos e sociais."""
    if not client.api_key:
        return "Erro: API Key não configurada."

    system_prompt = (
        "Você é um especialista em comunicação social e etiqueta brasileira. "
        "Sua função é receber frases curtas, diretas ou 'secas' (comuns em neurodivergentes) "
        "e reescrevê-las de forma educada, empática e profissional, mantendo o significado original. "
        "Dê apenas a frase reescrita, sem explicações extras."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Suavize esta frase: '{texto}'"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return "Não consegui suavizar o texto agora."

def calcular_bateria_social_gpt(texto: str) -> int:
    """Analisa o texto do usuário e estima o nível de bateria social de 0 a 100."""
    if not client.api_key:
        return 50 # Retorna um valor médio neutro em caso de erro

    system_prompt = (
        "Você é um analisador de energia social e sobrecarga cognitiva para pessoas neurodivergentes. "
        "Leia a intenção do usuário e estime o nível atual de disposição social dele em uma escala de 0 a 100. "
        "- 0 a 30 (Baixa): Textos diretos demais, irritados, relatando cansaço, aversão a barulho ou vontade de isolamento. "
        "- 40 a 60 (Média): Textos neutros, conversas do dia a dia, dúvidas simples. "
        "- 70 a 100 (Alta): Textos empolgados, longos, amigáveis ou buscando interação proativa. "
        "Responda APENAS com um número inteiro (ex: 25). Não escreva mais nada."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Calcule a bateria para: '{texto}'"}
            ],
            max_tokens=10,
            temperature=0.2 # Menor temperatura para respostas mais exatas
        )
        
        resultado = response.choices[0].message.content.strip()
        
        # Garante que vamos extrair apenas os números, caso a IA escreva texto junto
        numeros = re.findall(r'\d+', resultado)
        if numeros:
            nivel = int(numeros[0])
            return max(0, min(100, nivel)) # Garante que fique entre 0 e 100
        return 50
    except Exception as e:
        print(f"Erro ao calcular bateria: {e}")
        return 50