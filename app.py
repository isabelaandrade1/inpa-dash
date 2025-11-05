# app.py
import json, re, os, unicodedata, time, hashlib, io, requests
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash import dash_table

# TEMPLATE PLOTLY CUSTOMIZADO

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=14, color="#1F2937"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F7FAFC",
        colorway=["#0B5ED7", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE", "#EEF2FF",
                  "#10B981", "#F59E0B", "#EF4444"],
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(font=dict(size=16, color="#1F2937", family="Inter"), x=0.02, xanchor="left"),
        xaxis=dict(
            gridcolor="#E5E7EB",
            linecolor="#E5E7EB",
            tickfont=dict(size=12, color="#6B7280"),
            title=dict(font=dict(size=13, color="#6B7280"))
        ),
        yaxis=dict(
            gridcolor="#E5E7EB",
            linecolor="#E5E7EB",
            tickfont=dict(size=12, color="#6B7280"),
            title=dict(font=dict(size=13, color="#6B7280"))
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font=dict(family="Inter", size=12, color="#1F2937"),
            bordercolor="#E5E7EB"
        ),
        legend=dict(
            font=dict(size=12, color="#6B7280"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E5E7EB",
            borderwidth=1
        )
    )
)

# ============================================================================
# HELPERS DE COMPONENTES UI
# ============================================================================
def kpi_card(label: str, value: str, icon: str = "📊") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.Div(icon, style={"fontSize": "20px", "marginBottom": "8px", "opacity": "0.7"}),
            html.Div(value, style={
                "fontSize": "28px",
                "fontWeight": "700",
                "color": "#1F2937",
                "LineHeight": "1.2",
                "marginBottom": "4px"
            }),
            html.Div(label, style={
                "fontSize": "13px",
                "color": "#6B7280",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px",
                "fontWeight": "500"
            })
        ], style={"textAlign": "center", "padding": "20px"})
        , style={
            "borderRadius": "18px",
            "border": "1px solid #E5E7EB",
            "boxShadow": "0 6px 20px rgba(0,0,0,0.04)",
            "backgroundColor": "#FFFFFF",
            "height": "100%"
        }
    )

def chart_card(title: str, chart_component) -> dbc.Card:
    return dbc.Card([
        dbc.CardHeader(
            html.H6(title, style={
                "margin": "0",
                "fontSize": "13px",
                "fontWeight": "600",
                "color": "#6B7280",
                "textTransform": "uppercase",
                "letterSpacing": "0.8px"
            }),
            style={"backgroundColor": "#F7FAFC", "border": "none", "padding": "16px 20px"}
        ),
        dbc.CardBody(chart_component, style={"padding": "20px"})
    ], style={
        "borderRadius": "18px",
        "border": "1px solid #E5E7EB",
        "boxShadow": "0 6px 20px rgba(0,0,0,0.04)",
        "backgroundColor": "#FFFFFF",
        "marginBottom": "20px"
    })

