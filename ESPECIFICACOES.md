# Sereno AI — Especificações de Funcionalidades

**Versão do documento:** 1.1  
**Data:** 2026-04-26  
**Stack principal:** Python FastAPI · JavaScript Vanilla · Arduino · Google Gemini API · SQLite

---

## Visão Geral

O **Sereno** é um assistente de regulação sensorial e acessibilidade voltado para pessoas neurodivergentes (com foco em autismo). Combina inteligência artificial, feedback tátil via hardware e ferramentas de regulação sensorial para ajudar o usuário a monitorar e gerenciar sua energia social no dia a dia.

---

## Casos de Uso

### UC-01 — Monitorar energia antes de um evento social

**Ator:** Usuário neurodivergente  
**Contexto:** O usuário tem uma reunião, encontro ou compromisso social em breve e quer avaliar se tem energia suficiente para participar.

**Fluxo principal:**
1. O usuário abre o Sereno e descreve como está se sentindo no campo de texto da Bateria Social.
2. A IA analisa o texto e estima um nível de 0 a 100%.
3. O sistema exibe a cor correspondente (verde / laranja / vermelho) e um conselho personalizado via Make.com.
4. Se o nível estiver abaixo de 20%, o app sugere ativar o Modo Baixa Estimulação.
5. O usuário decide participar, adiar ou recusar o compromisso com base na leitura.

**Resultado esperado:** O usuário toma uma decisão informada sobre sua participação, sem depender apenas de intuição.

---

### UC-02 — Recuperar energia após sobrecarga sensorial

**Ator:** Usuário em estado de sobrecarga (meltdown ou shutdown iminente)  
**Contexto:** O usuário acabou de passar por uma situação muito estimulante (ambiente barulhento, reunião longa, interação social intensa) e precisa se regular.

**Fluxo principal:**
1. O usuário abre o Sereno e move o slider da Bateria Social para um nível baixo (ou usa a descrição em texto).
2. O app detecta nível crítico e ativa automaticamente o Modo Baixa Estimulação (cores neutras, sem animações).
3. O usuário acessa a seção de Regulação Sensorial e inicia a Respiração Guiada.
4. Paralelamente, ativa o Ruído Marrom para abafar estímulos sonoros externos.
5. Se o Arduino estiver conectado, o motor de passo inicia vibração tátil suave.
6. Após alguns minutos, o usuário atualiza o slider para refletir a melhora.

**Resultado esperado:** O usuário encontra calma guiada em menos de 5 minutos, sem precisar explicar o que está sentindo para ninguém.

---

### UC-03 — Recusar um convite sem criar conflito social

**Ator:** Usuário que precisa declinar um compromisso  
**Contexto:** O usuário recebe um convite (mensagem, e-mail, presencialmente) e quer recusar de forma educada, mas não sabe como formular a resposta sem soar indelicado.

**Fluxo principal:**
1. O usuário acessa o Tradutor Social e digita a frase que escreveria naturalmente (ex: *"Não posso, tô cansado."*).
2. A IA reescreve a frase em tom empático e socialmente adequado (ex: *"Infelizmente não poderei comparecer desta vez, pois preciso recarregar minhas energias."*).
3. O usuário copia o texto e envia pelo canal desejado (WhatsApp, e-mail, etc.).
4. O sistema registra a interação e atualiza automaticamente o nível de bateria com base no texto original.

**Resultado esperado:** O usuário comunica sua necessidade de forma clara e socialmente aceita, sem desgaste emocional adicional.

---

### UC-04 — Sair de uma situação desconfortável rapidamente

**Ator:** Usuário em situação social que excedeu seu limite  
**Contexto:** O usuário está num evento, reunião ou conversa e precisa se retirar imediatamente, mas tem dificuldade de formular palavras sob pressão.

**Fluxo principal:**
1. O usuário abre o Sereno discretamente no celular.
2. Acessa os Scripts Sociais Rápidos e seleciona a frase adequada (ex: *"Não estou me sentindo bem, preciso sair."*).
3. Toca no botão de voz para ouvir a frase sendo lida em voz alta, ou copia para enviar por mensagem.
4. Usa a frase para se comunicar e se retira do ambiente.

**Resultado esperado:** O usuário consegue se retirar com dignidade, sem precisar improvisar comunicação sob estresse.

---

### UC-05 — Identificar gatilhos sensoriais num ambiente

**Ator:** Usuário prestes a entrar em um ambiente desconhecido  
**Contexto:** O usuário vai a um lugar novo (restaurante, escritório, evento) e quer saber antecipadamente se o ambiente pode ser sensorialmente intenso.

