import google.generativeai as genai # type: ignore

# Substitua pela sua chave AIza...
CHAVE = "AIzaSyAP9QxJhb4Ikh-v6f-SAYSNO22gZvjOjII" 
genai.configure(api_key=CHAVE)

print("Tentando conectar com o Google Gemini...")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Oi, responda apenas 'Teste de conexão bem sucedido!'.")
    print("\nSUCESSO! A resposta da IA foi:")
    print(response.text)
except Exception as e:
    print("\nFALHA! O erro real que o Google está devolvendo é:")
    print(e)