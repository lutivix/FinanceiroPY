# 🗄️ Scripts Deprecated (Obsoletos)

> Arquivos que não funcionam mais ou foram substituídos por versões melhores.

---

## ⚠️ NÃO USAR ESTES ARQUIVOS

Estes scripts estão aqui apenas para referência histórica. **Não devem ser executados.**

---

## 📂 Conteúdo

### **Scripts SDK Pluggy (NÃO FUNCIONAM)** ❌

| Arquivo                  | Motivo                          | Substituído por                                     |
| ------------------------ | ------------------------------- | --------------------------------------------------- |
| `teste_pluggy.py`        | Usa SDK com bug de autenticação | `../../scripts/testes/teste_pluggy_rest.py`         |
| `teste_pluggy_rapido.py` | Usa SDK com bug de autenticação | `../../scripts/testes/verificar_dados_completos.py` |
| `testar_item_pluggy.py`  | Usa SDK com bug de autenticação | `../../scripts/testes/teste_pluggy_rest.py`         |
| `criar_item_pluggy.py`   | Usa SDK com bug de autenticação | Dashboard Pluggy (manual)                           |
| `teste_pluggy.bat`       | Chama script SDK obsoleto       | N/A                                                 |

**Problema:** SDK `pluggy-sdk` envia header `Authorization: Bearer {key}` em vez de `X-API-KEY: {key}`, causando erro 403.

**Solução:** Usar REST API direta com biblioteca `requests`.

### **Scripts de Fetch Obsoletos** 📊

| Arquivo                     | Motivo                                   | Substituído por                        |
| --------------------------- | ---------------------------------------- | -------------------------------------- |
| `listar_transacoes_itau.py` | Versão inicial com problemas de encoding | `buscar_itau_simples.py` (em produção) |

**Problema:** Emojis no console causavam erros no bash do Windows.

**Solução:** Versão `_simples` sem emojis.

### **HTML Prototypes (NÃO FUNCIONAM)** 🌐

| Arquivo                      | Motivo                 | Substituído por                            |
| ---------------------------- | ---------------------- | ------------------------------------------ |
| `pluggy_connect.html`        | Widget CDN não carrega | Dashboard Pluggy (manual)                  |
| `pluggy_dashboard_help.html` | Guia desatualizado     | `docs/Integracao/001_INTEGRACAO_PLUGGY.md` |

**Problema:** PluggyConnect Widget não funciona fora de trial. CDN não carrega.

**Solução:** Conectar contas via Dashboard Pluggy e usar REST API.

---

## 🔍 Por Que Manter?

Mantemos estes arquivos em vez de deletar por:

1. **Referência histórica** - Entender o que foi tentado
2. **Aprendizado** - Documentar erros para não repetir
3. **Comparação** - Ver evolução SDK → REST API
4. **Segurança** - Não deletar sem certeza absoluta

---

## ⏰ Quando Deletar

Estes arquivos podem ser **deletados com segurança** se:

- ✅ Soluções atuais estão funcionando por 3+ meses
- ✅ Nenhuma referência em código ativo
- ✅ Documentação completa das decisões técnicas
- ✅ Backup em commits Git (histórico preservado)

**Status atual:** Manter por enquanto (v2.2.0 - Nov/2025)

---

## 📋 Checklist para Cleanup Futuro

- [ ] 3 meses sem usar SDK (desde 10/11/2025)
- [ ] Confirmar REST API 100% estável
- [ ] Verificar sem referências no código
- [ ] Commit final antes de deletar
- [ ] Deletar pasta `_deprecated/` completa

**Data para revisão:** 10/02/2026

---

## 🔗 Links Relacionados

- [📜 scripts/README.md](../../../scripts/README.md) - Scripts ativos
- [📚 docs/Integracao/](../../../docs/Integracao/) - Documentação Open Finance
- [🔧 backend/src/](../) - Scripts de produção

---

**Criado em:** 11/11/2025  
**Motivo:** Organização v2.2.0 - Limpeza de scripts obsoletos
