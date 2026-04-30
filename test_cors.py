from fastapi.testclient import TestClient
from main import app  # Importa o seu app do main.py

client = TestClient(app)

def test_cors_origem_permitida():
    """Testa se uma origem autorizada recebe os cabeçalhos corretos."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST" # <- LINHA ADICIONADA AQUI
    }
    response = client.options("/api/ia", headers=headers)
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_cors_origem_bloqueada():
    """Testa se uma origem desconhecida é ignorada pelo CORS."""
    headers = {"Origin": "http://site-malicioso.com"}
    response = client.options("/api/ia", headers=headers)
    
    # Se a origem não é permitida, o FastAPI não envia o cabeçalho de allow-origin
    assert "access-control-allow-origin" not in response.headers

def test_cors_preflight_methods():
    """Testa se o preflight autoriza os métodos corretos (POST, GET, etc)."""
    headers = {
        "Origin": "http://localhost:8000",
        "Access-Control-Request-Method": "POST"
    }
    response = client.options("/api/ia", headers=headers)
    
    assert response.status_code == 200
    assert "POST" in response.headers["access-control-allow-methods"]

def test_cors_credentials_false():
    """Garante que a política de credenciais está desativada conforme a spec."""
    headers = {"Origin": "http://localhost:5173"}
    response = client.options("/api/ia", headers=headers)
    
    # Verifica se o cabeçalho de allow-credentials NÃO está na resposta
    assert "access-control-allow-credentials" not in response.headers