def create_ranking_list(data: pd.DataFrame, label_col: str, value_col: str, max_items: int = 10) -> html.Div:
    colors = ["#0B5ED7", "#3B82F6", "#60A5FA", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"]
    items = []
    for idx, row in data.head(max_items).iterrows():
        color = colors[idx % len(colors)]
        items.append(
            html.Div([
                html.Div(style={
                    "width": "10px",
                    "height": "10px",
                    "borderRadius": "50%",
                    "backgroundColor": color,
                    "marginRight": "12px",
                    "flexShrink": "0"
                }),
                html.Div(row[label_col], style={
                    "flex": "1",
                    "fontSize": "14px",
                    "color": "#1F2937",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap"
                }),
                html.Div(str(row[value_col]), style={
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "color": "#0B5ED7",
                    "marginLeft": "12px"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "padding": "10px 0",
                "borderBottom": "1px solid #F3F4F6"
            })
        )
    return html.Div(items, style={"padding": "0 4px"})

# =========================================================
# CONFIGURAÇÃO DE ARQUIVOS E GOOGLE SHEETS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Google Sheets Configuration
GOOGLE_SHEET_ID = "1hPoZOGtQV0fAMCFoviE9PVuhmYArA6BQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx"

EXCEL_PATH = DATA_DIR / "PROCESSOS_ASSINADOS.xlsx"  # Fallback local
BR_STATES_PATH = DATA_DIR / "br_states.geojson"

# =========================================================
# HELPERS DE ETL
# =========================================================
UF_NOMES = {
    "AC":"Acre","AL":"Alagoas","AM":"Amazonas","AP":"Amapá","BA":"Bahia","CE":"Ceará",
    "DF":"Distrito Federal","ES":"Espírito Santo","GO":"Goiás","MA":"Maranhão","MG":"Minas Gerais",
    "MS":"Mato Grosso do Sul","MT":"Mato Grosso","PA":"Pará","PB":"Paraíba","PE":"Pernambuco",
    "PI":"Piauí","PR":"Paraná","RJ":"Rio de Janeiro","RN":"Rio Grande do Norte","RO":"Rondônia",
    "RR":"Roraima","RS":"Rio Grande do Sul","SC":"Santa Catarina","SE":"Sergipe","SP":"São Paulo","TO":"Tocantins"
}
UF_SET = set(UF_NOMES.keys())

ISO3_TO_CONTINENT = {
    "BRA":"América do Sul","ARG":"América do Sul","CHL":"América do Sul","COL":"América do Sul","PER":"América do Sul",
    "URY":"América do Sul","PRY":"América do Sul","BOL":"América do Sul","ECU":"América do Sul","VEN":"América do Sul",
    "GUY":"América do Sul","SUR":"América do Sul","GUF":"América do Sul",
    "USA":"América do Norte","CAN":"América do Norte","MEX":"América do Norte",
    "GTM":"América Central","BLZ":"América Central","SLV":"América Central","HND":"América Central",
    "NIC":"América Central","CRI":"América Central","PAN":"América Central",
    "DEU":"Europa","FRA":"Europa","ESP":"Europa","PRT":"Europa","ITA":"Europa","GBR":"Europa","NLD":"Europa","SWE":"Europa",
    "NOR":"Europa","DNK":"Europa","FIN":"Europa","POL":"Europa","AUT":"Europa","CHE":"Europa","BEL":"Europa","IRL":"Europa",
    "GRC":"Europa","CZE":"Europa","HUN":"Europa","ROU":"Europa","BGR":"Europa","HRV":"Europa","SVK":"Europa","SVN":"Europa",
    "LTU":"Europa","LVA":"Europa","EST":"Europa","UKR":"Europa","RUS":"Europa",
    "MOZ":"África","ZAF":"África","AGO":"África","GHA":"África","EGY":"África",
    "NGA":"África","KEN":"África","ETH":"África","TZA":"África","UGA":"África","MAR":"África","DZA":"África",
    "CHN":"Ásia","JPN":"Ásia","KOR":"Ásia","IND":"Ásia","IDN":"Ásia","THA":"Ásia","VNM":"Ásia",
    "MYS":"Ásia","SGP":"Ásia","PHL":"Ásia","PAK":"Ásia","BGD":"Ásia","LKA":"Ásia","MMR":"Ásia",
    "KHM":"Ásia","LAO":"Ásia","NPL":"Ásia","AFG":"Ásia","IRN":"Ásia","IRQ":"Ásia","SAU":"Ásia",
    "ARE":"Ásia","ISR":"Ásia","TUR":"Ásia","KAZ":"Ásia","UZB":"Ásia","TWN":"Ásia","HKG":"Ásia",
    "AUS":"Oceania","NZL":"Oceania","PNG":"Oceania","FJI":"Oceania","NCL":"Oceania","PYF":"Oceania",
}

def load_iso3_centroids(path: Path) -> dict:
    if path.exists():
        try:
            centroids_df = pd.read_csv(path)
            return {row["iso3"]: (row["lat"], row["lon"]) for _, row in centroids_df.iterrows()}
        except Exception as e:
            print(f"⚠️  Erro ao carregar {path}: {e}")
    print(f"📥 Centroides não encontrados em {path}, tentando baixar GeoJSON...")
    try:
        import requests
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        geojson = r.json()
        centroids = {}
        try:
            from shapely.geometry import shape
            for feature in geojson.get("features", []):
                iso3 = feature.get("id")
                if iso3:
                    geom = shape(feature["geometry"])
                    centroid = geom.centroid
                    centroids[iso3] = (centroid.y, centroid.x)
        except ImportError:
            print("⚠️  shapely não disponível, usando centroide aproximado")
            for feature in geojson.get("features", []):
                iso3 = feature.get("id")
                if iso3:
                    coords = feature["geometry"].get("coordinates", [])
                    if coords:
                        all_points = []
                        def extract_points(c):
                            if isinstance(c, (int, float)):
                                return
                            if len(c) == 2 and isinstance(c[0], (int, float)):
                                all_points.append(c)
                            else:
                                for item in c:
                                    extract_points(item)
                        extract_points(coords)
                        if all_points:
                            avg_lon = sum(p[0] for p in all_points) / len(all_points)
                            avg_lat = sum(p[1] for p in all_points) / len(all_points)
                            centroids[iso3] = (avg_lat, avg_lon)
        if centroids:
            centroids_df = pd.DataFrame([
                {"iso3": iso3, "lat": lat, "lon": lon}
                for iso3, (lat, lon) in centroids.items()
            ])
            centroids_df.to_csv(path, index=False)
            print(f"✅ Centroides salvos em {path}")
        return centroids
    except Exception as e:
        print(f"❌ Erro ao baixar/calcular centroides: {e}")
        return {}

# ============================================================================
# PARSERS / NORMALIZADORES
# ============================================================================
def normaliza_modalidade(texto: str) -> str:
    if pd.isna(texto) or not str(texto).strip():
        return "Outros"
    s = str(texto).strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[-_/]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    rules = [
        (r'\btermo\s+ad[it]+[iv]*o\b',                 "Termo Aditivo"),
        (r'\bacordo[s]?\s+(de\s+)?parceria[s]?\b',     "Acordo de Parceria"),
        (r'\bacordo[s]?\s+de\s+coopera[cç]ao\b',       "Acordo de Cooperação"),
        (r'\bacordo[s]?\s+de\s+co[\s\-]?tutela\b',     "Acordo de Cotutela"),
        (r'\bmemorando\s+de\s+entendimento[s]?\b',     "Memorando de Entendimento (MoU)"),
        (r'\bm[\s\.]*o[\s\.]*u\b',                     "Memorando de Entendimento (MoU)"),
        (r'\bprotocolo\s+de\s+inten[cç](ao|oes)\b',    "Protocolo de Intenções"),
        (r'\bconve?nio\s+de\s+esta?gio\b',             "Convênio de Estágio"),
        (r'\bconve?nio[s]?\b',                         "Convênio"),
        (r'\btermo\s+de\s+coopera[cç]ao\b',            "Termo de Cooperação"),
        (r'\btermo\s+de\s+adesao\b',                   "Termo de Adesão"),
        (r'\btermo\s+de\s+parceria\b',                 "Termo de Parceria"),
        (r'\bcarta[\s\-\/]*convite\b',                 "Carta Convite"),
        (r'\bexpedi[cç]ao\s+de\s+certidao\b',          "Expedição de Certidão"),
        (r'\bexpedi[cç]ao\s+cientifica\b',             "Expedição Científica"),
        (r'\bprojeto[s]?\b',                           "Projeto"),
    ]
    for pat, label in rules:
        if re.search(pat, s):
            return label
    prefixes = {
        "termo aditivo": "Termo Aditivo",
        "termo adtivo": "Termo Aditivo",
        "acordo parceria": "Acordo de Parceria",
        "acordo de parceria": "Acordo de Parceria",
        "acordo de cooperacao": "Acordo de Cooperação",
        "acordo de cotutela": "Acordo de Cotutela",
        "acordo de co tutela": "Acordo de Cotutela",
        "memorando de entendimento": "Memorando de Entendimento (MoU)",
        "protocolo de intencoes": "Protocolo de Intenções",
        "convenio de estagio": "Convênio de Estágio",
        "convenio": "Convênio",
        "termo de cooperacao": "Termo de Cooperação",
        "termo de adesao": "Termo de Adesão",
        "termo de parceria": "Termo de Parceria",
        "carta convite": "Carta Convite",
        "expedicao de certidao": "Expedição de Certidão",
        "expedicao cientifica": "Expedição Científica",
        "projeto": "Projeto",
    }
    for pref, label in prefixes.items():
        if s.startswith(pref):
            return label
    return "Outros"

def parse_pais_ou_uf(val: str) -> dict:
    if pd.isna(val):
        return {"nivel":"pais","pais":pd.NA,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    s = str(val).strip()
    codes = re.findall(r'\(\s*([A-Za-z]{2,3})\s*\)', s)
    if not codes:
        pais_nome = s.strip()
        return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    cod = codes[-1].strip().upper()
    CODIGOS_INVALIDOS = {'-99', 'NULL', 'N/A', 'NA'}
    if cod in CODIGOS_INVALIDOS or cod.isdigit():
        pais_nome = re.sub(r'\([^)]+\)\s*$', "", s).strip()
        return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    if len(cod) == 2 and cod.isalpha():
        if cod in UF_SET:
            return {
                "nivel":"uf_br","pais":"Brasil","iso3":"BRA",
                "uf_sigla":cod,"uf_nome":UF_NOMES[cod]
            }
        else:
            pais_nome = re.sub(r'\([^)]+\)\s*$', "", s).strip()
            return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    elif len(cod) == 3 and cod.isalpha():
        pais_nome = re.sub(r'\([^)]+\)\s*$', "", s).strip()
        return {"nivel":"pais","pais": pais_nome if pais_nome else "Desconhecido",
                "iso3":cod,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    else:
        pais_nome = re.sub(r'\([^)]+\)\s*$', "", s).strip()
        return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}

def infer_year_from_num(num):
    if pd.isna(num): 
        return pd.NA
    m = re.search(r'/(20\d{2})\b', str(num))
    return int(m.group(1)) if m else pd.NA

def infer_year_multi_column(row, num_col="NÚMERO", date_cols=None):
    if num_col in row.index and pd.notna(row[num_col]):
        m = re.search(r'/(20\d{2})\b', str(row[num_col]))
        if m:
            return int(m.group(1))
    if date_cols:
        for col in date_cols:
            if col in row.index and pd.notna(row[col]):
                val = row[col]
                if isinstance(val, pd.Timestamp):
                    return val.year
                val_str = str(val).strip()
                m = re.search(r'\b(20\d{2})\b', val_str)
                if m:
                    return int(m.group(1))
    return pd.NA

# ============================================================================
# MAPAS (MUNDIAL E BRASIL) — corrigindo customdata
# ============================================================================
def _agg_pins_world(dff: pd.DataFrame, centroids: dict):
    paises = dff[dff["nivel_localizacao"] == "pais"].copy()
    grp = paises.groupby(["codigo_iso3", "eh_vigente"], dropna=True).size().reset_index(name="qtd")
    meta = paises.groupby("codigo_iso3", dropna=True)["pais"].first().rename("pais").reset_index()
    agg = grp.merge(meta, on="codigo_iso3", how="left")
    agg["lat"] = agg["codigo_iso3"].map(lambda iso: centroids.get(iso, (None, None))[0])
    agg["lon"] = agg["codigo_iso3"].map(lambda iso: centroids.get(iso, (None, None))[1])
    agg = agg.dropna(subset=["lat", "lon"])
    max_qtd = agg["qtd"].max() if len(agg) else 1
    agg["marker_size"] = agg["qtd"].apply(lambda q: max(8, min(24, 8 + (q / max_qtd) * 16)))
    return agg

def build_world_marker_map(dff: pd.DataFrame, centroids: dict, clicked_iso3: str = None) -> go.Figure:
    agg = _agg_pins_world(dff, centroids)
    fig = go.Figure()

    # Demais (cinza) – borda escura
    nao = agg[agg["eh_vigente"] == False]
    if len(nao):
        fig.add_trace(go.Scattergeo(
            lon=nao["lon"], lat=nao["lat"],
            mode="markers", name="Demais",
            marker=dict(
                size=nao["marker_size"],
                color="#4B5563",
                line=dict(color="#1F2937", width=1.4),
                opacity=0.90
            ),
            hovertemplate="<b>%{text}</b><br>%{customdata[1]} acordos<extra></extra>",
            text=nao["pais"], 
            customdata=nao[["codigo_iso3", "qtd"]].values,
            showlegend=True
        ))

    # Vigentes (verde) – mais saturado e com borda
    vig = agg[agg["eh_vigente"] == True]
    if len(vig):
        fig.add_trace(go.Scattergeo(
            lon=vig["lon"], lat=vig["lat"],
            mode="markers", name="Vigente",
            marker=dict(
                size=vig["marker_size"],
                color="#F97316",               # laranja vibrante
                line=dict(color="#FBBF24", width=1.6),
                opacity=0.95
            ),
            hovertemplate="<b>%{text}</b><br>%{customdata[1]} acordos (vigentes)<extra></extra>",
            text=vig["pais"], 
            customdata=vig[["codigo_iso3", "qtd"]].values,
            showlegend=True
        ))

    # ⬇️ Geografia com mais contraste
    fig.update_geos(
        projection_type="natural earth",
        showframe=True, framecolor="#1F2937",
        showcountries=True, countrycolor="#4B5563", countrywidth=1.1,
        showcoastlines=True, coastlinecolor="#374151", coastlinewidth=1.2,
        showland=True, landcolor="#E5E7EB",
        showocean=True, oceancolor="#BFDBFE",
        showlakes=True, lakecolor="#93C5FD",
        bgcolor="#FFFFFF"
    )
    fig.update_layout(
        template="none",                      # evita tons "lavados"
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF",
        geo=dict(bgcolor="#FFFFFF")
    )
    return fig

def build_brazil_marker_map(dff: pd.DataFrame, uf_centroids: dict) -> go.Figure:
    br = dff[dff["codigo_iso3"] == "BRA"].copy()
    grp = br.groupby(["uf_sigla", "eh_vigente"], dropna=False).size().reset_index(name="qtd")
    meta = br.groupby("uf_sigla", dropna=False)[["uf_nome"]].first().reset_index()
    agg = grp.merge(meta, on="uf_sigla", how="left")
    agg = agg[agg["uf_sigla"].notna()].copy()
    agg["lat"] = agg["uf_sigla"].map(lambda uf: uf_centroids.get(uf, (None, None))[0])
    agg["lon"] = agg["uf_sigla"].map(lambda uf: uf_centroids.get(uf, (None, None))[1])
    agg = agg.dropna(subset=["lat", "lon"])
    max_qtd = agg["qtd"].max() if len(agg) else 1
    agg["marker_size"] = agg["qtd"].apply(lambda q: max(8, min(28, 8 + (q / max_qtd) * 18)))

    fig = go.Figure()

    # Demais
    nao = agg[agg["eh_vigente"] == False]
    if len(nao):
        fig.add_trace(go.Scattergeo(
            lon=nao["lon"], lat=nao["lat"], mode="markers", name="Demais",
            marker=dict(
                size=nao["marker_size"],
                color="#4B5563",
                line=dict(color="#1F2937", width=1.4),
                opacity=0.90
            ),
            hovertemplate="<b>%{text}</b><br>%{customdata[1]} acordos<extra></extra>",
            text=nao["uf_sigla"], 
            customdata=nao[["uf_sigla", "qtd"]].values,
            showlegend=True
        ))

    # Vigentes
    vig = agg[agg["eh_vigente"] == True]
    if len(vig):
        fig.add_trace(go.Scattergeo(
            lon=vig["lon"], lat=vig["lat"], mode="markers", name="Vigente",
            marker=dict(
                size=vig["marker_size"],
                color="#F97316",
                line=dict(color="#FBBF24", width=1.6),
                opacity=0.95
            ),
            hovertemplate="<b>%{text}</b><br>%{customdata[1]} acordos (vigentes)<extra></extra>",
            text=vig["uf_sigla"], 
            customdata=vig[["uf_sigla", "qtd"]].values,
            showlegend=True
        ))

    # ⬇️ Geografia com mais contorno e fundo levemente azulado
    fig.update_geos(
        projection_type="mercator",
        center=dict(lat=-14, lon=-55),
        lataxis_range=[-35, 6], lonaxis_range=[-74, -32],
        showcountries=True, countrycolor="#374151", countrywidth=1.2,
        showcoastlines=True, coastlinecolor="#374151", coastlinewidth=1.0,
        showland=True, landcolor="#E5E7EB",
        showocean=True, oceancolor="#BFDBFE",
        showlakes=True, lakecolor="#93C5FD",
        bgcolor="#FFFFFF"
    )
    fig.update_layout(
        template="none",
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF",
        geo=dict(bgcolor="#FFFFFF")
    )
    return fig

# =========================================================
# CARREGAR DADOS DO GOOGLE SHEETS
# =========================================================
def load_data_from_google_sheets(sheet_url: str, timeout: int = 30, max_retries: int = 3) -> pd.DataFrame:
    """
    Carrega dados diretamente do Google Sheets de forma robusta.
    
    Args:
        sheet_url: URL de exportação do Google Sheets (.xlsx)
        timeout: Timeout em segundos para cada tentativa
        max_retries: Número máximo de tentativas
    
    Returns:
        DataFrame com os dados da planilha
    
    Raises:
        Exception: Se não conseguir carregar após todas as tentativas
    """
    print(f"🔄 Tentando carregar planilha do Google Sheets...")
    
    for tentativa in range(1, max_retries + 1):
        try:
            print(f"   Tentativa {tentativa}/{max_retries}...")
            
            # Download do arquivo Excel
            response = requests.get(sheet_url, timeout=timeout)
            response.raise_for_status()
            
            # Ler o conteúdo diretamente na memória
            excel_data = io.BytesIO(response.content)
            df = pd.read_excel(excel_data, engine='openpyxl')
            
            print(f"✅ Planilha carregada com sucesso! {len(df)} linhas encontradas.")
            return df
            
        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout na tentativa {tentativa}. A conexão está demorando muito...")
            if tentativa == max_retries:
                raise Exception(
                    "Não foi possível carregar a planilha: timeout após múltiplas tentativas. "
                    "Verifique sua conexão com a internet."
                )
            time.sleep(2 * tentativa)  # Espera progressiva
            
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Erro de conexão na tentativa {tentativa}...")
            if tentativa == max_retries:
                raise Exception(
                    "Não foi possível conectar ao Google Sheets. "
                    "Verifique sua conexão com a internet."
                )
            time.sleep(2 * tentativa)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(
                    "Acesso negado ao Google Sheets. "
                    "Verifique se a planilha está compartilhada publicamente ou com 'qualquer pessoa com o link'."
                )
            elif e.response.status_code == 404:
                raise Exception(
                    "Planilha não encontrada. Verifique se o ID da planilha está correto."
                )
            else:
                print(f"⚠️  Erro HTTP {e.response.status_code} na tentativa {tentativa}...")
                if tentativa == max_retries:
                    raise Exception(f"Erro ao acessar Google Sheets: {str(e)}")
            time.sleep(2 * tentativa)
            
        except Exception as e:
            print(f"⚠️  Erro inesperado na tentativa {tentativa}: {str(e)}")
            if tentativa == max_retries:
                raise Exception(f"Erro ao processar planilha: {str(e)}")
            time.sleep(2 * tentativa)
    
    raise Exception("Falha ao carregar dados após todas as tentativas.")

# Tentar carregar do Google Sheets primeiro, com fallback para arquivo local
try:
    df_raw = load_data_from_google_sheets(GOOGLE_SHEET_URL)
    DATA_SOURCE = "Google Sheets"
except Exception as e:
    print(f"❌ Erro ao carregar do Google Sheets: {str(e)}")
    print(f"🔄 Tentando carregar arquivo local como fallback...")
    
    if not EXCEL_PATH.exists():
        # Se não há fallback local, mostrar erro amigável
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        server = app.server
        app.layout = dbc.Container([
            dbc.Alert([
                html.H4("⚠️ Erro ao Carregar Dados", className="alert-heading"),
                html.P([
                    "Não foi possível carregar os dados do Google Sheets e não há arquivo local disponível.",
                    html.Br(), html.Br(),
                    html.Strong("Erro: "), str(e)
                ]),
                html.Hr(),
                html.P("Soluções possíveis:", className="mb-2", style={"fontWeight": "600"}),
                html.Ol([
                    html.Li([
                        html.Strong("Verifique sua conexão com a internet"), 
                        " - O aplicativo precisa acessar o Google Sheets online."
                    ]),
                    html.Li([
                        html.Strong("Verifique as permissões da planilha"), 
                        " - A planilha precisa estar compartilhada com 'qualquer pessoa com o link'."
                    ]),
                    html.Li([
                        html.Strong("Arquivo local alternativo"), 
                        " - Coloque o arquivo 'PROCESSOS_ASSINADOS.xlsx' na pasta 'data/' como backup."
                    ]),
                ]),
                html.Hr(),
                html.P("Formato esperado da planilha:", className="mb-1", style={"fontWeight": "600"}),
                html.Ul([
                    html.Li("Coluna 'PAÍS/ESTADO (ISO3)' → ex.: 'Reino Unido (GBR)' ou 'Amazonas (AM)'"),
                    html.Li("Coluna 'NÚMERO' → ex.: '01280.000381/2023-95' (contém o ano)"),
                    html.Li("Coluna 'STATUS'"),
                    html.Li("Coluna 'TIPO DE PROCESSO'"),
                    html.Li("Coluna 'Contatos' ou 'PESQUISADOR' → pesquisador responsável"),
                ]),
            ], color="danger")
        ], fluid=True, style={"maxWidth": "900px", "marginTop": "40px"})
        
        if __name__ == "__main__":
            app.run_server(debug=True, host="0.0.0.0", port=8050)
        raise SystemExit
    else:
        # Usar arquivo local como fallback
        try:
            df_raw = pd.read_excel(EXCEL_PATH)
            DATA_SOURCE = "Arquivo Local (Fallback)"
            print(f"✅ Dados carregados do arquivo local: {len(df_raw)} linhas")
        except Exception as local_error:
            raise Exception(
                f"Falha ao carregar tanto do Google Sheets quanto do arquivo local. "
                f"Google Sheets: {str(e)}. Arquivo local: {str(local_error)}"
            )

# tenta achar a coluna de país/estado
col_pais = None
for col in df_raw.columns:
    if "PAÍS" in col.upper() or "PAIS" in col.upper():
        col_pais = col; break
if col_pais is None:
    raise ValueError("Coluna de PAÍS/ESTADO não encontrada no Excel. Colunas: " + str(list(df_raw.columns)))

parsed = df_raw[col_pais].apply(parse_pais_ou_uf).apply(pd.Series)
df = df_raw.copy()
df["nivel_localizacao"] = parsed["nivel"]
df["pais"]             = parsed["pais"]
df["codigo_iso3"]      = parsed["iso3"]
df["uf_sigla"]         = parsed["uf_sigla"]
df["uf_nome"]          = parsed["uf_nome"]

date_cols_candidates = [c for c in df_raw.columns if any(kw in c.upper() for kw in ["DATA", "ANO", "YEAR", "DATE"])]
if date_cols_candidates:
        df["ano_assinatura"] = df.apply(
        lambda row: infer_year_multi_column(row, num_col="NÚMERO", date_cols=date_cols_candidates),
        axis=1
    )
else:
    df["ano_assinatura"] = df["NÚMERO"].apply(infer_year_from_num)

# Padronizações de campos-base
df["tipo"] = df["TIPO DE PROCESSO"].fillna("Não informado")

# Usar coluna "Contatos" se existir, senão usar "PESQUISADOR"
if "Contatos" in df.columns:
    df["pesquisador_responsavel"] = df["Contatos"].fillna("Não informado")
elif "PESQUISADOR" in df.columns:
    df["pesquisador_responsavel"] = df["PESQUISADOR"].fillna("Não informado")
else:
    df["pesquisador_responsavel"] = "Não informado"

df["status"] = df["STATUS"].astype(str)

# Modalidade normalizada
df["modalidade"] = df["TIPO DE PROCESSO"].fillna("Outros").apply(normaliza_modalidade)

# -------------------------
# Vigência robusta
# -------------------------
def eh_vigente_status(txt: str) -> bool:
    """
    Regras:
      - conta como vigente se houver 'vigente', 'vigentes', 'em vigor', 'assinado'
      - ignora quando houver negação próxima: 'não vigente', 'nao vigente', 'não está vigente', etc.
    """
    if not isinstance(txt, str) or not txt.strip():
        return False
    s = unicodedata.normalize("NFD", txt.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # remove acentos

    # negação explícita perto de 'vigente'
    if re.search(r"\bnao\s+vigent\w*\b", s) or re.search(r"\bnao\s+esta\s+vigent\w*\b", s):
        return False
    if re.search(r"\bnao\s+esta\s+em\s+vigor\b", s):
        return False
    if re.search(r"\bnao\s+assinado\b", s):
        return False

    # positivo
    if re.search(r"\bvigent\w*\b", s):
        return True
    if re.search(r"\bem\s+vigor\b", s):
        return True
    if re.search(r"\bassinad\w*\b", s):  # assinado/assinada
        return True

    return False

df["eh_vigente"] = df["status"].apply(eh_vigente_status)

# Continente
def infer_continent(row):
    if row["nivel_localizacao"] == "uf_br" or row["codigo_iso3"] == "BRA":
        return "América do Sul"
    iso = str(row["codigo_iso3"]) if pd.notna(row["codigo_iso3"]) else ""
    return ISO3_TO_CONTINENT.get(iso, "Não informado")

df["continente"] = df.apply(infer_continent, axis=1)

# -------------------------
# Opções de filtros
# -------------------------
anos_validos = pd.to_numeric(df["ano_assinatura"], errors="coerce").dropna().astype(int)
anos_opts = ["Todos"] + sorted(anos_validos.unique().tolist())
tipos_opts = sorted(df["tipo"].dropna().unique().tolist())
conts_opts = sorted(df["continente"].dropna().unique().tolist())
modalidades_opts = sorted(df["modalidade"].dropna().unique().tolist())

# =========================================================
# CENTROIDES
# =========================================================
CENTROIDS_PATH = DATA_DIR / "iso3_centroids.csv"
centroids_dict = load_iso3_centroids(CENTROIDS_PATH)
# Pequenos fallbacks úteis
FALLBACK_CENTROIDS = {
    "CHN": (35.0, 103.0),"USA": (37.0, -95.0),"GBR": (54.0, -2.0),"FRA": (46.0, 2.0),
    "DEU": (51.0, 10.0),"JPN": (36.0, 138.0),"IND": (20.0, 77.0),"CAN": (56.0, -106.0),
    "AUS": (-25.0, 133.0),"RUS": (60.0, 100.0),
}
for iso3, coords in FALLBACK_CENTROIDS.items():
    centroids_dict.setdefault(iso3, coords)

# UF centroids opcionais
UF_CENTROIDS_PATH = DATA_DIR / "uf_centroids.csv"
uf_centroids_dict = {}
if UF_CENTROIDS_PATH.exists():
    try:
        uf_centroids_df = pd.read_csv(UF_CENTROIDS_PATH)
        uf_centroids_dict = {row["uf"]: (row["lat"], row["lon"]) for _, row in uf_centroids_df.iterrows()}
    except Exception as e:
        print(f"⚠️  Erro ao carregar centroides de UFs: {e}")

# =========================================================
# GEOJSON UFs (compat futuro – não é necessário pro marker map)
# =========================================================
BR_STATES_PATH.parent.mkdir(parents=True, exist_ok=True)
if not BR_STATES_PATH.exists():
    try:
        import requests
        url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/ufs.json"
        r = requests.get(url, timeout=20)
        if r.ok:
            with open(BR_STATES_PATH, "w", encoding="utf-8") as f:
                f.write(r.text)
    except Exception:
        pass

# =========================================================
# APP & LAYOUT (com filtro GLOBAL por ANO)
# =========================================================
app = Dash(__name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
    ],
    external_scripts=["https://twemoji.maxcdn.com/v/latest/twemoji.min.js"],
    meta_tags=[{"name": "language", "content": "pt-BR"}]
)
app.index_string = """
<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        {%metas%}
        <title>INPA • Divisão de Cooperação e Intercambio</title>
        {%favicon%}
        {%css%}
        <style>
            :root, body, button, .btn {
                font-family: Inter, system-ui, -apple-system, "Apple Color Emoji",
                             "Segoe UI Emoji", "Noto Color Emoji", "Segoe UI Symbol", sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                if (window.twemoji) twemoji.parse(document.body, {folder: 'svg', ext: '.svg'});
            });
        </script>
        <footer>{%config%}{%scripts%}{%renderer%}</footer>
    </body>
</html>
"""
server = app.server

store_modo = dcc.Store(id="modo-mapa", data="world")

header = html.Div([
    html.Div([
        html.Img(
            src=app.get_asset_url("inpa_logo.png"),
            style={
                "height": "120px", 
                "width": "auto", 
                "display": "block",
                "margin": "0",
                "padding": "0"
            }
        ),
        html.H1("Divisão de Cooperação e Intercâmbio", style={
            "fontSize": "28px", 
            "fontWeight": "700", 
            "color": "#1F2937", 
            "margin": "0",
            "padding": "0",
            "lineHeight": "1",
            "display": "flex",
            "alignItems": "center"
        }),
    ], style={
        "display": "flex", 
        "alignItems": "center", 
        "gap": "14px",
        "justifyContent": "flex-start"
    }),
], style={
    "padding": "16px 24px",
    "backgroundColor": "#FFFFFF",
    "borderBottom": "1px solid #E5E7EB",
    "marginBottom": "20px",
    "borderRadius": "0 0 18px 18px",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.03)"
})

# Botão para toggle dos filtros
filters_toggle = html.Div([
    dbc.Button(
        [html.I(className="bi bi-funnel-fill", style={"marginRight": "8px"}), "Filtros"],
        id="toggle-filters",
        color="primary",
        size="sm",
        style={
            "borderRadius": "12px",
            "fontSize": "14px",
            "fontWeight": "600",
            "padding": "10px 20px",
            "boxShadow": "0 2px 8px rgba(11, 94, 215, 0.2)"
        }
    )
], style={"marginBottom": "12px"})

# Barra de filtros colapsável
filters_bar = dbc.Collapse(
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("ANO", className="mb-1", style={"fontSize":"12px","textTransform":"uppercase","color":"#6B7280","fontWeight":"600"}),
                    dcc.Dropdown(id="filtro-ano", options=[{"label": str(a), "value": a} for a in anos_opts],
                                 value="Todos", clearable=False, style={"fontSize":"14px"})
                ], md=2),
                dbc.Col([
                    html.Label("TIPOS DE PROCESSO", className="mb-1", style={"fontSize":"12px","textTransform":"uppercase","color":"#6B7280","fontWeight":"600"}),
                    dcc.Dropdown(id="filtro-tipos", options=[{"label": t, "value": t} for t in tipos_opts],
                                 value=tipos_opts, multi=True, placeholder="Selecione tipos...", style={"fontSize":"14px"})
                ], md=3),
                dbc.Col([
                    html.Label("MODALIDADES", className="mb-1", style={"fontSize":"12px","textTransform":"uppercase","color":"#6B7280","fontWeight":"600"}),
                    dcc.Dropdown(id="filtro-modalidades", options=[{"label": m, "value": m} for m in modalidades_opts],
                                 value=modalidades_opts, multi=True, placeholder="Selecione modalidades...", style={"fontSize":"14px"})
                ], md=3),
                dbc.Col([
                    html.Label("CONTINENTES", className="mb-1", style={"fontSize":"12px","textTransform":"uppercase","color":"#6B7280","fontWeight":"600"}),
                    dcc.Dropdown(id="filtro-continentes", options=[{"label": c, "value": c} for c in conts_opts],
                                 value=conts_opts, multi=True, placeholder="Selecione continentes...", style={"fontSize":"14px"})
                ], md=3),
                dbc.Col([
                    html.Label("STATUS", className="mb-1", style={"fontSize":"12px","textTransform":"uppercase","color":"#6B7280","fontWeight":"600"}),
                    dbc.RadioItems(
                        id="filtro-status",
                        options=[{"label":"Todos","value":"todos"},{"label":"Apenas vigentes","value":"vigentes"}],
                        value="todos", inline=True, input_style={"marginRight":"6px"}, style={"fontSize":"14px"}
                    )
                ], md=1),
            ], className="g-3")
        ]),
        style={"borderRadius":"14px","border":"1px solid #E5E7EB","marginBottom":"16px"}
    ),
    id="collapse-filters",
    is_open=False
)

