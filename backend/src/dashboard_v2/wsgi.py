"""
WSGI Entry Point para Dashboard v2
Para uso com Gunicorn ou Waitress em produção
"""

from main import app

# Exporta o servidor Dash para o WSGI
server = app.server

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(host='0.0.0.0', port=8052, debug=False)
