Documentação Completa — INPA Dashboard
======================================

Última atualização: 04/11/2025

Este documento consolida a visão técnica, operacional e de dados do projeto “INPA Dashboard — Divisão de Cooperação e Intercâmbio”. Ele complementa o README principal com detalhes de arquitetura, pipeline (ETL), fontes de dados, regras de negócio, testes, troubleshooting e roadmap.


1) Visão geral do sistema
-------------------------

- Framework: Dash (Plotly) + Pandas
- Finalidade: Visualizar acordos/convênios/parcerias do INPA por localização (País ou UF), modalidade, ano, status e categoria
- Fonte primária de dados: Google Sheets público (export .xlsx)
- Fallback local: `data/PROCESSOS_ASSINADOS.xlsx`
- Principais componentes do UI:
  - KPIs (cards): vigência geral, países com parcerias, novos acordos no ano, modalidade mais frequente
  - Mapa por marcadores: Mundo (por ISO-3) e Brasil (por UF), com mudança de modo por botões
  - Gráficos: pizza por modalidade; barras empilhadas por ano x vigência
  - Ranking: top 10 países parceiros
  - Tabela de detalhe: filtrável por clique no mapa e pelos filtros globais


2) Arquitetura e componentes
----------------------------

Arquivo principal: `app.py`

- Importa libs: `dash`, `dash_bootstrap_components`, `plotly`, `pandas`, `requests`, `openpyxl`
- Define template visual do Plotly (tipografia, cores, rótulos)
- Cria helpers de UI: `kpi_card`, `chart_card`, `create_ranking_list`
- Configura paths: `BASE_DIR`, `DATA_DIR`
- Define fonte de dados online: `GOOGLE_SHEET_ID` e URL de export `.xlsx`
- Define fallback local: `EXCEL_PATH = data/PROCESSOS_ASSINADOS.xlsx`
- Centróides:
  - Países (ISO-3): gera/baixa `data/iso3_centroids.csv` automaticamente (via world.geo.json)
  - UFs: opcional `data/uf_centroids.csv` (se existir)
  - Baixa `data/br_states.geojson` se ausente (para compatibilidade futura)
- UI (layout Dash):
  - Header com logo (`assets/inpa_logo.png`) e título
  - Filtros (collapse): ano, tipos, modalidades, continentes, status (todos/vigentes)
  - Botões “Mundial” e “Brasil” (modo do mapa)
  - Linhas com KPIs, mapa, gráficos e ranking
  - Tabela detalhada (DataTable) com colunas chave
- Callbacks:
  - Toggle de filtros (abrir/fechar)
  - Mudar de modo (mundo/BR) por botões e por clique no mapa
  - Redesenhar figuras e KPIs quando filtros mudam
  - Atualizar tabela ao clicar no mapa ou alterar filtros
  - Client-side callback para scroll automático até a tabela ao clicar no mapa


3) Pipeline de dados (ETL)
--------------------------

3.1 Carregamento
- Tenta baixar do Google Sheets (export .xlsx). Em caso de falha: usa `data/PROCESSOS_ASSINADOS.xlsx`.
- Em erro sem fallback, exibe alerta com instruções para corrigir (permite rodar app mesmo sem dados válidos, mas mostrando mensagem).

3.2 Colunas mínimas (planilha)
- `PAÍS/ESTADO (ISO3)` — País “Nome (ISO3)” ou UF “Estado (UF)”
- `NÚMERO` — número do processo com ano em `/20XX-`
- `STATUS` — usado para inferir vigência
- `TIPO DE PROCESSO` — descrição do tipo/modalidade
- `Contatos` ou `PESQUISADOR` — pesquisador responsável

3.3 Normalização e campos derivados
- Parser de localização: `parse_pais_ou_uf` → produz
  - `nivel_localizacao` ∈ {`pais`, `uf_br`}
  - `pais`
  - `codigo_iso3` (para `pais`)
  - `uf_sigla`, `uf_nome` (para `uf_br`)
- Ano de assinatura: `ano_assinatura`
  - Primeiro tenta extrair regex de `NÚMERO` (`/(20\d{2})\b`)
  - Fallback: examina colunas com palavras-chave (DATA/ANO/YEAR/DATE)
