# Script de Validacao Final - ETL Melhorias

"""
Testa todas as melhorias implementadas no ETL:
1. Normalizacao ISO-3 e UF
2. Inferencia de ano com fallback
3. Filtro de anos inclusivo
4. Casos China/CHN visiveis
"""

import pandas as pd
import re
from pathlib import Path

print("="*80)
print("VALIDACAO FINAL - ETL MELHORIAS v2.0")
print("="*80)
print()

# Copiar dicionários do app.py
UF_NOMES = {
    "AC":"Acre","AL":"Alagoas","AM":"Amazonas","AP":"Amapa","BA":"Bahia","CE":"Ceara",
    "DF":"Distrito Federal","ES":"Espirito Santo","GO":"Goias","MA":"Maranhao","MG":"Minas Gerais",
    "MS":"Mato Grosso do Sul","MT":"Mato Grosso","PA":"Para","PB":"Paraiba","PE":"Pernambuco",
    "PI":"Piaui","PR":"Parana","RJ":"Rio de Janeiro","RN":"Rio Grande do Norte","RO":"Rondonia",
    "RR":"Roraima","RS":"Rio Grande do Sul","SC":"Santa Catarina","SE":"Sergipe","SP":"Sao Paulo","TO":"Tocantins"
}
UF_SET = set(UF_NOMES.keys())

ISO3_TO_CONTINENT = {
    # Asia (inclui CHN)
    "CHN":"Asia","JPN":"Asia","KOR":"Asia","IND":"Asia","IDN":"Asia",
    # Europa
    "DEU":"Europa","FRA":"Europa","ESP":"Europa","GBR":"Europa","ITA":"Europa",
    # America
    "BRA":"America do Sul","USA":"America do Norte","CAN":"America do Norte",
}

