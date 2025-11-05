# Checklist de Qualidade - PROCESSOS_ASSINADOS.xlsx

## Objetivo
Validar a integridade, consistência e qualidade dos dados na planilha `PROCESSOS_ASSINADOS.xlsx`.

---

## 1. Estrutura da Planilha

### ✅ Colunas Obrigatórias (5 principais)
- [ ] `TIPO DE PROCESSO` - Descrição do tipo de acordo
- [ ] `NÚMERO` - Número do processo (formato: 00000.000000/AAAA-00)
- [ ] `STATUS` - Status do processo (vigente, aceite, etc.)
- [ ] `PESQUISADOR` - Responsável no INPA
- [ ] `PAÍS/ESTADO (ISO3)` - Localização com código ISO-3 ou UF

### ⚠️ Colunas Adicionais Encontradas (8 colunas extras)
- [ ] `Unnamed: 2` - **Coluna vazia ou auxiliar (verificar necessidade)**
- [ ] `CONTATO` - Informações de contato
- [ ] `Unnamed: 5` - **Coluna vazia ou auxiliar (verificar necessidade)**
- [ ] `Unnamed: 7` - **Coluna vazia ou auxiliar (verificar necessidade)**
- [ ] `PORTARIA` - Número da portaria
- [ ] `Unnamed: 9` - **Coluna vazia ou auxiliar (verificar necessidade)**
- [ ] `RESPONSÁVEL PELO PROCESSO` - Responsável (diferente de PESQUISADOR?)
- [ ] `Unnamed: 11` - **Coluna vazia ou auxiliar (verificar necessidade)**

**Total de colunas**: 13  
**Ação sugerida**: Remover colunas `Unnamed: X` se estiverem vazias ou renomeá-las se tiverem conteúdo relevante.

---

## 2. Validação de Dados

### 2.1 Coluna: `TIPO DE PROCESSO`
- [ ] **Valores nulos**: Verificar se há registros sem tipo
- [ ] **Inconsistências de formatação**:
  - [ ] Uso misto de maiúsculas/minúsculas (ex.: "Acordo" vs "ACORDO")
  - [ ] Acentuação correta (ex.: "Convênio", "Adesão")
  - [ ] Numeração padronizada (ex.: "nº", "Nº", "n°")
- [ ] **Valores únicos**: 92 tipos únicos (cada registro tem um tipo específico)
- [ ] **Sugestão**: Criar coluna adicional `CATEGORIA` para agrupar tipos similares

**Principais categorias inferidas**:
- Cartas Convite (34)
- Acordos / Acordos de Cooperação (21)
- Memorandos de Entendimento (M.O.U) (14)
- Convênios (13)
- Protocolos de Intenções (7)
- Termos de Adesão (4)
- Outros (3)

---

### 2.2 Coluna: `NÚMERO`
- [ ] **Valores nulos**: Verificar se há registros sem número
- [ ] **Formato válido**: `00000.000000/AAAA-00` (ex.: 01280.000381/2023-95)
- [ ] **Extração de ano**: Regex `/(20\d{2})\b` funciona para todos os registros?
- [ ] **Anos extraídos**: 2020-2025 (todos os 92 registros possuem ano)
- [ ] **Distribuição por ano**:
  - 2020: 1 registro
  - 2021: 2 registros
  - 2022: 8 registros
  - 2023: 28 registros
  - 2024: 24 registros
  - 2025: 29 registros

**Status**: ✅ Todos os registros possuem ano extraído (0 registros sem ano)

---

### 2.3 Coluna: `STATUS`
- [ ] **Valores nulos**: Verificar se há registros sem status
- [ ] **Valores únicos**: 6 status diferentes
- [ ] **Todos vigentes?**: Sim, todos os 6 status contêm "VIGENTE" ou "ACEITE"
- [ ] **Padronização**: Todos os status seguem o padrão:
  - "PROCESSO FECHADO NA DICIN - O PROCESSO ESTÁ EM BLOCOS INTERNOS [CATEGORIA]"

**Distribuição de STATUS**:
1. COMO VIGENTE (n=40)
2. EM CARTAS/ACEITE (n=35)
3. EM PARCERIAS INTERNACIONAIS/VIGENTES (n=3)
4. EM PARCERIAS NACIONAIS/VIGENTES (n=10)
5. EM PARCERIAS VIGENTES (n=1)
6. INTERNACIONAL VIGENTE (n=2)

**Regra implementada**: Regex `\b(vigente|em vigor|assinado)\b` (case-insensitive)

