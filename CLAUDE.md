# Sereno AI — Guia de Desenvolvimento

Assistente de regulação sensorial e acessibilidade para pessoas neurodivergentes. Monitora energia social, oferece ferramentas de calma e integra hardware físico (Arduino) para feedback tátil.

---

## Stack

### Estado Atual (fase 1 concluída parcialmente)
Monólito flat: FastAPI servindo HTML/CSS/JS estático + SQLite local + Arduino via PySerial.

### Stack Alvo (a partir da fase 2)
| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Backend | **FastAPI + Python 3.11+** | Async nativo, integração direta com PySerial e Gemini SDK |
| ORM | **SQLModel** | Pydantic + SQLAlchemy sem duplicação de schemas |
| Banco | **SQLite** (`sereno.db`) | Local-first, sem servidor, ideal para app pessoal |
| Frontend | **React 18 + Vite** | Gerenciamento de estado (bateria sincroniza N componentes) |
| Estilo | **Tailwind CSS** | Dark mode nativo, utilitários de acessibilidade |
| IA | **Google Gemini API** (`gemini-2.5-flash`) | Rápido, barato, multimodal |
| Hardware | **Arduino + PySerial** | Único caminho viável para serial USB em Python |
| Automação | **Make.com Webhook** | Conselhos personalizados por nível de bateria |

---

## Estrutura de Pastas

### Atual (estado real do repositório)
```
Sereno/
├── hardware/
│   └── sereno.ino          # Código Arduino (motor de passo 28BYJ-48)
├── main.py                 # Servidor FastAPI + todas as rotas
├── models.py               # SQLModel: User, Script, SocialBattery + schemas Pydantic
├── services.py             # Lógica de IA: Gemini, MMQ, suavização
├── database.py             # Engine SQLite + get_session
├── index.html              # UI (HTML único)
├── conexao.js              # Frontend JS (vanilla)
├── styles.css              # Estilos CSS + dark mode
├── sw.js                   # Service Worker (PWA)
├── manifest.json           # PWA manifest
├── sereno.db               # Banco SQLite (não versionado)
├── .env                    # GEMINI_API_KEY (não versionado)
├── ESPECIFICACOES.md       # Especificações completas de funcionalidades
└── CLAUDE.md               # Este arquivo
```

### Alvo (a partir da fase 2 — separação backend/frontend)
```
Sereno/
├── backend/
│   ├── main.py             # Entrypoint FastAPI
│   ├── database.py         # Engine e sessão
│   ├── models.py           # Tabelas SQLModel
│   ├── schemas.py          # Schemas Pydantic (request/response)
│   ├── services.py         # Lógica de IA e MMQ
│   ├── hardware.py         # Conexão e controle do Arduino
│   └── routes/
│       ├── battery.py      # /api/battery, /api/bateria/calcular
│       ├── chat.py         # /api/ia, /api/suavizar
│       ├── scripts.py      # /scripts
│       └── motor.py        # /api/motor
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SocialBattery.jsx
│   │   │   ├── ChatAssistant.jsx
│   │   │   ├── SocialTranslator.jsx
│   │   │   ├── ScriptList.jsx
│   │   │   ├── BreathingGuide.jsx
│   │   │   └── BrownNoise.jsx
│   │   ├── hooks/
│   │   │   ├── useBattery.js
│   │   │   └── useTheme.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   │   ├── manifest.json
│   │   ├── sw.js
│   │   └── icons/
│   ├── index.html
│   ├── tailwind.config.js
│   └── vite.config.js
├── hardware/
│   └── sereno.ino
├── .env                    # GEMINI_API_KEY (não versionado)
├── .gitignore
├── ESPECIFICACOES.md
└── CLAUDE.md
```

---

## Comandos

### Backend (atual e alvo)
```bash
# Instalar dependências
pip install fastapi uvicorn sqlmodel pyserial google-generativeai python-dotenv

# Rodar o servidor (estrutura atual)
uvicorn main:app --reload --port 8000

# Rodar o servidor (estrutura alvo)
uvicorn backend.main:app --reload --port 8000

# Rodar testes Python
pytest backend/tests/ -v

# Verificar tipos
mypy backend/
```

### Frontend (estrutura alvo)
```bash
cd frontend

# Instalar dependências
npm install

# Servidor de desenvolvimento (HMR)
npm run dev

# Build de produção
npm run build

# Preview do build
npm run preview

# Testes
npm run test
```

