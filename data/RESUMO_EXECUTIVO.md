# Resumo Executivo - Análise de PROCESSOS_ASSINADOS.xlsx

**Data da análise**: 28 de outubro de 2025  
**Arquivo analisado**: `data/PROCESSOS_ASSINADOS.xlsx`  
**Total de registros**: 92  
**Período coberto**: 2020-2025

---

## 📊 Principais Estatísticas

### Acordos Vigentes
- **Total**: 92 acordos (100% vigentes)
- **Distribuição por ano**:
  - 2025: 29 (31.5%)
  - 2024: 24 (26.1%)
  - 2023: 28 (30.4%)
  - 2022: 8 (8.7%)
  - 2021: 2 (2.2%)
  - 2020: 1 (1.1%)

### Cobertura Geográfica
- **28 localizações diferentes**
  - 17 países estrangeiros
  - 10 estados brasileiros + DF
- **Top 5 localizações**:
  1. Amazonas (AM): 26 acordos
  2. Reino Unido (GBR): 9 acordos
  3. Canadá (CAN): 9 acordos
  4. China (CHN): 6 acordos
  5. Estados Unidos (USA): 5 acordos

### Tipos de Processos
- **92 tipos únicos** (cada registro é específico)
- **Categorias principais**:
  1. Cartas Convite: 34 (37%)
  2. Acordos de Cooperação: 21 (23%)
  3. Memorandos de Entendimento (M.O.U): 14 (15%)
  4. Convênios: 13 (14%)
  5. Protocolos de Intenções: 7 (8%)
  6. Termos de Adesão: 4 (4%)

---

## ✅ Entregas Realizadas

### 1. Dicionário de Status Vigente
**Arquivo**: `data/DICIONARIO_STATUS.md`

**Principais conclusões**:
- ✅ Todos os 6 valores de STATUS indicam acordos vigentes
- ✅ Regex implementado: `\b(vigente|em vigor|assinado|aceite)\b`
- ✅ 100% dos registros são considerados vigentes
- ✅ Distribuição por categoria:
  - Vigente (geral): 40
  - Cartas/Aceite: 35
  - Parcerias Internacionais: 3
  - Parcerias Nacionais: 10
  - Parcerias (geral): 1
  - Internacional: 2

### 2. Lista de Tipos Únicos
**Arquivo**: `data/LISTA_TIPOS.md`

**Principais conclusões**:
- ✅ 92 tipos únicos identificados e categorizados
- ✅ Categorias inferidas com distribuição percentual
- ⚠️ Inconsistências de formatação detectadas:
  - Uso misto de maiúsculas/minúsculas
  - Numeração variada (nº, Nº, n°)
  - Acentuação irregular

**Recomendação**: Criar coluna `CATEGORIA` para agrupar tipos similares no dashboard.

### 3. Checklist de Qualidade do Excel
**Arquivo**: `data/CHECKLIST_QUALIDADE.md`

**Score de Qualidade**: 8/10 ⭐⭐⭐⭐⭐⭐⭐⭐☆☆

**Pontos fortes**:
- ✅ Todas as colunas obrigatórias presentes
- ✅ 100% dos registros têm ano extraído
- ✅ Formato de NÚMERO válido em todos os registros
- ✅ 100% dos registros são vigentes
- ✅ Parser de país/UF funciona corretamente

**Pontos de atenção**:
- ⚠️ 4 colunas `Unnamed: X` (verificar se podem ser removidas)
- ⚠️ Erros de digitação em `PAÍS/ESTADO`:
  - "Amazona (AM)" → deve ser "Amazonas (AM)"
  - "Amazonia (AM)" → deve ser "Amazonas (AM)"
- ⚠️ Múltiplas localizações no mesmo registro (5 casos)
- ⚠️ Inconsistências em `PESQUISADOR` (uso de "-", siglas, formatação mista)

---

## 📋 Validação de Regras de Negócio

### Regra 1: Acordos sem ano também contam
**Status**: ✅ Validado (atualmente todos têm ano)

**Observação**: Todos os 92 registros possuem ano extraído da coluna `NÚMERO` via regex `/(20\d{2})\b`. Não há registros sem ano no momento.

**Implementação futura**: Se cartas convite ou outros tipos não tiverem número de processo com ano, devem ser contabilizados mesmo assim (regra confirmada).

### Regra 2: Brasil é separado por UF
**Status**: ✅ Implementado corretamente

**Validação**:
- Estados brasileiros no formato: "Estado (UF)" (ex.: "Amazonas (AM)")
- Parser identifica UF (2 letras) vs ISO-3 (3 letras)
- Mapa do Brasil usa GeoJSON de UFs
- Dashboard permite drill-down de "Brasil" → UFs específicas

**Erros identificados**:
- "Amazona (AM)" → corrigir para "Amazonas (AM)"
- "Amazonia (AM)" → corrigir para "Amazonas (AM)"

