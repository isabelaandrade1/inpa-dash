# Pasta de Dados - INPA Dashboard

## Arquivos Principais

### 1. PROCESSOS_ASSINADOS.xlsx
**Planilha principal** com dados de acordos internacionais do INPA.

**Colunas obrigatórias**:
- `TIPO DE PROCESSO` - Descrição do tipo de acordo
- `NÚMERO` - Número do processo (formato: 00000.000000/AAAA-00)
- `STATUS` - Status do processo (vigente, aceite, etc.)
- `PESQUISADOR` - Responsável no INPA
- `PAÍS/ESTADO (ISO3)` - Localização com código ISO-3 ou UF

**Estatísticas** (última atualização: 28/10/2025):
- Total de registros: 92
- Período: 2020-2025
- 100% vigentes
- 28 localizações diferentes (17 países + 10 UFs brasileiras + DF)

---

## Documentação Gerada

### 2. RESUMO_EXECUTIVO.md
**Resumo completo** da análise da planilha com:
- Principais estatísticas e descobertas
- Validação de regras de negócio
- Score de qualidade (8/10)
- Próximos passos sugeridos

**Recomendado ler primeiro!**

---

### 3. DICIONARIO_STATUS.md
**Dicionário de STATUS** - Identifica quais valores indicam acordos vigentes.

**Conteúdo**:
- 6 valores únicos de STATUS
- Regex para identificar vigentes: `\b(vigente|em vigor|assinado|aceite)\b`
- Mapeamento completo de categorias
- 100% dos registros são vigentes

---

### 4. LISTA_TIPOS.md
**Lista de TIPOS DE PROCESSO** - Todos os 92 tipos únicos e categorias inferidas.

**Conteúdo**:
- 92 tipos únicos (lista completa ordenada)
- Categorias principais:
  - Cartas Convite (34)
  - Acordos de Cooperação (21)
  - Memorandos de Entendimento (14)
  - Convênios (13)
  - Protocolos de Intenções (7)
  - Termos de Adesão (4)
  - Outros (3)
- Distribuição percentual por categoria

---

### 5. CHECKLIST_QUALIDADE.md
**Checklist de qualidade** completo para validar a planilha Excel.

**Conteúdo**:
- Estrutura da planilha (13 colunas)
- Validação de dados por coluna
- Regras de negócio validadas
- Inconsistências detectadas
- Recomendações de melhoria
- Score de qualidade: 8/10 ⭐⭐⭐⭐⭐⭐⭐⭐☆☆

**Principais erros identificados**:
- ⚠️ "Amazona (AM)" → corrigir para "Amazonas (AM)"
- ⚠️ "Amazonia (AM)" → corrigir para "Amazonas (AM)"
- ⚠️ 4 colunas `Unnamed: X` (verificar se podem ser removidas)

---

### 6. SCRIPTS_VALIDACAO.md
**Scripts Python** prontos para validar e corrigir a planilha.

**Conteúdo**:
- Script 1: Correção de erros de digitação
- Script 2: Remoção de colunas vazias
- Script 3: Padronização de PESQUISADOR
- Script 4: Criação de coluna CATEGORIA
- Script 5: Separação de múltiplas localizações
- Script 6: Validação completa (all-in-one)
- Script 7: Testes automatizados de qualidade

**Como usar**:
```python
from scripts.validacao import validar_e_corrigir_planilha

df_corrigido = validar_e_corrigir_planilha(
    "data/PROCESSOS_ASSINADOS.xlsx",
    "data/PROCESSOS_ASSINADOS_VALIDADO.xlsx"
)
```

---

## Arquivos GeoJSON

### 7. br_states.geojson
**GeoJSON de estados brasileiros** para mapa de UFs no dashboard.

**Fonte**: Download automático de repositório público (GitHub)  
**Usado por**: `app.py` (função `ensure_br_states_geojson`)

---

## Como Navegar

1. **Primeira vez?** → Leia `RESUMO_EXECUTIVO.md`
2. **Precisa validar status?** → `DICIONARIO_STATUS.md`
3. **Quer ver tipos únicos?** → `LISTA_TIPOS.md`
4. **Validar qualidade da planilha?** → `CHECKLIST_QUALIDADE.md`
5. **Corrigir erros automaticamente?** → `SCRIPTS_VALIDACAO.md`

---

## Estrutura de Arquivos

```
data/
├── PROCESSOS_ASSINADOS.xlsx       # Planilha principal (92 registros)
├── README.md                       # Este arquivo (índice e navegação)
├── RESUMO_EXECUTIVO.md             # Resumo completo da análise
├── DICIONARIO_STATUS.md            # Dicionário de status vigente
├── LISTA_TIPOS.md                  # Lista de tipos únicos
├── CHECKLIST_QUALIDADE.md          # Checklist de validação
├── SCRIPTS_VALIDACAO.md            # Scripts Python prontos
└── br_states.geojson               # GeoJSON de UFs (auto-download)
```

---

## Próximos Passos

### Curto Prazo (Essencial)
1. ✅ Corrigir erros de digitação em PAÍS/ESTADO
2. ✅ Remover ou renomear colunas `Unnamed: X`
3. ✅ Padronizar PESQUISADOR (substituir "-")

### Médio Prazo (Recomendado)
1. ⚠️ Criar coluna `CATEGORIA` para tipos
2. ⚠️ Separar múltiplas localizações
3. ⚠️ Implementar script de validação automática

### Longo Prazo (Otimização)
1. 💡 API de validação para novos registros
2. 💡 Dashboard de qualidade de dados
3. 💡 Histórico de versões da planilha

---

**Última atualização**: 28 de outubro de 2025  
**Responsável**: Análise automatizada via Python/Pandas  
**Ambiente**: Python 3.11.9 (venv)  
**Dashboard**: `app.py` (Dash + Plotly).

Formato esperado mínimo:
- Coluna "PAÍS/ESTADO (ISO3)" com valores tipo "Reino Unido (GBR)" ou "Amazonas (AM)"
- Coluna "NÚMERO" contendo o ano no padrão ".../2023-xx"
- Coluna "STATUS"
- Coluna "TIPO DE PROCESSO"
- Coluna "PESQUISADOR"
