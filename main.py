# main.py
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4
import os
import io

# Importações do FastAPI
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Body # type: ignore
from fastapi.responses import JSONResponse, StreamingResponse # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore # <--- IMPORTAÇÃO ADICIONADA PARA INTEGRAÇÃO

# Importações de Banco de Dados e Segurança
from sqlmodel import SQLModel, Field, create_engine, Session, select # type: ignore
from passlib.hash import bcrypt # type: ignore
from jose import jwt, JWTError # type: ignore

# ---------- CONFIGURAÇÃO BÁSICA ----------
SECRET_KEY = os.getenv("SERENO_SECRET", "change_this_secret_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sereno.db")

# Configuração do Banco de Dados (SQLite)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(title="Sereno Backend", version="0.1.0")

# ---------- INTEGRAÇÃO: CORS (Permite conexão com o HTML) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua "*" pelo domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# ---------- MODELOS DO BANCO DE DADOS (SQLModel) ----------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    hashed_password: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Script(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    title: str
    message: str
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Setting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    json_settings: str  # Armazena JSON como string
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True, nullable=True)
    device_id: Optional[str] = Field(default=None, index=True)
    event_type: str  # ex: "pico_som"
    value: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Backup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    filename: str
    blob: bytes
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- UTILITÁRIOS DE BANCO DE DADOS ----------

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Cria as tabelas ao iniciar
create_db_and_tables()

# ---------- AUTENTICAÇÃO E SEGURANÇA (JWT) ----------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)

# Decodifica token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)

# ---------- ROTAS DE AUTENTICAÇÃO ----------

@app.post("/auth/register", tags=["auth"])
def register(email: str = Body(...), password: str = Body(...), session: Session = Depends(get_session)):
    """
    Registra um usuário novo.
    """
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email e senha são necessários.")
    
    q = session.exec(select(User).where(User.email == email)).first()
    if q:
        raise HTTPException(status_code=400, detail="Email já registrado.")
    
    user = User(email=email, hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}

@app.post("/auth/login", tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Login para obter o token de acesso.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}

# Utilitário: Pegar usuário do Header (manual)
from fastapi import Request # type: ignore

def get_current_user_from_header(request: Request, session: Session) -> Optional[User]:
    auth: str = request.headers.get("Authorization")
    if not auth:
        return None
    if not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        return None
    return get_user_by_id(session, user_id)


# ---------- ROTAS PRINCIPAIS ----------

@app.get("/scripts", tags=["scripts"])
def list_scripts(request: Request, session: Session = Depends(get_session)):
    """
    Retorna scripts sociais. Se logado, retorna os do usuário.
    Se anônimo, retorna scripts padrão.
    """
    user = get_current_user_from_header(request, session)
    if user:
        scripts = session.exec(select(Script).where(Script.owner_id == user.id)).all()
        return scripts
    
    # Scripts padrão para usuários anônimos
    defaults = [
        {"id": 1, "title": "Pedir tempo", "message": "Preciso de um minuto, por favor.", "category": "Geral"},
        {"id": 2, "title": "Barulho incômodo", "message": "O barulho está me deixando desconfortável.", "category": "Ambiente"},
        {"id": 3, "title": "Ajuda", "message": "Poderia me ajudar com isso?", "category": "Geral"}
    ]
    return defaults

