# Bug Fix - Duplicatas de Compras Parceladas

**Data:** 03/02/2026  
**Severidade:** Alta  
**Status:** ✅ Corrigido

---

## 📋 Descrição do Problema

O sistema estava descartando incorretamente compras parceladas de cartões de crédito como duplicatas. 

### Exemplo do Bug:
- **Janeiro**: "Mlp *kabum -kab08/10" (parcela 8 de 10) → ✅ Processada
- **Fevereiro**: "Mlp *kabum -kab09/10" (parcela 9 de 10) → ❌ Descartada como duplicata

### Causa Raiz:
O sistema estava normalizando descrições em dois lugares diferentes com lógicas conflitantes:

1. **Ao salvar (processadores)**: 
   - ❌ Normalizava E salvava a descrição normalizada
   - Perdia informação de parcelas de cartão

2. **Ao verificar duplicatas (repository)**:
   - ❌ Normalizava ambas as descrições para comparar
   - "Kabum 08/10" e "Kabum 09/10" viravam "KABUM" → falsa duplicata

---

## 🔍 Análise Técnica

### Diferença entre PIX e Cartões:

| Tipo | Sufixo XX/XX | Significado | Tratamento Correto |
|------|--------------|-------------|-------------------|
| **PIX** | "Transferência 31/05" | Data da compensação | ✅ Normalizar (mesma transação) |
| **Cartão** | "Kabum 09/10" | Parcela 9 de 10 | ❌ NÃO normalizar (parcelas diferentes) |

### Fluxo Correto Esperado:

```
1. Ler arquivo: "Pix Fulano 01/10" ou "Kabum 09/10"
2. Normalizar TEMPORARIAMENTE para categorização: "PIX FULANO" ou "KABUM"
3. Buscar categoria no dicionário
4. Salvar com descrição ORIGINAL: "Pix Fulano 01/10" ou "Kabum 09/10"
5. Verificar duplicata usando ORIGINAL + data + valor + mes_comp
```

---

## ✅ Solução Implementada

### 1. Processadores (pix.py e cards.py)
**Alteração:** Salvar descrição ORIGINAL sem normalização

**Antes:**
```python
description=self.normalize_description(row["Descricao"])
```

**Depois:**
```python
description=row["Descricao"].strip()  # Apenas remove espaços
```

**Arquivos:**
- `backend/src/processors/pix.py` (linha ~86)
- `backend/src/processors/cards.py` (linhas ~203, ~288)

### 2. Verificação de Duplicatas (transaction_repository.py)
**Alteração:** Comparar descrições ORIGINAIS diretamente

**Antes:**
```python
desc_norm = self.dedup_helper.normalize_description_for_dedup(transaction.description)
existing_norm = self.dedup_helper.normalize_description_for_dedup(existing_desc)
if existing_norm == desc_norm:
    return True  # Duplicata
```

**Depois:**
```python
cursor.execute("""
    SELECT Descricao, MesComp FROM lancamentos 
    WHERE Data = ? 
    AND ABS(Valor - ?) < 0.01
    AND UPPER(Fonte) = UPPER(?)
    AND UPPER(TRIM(Descricao)) = UPPER(TRIM(?))  -- Comparação direta
""")

# Verifica também mes_comp para distinguir parcelas
if transaction.mes_comp == existing_mes_comp:
    return True  # Duplicata
```

**Arquivo:**
- `backend/src/database/transaction_repository.py` (linhas ~131-179)

### 3. Categorização (categorization_service.py)
**Status:** ✅ Já estava correto

- Normaliza TEMPORARIAMENTE apenas para buscar no dicionário
- NÃO altera a descrição original da transação
- Atualiza apenas o campo `category`

**Arquivo:**
- `backend/src/services/categorization_service.py` (linhas ~36, ~118)

---

## 🎯 Impacto da Correção

### Antes (Comportamento Incorreto):
```
📥 Janeiro: "Kabum 08/10" → Normaliza → Salva "KABUM" → ✅ OK
📥 Fevereiro: "Kabum 09/10" → Normaliza → Compara com "KABUM" → ❌ DUPLICATA (ERRO!)
```

### Depois (Comportamento Correto):
```
📥 Janeiro: "Kabum 08/10" → Salva "Kabum 08/10" → ✅ OK
📥 Fevereiro: "Kabum 09/10" → Compara "Kabum 09/10" ≠ "Kabum 08/10" → ✅ NOVA TRANSAÇÃO!
```

---

## 🧪 Validação Necessária

Após esta correção, é importante:

1. **Reprocessar arquivos existentes** que tiveram parcelas ignoradas
2. **Verificar transações de cartão** nos últimos 3 meses
3. **Confirmar** que parcelas estão sendo processadas corretamente
4. **Atentar** para possível necessidade de ajuste no dicionário de categorias

---

## 📝 Observações Importantes

### Para Futuro:
- **PIX parcelado**: Atualmente não existe, mas se implementado, será necessário tratamento especial
- **Normalização**: Deve ocorrer APENAS para categorização, nunca para armazenamento
- **Deduplicação**: Sempre usar descrição original + data + valor + fonte + mes_comp

### Arquivos de Referência:
- `backend/src/processors/base.py` - Método `normalize_description()` (linha ~76)
- `backend/src/utils/deduplication_helper.py` - Helper não usado mais na deduplicação
- `backend/src/models/__init__.py` - Modelo `Transaction` com campo `mes_comp`

---

## ✅ Status Final

- [x] Bug identificado e analisado
- [x] Causa raiz determinada
- [x] Correção implementada em 3 arquivos
- [x] Documentação criada
- [ ] Testes executados (pendente)
- [ ] Reprocessamento de dados históricos (pendente)

---

**Documentado por:** GitHub Copilot  
**Aprovado por:** [Pendente]  
**Data de Deploy:** [Pendente]
