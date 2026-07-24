from flask import Blueprint, request, jsonify, current_app

from services.notificacao_service import verificar_e_notificar
from services.whatsapp_service import ConfiguracaoWhatsAppIncompleta

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/api/notificacoes')


@notificacoes_bp.route('/verificar', methods=['POST'])
def verificar():
    """
    Dispara a checagem de itens próximos do vencimento e envia o alerta por
    WhatsApp se houver algo a notificar.

    Protegido por token (não por sessão de usuário), porque quem chama essa
    rota normalmente é um serviço de cron externo, não uma pessoa logada no
    painel. Envie o token no header X-Notificacoes-Token.
    """
    token_recebido = request.headers.get('X-Notificacoes-Token')
    token_esperado = current_app.config.get('NOTIFICACOES_TOKEN')

    if not token_recebido or token_recebido != token_esperado:
        return jsonify({'mensagem': 'Token inválido ou ausente.'}), 403

    try:
        resultado = verificar_e_notificar()
        return jsonify(resultado), 200
    except ConfiguracaoWhatsAppIncompleta as erro:
        return jsonify({'mensagem': str(erro)}), 500