- Tipo/categoria
  - `tipo` é derivado de `TIPO DE PROCESSO` (texto original)
  - `modalidade` é uma normalização por regras e prefixos (ex.: “Acordo de Cooperação”, “Carta Convite”, “Convênio”, etc.)
- Pesquisador responsável: `pesquisador_responsavel`
  - Usa `Contatos` se existir; caso contrário, `PESQUISADOR`; senão “Não informado”
- Vigência: `eh_vigente`
  - Função `eh_vigente_status` (regex robusta para “vigente”, “em vigor”, “assinado” e negações próximas)
- Continente: `continente`
  - Usa `ISO3_TO_CONTINENT` com coberturas ampliadas; força “América do Sul” para Brasil/UFs

3.4 Opções de filtros (geradas do DataFrame)
- `anos_opts` — anos válidos + “Todos”
- `tipos_opts` — valores únicos de `tipo`
- `modalidades_opts` — valores únicos de `modalidade`
- `conts_opts` — valores únicos de `continente`


4) Funcionalidades de visualização
----------------------------------

4.1 Mapas (marker map)
- Mundo: marcador por país (ISO-3), tamanho proporcional à contagem; cores distintas para vigentes vs demais
- Brasil: marcador por UF (centroide), com lógica de contagem por UF
- Clique no marcador define filtro para tabela de detalhes; clicar em “BRA” no modo mundo alterna para modo Brasil

4.2 Gráficos e ranking
- Pizza por modalidade (exclui “Termo Aditivo” do gráfico, compacta raríssimos em “Outras”, preserva “Carta Convite”)
- Barras empilhadas por ano e vigência (Demais x Vigentes)
- Ranking top 10 países por contagem

4.3 KPIs
- Vigência geral (% e total)
- Países com parcerias (contagem ISO-3 distintos no filtro)
- Novos acordos (ano atual se “Todos”, ou o ano selecionado)
- Modalidade mais frequente (com % no período filtrado)


5) Regras de negócio e dados
----------------------------

- Acordos sem ano também devem ser contabilizados (regra prevista; no dataset atual 100% têm ano)
- Brasil é tratado por UF (quando `PAÍS/ESTADO (ISO3)` contiver uma UF válida)
- STATUS vigentes: regex abrange `vigente`, `vigentes`, `em vigor`, `assinado/assinada`, `aceite`, `ativo/ativa` (versão robusta sugerida)
- Modalidade: normalização de `TIPO DE PROCESSO` (ver regras em `normaliza_modalidade`)

Documentos de apoio em `data/`:
- `RESUMO_EXECUTIVO.md` — estatísticas e descobertas
- `DICIONARIO_STATUS.md` — regras e regex para vigência
- `LISTA_TIPOS.md` — 92 tipos únicos e categorias inferidas
- `CHECKLIST_QUALIDADE.md` — validações da planilha e recomendações
- `SCRIPTS_VALIDACAO.md` — scripts prontos (limpeza/correção/validação)
- `ENTREGA.md` — sumário final de entrega (escopo e resultados)


6) Execução local (detalhada)
-----------------------------

Pré-requisitos:
- Python 3.11+
- Windows PowerShell (o projeto foi usado em Windows; Linux/macOS também suportam com adaptações simples)

Passo a passo:

```powershell
# 1) Ambiente virtual (opcional, recomendado)
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 2) Dependências
pip install -r requirements.txt

# 3) Executar
python .\app.py
```

A aplicação abrirá em http://localhost:8050/

Notas:
- Sem internet ou sem compartilhamento público no Google Sheets, coloque `data/PROCESSOS_ASSINADOS.xlsx` (mesmo layout) para o fallback funcionar.
- O logo (`assets/inpa_logo.png`) é referenciado no header; caso não exista, adicione sua imagem ou remova a linha do `html.Img` no `app.py`.


7) Parâmetros e customização
----------------------------