**Fluxo principal:**
1. O usuário tira uma foto do ambiente com o celular.
2. Acessa o Assistente Multimodal e envia a imagem com ou sem texto descritivo.
3. A IA analisa a imagem em busca de gatilhos sensoriais: iluminação intensa, padrões visuais perturbadores, aglomeração, desorganização.
4. O assistente retorna uma avaliação com os riscos identificados e sugestões de adaptação (ex: *"Ambiente com iluminação fluorescente intensa — considere usar óculos escuros ou se sentar de costas para as lâmpadas."*).

**Resultado esperado:** O usuário entra no ambiente com estratégias preparadas, reduzindo a chance de sobrecarga inesperada.

---

### UC-06 — Acompanhar a tendência da bateria ao longo do dia

**Ator:** Usuário que quer entender seus padrões de energia  
**Contexto:** O usuário registra sua bateria múltiplas vezes ao dia e quer saber se está em queda consistente antes de atingir o limite.

**Fluxo principal:**
1. O usuário atualiza sua bateria social 3 ou mais vezes ao longo do dia (manhã, almoço, tarde).
2. O sistema aplica o algoritmo MMQ sobre os registros e detecta a tendência de queda.
3. Se a queda for maior que 5% por interação, o ícone da bateria começa a tremer e o alerta "Sobrecarga Iminente" é exibido.
4. O usuário recebe o alerta antes de atingir o limite e toma uma ação preventiva (pausa, saída do ambiente, regulação sensorial).

**Resultado esperado:** O usuário age preventivamente, evitando chegar ao estado de sobrecarga completa.

---

### UC-07 — Criar um script personalizado para situação recorrente

**Ator:** Usuário que enfrenta uma situação social específica com frequência  
**Contexto:** O usuário tem dificuldade recorrente em situações específicas (ex: pedir para baixar o volume, recusar contato físico) e quer ter uma frase pronta para usar sempre que precisar.

**Fluxo principal:**
1. O usuário acessa a seção de Scripts Sociais Rápidos e clica em adicionar novo script.
2. Digita a frase que deseja salvar (ex: *"Prefiro não ser abraçado, mas agradeço o carinho."*).
3. O script é salvo no banco e aparece na lista principal.
4. Nas próximas vezes, o usuário acessa diretamente o script salvo, copia ou ouve em voz alta.

**Resultado esperado:** O usuário constrói ao longo do tempo um repertório de frases personalizado para suas situações mais desafiadoras.

---

## Índice

