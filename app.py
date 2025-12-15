from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import logging
import os
from openai import OpenAI

# -------------------------------------------------------------
#  Sereno AI - Flask Backend
#  Respeita: privacidade, mínimo de coleta, sem diagnósticos.
# -------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Permite que o front-end acesse o backend

# Logger mínimo, sem armazenar identificação
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------
# Configuração do Cliente OpenAI
# -------------------------------------------------------------
# Tenta pegar a chave do ambiente. Se não existir, a IA não funcionará.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# -------------------------------------------------------------
# Função para gerar resposta segura com IA
# -------------------------------------------------------------
def gerar_resposta_segura(texto: str) -> str:
    """
    Função que conecta com a OpenAI.
    Garante que a resposta não faça diagnóstico ou afirmações sensíveis via System Prompt.
    """
    if not texto.strip():
        return "Nenhum texto recebido."
    
    if not api_key:
        return "Erro de configuração: Chave da API (OPENAI_API_KEY) não encontrada no servidor."

    try:
        # Chamada à API (Modelo leve sugerido: gpt-4o-mini ou gpt-3.5-turbo)
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Você é o Sereno AI, um assistente empático, calmo e seguro. "
                        "Responda de forma breve, acolhedora e prática. "
                        "IMPORTANTE: Não faça diagnósticos médicos ou psicológicos. "
                        "Se o assunto for grave, sugira buscar um profissional."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=250,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Erro na IA: {e}")
        return "No momento estou com dificuldade de conexão, mas recebi sua mensagem. Tente novamente em instantes."


# -------------------------------------------------------------
# Rota IA (Processamento Geral)
# -------------------------------------------------------------
@app.post("/api/ia")
def processar_ia():
    dados = request.get_json()
    texto = dados.get("texto", "")
    resposta = gerar_resposta_segura(texto)
    return jsonify({"resposta": resposta})


# -------------------------------------------------------------
# Rota inicial (Health Check)
# -------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Sereno AI Backend ativo."})


# -------------------------------------------------------------
# Rota para análise sensorial local-simulada
# -------------------------------------------------------------
@app.route("/api/sensor-check", methods=["POST"])
def sensor_check():
    """
    Recebe dados DE FORMA ANÔNIMA do front-end
    e responde com alertas sensoriais leves.
    """
    data = request.get_json() or {}
    sound_level = data.get("sound", None)
    brightness = data.get("brightness", None)

    response = {
        "sound_alert": False,
        "brightness_alert": False,
        "tips": []
    }

    # Lógica simples de verificação (Simulação de sensores)
    if sound_level is not None and sound_level > 70:
        response["sound_alert"] = True
        response["tips"].append(
            "Som elevado detectado. Considere usar abafadores ou pausar um pouco."
        )

    if brightness is not None and brightness > 80:
        response["brightness_alert"] = True
        response["tips"].append(
            "Brilho intenso detectado. Talvez reduzir a luminosidade da tela ou do ambiente ajude."
        )

    return jsonify(response)


# -------------------------------------------------------------
# Rota para auxiliar em interação social
# -------------------------------------------------------------
@app.route("/api/social-helper", methods=["POST"])
def social_helper():
    """
    A IA NÃO faz diagnóstico, apenas sugere estratégias sociais.
    Usa regras simples primeiro, e IA como fallback inteligente.
    """
    data = request.get_json() or {}
    situation = data.get("situation", "")

    if not situation:
        return jsonify({"response": "Pode me contar um pouco sobre a situação?"})

    resposta = ""

    # Estratégia Híbrida: Regras rápidas primeiro
    if "grupo" in situation.lower():
        resposta = "Em conversas em grupo, uma boa tática é observar quem fala menos e tentar interagir visualmente com essa pessoa primeiro."
    elif "barulho" in situation.lower():
        resposta = "Em ambientes barulhentos, tente se posicionar em um canto mais silencioso ou sugira ir para um local mais calmo."
    elif "cumprimentar" in situation.lower() or "oi" in situation.lower():
        resposta = "Um simples 'Oi, tudo bem?' geralmente é suficiente. Se quiser, pode comentar algo sobre o ambiente (ex: 'Está cheio hoje, né?')."
    else:
        # Se não caiu em nenhuma regra específica, usa a IA para gerar uma dica personalizada
        resposta = gerar_resposta_segura(f"Dê uma dica social breve e prática para a seguinte situação: {situation}")

    return jsonify({"response": resposta})


# -------------------------------------------------------------
# Execução
# -------------------------------------------------------------
if __name__ == "__main__":
    # Define a porta 5000 como padrão
    app.run(debug=True, host="0.0.0.0", port=5000)