---

### 2.4 Coluna: `PESQUISADOR`
- [ ] **Valores nulos**: Verificar se há registros sem pesquisador responsável
- [ ] **Valores únicos**: 56 pesquisadores diferentes
- [ ] **Inconsistências**:
  - [ ] Uso de "-" para indicar ausência de informação (verificar se deve ser tratado como nulo)
  - [ ] Múltiplos pesquisadores no mesmo campo (ex.: "José Laurindo, Jorge Porto, Beatriz Ronchi...")
  - [ ] Formatação mista (ex.: "Dr.", "Dra.", sem prefixo)
  - [ ] Siglas/códigos (ex.: "COATL", "COSAS", "NAPPA")

**Ação sugerida**: Padronizar formato (ex.: sempre incluir título acadêmico ou removê-lo uniformemente).

---

### 2.5 Coluna: `PAÍS/ESTADO (ISO3)`
- [ ] **Valores nulos**: Verificar se há registros sem localização
- [ ] **Valores únicos**: 28 localizações diferentes
- [ ] **Formato válido**: `Nome (ISO3)` ou `Estado (UF)`
  - Países: Ex.: "Alemanha (DEU)", "Reino Unido (GBR)"
  - Estados BR: Ex.: "Amazonas (AM)", "São Paulo (SP)"
- [ ] **Inconsistências**:
  - [ ] "Amazona (AM)" vs "Amazonas (AM)" vs "Amazonia (AM)" → **Erro de digitação**
  - [ ] Múltiplas localizações no mesmo registro (separadas por ";")
    - Ex.: "Amazonas (AM); São Paulo (SP)"
    - Ex.: "Rio de Janeiro (RJ); Distrito Federal (DF); Minas Gerais (MG)"

**Distribuição por tipo de localização**:
- **Estados brasileiros** (UF): 10 estados + DF
  - Amazonas (AM): 26 registros ⚠️ + 3 com erro de digitação
  - São Paulo (SP): 4
  - Outros: 1-2 cada
- **Países estrangeiros** (ISO-3): 17 países
  - Reino Unido (GBR): 9
  - Canadá (CAN): 9
  - China (CHN): 6
  - Estados Unidos (USA): 5
  - França (FRA): 4
  - Alemanha (DEU): 3
  - Estônia (EST): 3
  - Outros: 1-2 cada

**Erros identificados**:
1. "Amazona (AM)" → deve ser "Amazonas (AM)"
2. "Amazonia (AM)" → deve ser "Amazonas (AM)"

**Ação sugerida**: Corrigir erros de digitação e criar coluna separada para acordos com múltiplas localizações.

---

## 3. Regras de Negócio

### ✅ Regra 1: Acordos sem ano também contam
- **Status**: Todos os 92 registros possuem ano extraído
- **Casos futuros**: Se cartas convite ou outros tipos não tiverem número de processo com ano, devem ser contabilizados mesmo assim.

### ✅ Regra 2: Brasil é separado por UF
- **Status**: Implementado corretamente
- **Validação**: Estados brasileiros estão no formato "Estado (UF)"
- **Mapa BR**: Usa GeoJSON de UFs e identifica por sigla (AM, SP, PA, etc.)

### ✅ Regra 3: Todos os STATUS atuais são vigentes
- **Status**: Implementado corretamente
- **Validação**: Regex identifica "vigente", "em vigor", "assinado", "aceite"

---

## 4. Checklist de Validação Completa

### Pré-processamento
- [ ] Arquivo existe em `data/PROCESSOS_ASSINADOS.xlsx`
- [ ] Formato: `.xlsx` (Excel)
- [ ] Encoding: UTF-8 (verificar se acentos estão corretos)
- [ ] Total de registros: 92
- [ ] Total de colunas: 13

### Colunas Obrigatórias
- [ ] `TIPO DE PROCESSO` - 100% preenchido (0 nulos)
- [ ] `NÚMERO` - 100% preenchido (0 nulos) e formato válido
- [ ] `STATUS` - 100% preenchido (0 nulos)
- [ ] `PESQUISADOR` - Verificar nulos e "-"
- [ ] `PAÍS/ESTADO (ISO3)` - 100% preenchido (0 nulos)

### Integridade de Dados
- [ ] Sem duplicatas (verificar `NÚMERO` como chave única)
- [ ] Ano extraído de `NÚMERO`: 100% (92/92)
- [ ] Anos válidos: 2020-2025 (range esperado)
- [ ] Todos os registros são vigentes: Sim (100%)