1. [Bateria Social Inteligente](#1-bateria-social-inteligente)
2. [Assistente Multimodal (Chat com IA)](#2-assistente-multimodal-chat-com-ia)
3. [Tradutor Social](#3-tradutor-social)
4. [Scripts Sociais Rápidos](#4-scripts-sociais-rápidos)
5. [Regulação Sensorial](#5-regulação-sensorial)
6. [Monitoramento de Áudio](#6-monitoramento-de-áudio)
7. [Integração com Hardware (Arduino)](#7-integração-com-hardware-arduino)
8. [Modo Baixa Estimulação](#8-modo-baixa-estimulação)
9. [Tema e Acessibilidade](#9-tema-e-acessibilidade)
10. [Progressive Web App (PWA)](#10-progressive-web-app-pwa)
11. [Gerenciamento de Privacidade](#11-gerenciamento-de-privacidade)
12. [API — Endpoints](#12-api--endpoints)
13. [Modelos de Dados](#13-modelos-de-dados)
14. [Integrações Externas](#14-integrações-externas)
15. [Arquitetura Técnica](#15-arquitetura-técnica)

---

## 1. Bateria Social Inteligente

O módulo central da aplicação. Representa o nível de energia emocional/social do usuário em uma escala de 0 a 100%.

### 1.1 Ajuste Manual
- Slider interativo de 0 a 100% controlado pelo usuário.
- O percentual atual é exibido em tempo real ao lado de um ícone animado.
- A cor do indicador muda dinamicamente conforme o nível:
  - **Verde** (`#4caf50`): acima de 50% — energia adequada.
  - **Laranja** (`#ff9800`): entre 20% e 50% — energia baixa.
  - **Vermelho** (`#f44336`): abaixo de 20% — energia crítica.
- O ícone segue o mesmo esquema: ⚡ (alto) → 🔋 (médio) → 🪫 (baixo) → 💀 (crítico).

### 1.2 Cálculo Automático via IA
- O usuário descreve como está se sentindo em texto livre.
- A IA (Google Gemini) analisa o texto e estima um valor de 0 a 100.
- Retorna também uma breve previsão do estado atual.
- Rota: `POST /api/bateria/calcular`

### 1.3 Previsão de Sobrecarga (Algoritmo MMQ)
- Utiliza o método dos **Mínimos Quadrados** sobre os últimos 5 registros do histórico.
- Se a tendência de queda for maior que **-5% por interação**, um alerta de "Sobrecarga Iminente" é exibido.
- O ícone da bateria entra em animação de tremida (`shake-animation`) para chamar atenção.
- O alerta desaparece automaticamente após 3 segundos.

### 1.4 Conselho Personalizado via Automação
- A cada atualização do nível (manual ou via IA), um webhook é disparado para o Make.com.
- O Make.com retorna um conselho personalizado baseado no nível enviado.
- Exemplo de resposta: *"Tire um momento para relaxar e recarregar suas energias."*
- Há um delay intencional de 1500ms para aguardar a resposta da automação.

---

## 2. Assistente Multimodal (Chat com IA)

Interface de chat que permite conversar com a IA Gemini por texto e/ou imagem.

### 2.1 Entrada de Texto
- Campo de texto livre para o usuário digitar sua mensagem.
- Ao enviar, a mensagem é exibida no histórico e a IA responde.

### 2.2 Entrada de Imagem
- Botão 📷 permite anexar uma imagem (JPEG ou PNG).
- Preview do arquivo é exibido antes do envio.
- **Comportamento específico para imagens:** a IA analisa exclusivamente gatilhos sensoriais visíveis (iluminação intensa, padrões visuais perturbadores, desorganização do ambiente).

### 2.3 Perfil do Assistente
- A IA atua como **"Sereno AI"**, especializado em acessibilidade e regulação sensorial para neurodivergentes.
- Para mensagens de texto, oferece estratégias de calma e sugestões sociais.
- Rota: `POST /api/ia`

### 2.4 Histórico de Conversa
- Mensagens exibidas em tempo real no chat.
- Diferenciação visual: mensagens do usuário (verde, alinhadas à direita) vs. respostas da IA (cinza, alinhadas à esquerda).
- Scroll automático para a mensagem mais recente.

---

## 3. Tradutor Social

Converte frases diretas ou secas em comunicações mais empáticas e socialmente adequadas.

### 3.1 Funcionamento
- O usuário digita uma frase da forma como a escreveria naturalmente.
- A IA reescreve preservando a intenção, mas adaptando o tom para comunicação empática.
- **Exemplo:**
  - Entrada: *"Não vou, estou cansado."*
  - Saída: *"Infelizmente não poderei estar presente hoje, pois preciso recarregar minhas energias."*

### 3.2 Perfil da IA
- Especialista em etiqueta comunicativa brasileira.
- Foco em neurodiversidade: valida necessidades sem criar constrangimento social.
- Rota: `POST /api/suavizar`

### 3.3 Integração com Bateria
- Ao traduzir uma frase, o sistema automaticamente também calcula o nível de bateria a partir do texto original, atualizando o indicador principal.

---

## 4. Scripts Sociais Rápidos

Banco de frases pré-prontas para situações socialmente desafiadoras.

### 4.1 Frases Padrão (Fallback)
Quando nenhum script está cadastrado no banco, exibe frases de fallback:
- *"Preciso de um minuto para processar isso."*
- *"O ambiente está muito barulhento para mim."*
- *"Prefiro continuar essa conversa por texto."*
- *"Não estou me sentindo bem, preciso sair."*

### 4.2 Gerenciamento
- Listagem dos scripts via `GET /scripts`.
- Adição de novo script personalizado via `POST /scripts` com o campo `message`.

### 4.3 Interação com Scripts
- **Copiar para clipboard:** copia a frase com um clique.
- **Texto-para-fala:** lê a frase em voz alta usando a Web Speech Synthesis API (idioma: `pt-BR`).

---

## 5. Regulação Sensorial

Ferramentas para ajudar o usuário a se autorregular em momentos de sobrecarga sensorial.

### 5.1 Respiração Guiada
- Animação CSS de um círculo que "respira" (escala de 1× a 1,8× em 8 segundos).
- Texto alternado sincronizado com a animação: *"Inspire..."* / *"Expire..."*.
- Cor de calma: verde água (`#71D1B3`).

### 5.2 Ruído Marrom
- Gerador de ruído marrom via **Web Audio API** (filtro passa-baixa sobre ruído branco).
- Ruído marrom reduz picos de frequência e diminui a estimulação auditiva.
- Botão de play/pause (▶️ / ⏹️).
- Volume fixo em 0,5 (50%).

---

## 6. Monitoramento de Áudio

Simulação de detecção de ruído ambiente para alertar sobre ambientes sensorialmente intensos.

### 6.1 Microfone Toggle
- Botão ativa/desativa o monitoramento.
- O nível de ruído é simulado com variação aleatória (0–100%).
- Barra de progresso visual (medidor horizontal) atualizada a cada 800ms.

### 6.2 Alerta de Ruído Alto
- Se o nível simulado ultrapassar **85%**, o evento é registrado.
- O contador de alertas é incrementado e exibido na interface.
- O evento é enviado para o backend via `POST /events` com `{ type: "som_alto", value }`.

---

## 7. Integração com Hardware (Arduino)

Feedback tátil físico via motor de passo acoplado ao Arduino.

### 7.1 Hardware
- **Microcontrolador:** Arduino (porta `COM3`, 9600 baud).
- **Motor:** Stepper 28BYJ-48 (2048 passos/revolução, 10 RPM).
- **Driver:** ULN2003AN (pinos 8, 10, 9, 11).
- **Comunicação:** Serial USB via PySerial.

### 7.2 Comportamento do Motor
- **Ligar (`'1'`):** motor executa 100 passos por ciclo de forma contínua e suave.
- **Desligar (`'0'`):** motor para completamente.
- Rota de controle: `POST /api/motor` com `{ estado: "1" | "0" }`.

### 7.3 Modo Virtual (Fallback)
- Se o Arduino não estiver conectado, o sistema continua funcionando normalmente em modo virtual.
- A interface não quebra na ausência do hardware.

---

## 8. Modo Baixa Estimulação

Reduz a carga sensorial visual da interface para momentos de sobrecarga.

### 8.1 Ativação
- Botão dedicado na seção de Monitoramento.
- Ativação automática sugerida quando a bateria cai abaixo de 20% (com confirmação do usuário).

### 8.2 Efeitos Visuais
- A cor de destaque (`accent`) da interface é substituída por cinza neutro (`#9CA3AF`).
- Remove animações e elementos visuais de alta saturação.

### 8.3 Integração Hardware
- Ao ativar, envia sinal para o Arduino ligar o motor tátil (`estado: "1"`).
- Ao desativar, envia sinal para desligar (`estado: "0"`).

---

## 9. Tema e Acessibilidade

### 9.1 Alternância de Tema
- Botão no header alterna entre modo claro e escuro (ícones 🌙 / ☀️).
- A preferência é salva em `localStorage` com a chave `sereno_theme`.

### 9.2 Modo Claro
- Fundo: `#F6F8FA` (cinza muito claro).
- Texto: escuro (alto contraste).
- Cor de destaque: verde água (`#71D1B3`).

### 9.3 Modo Escuro
- Fundo: `#121212` (preto).
- Texto: claro.
- Cor de destaque: verde água (`#71D1B3`).

### 9.4 Layout Responsivo
- Design mobile-first.
- Em telas maiores que 768px, o layout usa grid de 2 colunas (2fr + 1fr).
- Em mobile, todos os cards empilham em coluna única.

### 9.5 Animações
| Nome | Duração | Descrição |
|------|---------|-----------|
| `breathe` | 8s (loop) | Expansão/contração do círculo de respiração |
| `shake` | 0,5s (loop) | Tremida do ícone em alerta de sobrecarga |
| `textFade` | 8s (loop) | Alternância entre "Inspire..." e "Expire..." |

---

## 10. Progressive Web App (PWA)

O Sereno pode ser instalado como aplicativo nativo em dispositivos móveis.

### 10.1 Manifest
- **Nome:** Sereno AI
- **Nome curto:** Sereno
- **Modo de exibição:** standalone (sem barra do navegador)
- **Cor do tema:** `#71D1B3` (verde água)
- **Ícones:** 192×192px e 512×512px

### 10.2 Service Worker
- Estratégia: **Cache First → Network Fallback**.
- Arquivos em cache: `/`, `/index.html`, `/styles.css`.
- Nome do cache: `sereno-app-v1`.
- Permite uso básico mesmo sem conexão com a internet.

---

## 11. Gerenciamento de Privacidade

### 11.1 Armazenamento
- Todos os dados são armazenados **localmente** no arquivo `sereno.db` (SQLite).
- Nenhum dado pessoal é enviado a servidores externos, exceto:
  - Textos enviados à API do Google Gemini para processamento.
  - Nível de bateria enviado ao webhook do Make.com.

### 11.2 Limpeza de Dados
- Botão "Limpar Dados Locais" disponível na seção de privacidade (funcionalidade futura).

### 11.3 Disclaimer
- Rodapé exibe: *"O Sereno não substitui terapia convencional."*

---

## 12. API — Endpoints

| Método | Rota | Payload | Descrição |
|--------|------|---------|-----------|
| `GET` | `/` | — | Status do servidor, banco de dados e Arduino |
| `POST` | `/api/ia` | `{ texto, imagem? }` | Chat multimodal com Gemini |
| `POST` | `/api/suavizar` | `{ texto }` | Tradutor social (reescrita empática) |
| `POST` | `/api/bateria/calcular` | `{ texto }` | Estimativa de bateria via IA + previsão MMQ |
| `POST` | `/api/battery` | `{ level: int }` | Registra nível de bateria manualmente |
| `GET` | `/api/battery/history` | — | Retorna os últimos 10 registros de bateria |
| `GET` | `/scripts` | — | Lista scripts sociais cadastrados |
| `POST` | `/scripts` | `{ message: str }` | Adiciona novo script social |
| `POST` | `/events` | `{ type, value }` | Registra evento (ex: som_alto) |
| `POST` | `/api/motor` | `{ estado: "0"\|"1" }` | Liga/desliga motor Arduino |

---

## 13. Modelos de Dados

### `SocialBattery`
Histórico de registros de bateria social.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int (PK) | Identificador único |
| `level` | int | Nível de 0 a 100 |
| `timestamp` | datetime | Data/hora do registro (padrão: agora) |

### `Script`
Scripts sociais pré-prontos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int (PK) | Identificador único |
| `owner_id` | int (FK, nullable) | Referência ao usuário dono |
| `message` | str | Texto do script |

### `User`
Usuários do sistema (disponível para autenticação futura).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int (PK) | Identificador único |
| `email` | str (unique) | E-mail do usuário |
| `hashed_password` | str | Senha com hash |
| `created_at` | datetime | Data de criação |

---

## 14. Integrações Externas

### 14.1 Google Gemini API
- **Modelo:** `gemini-2.5-flash`
- **Chave:** variável de ambiente `GEMINI_API_KEY`
- **Usos:**
  1. Chat geral e análise de imagens (`gerar_resposta_gpt`)
  2. Reescrita empática de textos (`suavizar_texto_gpt`)
  3. Estimativa de nível de bateria social (`calcular_bateria_social_gpt`)
- **Tratamento de erros:** retorna mensagem amigável em caso de falha ou chave ausente.

### 14.2 Make.com Webhook
- **Trigger:** toda atualização do nível de bateria (manual ou via IA).
- **Payload enviado:** `{ nivel: int }`
- **Resposta esperada:** `{ conselho: string }`
- **Delay:** 1500ms para aguardar resposta da automação.

### 14.3 Arduino (Serial USB)
- **Porta:** `COM3` (padrão)
- **Baud rate:** 9600
- **Biblioteca:** PySerial
- **Comandos:**
  - `b'1'` → liga o motor de passo
  - `b'0'` → desliga o motor de passo

---

## 15. Arquitetura Técnica

### 15.1 Backend
- **Framework:** FastAPI (Python)
- **Servidor:** Uvicorn (ASGI)
- **ORM:** SQLModel (Pydantic + SQLAlchemy)
- **Banco de dados:** SQLite (`sereno.db`)
- **IA:** Google Generative AI SDK
- **Hardware:** PySerial

### 15.2 Frontend
- **Markup:** HTML5 semântico
- **Estilo:** CSS3 com variáveis customizadas, animações e media queries
- **Lógica:** JavaScript Vanilla (sem frameworks)
- **APIs Web:** Fetch API, Web Audio API, Web Speech Synthesis API, Clipboard API

### 15.3 Hardware
- **Microcontrolador:** Arduino Uno/Nano
- **Motor:** Stepper 28BYJ-48
- **Driver:** ULN2003AN
- **Linguagem:** C++ (Arduino IDE, arquivo `sereno.ino`)

### 15.4 Configuração de Ambiente
```
GEMINI_API_KEY=<chave_do_google_cloud>
DATABASE_URL=sqlite:///./sereno.db   # opcional
```

### 15.5 Instalação e Execução
```bash
# Instalar dependências Python
pip install fastapi uvicorn sqlmodel pyserial google-generativeai python-dotenv

# Criar arquivo .env com GEMINI_API_KEY

# Iniciar servidor
uvicorn main:app --reload
```
A interface é servida diretamente pelo FastAPI e acessível em `http://localhost:8000`.

---

*Documento gerado automaticamente a partir do código-fonte do projeto Sereno.*
