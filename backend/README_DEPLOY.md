# 🚀 Dashboard Financeiro v2 - Deploy Rápido

## ⚡ Quick Start - Produção

### Windows
```cmd
cd backend
pip install -r requirements-dashboard.txt
start-dashboard-prod.bat
```

### Linux/Mac
```bash
cd backend
pip install -r requirements-dashboard.txt
chmod +x start-dashboard-prod.sh
./start-dashboard-prod.sh
```

Acesse: **http://localhost:8052**

---

## 📖 Documentação Completa

Veja [docs/Deploy/DEPLOY_DASHBOARD_V2.md](../docs/Deploy/DEPLOY_DASHBOARD_V2.md) para:
- ✅ Configuração como serviço (Systemd/Windows Service)
- 🌐 Nginx reverse proxy
- 🔒 HTTPS com Let's Encrypt
- 🐛 Troubleshooting completo
- 📊 Monitoramento e logs

---

## 🛠️ Comandos Úteis

### Desenvolvimento (com hot-reload)
```bash
cd backend/src/dashboard_v2
python main.py
```

### Produção (servidor WSGI)
```bash
# Windows
waitress-serve --host=0.0.0.0 --port=8052 wsgi:server

# Linux
gunicorn wsgi:server --bind 0.0.0.0:8052 --workers 4
```

### Health Check
```bash
curl http://localhost:8052/health
```

---

## 📦 Dependências

- Python 3.8+
- Dash 2.14+
- Plotly 5.18+
- Pandas 1.5+
- Gunicorn/Waitress (produção)

Instalação: `pip install -r requirements-dashboard.txt`

---

## 🔧 Variáveis de Ambiente (Opcional)

```bash
export DASH_DEBUG=false        # true para desenvolvimento
export DASH_PORT=8052          # Porta customizada
export DASH_HOST=0.0.0.0       # Host (0.0.0.0 para acesso externo)
```

---

**✨ Desenvolvido por LF Sistemas**