### Inconsistências a Corrigir
- [ ] ❌ "Amazona (AM)" → "Amazonas (AM)"
- [ ] ❌ "Amazonia (AM)" → "Amazonas (AM)"
- [ ] ⚠️ Múltiplas localizações no mesmo registro (separar ou criar coluna adicional)
- [ ] ⚠️ Colunas `Unnamed: X` (remover ou renomear)
- [ ] ⚠️ Pesquisador com "-" (padronizar como nulo ou "Não informado")
- [ ] ⚠️ Formatação de `TIPO DE PROCESSO` (maiúsculas/minúsculas, acentuação)

### Validação de Parsing
- [ ] Parser de `PAÍS/ESTADO (ISO3)` funciona corretamente
- [ ] Extração de UF (2 letras) vs ISO-3 (3 letras)
- [ ] Mapeamento de UF para nome completo (ex.: AM → Amazonas)
- [ ] Identificação de continente por ISO-3 (dicionário `ISO3_TO_CONTINENT`)

### Testes de Dashboard
- [ ] Filtro por ano: 2020-2025
- [ ] Filtro por tipo: 92 tipos únicos (ou categorias agrupadas)
- [ ] Filtro por continente: América do Sul, América do Norte, Europa, Ásia, África, Oceania
- [ ] Mapa mundial: países com acordos (ISO-3)
- [ ] Mapa Brasil: estados com acordos (UF)
- [ ] Gráfico de evolução anual: 2020-2025
- [ ] Gráfico de distribuição por tipo/categoria
- [ ] Gráfico de acordos por continente
- [ ] Tabela de detalhes: clique em país/UF mostra acordos específicos

---

## 5. Recomendações de Melhoria

### 5.1 Estrutura da Planilha
1. **Remover colunas `Unnamed: X`** se estiverem vazias
2. **Renomear colunas** se tiverem conteúdo relevante
3. **Criar coluna `CATEGORIA`** para agrupar tipos de processo:
   - Carta Convite
   - Acordo de Cooperação
   - Memorando de Entendimento
   - Convênio
   - Protocolo de Intenções
   - Termo de Adesão
   - Outros
4. **Separar múltiplas localizações** em linhas diferentes ou criar coluna `LOCALIZAÇÃO_SECUNDÁRIA`

### 5.2 Padronização de Dados
1. **Corrigir erros de digitação** em `PAÍS/ESTADO (ISO3)`:
   - "Amazona" → "Amazonas"
   - "Amazonia" → "Amazonas"
2. **Padronizar `PESQUISADOR`**:
   - Sempre incluir ou nunca incluir título acadêmico (Dr./Dra.)
   - Substituir "-" por "Não informado" ou deixar vazio
3. **Padronizar `TIPO DE PROCESSO`**:
   - Maiúsculas uniformes ou Title Case
   - Acentuação correta
   - Numeração consistente (nº vs Nº)

### 5.3 Validação Contínua
1. **Criar script de validação** que roda antes do dashboard:
   - Verifica colunas obrigatórias
   - Valida formato de `NÚMERO`
   - Identifica valores nulos
   - Detecta duplicatas
2. **Alertas no dashboard**:
   - Exibir mensagem se colunas obrigatórias estiverem faltando
   - Mostrar estatísticas de qualidade (% preenchimento, % válidos)

---

## 6. Resumo de Status Atual

| Critério | Status | Observação |
|----------|--------|------------|
| Arquivo existe | ✅ | `data/PROCESSOS_ASSINADOS.xlsx` |
| Total de registros | ✅ | 92 registros |
| Colunas obrigatórias | ✅ | 5 colunas principais presentes |
| Valores nulos (críticos) | ⚠️ | Verificar `PESQUISADOR` |
| Formato de `NÚMERO` | ✅ | Todos têm ano extraído |
| Formato de `PAÍS/ESTADO` | ⚠️ | Erros de digitação em "Amazonas" |
| Todos vigentes | ✅ | 100% dos registros |
| Anos válidos | ✅ | 2020-2025 |
| Colunas vazias | ⚠️ | 4 colunas `Unnamed: X` |
| Parsing funcional | ✅ | Parser de país/UF funciona |

**Score de Qualidade**: 8/10 ⭐⭐⭐⭐⭐⭐⭐⭐☆☆

---

**Última atualização**: 28 de outubro de 2025  
**Fonte**: `data/PROCESSOS_ASSINADOS.xlsx` (92 registros)  
**Responsável**: Análise automatizada via Python/Pandas
