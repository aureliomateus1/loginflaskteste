import os


def _bool_env(nome, padrao=True):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in ('1', 'true', 'sim', 'yes')


class Config:
    # ===== Aplicação =====
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-provisoria-trocar-em-producao')

    # ===== Banco de dados =====
    # Se DATABASE_URL existir (Render com PostgreSQL conectado), usa Postgres.
    # Caso contrário, usa SQLite local (banco.db).
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # ===== Notificações via WhatsApp (Twilio) =====
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    # Número padrão do Sandbox do Twilio. Ao migrar para produção, troca pelo
    # número WhatsApp Business aprovado.
    TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
    # Número que deve receber os alertas, formato: whatsapp:+55DDDNUMERO
    WHATSAPP_DESTINO = os.environ.get('WHATSAPP_DESTINO')

    # Quantos dias antes do vencimento um item entra no alerta (inclui vencidos)
    DIAS_ALERTA = int(os.environ.get('DIAS_ALERTA', 3))

    # Token exigido pelo endpoint /api/notificacoes/verificar, usado por um
    # cron externo (já que o plano free do Render "dorme" e não garante que o
    # agendador interno rode todo dia no horário certo)
    NOTIFICACOES_TOKEN = os.environ.get('NOTIFICACOES_TOKEN', 'troque-este-token')

    # Horário (HH:MM, fuso America/Sao_Paulo) em que o agendador interno roda,
    # útil quando a aplicação está hospedada num serviço que fica sempre ativo
    NOTIFICACOES_HORA = os.environ.get('NOTIFICACOES_HORA', '08:00')

    # Liga/desliga o agendador interno (BackgroundScheduler). Em ambientes que
    # dormem (Render free), prefira deixar False e usar um cron externo
    # chamando /api/notificacoes/verificar.
    SCHEDULER_ATIVO = _bool_env('SCHEDULER_ATIVO', padrao=False)
