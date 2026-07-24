from datetime import datetime
from flask import current_app

from database import conectar
from services.whatsapp_service import enviar_whatsapp


def buscar_itens_criticos():
    """Retorna itens vencidos ou a N dias do vencimento (N = DIAS_ALERTA)."""
    dias_alerta = current_app.config.get('DIAS_ALERTA', 3)

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT nome, categoria, lote, data FROM vencimentos ORDER BY data ASC')
    linhas = cursor.fetchall()
    conexao.close()

    hoje = datetime.now().date()
    criticos = []

    for nome, categoria, lote, data_iso in linhas:
        data = datetime.strptime(data_iso, "%Y-%m-%d").date()
        dias = (data - hoje).days
        if dias <= dias_alerta:
            criticos.append({
                'nome': nome,
                'categoria': categoria,
                'lote': lote,
                'dias': dias,
                'data': data.strftime('%d/%m/%Y'),
            })

    return criticos


def montar_mensagem(itens):
    if not itens:
        return None

    linhas = ['*Alerta de vencimentos*', '']
    for item in itens:
        situacao = 'VENCIDO' if item['dias'] < 0 else f"vence em {item['dias']} dia(s)"
        linhas.append(f"- {item['nome']} ({item['categoria']}, lote {item['lote']}) — {situacao} [{item['data']}]")

    return '\n'.join(linhas)


def verificar_e_notificar():
    """Busca itens críticos, monta a mensagem e envia via WhatsApp se houver algo a alertar."""
    itens = buscar_itens_criticos()
    mensagem = montar_mensagem(itens)

    if not mensagem:
        return {'enviado': False, 'motivo': 'Nenhum item vencido ou próximo do vencimento.', 'itens': 0}

    resultado_envio = enviar_whatsapp(mensagem)
    return {
        'enviado': True,
        'itens': len(itens),
        'sids': resultado_envio['sids'],
        'erros': resultado_envio['erros'],
    }
