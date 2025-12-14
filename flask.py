from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import logging

# -------------------------------------------------------------
#  Sereno AI - Flask Backend (Base Template)
#  Respeita: privacidade, mínimo de coleta, sem diagnósticos.
# -------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Permite que o front-end acesse o backend

# Logger mínimo, sem armazenar identificação
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------
# Função simples para gerar resposta segura (placeholder)
# -------------------------------------------------------------
def gerar_resposta_segura(texto: str) -> str:
    """
    Função placeholder — substitua pelo seu modelo de IA local.
    Garante que a resposta não faça diagnóstico ou afirmações sensíveis.
    """
    if not texto.strip():
        return "Nenhum texto recebido."

    # Resposta simples e segura
    return f"Recebi seu texto: '{texto}'. Posso ajudar a reformular, explicar ou continuar a ideia."


# -------------------------------------------------------------
# Nova rota IA (adicionada conforme solicitado)
# -------------------------------------------------------------
@app.post("/api/ia")
def processar_ia():
    dados = request.get_json()
    texto = dados.get("texto", "")
    resposta = gerar_resposta_segura(texto)
    return jsonify({"resposta": resposta})


# -------------------------------------------------------------
# Rota inicial
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

    data = request.get_json()
    sound_level = data.get("sound", None)
    brightness = data.get("brightness", None)

    response = {
        "sound_alert": False,
        "brightness_alert": False,
        "tips": []
    }

    if sound_level is not None and sound_level > 70:
        response["sound_alert"] = True
        response["tips"].append(
            "Som elevado detectado. Considere usar abafadores ou pausar um pouco."
        )

    if brightness is not None and brightness > 80:
        response["brightness_alert"] = True
        response["tips"].append(
            "Brilho intenso detectado. Talvez reduzir luminosidade ajude."
        )

    return jsonify(response)


# -------------------------------------------------------------
# Rota para auxiliar em interação social
# -------------------------------------------------------------
@app.route("/api/social-helper", methods=["POST"])
def social_helper():
    """
    A IA NÃO faz diagnóstico, apenas sugere estratégias sociais.
    """

    data = request.get_json()
    situation = data.get("situation", "")

    if not situation:
        return jsonify({"response": "Pode me contar um pouco sobre a situação?"})

    # Respostas simples — você pode substituir por modelos LLM locais
    resposta = ""

    if "grupo" in situation.lower():
        resposta = "Em conversas em grupo, você pode observar quem fala menos e interagir com essa pessoa primeiro."
    elif "barulho" in situation.lower():
        resposta = "Em ambientes barulhentos, tente se aproximar de alguém em um canto mais silencioso."
    else:
        resposta = "Ok! Uma boa estratégia é usar frases curtas e pausas longas. Quer tentar me dizer mais detalhes?"

    return jsonify({"response": resposta})


# -------------------------------------------------------------
# Execução
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