### Hardware
```bash
# Verificar porta do Arduino (macOS/Linux)
ls /dev/tty.*

# Verificar porta do Arduino (Windows)
# Abrir Gerenciador de Dispositivos → Portas COM

# Upload do firmware via Arduino IDE
# Abrir hardware/sereno.ino → selecionar porta → Upload
```

### Variáveis de ambiente necessárias (`.env`)
```env
GEMINI_API_KEY=AIza...
DATABASE_URL=sqlite:///./sereno.db
ARDUINO_PORT=COM3           # Ajustar para a porta real
```

---

## Fases de Desenvolvimento

### Fase 1 — Fundação (MVP funcional)
Objetivo: app funcional sem IA, demonstrável e instalável como PWA.

- [ ] Setup: FastAPI + SQLite + React + Vite + Tailwind
- [ ] Bateria Social: slider manual com feedback visual (cor + ícone por faixa)
- [ ] Scripts Sociais: lista estática (fallback), copiar para clipboard, TTS (`pt-BR`)
- [ ] Dark / Light Mode com persistência em `localStorage`
- [ ] Layout responsivo: mobile-first, grid 2 colunas em ≥768px
- [ ] PWA básico: manifest + service worker com cache estático

### Fase 2 — Inteligência Artificial
Objetivo: Gemini integrado nas três funções principais.

- [ ] Cálculo automático da bateria a partir de texto livre (`/api/bateria/calcular`)
- [ ] Chat com assistente de texto (`/api/ia`) — perfil Sereno AI
- [ ] Tradutor Social: suavização de frases (`/api/suavizar`)
- [ ] Tradutor dispara atualização automática do nível de bateria
- [ ] Tratamento de erro amigável quando `GEMINI_API_KEY` está ausente

### Fase 3 — Regulação Sensorial
Objetivo: ferramentas de calma funcionando com qualidade.

- [ ] Respiração Guiada: animação CSS + alternância Inspire/Expire (8s)
- [ ] Ruído Marrom: Web Audio API, play/pause, volume 0.5
- [ ] Modo Baixa Estimulação: troca de `accent` color para neutro (`#9CA3AF`)
- [ ] Ativação automática do Modo Baixa Estimulação quando bateria < 20%
- [ ] Histórico de bateria persistido no banco + endpoint `GET /api/battery/history`

### Fase 4 — Recursos Avançados de IA e Dados
Objetivo: inteligência preditiva e entrada multimodal.

- [ ] Análise de imagens no chat (multimodal Gemini)
- [ ] Algoritmo MMQ: previsão de sobrecarga sobre os últimos 5 registros
- [ ] Alerta "Sobrecarga Iminente" com animação `shake` (desaparece em 3s)
- [ ] Monitoramento de áudio real via microfone (`getUserMedia`) — substituir simulação
- [ ] Gráfico de histórico da bateria (tendência ao longo do tempo)
- [ ] CRUD completo de scripts (adicionar e remover scripts personalizados)

### Fase 5 — Hardware e Automação
Objetivo: integração física e automações externas.

- [ ] `hardware.py`: encapsular conexão Arduino com fallback virtual
- [ ] Endpoint `POST /api/motor` liga/desliga motor de passo (28BYJ-48)
- [ ] Modo Baixa Estimulação aciona motor automaticamente
- [ ] Webhook Make.com: dispara ao atualizar bateria, exibe conselho retornado
- [ ] Porta do Arduino configurável via variável de ambiente `ARDUINO_PORT`

### Fase 6 — Produção e Polimento
Objetivo: app pronto para uso contínuo e distribuição.

- [ ] Service Worker completo: cache estratégico de todos os assets e respostas da API
- [ ] Funcionalidade "Limpar Dados Locais" (zera banco + `localStorage`)
- [ ] Autenticação JWT (para versão multi-dispositivo futura)
- [ ] Testes automatizados: Pytest (backend) + Vitest/Playwright (frontend)
- [ ] Documentação Swagger exposta em `/docs` (gerada pelo FastAPI)
- [ ] Host/porta configuráveis para rodar em Raspberry Pi com Arduino permanente

---

## Convenções de Código

### Python (Backend)

