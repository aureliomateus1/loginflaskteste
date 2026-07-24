import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega o .env (se existir) para dentro das variáveis de ambiente do
# processo. Em produção (Render), as variáveis já vêm do próprio ambiente
# e esse load_dotenv() simplesmente não encontra nada pra fazer — é seguro
# manter em ambos os casos.
load_dotenv()

from config import Config
from database import criar_tabela
from api.auth import auth_bp
from api.vencimentos import vencimentos_bp
from api.notificacoes import notificacoes_bp
from services.scheduler import iniciar_scheduler

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

# Extensões que o frontend pode pedir diretamente por caminho (CSS, JS, ícone)
EXTENSOES_ESTATICAS = ('.css', '.js', '.ico', '.png', '.jpg', '.jpeg', '.svg')


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    criar_tabela()

    app.register_blueprint(auth_bp)
    app.register_blueprint(vencimentos_bp)
    app.register_blueprint(notificacoes_bp)

    # ===== Páginas =====
    @app.route('/')
    def login_page():
        return send_from_directory(FRONTEND_DIR, 'auth.html')

    @app.route('/painel')
    def painel():
        return send_from_directory(FRONTEND_DIR, 'vencimentos.html')

    # ===== Arquivos estáticos do frontend (CSS, JS, imagens) =====
    @app.route('/<path:caminho>')
    def arquivos_estaticos(caminho):
        if caminho.endswith(EXTENSOES_ESTATICAS) or caminho.startswith('imagens/'):
            return send_from_directory(FRONTEND_DIR, caminho)
        return ('Não encontrado', 404)

    if app.config.get('SCHEDULER_ATIVO'):
        iniciar_scheduler(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
