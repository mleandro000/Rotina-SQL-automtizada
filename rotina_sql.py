#!/usr/bin/env python3
"""
rotina_telegram.py

Automação diária de rotina SQL com notificações via Telegram e logs rotativos.
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import asyncio
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from telegram import Bot
# Import condicional de Request/HTTPXRequest para compatibilidade com v13+ e v20+
try:
    from telegram.utils.request import Request as PTBRequest
    RequestClass = PTBRequest
    REQUEST_PARAMS = dict(con_pool_size=16, pool_timeout=5.0)
except ImportError:
    from telegram.request import HTTPXRequest as PTBRequest
    RequestClass = PTBRequest
    REQUEST_PARAMS = dict(connection_pool_size=16, pool_timeout=5.0)
from dotenv import load_dotenv, find_dotenv

# --------------------------------------------------
# Configurações iniciais
# --------------------------------------------------
# Política de loop no Windows para evitar "Event loop is closed"
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Carrega variáveis de ambiente
dotenv_path = find_dotenv(usecwd=True)
load_dotenv(dotenv_path)

# Variáveis de ambiente obrigatórias
SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not all([SQL_SERVER, SQL_DATABASE, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    raise RuntimeError(
        "Faltam variáveis de ambiente: SQL_SERVER, SQL_DATABASE, "
        "TELEGRAM_TOKEN, TELEGRAM_CHAT_ID"
    )

# Configuração de logging com rotação
logger = logging.getLogger("rotina")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('rotina.log', maxBytes=5*1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(handler)

# Configura o Bot do Telegram com pool otimizado
def create_bot():
    request = RequestClass(**REQUEST_PARAMS)
    return Bot(token=TELEGRAM_TOKEN, request=request)
bot = create_bot()

# --------------------------------------------------
# Funções utilitárias
# --------------------------------------------------

def notify(message: str) -> None:
    """
    Envia uma mensagem via Telegram usando um loop dedicado.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message))
    except Exception as err:
        logger.error(f"Falha ao enviar Telegram: {err}")
    finally:
        loop.close()

# --------------------------------------------------
# Lógica principal do job
# --------------------------------------------------
def job() -> None:
    """
    Executa rotina SQL e notifica início, sucesso ou erro, registrando métricas.
    """
    start = datetime.now()
    notify(f"[ROUTINA] Início: {start:%Y-%m-%d %H:%M:%S}")
    logger.info(f"[ROUTINA] Início: {start:%Y-%m-%d %H:%M:%S}")

    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    try:
        import pyodbc
        with pyodbc.connect(conn_str) as conn:
            cur = conn.cursor()
            cur.execute("""
                DECLARE @MaxUpdateDate DATETIME;
                SELECT @MaxUpdateDate = MAX(UpdateDate)
                  FROM [ContosoRetailDW].[dbo].[DimAccount];

                IF OBJECT_ID('dbo.DimAccountLatest','U') IS NOT NULL
                    DROP TABLE dbo.DimAccountLatest;

                SELECT *
                  INTO dbo.DimAccountLatest
                  FROM [ContosoRetailDW].[dbo].[DimAccount]
                 WHERE UpdateDate = @MaxUpdateDate;
            """)
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM dbo.DimAccountLatest")
            count = cur.fetchone()[0]

        end = datetime.now()
        duration = (end - start).total_seconds()
        msg = (
            f"[ROUTINA] Concluída: {end:%Y-%m-%d %H:%M:%S}"  
            f" | Duração: {duration:.1f}s | Linhas: {count}"
        )
        notify(msg)
        logger.info(msg)
    except Exception as err:
        error_msg = f"[ROUTINA] ERRO: {err}"
        notify(error_msg)
        logger.error(error_msg)

# --------------------------------------------------
if __name__ == "__main__":
    HOUR, MINUTE = 14, 50
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        job,
        trigger='cron',
        hour=HOUR,
        minute=MINUTE,
        misfire_grace_time=300
    )

    # Listener para eventos de job
    def listener(event):
        if event.exception:
            notify(f"[SCHEDULER] ERRO no job: {event.exception}")
        else:
            notify(f"[SCHEDULER] Job executado com sucesso às {datetime.now():%H:%M:%S}")
    scheduler.add_listener(
        listener,
        EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
    )

    start_msg = f"[SCHEDULER] Iniciado — agendado para {HOUR:02d}:{MINUTE:02d} BRT"
    notify(start_msg)
    logger.info(start_msg)

    scheduler.start()
