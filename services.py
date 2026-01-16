# services.py
import os
from openai import OpenAI # type: ignore
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