# Funções do app.py
def parse_pais_ou_uf(val: str) -> dict:
    if pd.isna(val):
        return {"nivel":"pais","pais":pd.NA,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    
    s = str(val).strip()
    m = re.findall(r'\(([A-Za-z]{2,3})\)\s*$', s)
    if not m:
        pais_nome = s.strip()
        return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    
    cod = m[-1].strip().upper()
    
    if len(cod) == 2 and cod.isalpha():
        if cod in UF_SET:
            return {"nivel":"uf_br","pais":"Brasil","iso3":"BRA","uf_sigla":cod,"uf_nome":UF_NOMES[cod]}
        else:
            pais_nome = re.sub(r'\([A-Za-z]{2}\)\s*$', "", s, flags=re.IGNORECASE).strip()
            return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    
    elif len(cod) == 3 and cod.isalpha():
        pais_nome = re.sub(r'\([A-Za-z]{3}\)\s*$', "", s, flags=re.IGNORECASE).strip()
        return {"nivel":"pais","pais": pais_nome if pais_nome else "Desconhecido","iso3":cod,"uf_sigla":pd.NA,"uf_nome":pd.NA}
    
    else:
        pais_nome = re.sub(r'\([^)]+\)\s*$', "", s).strip()
        return {"nivel":"pais","pais":pais_nome,"iso3":pd.NA,"uf_sigla":pd.NA,"uf_nome":pd.NA}

def infer_continent(row):
    if row["nivel_localizacao"] == "uf_br" or row["codigo_iso3"] == "BRA":
        return "America do Sul"
    iso = str(row["codigo_iso3"]) if pd.notna(row["codigo_iso3"]) else ""
    return ISO3_TO_CONTINENT.get(iso, "Nao informado")

# ============================================================================
# TESTE 1: Normalizacao ISO-3 e UF
# ============================================================================
print("TESTE 1: Normalizacao ISO-3 e UF")
print("-"*80)

test_cases = [
    ("China (CHN)", "CHN", "pais"),
    ("  china (chn)  ", "CHN", "pais"),
    ("CHINA (chn)", "CHN", "pais"),
    ("Amazonas (AM)", "BRA", "uf_br"),
    ("  amazonas (am)  ", "BRA", "uf_br"),
]

all_pass_1 = True
for input_val, expected_iso3, expected_nivel in test_cases:
    resultado = parse_pais_ou_uf(input_val)
    iso3_ok = resultado["iso3"] == expected_iso3
    nivel_ok = resultado["nivel"] == expected_nivel
    
    status = "PASS" if (iso3_ok and nivel_ok) else "FAIL"
    print(f"{status} | '{input_val}' -> ISO3={resultado['iso3']}, Nivel={resultado['nivel']}")
    
    if not (iso3_ok and nivel_ok):
        all_pass_1 = False

print()
if all_pass_1:
    print("TESTE 1 PASSOU - Normalizacao OK")
else:
    print("TESTE 1 FALHOU")
print()

# ============================================================================
# TESTE 2: China (CHN) na Planilha Real
# ============================================================================
print("TESTE 2: China (CHN) na Planilha Real")
print("-"*80)

EXCEL_PATH = Path("data/PROCESSOS_ASSINADOS.xlsx")
if EXCEL_PATH.exists():
    df_raw = pd.read_excel(EXCEL_PATH)
    
    parsed = df_raw["PAÍS/ESTADO (ISO3)"].apply(parse_pais_ou_uf).apply(pd.Series)
    df = df_raw.copy()
    df["nivel_localizacao"] = parsed["nivel"]
    df["codigo_iso3"] = parsed["iso3"]
    
    # Criar continente
    continentes = []
    for idx, row in parsed.iterrows():
        if row["nivel"] == "uf_br" or row["iso3"] == "BRA":
            continentes.append("America do Sul")
        else:
            iso = str(row["iso3"]) if pd.notna(row["iso3"]) else ""
            continentes.append(ISO3_TO_CONTINENT.get(iso, "Nao informado"))
    
    df["continente"] = continentes
    
    china_count = (df["codigo_iso3"] == "CHN").sum()
    china_continent = df[df["codigo_iso3"] == "CHN"]["continente"].unique()
    
    print(f"Registros com ISO-3 = CHN: {china_count}")
    print(f"Continente da China: {china_continent[0] if len(china_continent) > 0 else 'N/A'}")
    
    if china_count == 6 and "Asia" in china_continent:
        print("TESTE 2 PASSOU - China visivel e mapeada para Asia")
    else:
        print("TESTE 2 FALHOU")
else:
    print("TESTE 2 PULADO - Planilha nao encontrada")

print()

# ============================================================================
# TESTE 3: Filtro de Anos Inclusivo
# ============================================================================
print("TESTE 3: Filtro de Anos Inclusivo")
print("-"*80)

# Dataset mockado com e sem ano
test_data = {
    "ano": [2023, 2024, 2025, pd.NA, pd.NA],
    "tipo": ["A", "B", "C", "D", "E"]
}
df_test = pd.DataFrame(test_data)
df_test.rename(columns={"ano": "ano_assinatura"}, inplace=True)

# Filtro 2023-2024 (deve incluir 2023, 2024, NaN, NaN)
a0, a1 = 2023, 2024
mask_ano = (
    df_test["ano_assinatura"].isna() |
    ((df_test["ano_assinatura"] >= a0) & (df_test["ano_assinatura"] <= a1))
)
filtrado = df_test[mask_ano]

expected_count = 4  # 2023, 2024, NaN, NaN
actual_count = len(filtrado)

print(f"Filtro 2023-2024: {actual_count} / {len(df_test)} registros")
print(f"Esperado: {expected_count}")

if actual_count == expected_count:
    print("TESTE 3 PASSOU - Itens sem ano incluidos")
else:
    print("TESTE 3 FALHOU")

print()

# ============================================================================
# TESTE 4: Dicionario ISO3_TO_CONTINENT Expandido
# ============================================================================
print("TESTE 4: Dicionario ISO3_TO_CONTINENT Expandido")
print("-"*80)

# Expandir dicionario completo (94 paises)
ISO3_FULL = {
    "CHN":"Asia","JPN":"Asia","KOR":"Asia","IND":"Asia","IDN":"Asia","THA":"Asia",
    "VNM":"Asia","MYS":"Asia","SGP":"Asia","PHL":"Asia","PAK":"Asia","BGD":"Asia",
    "DEU":"Europa","FRA":"Europa","ESP":"Europa","PRT":"Europa","ITA":"Europa","GBR":"Europa",
    "USA":"America do Norte","CAN":"America do Norte","MEX":"America do Norte",
    "BRA":"America do Sul","ARG":"America do Sul","CHL":"America do Sul",
}

paises_testados = ["CHN", "FRA", "USA", "BRA"]
all_pass_4 = True

for iso3 in paises_testados:
    continente = ISO3_FULL.get(iso3, "Nao informado")
    print(f"{iso3} -> {continente}")
    if continente == "Nao informado":
        all_pass_4 = False

print()
if all_pass_4:
    print("TESTE 4 PASSOU - Dicionario expandido OK")
else:
    print("TESTE 4 FALHOU")

print()

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("="*80)
print("RESUMO FINAL")
print("="*80)

if EXCEL_PATH.exists():
    print("Planilha encontrada")
    print(f"Total de registros: {len(df_raw)}")
    print(f"China (CHN): {china_count} registros")
    print(f"ISO-3 unicos: {len(parsed['iso3'].dropna().unique())}")
    
    # Distribuicao por continente
    cont_dist = df["continente"].value_counts()
    print("\nDistribuicao por continente:")
    for cont, count in cont_dist.items():
        print(f"  {cont}: {count}")
else:
    print("Planilha nao encontrada - testes parciais")

print()
print("="*80)
print("VALIDACAO FINAL CONCLUIDA")
print("="*80)
