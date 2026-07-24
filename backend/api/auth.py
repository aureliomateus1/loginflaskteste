from flask import Blueprint, request, jsonify, session
from database import conectar, PLACEHOLDER
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from auth_utils import sessao_valida

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Guarda tentativas de login por usuário, em memória:
# {'usuario': {'tentativas': N, 'bloqueado_até': datetime ou None}}
tentativas_login = {}

MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MINUTOS = 5


@auth_bp.route('/cadastro', methods=['POST'])
def cadastrar():
    dados = request.get_json()
    user = dados.get('user')
    senha = dados.get('pass')

    if not user or not senha:
        return jsonify({'mensagem': 'Usuário e senha são obrigatórios!'}), 400

    if len(senha) < 6:
        return jsonify({'mensagem': 'A senha precisa ter no mínimo 6 caracteres!'}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f'SELECT * FROM usuarios WHERE usuario = {PLACEHOLDER}', (user,))
    existente = cursor.fetchone()

    if existente:
        conexao.close()
        return jsonify({'mensagem': 'Usuário já existe!'}), 400

    senha_hash = generate_password_hash(senha)
    cursor.execute(f'INSERT INTO usuarios (usuario, senha) VALUES ({PLACEHOLDER}, {PLACEHOLDER})', (user, senha_hash))
    conexao.commit()
    conexao.close()
    return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    user = dados.get('user')
    senha = dados.get('pass')

    agora = datetime.now()

    if user in tentativas_login:
        info = tentativas_login[user]
        if info.get('bloqueado_até') and agora < info['bloqueado_até']:
            segundos_restantes = int((info['bloqueado_até'] - agora).total_seconds())
            return jsonify({'mensagem': f'Muitas tentativas. Tente novamente em {segundos_restantes} segundos.'}), 429

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f'SELECT * FROM usuarios WHERE usuario = {PLACEHOLDER}', (user,))
    resultado = cursor.fetchone()
    conexao.close()

    if resultado and check_password_hash(resultado[1], senha):
        tentativas_login.pop(user, None)
        session['usuario'] = user
        session['ultimo_acesso'] = datetime.now().isoformat()
        session.permanent = False
        return jsonify({'mensagem': 'Login realizado com sucesso!'}), 200
    else:
        info = tentativas_login.get(user, {'tentativas': 0, 'bloqueado_até': None})
        info['tentativas'] += 1

        if info['tentativas'] >= MAX_TENTATIVAS:
            info['bloqueado_até'] = agora + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            info['tentativas'] = 0
            tentativas_login[user] = info
            return jsonify({'mensagem': f'Muitas tentativas incorretas. Bloqueado por {TEMPO_BLOQUEIO_MINUTOS} minutos.'}), 429

        tentativas_login[user] = info
        return jsonify({'mensagem': 'Usuário ou senha incorretos!'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return jsonify({'mensagem': 'Logout realizado com sucesso!'}), 200


@auth_bp.route('/verificar-sessao', methods=['GET'])
def verificar_sessao():
    if sessao_valida():
        return jsonify({'autenticado': True, 'usuario': session['usuario']}), 200
    else:
        return jsonify({'autenticado': False}), 401