```python
# Rotas: sempre retornar schema Pydantic, nunca dict puro
@app.post("/api/battery", response_model=BatteryResponse)
async def log_battery(payload: BatteryRequest, session: Session = Depends(get_session)):
    ...

# Serviços: funções síncronas para Gemini (SDK não é async), async para I/O de rede
def calcular_bateria_social_gpt(texto: str) -> int:
    ...

# Modelos: separar tabelas (SQLModel table=True) de schemas de request/response (BaseModel)
class SocialBattery(SQLModel, table=True): ...   # tabela
class BatteryRequest(BaseModel): ...             # schema de entrada
class BatteryResponse(BaseModel): ...            # schema de saída
```

- **Estilo:** PEP 8, type hints em todas as assinaturas, `Optional[X]` para nullable
- **Nomenclatura:** `snake_case` para variáveis, funções e arquivos
- **Classes:** `PascalCase`
- **Constantes:** `UPPER_SNAKE_CASE`
- **Sem comentários** explicando *o quê* — apenas o *porquê* quando não óbvio
- Variável global `historico_usuario` em `main.py` deve ser migrada para o banco na fase 4

### JavaScript / React (Frontend)

```jsx
// Componentes: sempre funcionais com hooks
export function SocialBattery({ level, onChange }) { ... }

// Hooks customizados: extrair lógica de estado e efeitos colaterais
export function useBattery() {
  const [level, setLevel] = useState(50)
  // ...
  return { level, setLevel, history }
}

// Chamadas à API: centralizar em um módulo api.js
export const api = {
  updateBattery: (level) => fetch('/api/battery', { method: 'POST', ... }),
  calculateBattery: (texto) => fetch('/api/bateria/calcular', ...),
}
```

- **Nomenclatura:** `camelCase` para variáveis e funções, `PascalCase` para componentes
- **Arquivos de componente:** `PascalCase.jsx`
- **Hooks customizados:** prefixo `use`, arquivo em `hooks/`
- Sem `class` components
- Props obrigatórias sem `defaultProps` — deixar o erro aparecer cedo

### CSS / Tailwind

- Usar variáveis CSS (`--accent`, `--bg`, `--text`) para temas — já definidas em `styles.css`
- Em Tailwind: preferir utilitários a classes customizadas; criar componente quando o conjunto se repete 3+ vezes
- Dark mode via `class` strategy (`dark:` prefix) — não `media query`
- Animações em `@keyframes` nomeadas descritivamente: `breathe`, `shake`, `textFade`

### API

- Rotas no padrão REST: substantivos no plural, verbos HTTP corretos
- Respostas de erro com shape consistente: `{ "detail": "mensagem de erro" }`
- `POST /api/motor` deve aceitar `{ "estado": "1" | "0" }` — nunca boolean (compatibilidade com Arduino serial)
- CORS configurado com `allow_origins=["*"]` apenas em desenvolvimento; restringir em produção

### Git

- Commits em português, imperativo: `"Adiciona cálculo MMQ"`, `"Corrige fallback Arduino"`
- Branches por fase: `fase-1/fundacao`, `fase-2/ia`, `fase-3/sensorial`, etc.
- Nunca versionar: `sereno.db`, `.env`, `__pycache__/`, `node_modules/`, `dist/`

---

## Decisões de Arquitetura

**Por que FastAPI e não Next.js full-stack?**
O backend precisa do PySerial rodando localmente para comunicar com o Arduino via USB. FastAPI como servidor local + React como SPA servida por ele é a arquitetura mais simples para esse caso.

**Por que SQLite e não PostgreSQL?**
O Sereno é um app pessoal e local-first. SQLite sem servidor elimina uma dependência de infraestrutura e funciona offline. Migrar para PostgreSQL seria relevante apenas se o app tiver múltiplos usuários em dispositivos diferentes.

**Por que o histórico MMQ está em memória (`historico_usuario` global)?**
Decisão temporária de prototipagem. Na Fase 4, mover para consulta direta em `SocialBattery` — os últimos 5 registros já estão persistidos no banco.

**Por que Make.com e não lógica local para conselhos?**
O webhook permite que conselhos sejam modificados sem deploy de código. O tradeoff é latência (1500ms delay) e dependência de serviço externo. Alternativa futura: mover lógica de conselho para um prompt dedicado no Gemini.
