Gere um checklist de pré-deploy para a mudança ou fase indicada.

Leia o diff atual (ou o escopo informado) e o CLAUDE.md, depois produza um checklist organizado por categoria.

**Backend**
- [ ] Todas as rotas novas têm schema de resposta (`response_model=`)
- [ ] Variáveis de ambiente necessárias estão documentadas no CLAUDE.md
- [ ] Migrações de banco de dados foram aplicadas (se modelos mudaram)
- [ ] Endpoints com hardware têm fallback virtual funcionando
- [ ] CORS restrito ao origin correto (não `"*"` em produção)

**Frontend**
- [ ] Build de produção passa sem erros (`npm run build`)
- [ ] Dark mode e light mode testados
- [ ] Layout responsivo testado em mobile (375px) e desktop (1280px)
- [ ] Modo baixa estimulação testado com bateria < 20%

**IA e Integrações**
- [ ] `GEMINI_API_KEY` configurada no ambiente de destino
- [ ] Tratamento de erro testado com chave ausente ou API indisponível
- [ ] Webhook Make.com testado com payload real

**Hardware (se aplicável)**
- [ ] `ARDUINO_PORT` configurada corretamente
- [ ] Fallback virtual verificado com Arduino desconectado
- [ ] Motor testado manualmente (liga e desliga via `/api/motor`)

**Qualidade**
- [ ] Nenhum `console.log` ou `print()` de debug esquecido
- [ ] Nenhum `TODO` bloqueante no escopo desta entrega
- [ ] Testes relevantes passando

**PWA (se assets mudaram)**
- [ ] `sw.js` atualizado com novos arquivos no cache
- [ ] Manifest e ícones corretos

Para cada item marcado como ❌ ou em dúvida, explique o risco de não resolver antes do deploy.
