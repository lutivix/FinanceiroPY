#!/usr/bin/env python3
"""
Verificar quais bancos brasileiros estão disponíveis no Plaid Sandbox
"""
from plaid.api import plaid_api
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.country_code import CountryCode
from plaid import Configuration, ApiClient, Environment

CLIENT_ID = '69e7b1383357a7000e4e1ebb'
SECRET = '9229419b2929fdb0b28082ed5a4592'

print("="*60)
print("🔍 VERIFICANDO BANCOS BRASILEIROS NO SANDBOX")
print("="*60)

configuration = Configuration(
    host=Environment.Sandbox,
    api_key={'clientId': CLIENT_ID, 'secret': SECRET}
)
client = plaid_api.PlaidApi(ApiClient(configuration))

# Tentar buscar instituições brasileiras
print("\n[1/2] 🇧🇷 Buscando instituições brasileiras (BR)...")
try:
    request = InstitutionsGetRequest(
        count=100,
        offset=0,
        country_codes=[CountryCode('BR')],
    )
    response = client.institutions_get(request)
    institutions = response['institutions']
    
    if institutions:
        print(f"   ✅ {len(institutions)} instituições brasileiras encontradas!\n")
        
        # Procurar especificamente Itaú
        itau_banks = [inst for inst in institutions if 'itau' in inst['name'].lower()]
        
        if itau_banks:
            print("   🏦 BANCOS ITAÚ DISPONÍVEIS:")
            for bank in itau_banks:
                print(f"\n      📌 {bank['name']}")
                print(f"         ID: {bank['institution_id']}")
                print(f"         Produtos: {', '.join(bank.get('products', []))}")
        else:
            print("   ⚠️  Itaú não encontrado especificamente")
            print("   📋 Mas há outras instituições brasileiras:")
            for inst in institutions[:10]:  # Mostrar primeiras 10
                print(f"      - {inst['name']} (ID: {inst['institution_id']})")
    else:
        print("   ⚠️  Nenhuma instituição brasileira encontrada")
        
except Exception as e:
    error_str = str(e)
    print(f"   ❌ Erro ao buscar instituições BR: {e}")
    
    if 'INVALID_FIELD' in error_str or 'country' in error_str.lower():
        print("\n   ℹ️  BRASIL NÃO HABILITADO NO SANDBOX")
        print("\n   📝 POSSÍVEIS RAZÕES:")
        print("      1. País BR requer aprovação/solicitação especial")
        print("      2. Sandbox pode ter lista limitada de países")
        print("      3. BR só disponível em Production (após aprovação)")
        print("\n   🔧 SOLUÇÕES:")
        print("      A. Solicitar acesso ao BR via dashboard")
        print("      B. Aguardar aprovação de Production")
        print("      C. Testar com US agora, migrar para BR depois")

# Tentar buscar instituições US para comparação
print("\n[2/2] 🇺🇸 Buscando instituições US (para comparação)...")
try:
    request_us = InstitutionsGetRequest(
        count=20,
        offset=0,
        country_codes=[CountryCode('US')],
    )
    response_us = client.institutions_get(request_us)
    institutions_us = response_us['institutions']
    
    if institutions_us:
        print(f"   ✅ {len(institutions_us)} instituições US encontradas")
        print("\n   📋 Exemplos (primeiras 5):")
        for inst in institutions_us[:5]:
            print(f"      - {inst['name']} (ID: {inst['institution_id']})")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Conclusão
print("\n" + "="*60)
print("📊 CONCLUSÃO")
print("="*60)
print("""
🎯 OPÇÕES DISPONÍVEIS:

1️⃣ OPÇÃO A - DESENVOLVER COM US AGORA (RECOMENDADO)
   ✅ US funciona imediatamente no sandbox
   ✅ Lógica de código é IDÊNTICA (só muda institution_id)
   ✅ Quando produção aprovar → trocar para BR
   ✅ Estrutura de dados é a mesma
   
   VANTAGEM: Não perde tempo esperando, desenvolve AGORA
   
2️⃣ OPÇÃO B - SOLICITAR ACESSO BR NO SANDBOX
   ⏳ Precisa abrir ticket no dashboard
   ⏳ Pode demorar 1-3 dias para aprovar
   ⏳ Pode só estar disponível em Production
   
   VANTAGEM: Testa com banco real brasileiro
   DESVANTAGEM: Perde tempo esperando

3️⃣ OPÇÃO C - AGUARDAR PRODUCTION
   ⏳ Aprovação production levará 1-5 dias
   ✅ Quando aprovar, terá acesso a bancos BR reais
   ✅ Poderá conectar Itaú real
   
   VANTAGEM: Dados reais desde o início
   DESVANTAGEM: Não desenvolve enquanto espera

🏆 RECOMENDAÇÃO:
   Use OPÇÃO A → Desenvolva com US no sandbox AGORA
   
   POR QUÊ?
   - Código é o mesmo (instituição é só um parâmetro)
   - Aprende a API Plaid imediatamente
   - Quando production aprovar, troca 2 linhas:
     * country_codes = US → BR
     * institution_id = ins_109508 → ins_itau_br
   
   EXEMPLO:
   # Sandbox US (agora)
   institution_id = 'ins_109508'  # First Platypus Bank
   
   # Production BR (depois)
   institution_id = 'ins_116943'  # Itaú (exemplo, ID real virá)
""")
print("="*60)

# Verificar se há sugestão de sandbox brasileiro
print("\n💡 DICA: Verifique seu dashboard Plaid:")
print("   https://dashboard.plaid.com/developers/api")
print("   → Link Customization → Supported countries")
print("   → Veja se BR está listado ou se pode solicitar")
