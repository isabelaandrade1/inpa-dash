# Dicionário de STATUS - Acordos Vigentes

## Objetivo
Identificar quais valores da coluna `STATUS` representam acordos **vigentes** (ativos, em vigor, assinados).

---

## Valores Únicos de STATUS na Planilha

A planilha `PROCESSOS_ASSINADOS.xlsx` contém **6 valores únicos** na coluna `STATUS`:

1. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS COMO VIGENTE** (n=40)
2. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM CARTAS/ACEITE** (n=35)
3. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS INTERNACIONAIS/VIGENTES** (n=3)
4. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS NACIONAIS/VIGENTES** (n=10)
5. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS VIGENTES** (n=1)
6. **PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS INTERNACIONAL VIGENTE** (n=2)

---

## Regra para Identificar STATUS "Vigente"

### Palavras-chave que indicam STATUS vigente:
- `vigente` (singular)
- `vigentes` (plural)
- `em vigor`
- `assinado`
- `ativo`
- `aceite` (indica aceitação/vigência)

### Regex recomendado (Python):
```python
status_lower = df["STATUS"].str.lower()
df["eh_vigente"] = status_lower.str.contains(
    r"\b(vigente|vigentes|em vigor|assinado|ativo|aceite)\b", 
    regex=True, 
    na=False
)
```

### Observação importante:
- **Todos os 6 valores** na planilha atual contêm a palavra **"VIGENTE"** ou **"ACEITE"**.
- Portanto, **todos os 92 registros** são considerados vigentes.
- A distinção entre eles está apenas na **categoria** (internacional, nacional, cartas/aceite).

---

## Mapeamento Completo

| STATUS | Vigente? | Categoria |
|--------|----------|-----------|
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS COMO VIGENTE | ✅ Sim | Geral |
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM CARTAS/ACEITE | ✅ Sim | Cartas convite |
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS INTERNACIONAIS/VIGENTES | ✅ Sim | Parcerias internacionais |
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS NACIONAIS/VIGENTES | ✅ Sim | Parcerias nacionais |
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS VIGENTES | ✅ Sim | Parcerias (geral) |
| PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS INTERNACIONAL VIGENTE | ✅ Sim | Internacional |

---

## Casos Especiais

### Cartas Convite (sem ano extraído):
- **Observação**: Atualmente **TODOS os 92 registros** possuem ano extraído da coluna `NÚMERO`.
- Não há registros sem ano na amostra atual.
- Regra de negócio confirmada: **acordos sem ano também devem ser contabilizados** (exemplo: cartas convite que usam apenas número sequencial).

### Acordos Futuros (STATUS não-vigente):
Se no futuro a planilha incluir status como:
- "ENCERRADO"
- "CANCELADO"
- "EM ANÁLISE"
- "ARQUIVADO"
- "EXPIRADO"

Estes **NÃO** devem ser considerados vigentes.

---

## Implementação no Código (`app.py`)

```python
# Linha 103 do app.py (atual):
status_lower = df["status"].str.lower()
df["eh_vigente"] = status_lower.str.contains(
    r"\b(vigente|em vigor|assinado)\b", 
    regex=True
)
```

### Sugestão de melhoria:
```python
# Versão ampliada (mais robusta):
status_lower = df["status"].str.lower()
df["eh_vigente"] = status_lower.str.contains(
    r"\b(vigente|vigentes|em vigor|assinado|assinada|ativo|ativa|aceite)\b", 
    regex=True, 
    na=False  # Adicionar para evitar NaN
)
```

---

## Validação

✅ **Total de registros vigentes**: 92 / 92 (100%)  
✅ **Distribuição por categoria**:
- Vigente (geral): 40
- Cartas/Aceite: 35
- Parcerias Internacionais: 3
- Parcerias Nacionais: 10
- Parcerias (geral): 1
- Internacional: 2

---

**Última atualização**: 28 de outubro de 2025  
**Fonte**: `data/PROCESSOS_ASSINADOS.xlsx` (92 registros)
