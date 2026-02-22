# database.py
import os
from sqlmodel import create_engine, Session, SQLModel # type: ignore

# Lê a URL do banco (ou cria um arquivo local sqlite caso não exista)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sereno.db")

# Cria o "motor" que conecta com o banco
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Cria as tabelas no banco de dados se elas ainda não existirem."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Gera uma sessão de conexão temporária para cada requisição."""
    with Session(engine) as session:
        yield session