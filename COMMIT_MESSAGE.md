# Commit v2.1.0

Luciano - feat(v2.1): integração Open Finance + reorganização da documentação

## Resumo

Adiciona integração com Pluggy Open Finance e reestrutura completamente a documentação do projeto em categorias temáticas.

## Features

### Open Finance

- REST API Pluggy implementada
- Conta Mercado Pago conectada (saldo + transações)
- Sandbox Nubank configurado
- Segurança OAuth2 + read-only access
- Conformidade LGPD documentada

### Reorganização Documentação

- 3 categorias: Desenvolvimento (8 docs), Integração (4 docs), Testing (4 docs)
- 21 documentos organizados com padrão XXX_NOME.md
- 9 novos documentos criados (READMEs + guias técnicos)
- 12 documentos renumerados e categorizados

### Estrutura

- `/config/` - Configurações centralizadas
- `/docs/{categoria}/` - Documentação organizada
- READMEs de navegação em cada categoria
- `Integracao_PROXIMO_CHAT.md` - Contexto rápido para IA

## Arquivos

**Novos (9):**

- config/README.md
- docs/README.md + Integracao_PROXIMO_CHAT.md
- docs/{Desenvolvimento,Integracao,Testing}/README.md
- docs/Desenvolvimento/007_REORGANIZACAO_COMPLETA.md
- docs/Desenvolvimento/008_COMMIT_V2.0.2_CICLO_19-18.md
- docs/Integracao/003_ARQUITETURA_PLUGGY.md
- docs/Integracao/004_SEGURANCA_OPENFINANCE.md

**Modificados:**

- README.md - v2.1, badges Open Finance, roadmap com Mobile (v2.3)
- CHANGELOG.md - entrada v2.1.0 completa
- 12 docs movidos para categorias temáticas

## Breaking Changes

- Docs movidos: `docs/*.md` → `docs/{categoria}/XXX_*.md`
- Config movido: `backend/src/config.ini` → `config/config.ini`
- Links atualizados no README

## Documentação

Ver detalhes em:

- CHANGELOG.md [2.1.0]
- docs/Integracao_PROXIMO_CHAT.md
- docs/Desenvolvimento/007_REORGANIZACAO_COMPLETA.md
- docs/Desenvolvimento/008_COMMIT_V2.0.2_CICLO_19-18.md (bugfix anterior)

---

v2.1.0 | 2025-01-27 | Luciano

**Relates to:** Ciclo mensal 19-18
**Version:** v2.0.2-dev
**Date:** 2025-10-28

```

```
