INPA Dashboard - Divisão de Cooperação e Intercâmbio
====================================================

Este repositório contém um dashboard interativo (Dash/Plotly) para visualizar acordos, convênios e parcerias do INPA, com dados oriundos de uma planilha pública do Google Sheets e fallback para um arquivo local Excel.

- App: `app.py` (Dash + Plotly + Pandas)
- Dados: Google Sheets (ID configurável) ou `data/PROCESSOS_ASSINADOS.xlsx`
- Visualizações: Mapa mundial/BR por marcadores, KPIs, pizza por modalidade, barras empilhadas por ano, ranking top países, tabela detalhada.

Para a documentação completa (visão técnica e operacional), consulte: `DOCUMENTACAO_COMPLETA.md`.


Como executar (Windows PowerShell)
----------------------------------

Pré-requisitos:
- Python 3.11+ (recomendado)
- Acesso à internet para Google Sheets OU arquivo local `data/PROCESSOS_ASSINADOS.xlsx`

Passos:

```powershell
# 1) Criar ambiente virtual (opcional, recomendado)
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 2) Instalar dependências
pip install -r requirements.txt

# 3) Executar o dashboard
python .\app.py
```

Acesse o app em http://localhost:8050/

Caso não haja acesso ao Google Sheets, coloque um arquivo `PROCESSOS_ASSINADOS.xlsx` em `data/` (mesmo layout esperado) e o app usará esse fallback automaticamente.


Principais funcionalidades
--------------------------

- Alternância de modo do mapa: Mundial 🌍 e Brasil 🇧🇷 (por UF)
- Filtros globais: Ano, Tipo, Modalidade, Continente, Status (apenas vigentes ou todos)
- KPIs: Vigência geral, Países com parcerias, Novos acordos (ano), Modalidade mais frequente
- Gráficos: distribuição por modalidade (pizza), evolução temporal (barras empilhadas)
- Ranking de países (top 10) e tabela detalhada filtrável por clique no mapa
- Layout moderno, acessível e responsivo (Bootstrap + Inter)


Estrutura do repositório (essencial)
------------------------------------

```
inpa-dash/
├─ app.py                      # Código do dashboard (Dash/Plotly/Pandas)
├─ requirements.txt            # Dependências do projeto
├─ DOCUMENTACAO_COMPLETA.md    # Documentação técnica e operacional detalhada
├─ VALIDACAO_COMPLETA.md       # (se aplicável) Relato consolidado de validações
├─ assets/
│   └─ styles.css              # Estilos customizados (opcional)
├─ data/
│   ├─ PROCESSOS_ASSINADOS.xlsx (opcional, fallback local)
│   ├─ br_states.geojson       # GeoJSON de UFs (auto-baixado se ausente)
│   ├─ RESUMO_EXECUTIVO.md     # Estatísticas e descobertas
│   ├─ DICIONARIO_STATUS.md    # Regras para STATUS vigente
│   ├─ LISTA_TIPOS.md          # Tipos/categorias de processos
│   ├─ CHECKLIST_QUALIDADE.md  # Validação de estrutura e dados
│   ├─ SCRIPTS_VALIDACAO.md    # Scripts para limpeza e validação
│   └─ README.txt              # Índice dos arquivos de dados
├─ logs/                       # (opcional) Saídas e erros de execução
└─ test_google_sheets.py       # Teste de conectividade com o Google Sheets
```


Configuração de dados
---------------------

O `app.py` tenta carregar primeiro do Google Sheets:

- ID configurado em `GOOGLE_SHEET_ID`
- URL de exportação automática: `https://docs.google.com/spreadsheets/d/{ID}/export?format=xlsx`

Se falhar, tenta `data/PROCESSOS_ASSINADOS.xlsx`. Sem um dos dois, o app exibe uma mensagem de erro amigável explicando o que fazer.

Colunas mínimas esperadas na planilha:
- `PAÍS/ESTADO (ISO3)` — País no formato "Nome (ISO3)" ou UF "Estado (UF)"
- `NÚMERO` — contém o ano no padrão .../2023-xx (regex `/(20\d{2})\b`)
- `STATUS` — utilizado para inferir vigência (regex robusta)
- `TIPO DE PROCESSO`
- `Contatos` ou `PESQUISADOR` — responsável


Documentos úteis
----------------

- Resumo executivo: `data/RESUMO_EXECUTIVO.md`
- Dicionário de STATUS: `data/DICIONARIO_STATUS.md`
- Lista e categorias de tipos: `data/LISTA_TIPOS.md`
- Checklist de qualidade: `data/CHECKLIST_QUALIDADE.md`
- Scripts de validação/correção: `data/SCRIPTS_VALIDACAO.md`
- Guia de uso rápido: `data/GUIA_USO_RAPIDO.md`
- Entrega/relato: `data/ENTREGA.md`


Suporte rápido
--------------

- Sem internet? Use o Excel em `data/`.
- Erro 403 no Sheets? Compartilhe a planilha com "qualquer pessoa com o link".
- Campos faltando? Verifique as colunas mínimas acima e `data/CHECKLIST_QUALIDADE.md`.
- Teste a integração: `python .\test_google_sheets.py`


Licença e créditos
------------------

Projeto interno INPA para visualização de cooperações e intercâmbios. Código em Python/Dash; dados pertencem aos seus respectivos responsáveis. Consulte a equipe da DICIN/INPA para dúvidas sobre uso e compartilhamento dos dados.