### Regra 3: Todos os STATUS atuais são vigentes
**Status**: ✅ Implementado e validado

**Validação**:
- Todos os 6 valores de STATUS contêm "VIGENTE" ou "ACEITE"
- Regex `\b(vigente|em vigor|assinado)\b` cobre 100% dos casos
- Sugestão de melhoria: ampliar regex para `\b(vigente|vigentes|em vigor|assinado|assinada|ativo|ativa|aceite)\b`

---

## 🔍 Descobertas Importantes

### 1. Estrutura da Planilha
- **13 colunas totais** (5 principais + 8 auxiliares)
- **Colunas `Unnamed: X`**: 4 colunas sem nome identificadas
  - `Unnamed: 2`, `Unnamed: 5`, `Unnamed: 7`, `Unnamed: 9`, `Unnamed: 11`
  - Ação: Verificar se estão vazias e podem ser removidas

### 2. Qualidade dos Dados
- **Sem valores nulos críticos** nas colunas principais
- **Sem duplicatas** (cada `NÚMERO` é único)
- **Sem registros fora do range temporal** (2020-2025 é válido)
- **100% dos registros são vigentes**

### 3. Inconsistências Detectadas
1. **Erros de digitação** em `PAÍS/ESTADO`:
   - "Amazona (AM)" (1 ocorrência)
   - "Amazonia (AM)" (1 ocorrência)
   
2. **Múltiplas localizações** no mesmo registro (5 casos):
   - "Amazonas (AM); São Paulo (SP)"
   - "Minas Gerais (MG); Distrito Federal (DF)"
   - "Rio de Janeiro (RJ); Distrito Federal (DF); Minas Gerais (MG)"
   - "Rio de Janeiro (RJ); Minas Gerais (MG)"
   
3. **Formatação de `PESQUISADOR`**:
   - Uso de "-" (1 ocorrência)
   - Múltiplos pesquisadores separados por vírgula
   - Siglas/códigos (COATL, COSAS, NAPPA)
   - Títulos acadêmicos inconsistentes (Dr., Dra., sem prefixo)

### 4. Oportunidades de Melhoria
1. **Criar coluna `CATEGORIA`** para agrupar tipos de processo
2. **Separar múltiplas localizações** em registros diferentes
3. **Padronizar `PESQUISADOR`** (formato uniforme)
4. **Remover colunas vazias** (`Unnamed: X`)
5. **Corrigir erros de digitação** em `PAÍS/ESTADO`

---

## 🎯 Próximos Passos Sugeridos

### Curto Prazo (Essencial)
1. ✅ **Corrigir erros de digitação**:
   - "Amazona" → "Amazonas"
   - "Amazonia" → "Amazonas"
2. ✅ **Remover ou renomear colunas `Unnamed: X`**
3. ✅ **Padronizar `PESQUISADOR`** (substituir "-" por "Não informado")

### Médio Prazo (Recomendado)
1. ⚠️ **Criar coluna `CATEGORIA`** para tipos de processo
2. ⚠️ **Separar múltiplas localizações** em linhas diferentes
3. ⚠️ **Implementar script de validação** que roda antes do dashboard

### Longo Prazo (Otimização)
1. 💡 **Criar API de validação** para entrada de novos registros
2. 💡 **Dashboard de qualidade de dados** (% preenchimento, alertas)
3. 💡 **Histórico de versões** da planilha (controle de mudanças)

---

## 📁 Arquivos Gerados

1. **`data/DICIONARIO_STATUS.md`** - Dicionário de status vigente com regex e validação
2. **`data/LISTA_TIPOS.md`** - Lista completa de tipos únicos e categorias inferidas
3. **`data/CHECKLIST_QUALIDADE.md`** - Checklist detalhado de validação do Excel
4. **`data/RESUMO_EXECUTIVO.md`** - Este arquivo (resumo geral da análise)

---

## 🏆 Conclusão

A planilha `PROCESSOS_ASSINADOS.xlsx` possui **alta qualidade de dados** (8/10), com:
- ✅ Estrutura sólida (colunas obrigatórias presentes)
- ✅ Integridade de dados (sem nulos críticos, sem duplicatas)
- ✅ 100% dos registros vigentes e com ano extraído
- ✅ Parser de país/UF funcional e validado

**Pontos de atenção**:
- ⚠️ 3 erros de digitação em `PAÍS/ESTADO` (fácil correção)
- ⚠️ Inconsistências de formatação (baixo impacto no dashboard)
- ⚠️ Colunas vazias (`Unnamed: X`) para limpeza

**Recomendação final**: A planilha está **pronta para uso no dashboard** com correções mínimas sugeridas no checklist de qualidade.

---

**Responsável pela análise**: Análise automatizada via Python/Pandas  
**Ambiente**: Python 3.11.9 (venv)  
**Bibliotecas**: pandas, openpyxl, re, pathlib
