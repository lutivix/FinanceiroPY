#!/usr/bin/env python3
"""
Teste de conectividade básica com Plaid API
Diagnostica problemas de rede, proxy e firewall
"""
import urllib3
import ssl
import socket

print("="*60)
print("🔍 DIAGNÓSTICO DE CONEXÃO PLAID")
print("="*60)

# 1. Teste DNS
print("\n[1/4] 🌐 Resolvendo DNS sandbox.plaid.com...")
try:
    ip = socket.gethostbyname('sandbox.plaid.com')
    print(f"   ✅ DNS OK: {ip}")
except Exception as e:
    print(f"   ❌ Erro DNS: {e}")
    print("\n💡 SOLUÇÃO: Verifique sua conexão com internet")
    exit(1)

# 2. Teste TCP
print("\n[2/4] 🔌 Testando conexão TCP na porta 443...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('sandbox.plaid.com', 443))
    sock.close()
    
    if result == 0:
        print("   ✅ Porta 443 acessível")
    else:
        print(f"   ❌ Porta 443 bloqueada (código: {result})")
        print("\n💡 SOLUÇÃO: Firewall está bloqueando. Verifique:")
        print("   - Firewall do Windows")
        print("   - Antivírus")
        print("   - Firewall corporativo")
        exit(1)
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# 3. Teste HTTPS
print("\n[3/4] 🔒 Testando conexão HTTPS...")
try:
    http = urllib3.PoolManager(
        cert_reqs=ssl.CERT_REQUIRED,
        timeout=urllib3.Timeout(connect=5.0, read=10.0)
    )
    
    response = http.request('GET', 'https://sandbox.plaid.com')
    print(f"   ✅ HTTPS OK (Status: {response.status})")
except urllib3.exceptions.SSLError as e:
    print(f"   ❌ Erro SSL: {e}")
    print("\n💡 SOLUÇÃO: Certificados SSL. Possível proxy interceptando.")
    print("   Execute: py -m pip install --upgrade certifi")
    exit(1)
except urllib3.exceptions.MaxRetryError as e:
    print(f"   ❌ Timeout/Retry: {e}")
    print("\n💡 SOLUÇÃO: Conexão muito lenta ou proxy bloqueando")
    exit(1)
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# 4. Teste Plaid API
print("\n[4/4] 🧪 Testando endpoint Plaid API...")
try:
    from plaid import Configuration, ApiClient, Environment
    from plaid.api import plaid_api
    
    configuration = Configuration(
        host=Environment.Sandbox,
        api_key={
            'clientId': '69e7b1383357a7000e4e1ebb',
            'secret': '9229419b2929fdb0b28082ed5a4592',
        }
    )
    
    client = plaid_api.PlaidApi(ApiClient(configuration))
    
    # Teste simples - apenas criar configuração
    print("   ✅ Cliente Plaid criado com sucesso")
    
    # Tentar chamada real
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="Test",
        country_codes=[CountryCode('BR')],
        language='pt',
        user=LinkTokenCreateRequestUser(client_user_id='test')
    )
    
    response = client.link_token_create(request)
    print(f"   ✅ API funcionando! Token: {response['link_token'][:20]}...")
    
except ImportError:
    print("   ❌ plaid-python não instalado")
    print("\n💡 SOLUÇÃO: py -m pip install plaid-python")
    exit(1)
except Exception as e:
    print(f"   ❌ Erro API: {e}")
    print("\n💡 Possíveis causas:")
    print("   - Credenciais inválidas")
    print("   - Firewall bloqueando API")
    print("   - Proxy interceptando requisições")
    exit(1)

# Sucesso!
print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*60)
print("""
🎯 PRÓXIMOS PASSOS:
   1. Execute: py test_plaid_sandbox.py
   2. Se falhar, verifique firewall/proxy
   3. Em caso de problemas, teste em outra rede
""")
print("="*60)
