from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

_scheduler = None


def iniciar_scheduler(app):
    """
    Inicia um BackgroundScheduler que roda a checagem de vencimentos todo dia
    no horário configurado (NOTIFICACOES_HORA).

    ATENÇÃO: isso só funciona de forma confiável em serviços que ficam sempre
    ativos. No plano free do Render, a aplicação "dorme" após um período sem
    acesso e esse agendador para de rodar junto. Para produção nesse cenário,
    prefira um cron externo (Render Cron Job, cron-job.org, GitHub Actions
    schedule) chamando POST /api/notificacoes/verificar com o header
    X-Notificacoes-Token.
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    hora_str = app.config.get('NOTIFICACOES_HORA', '08:00')
    hora, minuto = hora_str.split(':')

    _scheduler = BackgroundScheduler(timezone='America/Sao_Paulo')

    def job():
        with app.app_context():
            from services.notificacao_service import verificar_e_notificar
            try:
                resultado = verificar_e_notificar()
                app.logger.info(f'[notificacoes] Checagem diária: {resultado}')
            except Exception as erro:
                app.logger.error(f'[notificacoes] Falha ao enviar notificação: {erro}')

    _scheduler.add_job(job, CronTrigger(hour=int(hora), minute=int(minuto)))
    _scheduler.start()
    return _scheduler
