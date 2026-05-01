Gere ou atualize a documentação para o arquivo, endpoint ou módulo indicado.

Leia o código relevante e o CLAUDE.md antes de escrever qualquer coisa.

Regras para esta documentação:
- Escreva em português
- Explique o PORQUÊ, não o quê (o código já diz o quê)
- Não documente o óbvio
- Máximo de 1 linha de comentário inline por bloco não óbvio

Dependendo do alvo, produza o formato adequado:

**Para um endpoint da API:**
- Descrição do que o endpoint faz e quando deve ser chamado
- Parâmetros de entrada (com tipos e restrições)
- Formato da resposta de sucesso
- Possíveis erros e o que causam
- Exemplo de request/response em JSON

**Para um módulo Python (services.py, etc.):**
- Docstring curta na função (máximo 2 linhas) explicando o propósito não-óbvio
- Documentação das decisões de design relevantes (ex: por que regex e não JSON parse na resposta do Gemini)
- Dependências externas e como falham

**Para um componente React:**
- Props com tipos e descrição de cada uma
- Comportamentos de estado não óbvios
- Efeitos colaterais (chamadas à API, localStorage, Web Audio)

**Para atualizar o ESPECIFICACOES.md:**
- Identifique seções desatualizadas comparando com o código atual
- Atualize apenas o que mudou — não reescreva o documento inteiro

Não adicione comentários explicando o que o código faz linha a linha. Isso não é documentação útil.
