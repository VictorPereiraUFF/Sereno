"""
Testes unitários para a configuração de CORS (issue #1).

Valida que:
- Origens permitidas recebem o header Access-Control-Allow-Origin correto
- Origens não permitidas não recebem header CORS
- allow_credentials=False nunca expõe Access-Control-Allow-Credentials: true
- Preflight (OPTIONS) funciona para origens permitidas e é bloqueado para não permitidas
"""

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
]

BLOCKED_ORIGINS = [
    "http://evil.com",
    "http://localhost:3000",
    "null",
]


class TestOrigensPermitidas:
    def test_localhost_5173_recebe_header_allow_origin(self, client):
        response = client.get("/", headers={"Origin": "http://localhost:5173"})
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_localhost_8000_recebe_header_allow_origin(self, client):
        response = client.get("/", headers={"Origin": "http://localhost:8000"})
        assert response.headers.get("access-control-allow-origin") == "http://localhost:8000"

    def test_origem_permitida_retorna_200(self, client):
        response = client.get("/", headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 200


class TestOrigensNaoPermitidas:
    def test_origem_desconhecida_nao_recebe_allow_origin(self, client):
        response = client.get("/", headers={"Origin": "http://evil.com"})
        assert "access-control-allow-origin" not in response.headers

    def test_localhost_3000_nao_permitido(self, client):
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" not in response.headers

    def test_origem_null_nao_permitida(self, client):
        response = client.get("/", headers={"Origin": "null"})
        assert "access-control-allow-origin" not in response.headers


class TestCredentials:
    def test_allow_credentials_nunca_exposto(self, client):
        for origin in ALLOWED_ORIGINS:
            response = client.get("/", headers={"Origin": origin})
            value = response.headers.get("access-control-allow-credentials", "")
            assert value != "true", (
                f"Origin {origin} retornou Access-Control-Allow-Credentials: true — "
                "isso é inválido quando credentials=False"
            )

    def test_origem_bloqueada_sem_credentials(self, client):
        for origin in BLOCKED_ORIGINS:
            response = client.get("/", headers={"Origin": origin})
            assert response.headers.get("access-control-allow-credentials") != "true"


class TestPreflight:
    def test_preflight_origem_permitida_retorna_200(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200

    def test_preflight_origem_permitida_expoe_allow_origin(self, client):
        response = client.options(
            "/api/ia",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_preflight_origem_bloqueada_nao_expoe_allow_origin(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert "access-control-allow-origin" not in response.headers

    def test_preflight_sem_credentials_true(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-credentials") != "true"