- ID da planilha Google: edite `GOOGLE_SHEET_ID` em `app.py`
- Timeout/retries do download: ajuste `load_data_from_google_sheets(sheet_url, timeout, max_retries)`
- Regex de vigência: refine `eh_vigente_status` conforme novas categorias de STATUS
- Normalização de modalidades: ajuste regras/prefixos em `normaliza_modalidade`
- Continentes: dicionário `ISO3_TO_CONTINENT` ampliável
- CSV de centróides:
  - Países: `data/iso3_centroids.csv` (auto-gerado)
  - UFs: `data/uf_centroids.csv` (opcional, manual)


8) Testes e validações
-----------------------

- Integração Google Sheets: `test_google_sheets.py`
  - Testa conectividade, download, leitura e estrutura mínima das colunas
- Validação ETL final: `data/teste_etl_final.py`
  - Exercita parsing ISO-3/UF, ano com fallback, filtro inclusivo e dicionário de continentes
- Scripts de qualidade: ver `data/SCRIPTS_VALIDACAO.md` (testes automatizados e limpeza/correções)

Execução (opcional):

```powershell
# Teste de integração com Google Sheets
python .\test_google_sheets.py

# Testes de validação ETL (dependem do Excel local)
python .\data\teste_etl_final.py
```

Observações:
- Os testes que dependem do Google podem falhar sem internet ou se a planilha não estiver pública.
- Os testes de ETL dependem do arquivo `data/PROCESSOS_ASSINADOS.xlsx` presente.


9) Troubleshooting
------------------

Problema: Erro 403 ao baixar do Google Sheets
- Causa: Planilha não está pública
- Ação: Compartilhe com “qualquer pessoa com o link”

Problema: O app abre com alerta de erro e não carrega dados
- Causas: Sem internet e sem fallback local; colunas mínimas ausentes
- Ações: Coloque `PROCESSOS_ASSINADOS.xlsx` em `data/` com as 5 colunas mínimas; veja `data/CHECKLIST_QUALIDADE.md`

Problema: País/UF não aparecem corretamente
- Causas: Erros de digitação em `PAÍS/ESTADO (ISO3)` ou múltiplas localizações na mesma célula
- Ações: Rode os scripts de correção em `data/SCRIPTS_VALIDACAO.md`

Problema: Logo não aparece
- Causa: `assets/inpa_logo.png` ausente
- Ação: Adicione o arquivo ou remova o `html.Img` do header em `app.py`


10) Desempenho e limites
------------------------

- O processamento é O(n) sobre o número de linhas da planilha
- Centróides são cacheados em CSV para evitar recalcular/baixar
- Gráficos e DataTable são suficientes para centenas a poucos milhares de linhas (escala modesta)
- Para datasets maiores: considere pré-ETL, caching, e/ou paginação mais forte na tabela


11) Segurança e privacidade
---------------------------

- O app consome um Google Sheets público por design (sem credenciais)
- Se usar dados sensíveis, mude a fonte para um backend autenticado (API) ou use credenciais de serviço
- Logs: a pasta `logs/` está disponível para registrar saídas se desejado (não há logging obrigatório no código atual)


12) Roadmap (sugestões)
------------------------

Curto prazo
- Padronizar `PESQUISADOR` e corrigir grafias (scripts prontos)
- Remover colunas `Unnamed: X` no Excel

Médio prazo
- Criar coluna `CATEGORIA` na planilha e migrar filtros do `tipo` para `CATEGORIA`
- Separar múltiplas localizações em linhas distintas
- Adicionar logging e testes unitários para helpers ETL

Longo prazo
- API de validação e ingestion
- Dashboard de qualidade de dados
- Versões/histórico da planilha (controle de mudanças)


13) Referências rápidas
-----------------------

- Execução local (PowerShell): ver seção 6
- Dicionário de STATUS: `data/DICIONARIO_STATUS.md`
- Tipos/categorias: `data/LISTA_TIPOS.md`
- Checklist e qualidade: `data/CHECKLIST_QUALIDADE.md`
- Scripts de validação/correção: `data/SCRIPTS_VALIDACAO.md`
- Estatísticas e resumo: `data/RESUMO_EXECUTIVO.md`


14) Licença e créditos
----------------------

Projeto interno INPA para visualização de cooperações e intercâmbios. Código em Python/Dash; dados pertencem aos seus respectivos responsáveis (DICIN/INPA). Verifique permissões antes de publicar/compartilhar dados.
