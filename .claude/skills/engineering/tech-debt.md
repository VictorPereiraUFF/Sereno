Faça um levantamento de dívida técnica no projeto ou no arquivo indicado.

Leia o código relevante e o CLAUDE.md, depois liste os itens encontrados agrupados por categoria:

**Categoria A — Dívida estrutural** (impacta evolução do código)
- Ex: variável global `historico_usuario` em main.py que deveria estar no banco
- Ex: ausência de separação backend/frontend ainda em estrutura flat

**Categoria B — Dívida de qualidade** (impacta manutenção)
- Ex: rotas sem schema de resposta tipado (retornam dict puro)
- Ex: sem tratamento de erro padronizado

**Categoria C — Dívida de segurança** (impacta produção)
- Ex: CORS com `allow_origins=["*"]`
- Ex: sem validação de range em `level` (aceita -999 ou 500)

**Categoria D — Dívida de testes** (impacta confiabilidade)
- Ex: zero cobertura de testes atualmente

Para cada item, indique:
- **Localização:** arquivo:linha
- **Impacto:** o que pode quebrar ou dificultar se não for resolvido
- **Esforço estimado:** pequeno (< 1h) / médio (meio dia) / grande (1+ dias)
- **Fase do roadmap em que deve ser resolvido** (conforme CLAUDE.md)

Finalize com uma lista priorizada dos 3 itens mais urgentes.
