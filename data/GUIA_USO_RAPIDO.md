# Guia de Uso Rápido - Documentação INPA Dashboard

Este guia mostra como usar os documentos gerados para tarefas comuns do dia a dia.

---

## 🎯 Cenário 1: Preciso adicionar um novo registro na planilha

### Passo 1: Verificar formato esperado
Consulte: **`CHECKLIST_QUALIDADE.md`** → Seção 2 (Validação de Dados)

**Formato obrigatório**:
- `TIPO DE PROCESSO`: Texto livre (ex.: "Acordo de Cooperação entre INPA e XXX")
- `NÚMERO`: `00000.000000/AAAA-00` (ex.: `01280.000381/2025-95`)
- `STATUS`: Use um dos 6 valores padronizados (consulte `DICIONARIO_STATUS.md`)
- `PESQUISADOR`: Nome do responsável (ex.: "Dr. João Silva")
- `PAÍS/ESTADO (ISO3)`: 
  - Para países: `Nome (ISO3)` (ex.: "França (FRA)")
  - Para UFs: `Estado (UF)` (ex.: "Amazonas (AM)")

### Passo 2: Escolher STATUS correto
Consulte: **`DICIONARIO_STATUS.md`** → Tabela de mapeamento

**Opções disponíveis**:
1. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS COMO VIGENTE
2. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM CARTAS/ACEITE
3. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS INTERNACIONAIS/VIGENTES
4. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS NACIONAIS/VIGENTES
5. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS EM PARCERIAS VIGENTES
6. PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS INTERNACIONAL VIGENTE

**Dica**: Use opção 2 para Cartas Convite, opção 3 para acordos internacionais, opção 4 para nacionais.

### Passo 3: Validar antes de salvar
Rode o script de validação: **`SCRIPTS_VALIDACAO.md`** → Script 7 (Testes)

```python
from scripts.validacao import testar_qualidade_planilha

testar_qualidade_planilha("data/PROCESSOS_ASSINADOS.xlsx")
```

---

## 🎯 Cenário 2: Dashboard não está mostrando um acordo como vigente

### Passo 1: Verificar STATUS do registro
Abra: **`PROCESSOS_ASSINADOS.xlsx`**

Encontre o registro e verifique a coluna `STATUS`.

### Passo 2: Consultar regex de vigência
Abra: **`DICIONARIO_STATUS.md`** → Seção "Regra para Identificar STATUS Vigente"

**Regex atual**: `\b(vigente|em vigor|assinado|aceite)\b`

**Verifique se o STATUS contém**:
- "vigente" ✅
- "em vigor" ✅
- "assinado" ✅
- "aceite" ✅

### Passo 3: Corrigir se necessário
Se o STATUS não contém nenhuma dessas palavras, atualize para um dos 6 valores padrão listados em `DICIONARIO_STATUS.md`.

### Passo 4: Reiniciar dashboard
```powershell
# Parar o app (Ctrl+C no terminal)
# Iniciar novamente
C:/Users/Isabela/Downloads/inpa-dash/inpa-dash/.venv/Scripts/python.exe .\app.py
```

---

## 🎯 Cenário 3: Preciso agrupar tipos de processo no dashboard

### Passo 1: Criar coluna CATEGORIA
Use: **`SCRIPTS_VALIDACAO.md`** → Script 4 (Criar coluna CATEGORIA)

```python
import pandas as pd
from pathlib import Path

# Carregar planilha
df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

# Função de categorização
def categorizar_tipo(tipo):
    if pd.isna(tipo):
        return "Não informado"
    tipo_lower = str(tipo).lower()
    if "carta convite" in tipo_lower:
        return "Carta Convite"
    elif "conv" in tipo_lower:
        return "Convênio"
    elif "acordo" in tipo_lower:
        return "Acordo de Cooperação"
    elif "memorando" in tipo_lower or "m.o.u" in tipo_lower:
        return "Memorando de Entendimento"
    elif "protocolo" in tipo_lower:
        return "Protocolo de Intenções"
    elif "termo de ades" in tipo_lower:
        return "Termo de Adesão"
    else:
        return "Outros"

# Aplicar
df["CATEGORIA"] = df["TIPO DE PROCESSO"].apply(categorizar_tipo)

# Salvar
df.to_excel("data/PROCESSOS_ASSINADOS.xlsx", index=False)
```

