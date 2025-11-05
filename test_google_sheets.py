"""
Script de Teste - Integração Google Sheets
Testa a conexão e leitura da planilha do Google Sheets
"""

import io
import time
import requests
import pandas as pd

# Configuração
GOOGLE_SHEET_ID = "1hPoZOGtQV0fAMCFoviE9PVuhmYArA6BQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx"

def test_connection():
    """Testa a conexão com o Google Sheets"""
    print("="*70)
    print("🧪 TESTE DE INTEGRAÇÃO COM GOOGLE SHEETS")
    print("="*70)
    print()
    
    print("📋 Informações da Planilha:")
    print(f"   ID: {GOOGLE_SHEET_ID}")
    print(f"   URL: {GOOGLE_SHEET_URL}")
    print()
    
    # Teste 1: Verificar conectividade básica
    print("🔍 Teste 1: Verificando conectividade...")
    try:
        response = requests.head(GOOGLE_SHEET_URL, timeout=10)
        print(f"   ✅ Conectividade OK (Status: {response.status_code})")
    except requests.exceptions.Timeout:
        print("   ❌ FALHA: Timeout ao conectar")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ FALHA: Sem conexão com internet")
        return False
    except Exception as e:
        print(f"   ❌ FALHA: {str(e)}")
        return False
    print()
    
    # Teste 2: Baixar planilha
    print("📥 Teste 2: Baixando planilha...")
    try:
        start_time = time.time()
        response = requests.get(GOOGLE_SHEET_URL, timeout=30)
        download_time = time.time() - start_time
        
        if response.status_code == 200:
            size_kb = len(response.content) / 1024
            print(f"   ✅ Download concluído em {download_time:.2f}s")
            print(f"   📦 Tamanho: {size_kb:.2f} KB")
        elif response.status_code == 403:
            print("   ❌ FALHA: Acesso negado (403)")
            print("   💡 Solução: Compartilhe a planilha com 'qualquer pessoa com o link'")
            return False
        elif response.status_code == 404:
            print("   ❌ FALHA: Planilha não encontrada (404)")
            print("   💡 Solução: Verifique se o ID da planilha está correto")
            return False
        else:
            print(f"   ❌ FALHA: Status HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FALHA: {str(e)}")
        return False
    print()
    
    # Teste 3: Ler dados
    print("📊 Teste 3: Lendo dados da planilha...")
    try:
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')
        
        print(f"   ✅ Dados carregados com sucesso")
        print(f"   📏 Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
        print()
        print("   📋 Colunas encontradas:")
        for i, col in enumerate(df.columns, 1):
            print(f"      {i}. {col}")
    except Exception as e:
        print(f"   ❌ FALHA ao processar Excel: {str(e)}")
        return False
    print()
    
    # Teste 4: Validar colunas essenciais
    print("✅ Teste 4: Validando estrutura da planilha...")
    required_cols = ["NÚMERO", "STATUS", "TIPO DE PROCESSO"]
    missing_cols = []
    
    for col in required_cols:
        if col in df.columns:
            print(f"   ✅ '{col}' encontrada")
        else:
            print(f"   ❌ '{col}' NÃO encontrada")
            missing_cols.append(col)
    
    # Verificar coluna de país (pode ter variações)
    pais_cols = [c for c in df.columns if "PAÍS" in c.upper() or "PAIS" in c.upper()]
    if pais_cols:
        print(f"   ✅ Coluna de país encontrada: '{pais_cols[0]}'")
    else:
        print(f"   ⚠️  Nenhuma coluna de país encontrada")
        missing_cols.append("PAÍS/ESTADO")
    
    # Verificar coluna de pesquisador
    pesq_cols = [c for c in df.columns if "CONTATO" in c.upper() or "PESQUISADOR" in c.upper()]
    if pesq_cols:
        print(f"   ✅ Coluna de pesquisador encontrada: '{pesq_cols[0]}'")
    else:
        print(f"   ⚠️  Nenhuma coluna de pesquisador encontrada")
    print()
    
    # Teste 5: Amostra de dados
    print("🔍 Teste 5: Amostra de dados (primeiras 3 linhas)...")
    if len(df) > 0:
        print(df.head(3).to_string())
    else:
        print("   ⚠️  Planilha está vazia")
    print()
    
    # Resumo final
    print("="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    if missing_cols:
        print(f"⚠️  AVISOS: {len(missing_cols)} coluna(s) essencial(is) não encontrada(s):")
        for col in missing_cols:
            print(f"   - {col}")
        print()
        print("💡 O aplicativo pode não funcionar corretamente sem essas colunas.")
        print()
        return False
    else:
        print("✅ SUCESSO: Todas as validações passaram!")
        print(f"✅ Planilha pronta para uso com {len(df)} registros")
        print()
        return True

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("🎉 Integração configurada corretamente!")
        print("👉 Execute 'python app.py' para iniciar o dashboard")
    else:
        print("❌ Problemas detectados na integração")
        print("👉 Revise as mensagens acima e corrija os problemas")
        print("👉 Consulte GOOGLE_SHEETS_INTEGRATION.md para mais detalhes")
    
    print()
    print("="*70)
