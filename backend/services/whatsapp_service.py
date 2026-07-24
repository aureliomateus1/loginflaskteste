from flask import current_app
from twilio.rest import Client


class ConfiguracaoWhatsAppIncompleta(Exception):
    """Levantada quando faltam variáveis de ambiente do Twilio."""
    pass


def enviar_whatsapp(texto):
    """
    Envia uma mensagem de texto via Twilio WhatsApp para um ou mais números.

    Requer as variáveis de ambiente TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e
    WHATSAPP_DESTINO configuradas. TWILIO_WHATSAPP_FROM tem um valor padrão
    apontando para o número de Sandbox do Twilio.

    WHATSAPP_DESTINO aceita múltiplos números separados por vírgula, ex:
    "whatsapp:+5511999999999,whatsapp:+5511888888888". A mensagem é enviada
    para cada um individualmente — se um número falhar (ex: não deu join no
    Sandbox), os outros ainda recebem normalmente.

    IMPORTANTE (Sandbox): cada número de destino precisa ter enviado
    "join <código>" para o número de Sandbox antes de poder receber
    mensagens. Fora da janela de 24h de conversa, o WhatsApp Business
    Platform exige o uso de um template pré-aprovado para mensagens
    iniciadas pela empresa — isso vale mesmo em Sandbox. Para uso contínuo
    em produção, será necessário migrar para um número WhatsApp Business
    aprovado pela Meta.

    Retorna um dict: {'sids': [...], 'erros': [...]}
    """
    sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    token = current_app.config.get('TWILIO_AUTH_TOKEN')
    remetente = current_app.config.get('TWILIO_WHATSAPP_FROM')
    destino_bruto = current_app.config.get('WHATSAPP_DESTINO')

    if not sid or not token or not destino_bruto:
        raise ConfiguracaoWhatsAppIncompleta(
            'Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e WHATSAPP_DESTINO '
            'nas variáveis de ambiente antes de enviar notificações.'
        )

    destinos = [d.strip() for d in destino_bruto.split(',') if d.strip()]
    if not destinos:
        raise ConfiguracaoWhatsAppIncompleta('WHATSAPP_DESTINO está vazio.')

    cliente = Client(sid, token)
    sids = []
    erros = []

    for destino in destinos:
        try:
            mensagem = cliente.messages.create(from_=remetente, body=texto, to=destino)
            sids.append(mensagem.sid)
        except Exception as erro:
            erros.append(f'{destino}: {erro}')

    if not sids and erros:
        raise ConfiguracaoWhatsAppIncompleta(
            'Falha ao enviar para todos os destinos configurados: ' + '; '.join(erros)
        )

    return {'sids': sids, 'erros': erros}