# Botões de modo de mapa (acima do mapa)
map_mode_buttons = html.Div([
    dbc.Button("🌍 Mundial", id="btn-world", color="light", size="sm", 
              style={"borderRadius": "10px", "marginRight": "8px", "fontSize": "13px", "fontWeight": "600", "color": "#000000"}),
    dbc.Button(
        [html.Img(src="https://flagcdn.com/w20/br.png",
                  style={"height":"14px","marginRight":"6px"}), "Brasil"],
        id="btn-br", color="light", size="sm",
        style={"borderRadius": "10px", "fontSize": "13px", "fontWeight": "600", "color": "#000000"}
    ),
], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"})

# Stores para scroll automático
scroll_store = dcc.Store(id="scroll-trigger")
scroll_sink = html.Div(id="scroll-sink", style={"display": "none"})

app.layout = dbc.Container([
    header, store_modo, scroll_store, scroll_sink, filters_toggle, filters_bar,
    dbc.Row([
        dbc.Col(html.Div(id="kpi-total"), md=3),
        dbc.Col(html.Div(id="kpi-paises"), md=3),
        dbc.Col(html.Div(id="kpi-tipos"), md=3),
        dbc.Col(html.Div(id="kpi-vigentes"), md=3),
    ], className="mb-3"),
    map_mode_buttons,
    dbc.Row([
        dbc.Col(
            chart_card("Mapa de Distribuição Geográfica", dcc.Graph(id="mapa", config={"displayModeBar": False}, style={"height":"520px"})), md=12)
    ], className="mb-3"),
    dbc.Row([
        dbc.Col(chart_card("Distribuição por Modalidade", dcc.Graph(id="graf-por-modalidade", config={"displayModeBar": False}, style={"height":"320px"})), md=4),
        dbc.Col(chart_card("Evolução Temporal de Acordos", dcc.Graph(id="graf-evolucao", config={"displayModeBar": False}, style={"height":"320px"})), md=4),
        dbc.Col(chart_card("Top 10 Países Parceiros", html.Div(id="ranking-parceiros")), md=4),
    ], className="mb-3"),
    html.Div(id="anchor-detalhe"),
    chart_card("Detalhamento dos Acordos", dash_table.DataTable(
        id="tabela-detalhe",
        columns=[
            {"name":"Número do Processo","id":"numero_processo"},
            {"name":"País","id":"pais"},
            {"name":"UF","id":"uf_sigla"},
            {"name":"Tipo","id":"tipo"},
            {"name":"Modalidade","id":"modalidade"},
            {"name":"Ano","id":"ano_assinatura"},
            {"name":"Status","id":"status"},
            {"name":"Pesquisador Responsável","id":"pesquisador_responsavel"},
            {"name":"Vigente","id":"Vigente"},
        ],
        page_size=15,
        style_table={"overflowX":"auto"},
        style_cell={"fontFamily":"Inter, sans-serif","fontSize":"13px","padding":"12px 16px","textAlign":"left"},
        style_header={
            "fontWeight":"600","fontSize":"12px","textTransform":"uppercase","letterSpacing":"0.5px",
            "color":"#6B7280","backgroundColor":"#F7FAFC","borderBottom":"2px solid #E5E7EB"
        },
        style_data={"color":"#1F2937","backgroundColor":"#FFFFFF","borderBottom":"1px solid #F3F4F6"},
        style_data_conditional=[
            {"if": {"state": "selected"}, "backgroundColor": "#EEF2FF", "border": "1px solid #0B5ED7"},
            {"if": {"filter_query": "{Vigente} = 'Sim'"},
             "backgroundColor": "#ECFDF5", "borderLeft": "3px solid #10B981"},
        ]
    )),
], fluid=True, style={"maxWidth":"1400px","padding":"20px"})

# =========================================================
# FILTRO ÚNICO (com ANO como valor único ou 'Todos')
# =========================================================
def filtra(df_in: pd.DataFrame, ano_sel, tipos, conts, modalidades=None, status_mode: str = "todos") -> pd.DataFrame:
    d = df_in.copy()

    # Ano global
    if ano_sel != "Todos":
        ano_num = pd.to_numeric(d["ano_assinatura"], errors="coerce")
        d = d[ano_num == int(ano_sel)]

    if tipos:
        d = d[d["tipo"].isin(tipos)]
    if modalidades:
        d = d[d["modalidade"].isin(modalidades)]
    if conts:
        d = d[d["continente"].isin(conts)]
    if status_mode == "vigentes":
        d = d[d["eh_vigente"]]

    return d

# =========================================================
# CLIENTSIDE CALLBACK para scroll automático
# =========================================================
app.clientside_callback(
    """
    function(scrollData) {
        if (scrollData && scrollData.ts) {
            setTimeout(function() {
                const anchor = document.getElementById('anchor-detalhe');
                if (anchor) {
                    anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 300);
        }
        return '';
    }
    """,
    Output("scroll-sink", "children"),
    Input("scroll-trigger", "data")
)

# =========================================================
# CALLBACKS
# =========================================================
@app.callback(
    Output("collapse-filters", "is_open"),
    Input("toggle-filters", "n_clicks"),
    State("collapse-filters", "is_open"),
    prevent_initial_call=True
)
def toggle_filters(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("scroll-trigger", "data"),
    Input("mapa", "clickData"),
    prevent_initial_call=True
)
def trigger_scroll(clickData):
    """Dispara scroll automático quando há clique numa bolha do mapa"""
    if not clickData or "points" not in clickData:
        return None
    # Só executa se o clique for numa bolha (tem customdata ou text)
    point = clickData["points"][0]
    if point.get("customdata") is not None or point.get("text"):
        return {"ts": time.time()}
    return None

@app.callback(
    Output("btn-world", "color"),
    Output("btn-br", "color"),
    Output("btn-world", "outline"),
    Output("btn-br", "outline"),
    Input("modo-mapa", "data"),
    prevent_initial_call=False
)
def sync_botao_modo(modo):
    if modo == "world":
        # Mundial ativo (azul), Brasil inativo (claro)
        return "primary", "light", False, True
    else:
        # Brasil ativo (azul), Mundial inativo (claro)
        return "light", "primary", True, False

@app.callback(
    Output("modo-mapa","data"),
    Input("btn-br","n_clicks"),
    Input("btn-world","n_clicks"),
    Input("mapa","clickData"),
    State("modo-mapa","data"),
    prevent_initial_call=True
)
def troca_modo(n_br, n_world, clickData, modo):
    ctx = dash.callback_context
    if not ctx.triggered:
        return modo
    trig = ctx.triggered[0]["prop_id"].split(".")[0]
    if trig == "btn-br":
        return "br"
    if trig == "btn-world":
        return "world"
    if trig == "mapa":
        try:
            # se clicar no Brasil no modo mundial, troca pra BR
            loc = clickData["points"][0].get("location")
            if modo == "world" and loc == "BRA":
                return "br"
        except Exception:
            pass
    return modo

@app.callback(
    Output("mapa","figure"),
    Output("graf-por-modalidade","figure"),
    Output("graf-evolucao","figure"),
    Output("ranking-parceiros","children"),
    Output("kpi-total","children"),
    Output("kpi-paises","children"),
    Output("kpi-tipos","children"),
    Output("kpi-vigentes","children"),
    Input("modo-mapa","data"),
    Input("filtro-ano","value"),
    Input("filtro-tipos","value"),
    Input("filtro-continentes","value"),
    Input("filtro-modalidades","value"),
    Input("filtro-status","value"),
)
def desenha(modo, ano_sel, tipos, conts, modalidades, status_mode):
    dff = filtra(df, ano_sel, tipos, conts, modalidades, status_mode=status_mode)

    # KPIs NOVOS
    # 1. Vigência Geral (% e total de vigentes)
    total_acordos = len(dff)
    vigentes_total = dff["eh_vigente"].sum()
    vigentes_perc = (dff["eh_vigente"].mean() * 100.0) if total_acordos > 0 else 0.0
    kpi1 = kpi_card("Vigência Geral", f"{vigentes_perc:.1f}% ({vigentes_total})", "✅")
    
    # 2. Países com Parcerias (número de países únicos no período filtrado)
    paises_com_acordos = dff[dff["nivel_localizacao"] == "pais"]["codigo_iso3"].nunique()
    kpi2 = kpi_card("Países com Parcerias", str(paises_com_acordos), "🌍")
    
    # 3. Novos Acordos (Ano Atual)
    if ano_sel != "Todos":
        novos_ano = total_acordos
        ano_label = ano_sel
    else:
        # Se "Todos" está selecionado, pegar o ano atual (2025)
        ano_atual = 2025
        ano_num = pd.to_numeric(dff["ano_assinatura"], errors="coerce")
        novos_ano = (ano_num == ano_atual).sum()
        ano_label = ano_atual
    kpi3 = kpi_card(f"Novos Acordos ({ano_label})", str(novos_ano), "📅")
    
    # 4. Modalidade Mais Frequente
    if total_acordos > 0:
        modalidade_counts = dff["modalidade"].value_counts()
        modalidade_lider = modalidade_counts.idxmax()
        perc_lider = (modalidade_counts.max() / total_acordos * 100.0)
        kpi4 = kpi_card("Modalidade Mais Frequente", f"{modalidade_lider} ({perc_lider:.0f}%)", "📋")
    else:
        kpi4 = kpi_card("Modalidade Mais Frequente", "—", "📋")

    # MAPA
    fig_map = build_brazil_marker_map(dff, uf_centroids_dict) if modo == "br" else build_world_marker_map(dff, centroids_dict)

    # POR MODALIDADE (exclui "Termo Aditivo" do gráfico)
    modal = (
        dff[dff["modalidade"] != "Termo Aditivo"]
        .groupby("modalidade", dropna=False).size().reset_index(name="qtd")
        .sort_values("qtd", ascending=False).copy()
    )
    # compacta itens com qtd==1 em "Outras", mantendo "Carta Convite"
    carta = modal[modal["modalidade"] == "Carta Convite"]
    resto = modal[modal["modalidade"] != "Carta Convite"]
    únicas = resto[resto["qtd"] == 1]
    demais = resto[resto["qtd"] > 1]
    blocos = []
    if len(demais): blocos.append(demais)
    if len(carta): blocos.append(carta)
    if len(únicas):
        blocos.append(pd.DataFrame([{"modalidade":"Outras","qtd": int(únicas["qtd"].sum())}]))
    modal_plot = (pd.concat(blocos, ignore_index=True) if blocos else modal).sort_values("qtd", ascending=False)

    fig_modal = go.Figure()
    fig_modal.add_trace(go.Pie(
        labels=modal_plot["modalidade"], values=modal_plot["qtd"],
        hole=0.60, textposition="outside", textinfo="label+percent",
        textfont=dict(size=11, color="#1F2937", family="Inter, sans-serif"),
        marker=dict(line=dict(color="#FFFFFF", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} acordos (%{percent})<extra></extra>",
        pull=[0.05 if i==0 else 0 for i in range(len(modal_plot))], sort=False,
        automargin=True
    ))
    fig_modal.update_layout(
        template=PLOTLY_TEMPLATE, 
        showlegend=False, 
        height=350, 
        margin=dict(l=40, r=40, t=40, b=40),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    # EVOLUÇÃO temporal - Barras empilhadas por status
    ev_data = dff.dropna(subset=["ano_assinatura"]).copy()
    ev_data["ano_assinatura"] = pd.to_numeric(ev_data["ano_assinatura"], errors="coerce")
    ev_data = ev_data.dropna(subset=["ano_assinatura"])
    
    # Agrupar por ano e status de vigência
    ev = ev_data.groupby(["ano_assinatura", "eh_vigente"], as_index=False).size().rename(columns={"size": "qtd"})
    ev = ev.sort_values("ano_assinatura")
    
    # Separar vigentes e demais
    vigentes = ev[ev["eh_vigente"] == True]
    demais = ev[ev["eh_vigente"] == False]
    
    fig_ev = go.Figure()
    
    # Barra de Demais (cinza) - primeiro para ficar embaixo
    fig_ev.add_trace(go.Bar(
        x=demais["ano_assinatura"],
        y=demais["qtd"],
        name="Demais",
        marker=dict(color="#9CA3AF", line=dict(color="#FFFFFF", width=1)),
        hovertemplate="<b>%{x}</b><br>Demais: %{y}<extra></extra>"
    ))
    
    # Barra de Vigentes (verde) - por cima
    fig_ev.add_trace(go.Bar(
        x=vigentes["ano_assinatura"],
        y=vigentes["qtd"],
        name="Vigentes",
        marker=dict(color="#10B981", line=dict(color="#FFFFFF", width=1)),
        hovertemplate="<b>%{x}</b><br>Vigentes: %{y}<extra></extra>"
    ))
    
    fig_ev.update_layout(
        template=PLOTLY_TEMPLATE, 
        height=320, 
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(title="", tickformat="d"),
        yaxis=dict(title="", tickformat="d"),
        barmode="stack",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        hovermode="x unified"
    )

    # RANKING parceiros
    parceiros = (dff.groupby("pais", dropna=False).size().reset_index(name="qtd")
                   .sort_values("qtd", ascending=False))
    parceiros = parceiros[parceiros["pais"].notna()]
    ranking = create_ranking_list(parceiros, "pais", "qtd", max_items=10)

    return fig_map, fig_modal, fig_ev, ranking, kpi1, kpi2, kpi3, kpi4

@app.callback(
    Output("tabela-detalhe","data"),
    Input("mapa","clickData"),
    Input("modo-mapa","data"),
    Input("filtro-ano","value"),
    Input("filtro-tipos","value"),
    Input("filtro-continentes","value"),
    Input("filtro-modalidades","value"),
    Input("filtro-status","value"),
)
def atualiza_tabela(clickData, modo, ano_sel, tipos, conts, modalidades, status_mode):
    dff = filtra(df, ano_sel, tipos, conts, modalidades, status_mode=status_mode)

    if clickData and "points" in clickData:
        try:
            p = clickData["points"][0]
            # usamos customdata = (identificador, qtd)
            if modo == "br":
                ident = None
                if "customdata" in p and isinstance(p["customdata"], (list, tuple)) and len(p["customdata"]) >= 1:
                    ident = p["customdata"][0]
                if ident:
                    dff = dff[(dff["codigo_iso3"] == "BRA") & (dff["uf_sigla"] == ident)]
                else:
                    loc = p.get("location")
                    if loc:
                        dff = dff[(dff["codigo_iso3"] == "BRA") & (dff["uf_sigla"] == loc)]
            else:
                ident = None
                if "customdata" in p and isinstance(p["customdata"], (list, tuple)) and len(p["customdata"]) >= 1:
                    ident = p["customdata"][0]
                if ident:
                    dff = dff[dff["codigo_iso3"] == ident]
                else:
                    loc = p.get("location")
                    if loc:
                        dff = dff[dff["codigo_iso3"] == loc]
        except Exception as e:
            print(f"⚠️ clique mapa: {e}")

    cols = ["pais","uf_sigla","tipo","modalidade","ano_assinatura","status","pesquisador_responsavel"]
    det = dff[cols].sort_values(["pais","uf_sigla","ano_assinatura"], ascending=[True, True, False]).head(400).copy()
    det["Vigente"] = dff.loc[det.index, "eh_vigente"].map({True:"Sim", False:"Não"}).fillna("Não")
    
    # Adicionar número do processo
    if "NÚMERO" in dff.columns:
        det["numero_processo"] = dff.loc[det.index, "NÚMERO"].fillna("—")
    else:
        det["numero_processo"] = "—"
    
    return det.to_dict("records")

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

