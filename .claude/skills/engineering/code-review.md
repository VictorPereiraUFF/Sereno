Faça uma revisão de código completa do arquivo ou módulo indicado (ou do diff atual se nenhum arquivo for especificado).

Avalie os seguintes pontos, nesta ordem:

1. **Correção** — O código faz o que deveria? Há bugs óbvios, edge cases não tratados, ou comportamento inesperado?
2. **Segurança** — Há riscos de injeção, dados expostos, CORS aberto demais, ou validação ausente em entradas externas?
3. **Qualidade** — O código é legível? Há duplicação desnecessária, abstrações prematuras, ou lógica que poderia ser simplificada?
4. **Convenções do projeto** — O código segue as convenções definidas no CLAUDE.md? (snake_case Python, camelCase JS, sem comentários de "o quê", type hints nas assinaturas Python, etc.)
5. **Performance** — Há N+1 queries, loops desnecessários, ou chamadas síncronas onde poderiam ser assíncronas?

Para cada problema encontrado, indique:
- **Localização:** arquivo e linha
- **Severidade:** crítico / importante / sugestão
- **O problema:** o que está errado e por quê
- **A correção:** o que fazer (código concreto quando relevante)

Se não houver problemas em uma categoria, diga explicitamente que está ok — não omita categorias.
Finalize com um resumo em uma linha: se o código está pronto para merge ou precisa de ajustes.
