Defina uma estratégia de testes para o arquivo, módulo ou funcionalidade indicada.

Leia o código relevante primeiro, depois produza:

1. **O que precisa ser testado** — liste as unidades de comportamento testáveis (não os arquivos, mas os comportamentos: "quando bateria < 20%, deve ativar modo baixa estimulação")

2. **Pirâmide de testes recomendada** para este módulo:
   - Unitários: o quê testar isoladamente e com quê (pytest / vitest)
   - Integração: quais fluxos end-to-end precisam de cobertura real (ex: FastAPI + SQLite sem mock)
   - E2E / manual: o que só pode ser verificado no browser ou com hardware

3. **Casos críticos** — os 3–5 cenários que, se quebrar, causam impacto real ao usuário (ex: Gemini indisponível, Arduino desconectado, bateria cai para 0)

4. **O que NÃO testar** — dependências externas que devem ser mockadas (Gemini API, Make.com webhook) e por quê

5. **Exemplo de teste** — escreva 1 teste concreto e bem nomeado para o caso mais crítico identificado, seguindo as convenções do projeto

Seja específico ao projeto Sereno. Não gere estratégias genéricas.
