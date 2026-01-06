# 🚀 Deploy Dashboard v2 - Guia Completo

## 📋 Índice
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Deploy Windows](#deploy-windows)
- [Deploy Linux](#deploy-linux)
- [Configuração como Serviço](#configuração-como-serviço)
- [Nginx Reverse Proxy](#nginx-reverse-proxy)
- [Troubleshooting](#troubleshooting)

---

## ✅ Pré-requisitos

### Sistema
- Python 3.8+
- Acesso ao servidor (SSH ou RDP)
- Banco de dados SQLite em `dados/db/financeiro.db`

### Permissões
- Acesso de leitura/escrita à pasta do projeto
- Permissão para abrir porta 8052 (ou porta customizada)

---

## 📦 Instalação

### 1. Instalar Dependências

```bash
# Entrar na pasta do projeto
cd /path/to/Financeiro/backend

# Instalar dependências do dashboard
pip install -r requirements-dashboard.txt
```

**Dependências instaladas:**
- `dash` - Framework web
- `dash-bootstrap-components` - Componentes UI
- `plotly` - Gráficos interativos
- `pandas` - Manipulação de dados
- `gunicorn` - Servidor WSGI (Linux/Mac)
- `waitress` - Servidor WSGI (Windows)

### 2. Verificar Configuração

```bash
# Testar se o app inicia sem erros
cd backend/src/dashboard_v2
python main.py
```

Se aparecer:
```
🚀 Iniciando Dashboard Financeiro v2.0...
📊 Acesse: http://localhost:8052
```

✅ Configuração OK!

---

## 🪟 Deploy Windows

### Opção 1: Script Automático

```cmd
# Executar script de produção
cd D:\Professional\Projetos\Github\Financeiro\backend
start-dashboard-prod.bat
```

### Opção 2: Comando Manual

```cmd
cd backend\src\dashboard_v2
waitress-serve --host=0.0.0.0 --port=8052 --threads=4 wsgi:server
```

### Rodar em Background (Windows)

```cmd
# Criar tarefa agendada
schtasks /create /tn "Dashboard Financeiro" ^
    /tr "D:\Professional\Projetos\Github\Financeiro\backend\start-dashboard-prod.bat" ^
    /sc onstart /ru SYSTEM
```

Ou usar **NSSM (Non-Sucking Service Manager)**:

```cmd
# Baixar NSSM: https://nssm.cc/download
nssm install DashboardFinanceiro
# Path: C:\Python\python.exe
# Startup directory: D:\...\backend\src\dashboard_v2
# Arguments: -m waitress --host=0.0.0.0 --port=8052 wsgi:server

# Iniciar serviço
nssm start DashboardFinanceiro
```

---

## 🐧 Deploy Linux

### Opção 1: Script Automático

```bash
# Dar permissão de execução
chmod +x backend/start-dashboard-prod.sh

# Executar
./backend/start-dashboard-prod.sh
```

### Opção 2: Comando Manual

```bash
cd backend/src/dashboard_v2

gunicorn wsgi:server \
    --bind 0.0.0.0:8052 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

**Parâmetros:**
- `--workers 4` - 4 processos workers (ajuste conforme CPU)
- `--threads 2` - 2 threads por worker
- `--timeout 120` - Timeout de 120s para requests longos
- `--access-logfile -` - Logs de acesso no stdout
- `--error-logfile -` - Logs de erro no stdout

### Rodar em Background (Linux)

```bash
# Usando nohup
nohup ./backend/start-dashboard-prod.sh > dashboard.log 2>&1 &

# Verificar processo
ps aux | grep gunicorn

# Parar processo
pkill -f gunicorn
```

---

## ⚙️ Configuração como Serviço

### Systemd (Linux)

1. **Editar arquivo de serviço:**

```bash
sudo nano /etc/systemd/system/dashboard-financeiro.service
```

2. **Copiar conteúdo (ajustar caminhos):**

```ini
[Unit]
Description=Dashboard Financeiro v2
After=network.target

[Service]
Type=simple
User=seu-usuario
Group=seu-grupo
WorkingDirectory=/home/usuario/Financeiro/backend/src/dashboard_v2
Environment="PATH=/home/usuario/venv/bin"
ExecStart=/home/usuario/venv/bin/gunicorn wsgi:server --bind 0.0.0.0:8052 --workers 4 --threads 2 --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Ativar e iniciar:**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar inicialização automática
sudo systemctl enable dashboard-financeiro

# Iniciar serviço
sudo systemctl start dashboard-financeiro

# Verificar status
sudo systemctl status dashboard-financeiro

# Ver logs
sudo journalctl -u dashboard-financeiro -f
```

4. **Comandos úteis:**

```bash
# Parar
sudo systemctl stop dashboard-financeiro

# Reiniciar
sudo systemctl restart dashboard-financeiro

# Desabilitar inicialização automática
sudo systemctl disable dashboard-financeiro
```

---

## 🌐 Nginx Reverse Proxy

Para expor o dashboard com domínio próprio:

### 1. Instalar Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Configurar Virtual Host

```bash
sudo nano /etc/nginx/sites-available/dashboard-financeiro
```

**Conteúdo:**

```nginx
server {
    listen 80;
    server_name financeiro.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8052;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (para Dash callbacks)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### 3. Ativar Configuração

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/dashboard-financeiro /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 4. HTTPS com Let's Encrypt (Opcional)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d financeiro.seudominio.com

# Renovação automática (já configurada pelo certbot)
sudo certbot renew --dry-run
```

---

## 🔧 Configurações de Produção

### 1. Desabilitar Debug

No arquivo [main.py](../../backend/src/dashboard_v2/main.py#L498-L503), linha 498:

```python
# ANTES (desenvolvimento)
app.run(
    host='0.0.0.0',
    port=8052,
    debug=True  # ❌ Inseguro em produção
)

# DEPOIS (produção)
app.run(
    host='0.0.0.0',
    port=8052,
    debug=False  # ✅ Seguro
)
```

### 2. Variáveis de Ambiente

Criar arquivo `.env`:

```bash
# backend/src/dashboard_v2/.env
DASH_ENV=production
DASH_PORT=8052
DASH_HOST=0.0.0.0
DB_PATH=../../dados/db/financeiro.db
```

### 3. Firewall

```bash
# Linux (UFW)
sudo ufw allow 8052/tcp

# Windows
netsh advfirewall firewall add rule name="Dashboard Financeiro" dir=in action=allow protocol=TCP localport=8052
```

---

## 🐛 Troubleshooting

### Erro: "Address already in use"

```bash
# Linux
sudo lsof -i :8052
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :8052
taskkill /PID <PID> /F
```

### Erro: "ModuleNotFoundError"

```bash
# Reinstalar dependências
pip install -r requirements-dashboard.txt --force-reinstall
```

### Erro: "Database is locked"

```bash
# Verificar permissões
chmod 664 dados/db/financeiro.db
chmod 775 dados/db/

# Verificar processos usando o banco
lsof dados/db/financeiro.db
```

### Dashboard Lento

1. **Aumentar workers:**
```bash
gunicorn wsgi:server --workers 8  # Ajustar conforme CPU
```

2. **Adicionar cache:**
```python
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
```

3. **Otimizar queries:**
- Criar índices no SQLite
- Limitar dados carregados (últimos 12 meses)

### Logs Não Aparecem

```bash
# Redirecionar para arquivo
gunicorn wsgi:server --bind 0.0.0.0:8052 \
    --access-logfile access.log \
    --error-logfile error.log

# Ou usar journalctl (systemd)
sudo journalctl -u dashboard-financeiro -f
```

---

## 📊 Monitoramento

### 1. Health Check

Adicionar em [main.py](../../backend/src/dashboard_v2/main.py):

```python
@app.server.route('/health')
def health():
    return {'status': 'ok'}, 200
```

### 2. Monitorar com Curl

```bash
# Script de monitoramento
while true; do
    curl -s http://localhost:8052/health > /dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Dashboard offline!"
        # Enviar alerta (email, slack, etc)
    fi
    sleep 60
done
```

---

## 🎯 Checklist de Deploy

- [ ] Dependências instaladas (`requirements-dashboard.txt`)
- [ ] Banco de dados acessível (`dados/db/financeiro.db`)
- [ ] Debug desabilitado (`debug=False`)
- [ ] Firewall configurado (porta 8052)
- [ ] Serviço systemd criado (opcional)
- [ ] Nginx configurado (opcional)
- [ ] HTTPS configurado (opcional)
- [ ] Backup do banco configurado
- [ ] Logs sendo gravados
- [ ] Health check funcionando
- [ ] Testes de carga realizados

---

## 📚 Recursos Adicionais

- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Waitress Docs](https://docs.pylonsproject.org/projects/waitress/)
- [Dash Deployment Guide](https://dash.plotly.com/deployment)
- [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

---

**✨ Dashboard pronto para produção!**

Para suporte: Consulte logs em `/var/log/nginx/` (Nginx) ou `journalctl -u dashboard-financeiro` (Systemd)
