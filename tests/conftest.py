import sys
from unittest.mock import MagicMock, patch
import pytest

# --- Mocks de dependências externas (executadas no nível do módulo ao importar) ---

# pyserial pode não estar instalado no ambiente de testes
serial_mock = MagicMock()
serial_mock.SerialException = Exception
sys.modules.setdefault("serial", serial_mock)

# google.genai inicializa o cliente com api_key no nível do módulo em services.py
genai_mock = MagicMock()
genai_mock.Client.return_value = MagicMock()
sys.modules["google.genai"] = genai_mock
sys.modules["google"] = MagicMock(genai=genai_mock)

with patch("time.sleep"):
    import main  # noqa: E402

from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    return TestClient(main.app, raise_server_exceptions=True)
