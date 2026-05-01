# security.py
from cryptography.fernet import Fernet
import os

ARQUIVO_CHAVE = "secret.key"

def _carregar_chave() -> bytes:
    """Gera uma chave mestre se não existir, ou carrega a existente."""
    if not os.path.exists(ARQUIVO_CHAVE):
        chave = Fernet.generate_key()
        with open(ARQUIVO_CHAVE, "wb") as key_file:
            key_file.write(chave)
    
    with open(ARQUIVO_CHAVE, "rb") as key_file:
        return key_file.read()

# Instancia o motor de criptografia (AES)
_motor_cripto = Fernet(_carregar_chave())

def proteger_dado(texto: str) -> str:
    """Recebe um texto limpo e retorna a versão criptografada."""
    if not texto:
        return texto
    return _motor_cripto.encrypt(texto.encode('utf-8')).decode('utf-8')

def revelar_dado(texto_cifrado: str) -> str:
    """Recebe o texto criptografado e devolve a versão limpa."""
    if not texto_cifrado:
        return texto_cifrado
    try:
        return _motor_cripto.decrypt(texto_cifrado.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Erro ao descriptografar dado: {e}")
        return "[Dado Corrompido ou Chave Inválida]"