### Passo 2: Atualizar app.py
Edite `app.py` e substitua `tipo` por `CATEGORIA` nos filtros e gráficos.

**Exemplo**:
```python
# Antes:
tipos_opts = sorted(df["tipo"].dropna().unique().tolist())

# Depois:
tipos_opts = sorted(df["CATEGORIA"].dropna().unique().tolist())
```

---

## 🎯 Cenário 4: Corrigir erros de "Amazona" e "Amazonia"

### Opção 1: Correção manual
1. Abra `PROCESSOS_ASSINADOS.xlsx`
2. Use Ctrl+H (localizar e substituir)
3. Substitua:
   - "Amazona (AM)" → "Amazonas (AM)"
   - "Amazonia (AM)" → "Amazonas (AM)"
4. Salve o arquivo

### Opção 2: Correção automática (Python)
Use: **`SCRIPTS_VALIDACAO.md`** → Script 1 (Correção de erros)

```python
import pandas as pd

df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

df["PAÍS/ESTADO (ISO3)"] = df["PAÍS/ESTADO (ISO3)"].replace({
    "Amazona (AM)": "Amazonas (AM)",
    "Amazonia (AM)": "Amazonas (AM)"
})

df.to_excel("data/PROCESSOS_ASSINADOS.xlsx", index=False)
print("✅ Erros corrigidos!")
```

---

## 🎯 Cenário 5: Verificar quantos acordos temos com país X

### Método 1: Consultar LISTA_TIPOS.md
Abra: **`LISTA_TIPOS.md`** → Seção "Todos os valores (ordenados)"

Busque por "Nome do País (ISO3)" e veja o `(n=X)` ao lado.

**Exemplo**: "Reino Unido (GBR)" mostra `(n=9)` → 9 acordos.

### Método 2: Consultar no dashboard
1. Acesse: http://localhost:8050/
2. Clique no país no mapa mundial
3. Veja a tabela de detalhes abaixo

### Método 3: Consultar via Python
```python
import pandas as pd

df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

# Substituir "França (FRA)" pelo país desejado
pais = "França (FRA)"
total = (df["PAÍS/ESTADO (ISO3)"] == pais).sum()

print(f"Total de acordos com {pais}: {total}")
```

---

## 🎯 Cenário 6: Gerar relatório de acordos vigentes por ano

### Script rápido:
```python
import pandas as pd
import re

df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

# Extrair ano
def extract_year(val):
    if pd.isna(val):
        return None
    m = re.search(r'/(20\d{2})\b', str(val))
    return int(m.group(1)) if m else None

df["ano"] = df["NÚMERO"].apply(extract_year)

# Filtrar vigentes
status_lower = df["STATUS"].str.lower()
df["vigente"] = status_lower.str.contains(
    r"\b(vigente|em vigor|assinado|aceite)\b",
    regex=True,
    na=False
)

vigentes = df[df["vigente"]]

# Agrupar por ano
relatorio = vigentes.groupby("ano").size().reset_index(name="total")

print("RELATÓRIO DE ACORDOS VIGENTES POR ANO")
print("="*40)
for idx, row in relatorio.iterrows():
    print(f"{int(row['ano'])}: {row['total']} acordos")
```

**Saída esperada**:
```
RELATÓRIO DE ACORDOS VIGENTES POR ANO
========================================
2020: 1 acordos
2021: 2 acordos
2022: 8 acordos
2023: 28 acordos
2024: 24 acordos
2025: 29 acordos
```