@app.post("/scripts", status_code=201, tags=["scripts"])
def create_script(payload: dict = Body(...), request: Request = None, session: Session = Depends(get_session)):
    """
    Cria script (Apenas autenticado).
    """
    user = get_current_user_from_header(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    
    title = payload.get("title")
    message = payload.get("message")
    category = payload.get("category")
    
    if not title or not message:
        raise HTTPException(status_code=400, detail="title e message são obrigatórios.")
    
    s = Script(owner_id=user.id, title=title, message=message, category=category)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s

@app.delete("/scripts/{script_id}", status_code=204, tags=["scripts"])
def delete_script(script_id: int, request: Request = None, session: Session = Depends(get_session)):
    user = get_current_user_from_header(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    
    s = session.get(Script, script_id)
    if not s or s.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Script não encontrado.")
    
    session.delete(s)
    session.commit()
    return JSONResponse(status_code=204, content={})

@app.get("/settings", tags=["settings"])
def get_settings(request: Request, session: Session = Depends(get_session)):
    """
    Retorna configurações do usuário.
    """
    user = get_current_user_from_header(request, session)
    if not user:
        return {"theme": "soft", "sound_threshold": 0.65, "animations": False, "data_logging": False}
    
    st = session.exec(select(Setting).where(Setting.owner_id == user.id)).first()
    if not st:
        return {"theme": "soft", "sound_threshold": 0.65, "animations": False, "data_logging": False}
    
    return {"json_settings": st.json_settings, "updated_at": st.updated_at}

@app.post("/settings", tags=["settings"])
def post_settings(payload: dict = Body(...), request: Request = None, session: Session = Depends(get_session)):
    """
    Salva configurações.
    """
    user = get_current_user_from_header(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    
    st = session.exec(select(Setting).where(Setting.owner_id == user.id)).first()
    from json import dumps
    js = dumps(payload)
    
    if not st:
        st = Setting(owner_id=user.id, json_settings=js)
        session.add(st)
    else:
        st.json_settings = js
        st.updated_at = datetime.utcnow()
        session.add(st)
    
    session.commit()
    session.refresh(st)
    return {"status": "ok", "updated_at": st.updated_at}

@app.post("/events", status_code=201, tags=["events"])
def log_event(payload: dict = Body(...), request: Request = None, session: Session = Depends(get_session)):
    """
    Recebe eventos de sensores (ex: pico_som) para log (opcional).
    """
    if not payload.get("event_type"):
        raise HTTPException(status_code=400, detail="event_type obrigatório")
    
    user = get_current_user_from_header(request, session)
    owner_id = user.id if user else None
    
    device_id = payload.get("device_id")
    value = payload.get("value")
    ts = payload.get("timestamp")
    
    try:
        ts_parsed = datetime.fromisoformat(ts) if ts else datetime.utcnow()
    except:
        ts_parsed = datetime.utcnow()
    
    ev = Event(owner_id=owner_id, device_id=device_id, event_type=payload.get("event_type"), value=value, timestamp=ts_parsed)
    session.add(ev)
    session.commit()
    session.refresh(ev)
    
    return {"status": "logged", "id": ev.id, "timestamp": ev.timestamp}

# ---------- ROTA DE BACKUP (Arquivo Criptografado) ----------

@app.post("/backup", tags=["backup"], status_code=201)
async def upload_backup(file: UploadFile = File(...), request: Request = None, session: Session = Depends(get_session)):
    """
    Recebe arquivo de backup criptografado do usuário.
    """
    user = get_current_user_from_header(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    
    # Bloqueia arquivos de mídia
    if file.content_type and (file.content_type.startswith("audio/") or file.content_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="Apenas backups criptografados são permitidos.")
    
    contents = await file.read()
    b = Backup(owner_id=user.id, filename=file.filename, blob=contents)
    session.add(b)
    session.commit()
    session.refresh(b)
    
    return {"status": "stored", "backup_id": b.id, "created_at": b.created_at}

@app.get("/backup/latest", tags=["backup"])
def download_latest_backup(request: Request, session: Session = Depends(get_session)):
    """
    Baixa o último backup salvo.
    """
    user = get_current_user_from_header(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    
    b = session.exec(select(Backup).where(Backup.owner_id == user.id).order_by(Backup.created_at.desc())).first()
    if not b:
        raise HTTPException(status_code=404, detail="Nenhum backup encontrado.")
    
    return StreamingResponse(io.BytesIO(b.blob), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={b.filename}"})

# ---------- ROTA DE DESENVOLVIMENTO ----------
@app.delete("/dev/reset-db", tags=["dev"])
def reset_db():
    # CUIDADO: Apenas para testes locais
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    return {"status": "reset"}

# ---------- INICIALIZAÇÃO ----------
if __name__ == "__main__":
    import uvicorn # type: ignore
    # Roda o servidor na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
[cite_start]``` [cite: 11, 14, 25, 27, 36, 43] # type: ignore