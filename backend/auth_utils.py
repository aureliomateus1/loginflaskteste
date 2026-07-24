from datetime import datetime, timedelta
from flask import session

SESSAO_TIMEOUT_MINUTOS = 30


def sessao_valida():
    """
    Verifica se existe um usuário autenticado na sessão e se ela não expirou
    por inatividade. Substitui o antigo modelo de "sessão de uso único", que
    invalidava a sessão na primeira checagem — o que quebrava qualquer
    chamada de API feita logo em seguida na mesma página.

    Cada chamada autenticada renova o timer de inatividade. Depois de
    SESSAO_TIMEOUT_MINUTOS sem nenhuma requisição, a sessão expira sozinha.
    """
    if 'usuario' not in session:
        return False

    agora = datetime.now()
    ultimo_acesso = session.get('ultimo_acesso')

    if ultimo_acesso:
        try:
            ultimo_dt = datetime.fromisoformat(ultimo_acesso)
        except ValueError:
            ultimo_dt = agora
        if agora - ultimo_dt > timedelta(minutes=SESSAO_TIMEOUT_MINUTOS):
            session.pop('usuario', None)
            session.pop('ultimo_acesso', None)
            return False

    session['ultimo_acesso'] = agora.isoformat()
    return True