---

## 🎯 Cenário 7: Validar se há registros duplicados

### Script de verificação:
```python
import pandas as pd

df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

# Verificar duplicatas na coluna NÚMERO
duplicatas = df[df["NÚMERO"].duplicated(keep=False)]

if len(duplicatas) > 0:
    print(f"⚠️  {len(duplicatas)} registros duplicados encontrados:")
    print(duplicatas[["NÚMERO", "TIPO DE PROCESSO", "PESQUISADOR"]])
else:
    print("✅ Nenhuma duplicata encontrada!")
```

---

## 🎯 Cenário 8: Exportar lista de pesquisadores únicos

### Script rápido:
```python
import pandas as pd

df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

pesquisadores = df["PESQUISADOR"].dropna().unique()
pesquisadores = sorted([p for p in pesquisadores if p != "-"])

print(f"Total de pesquisadores únicos: {len(pesquisadores)}\n")
for i, p in enumerate(pesquisadores, 1):
    print(f"{i:2d}. {p}")
```

---

## 🎯 Cenário 9: Dashboard não está carregando (erro 500)

### Checklist de troubleshooting:

1. **Verificar se planilha existe**:
   ```powershell
   Test-Path ".\data\PROCESSOS_ASSINADOS.xlsx"
   ```
   Se retornar `False`, coloque a planilha na pasta `data/`.

2. **Verificar logs**:
   ```powershell
   Get-Content .\logs\err.log -Tail 50
   ```

3. **Verificar se todas as colunas obrigatórias existem**:
   Consulte: **`CHECKLIST_QUALIDADE.md`** → Seção 1 (Estrutura)

4. **Rodar testes de qualidade**:
   ```python
   from scripts.validacao import testar_qualidade_planilha
   testar_qualidade_planilha("data/PROCESSOS_ASSINADOS.xlsx")
   ```

5. **Verificar encoding**:
   Se houver erros de caracteres especiais, salve a planilha com encoding UTF-8.

---

## 🎯 Cenário 10: Preciso criar backup antes de fazer mudanças

### Script de backup automático:
```python
import pandas as pd
from pathlib import Path
from datetime import datetime

# Carregar planilha original
df = pd.read_excel("data/PROCESSOS_ASSINADOS.xlsx")

# Criar nome com timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"data/backup/PROCESSOS_ASSINADOS_{timestamp}.xlsx"

# Criar pasta de backup se não existir
Path("data/backup").mkdir(exist_ok=True)

# Salvar backup
df.to_excel(backup_path, index=False)
print(f"✅ Backup criado: {backup_path}")
```

---

## 📚 Referência Rápida de Arquivos

| Preciso... | Consultar... |
|-----------|--------------|
| Visão geral completa | `RESUMO_EXECUTIVO.md` |
| Validar formato de STATUS | `DICIONARIO_STATUS.md` |
| Ver todos os tipos de processo | `LISTA_TIPOS.md` |
| Validar qualidade da planilha | `CHECKLIST_QUALIDADE.md` |
| Corrigir erros automaticamente | `SCRIPTS_VALIDACAO.md` |
| Índice e navegação | `README.md` |

---

## 🛠️ Comandos Úteis

### Iniciar dashboard:
```powershell
C:/Users/Isabela/Downloads/inpa-dash/inpa-dash/.venv/Scripts/python.exe .\app.py
```

### Acessar dashboard:
http://localhost:8050/

### Parar dashboard:
Ctrl+C no terminal

### Verificar porta 8050:
```powershell
netstat -a -n -o | findstr ":8050"
```

### Ler logs:
```powershell
Get-Content .\logs\out.log -Tail 100
Get-Content .\logs\err.log -Tail 100
```

---

**Última atualização**: 28 de outubro de 2025  
**Responsável**: Documentação automatizada  
**Versão**: 1.0
