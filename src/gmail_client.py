import os
import pickle
import re
import base64
import logging
from email import message_from_bytes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURAZIONE GMAIL (HARDCODED PER TEST)
# ============================================================
GMAIL_SENDER_EMAIL = "cuffaricristianfelice@gmail.com"
GMAIL_APP_PASSWORD = "nyca vbcq dlpd yxgg"  # Sostituisci con la tua password app

def get_gmail_service():
    """
    RESTITUISCE UN SERVIZIO GMAIL "FITTIZIO" PER INVIO EMAIL VIA SMTP.
    (NON USA LE API GOOGLE PER LEGGERE, USA SOLO SMTP PER INVIO)
    """
    # Questa funzione è mantenuta per compatibilità con il codice esistente.
    # Restituisce un oggetto contenitore con i parametri per l'invio.
    class GmailService:
        def __init__(self, sender, password):
            self.sender = sender
            self.password = password
    return GmailService(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)

def send_report_email(service, to_email, subject, html_body):
    """
    Invia un'email HTML via SMTP Gmail.
    - service: oggetto restituito da get_gmail_service()
    - to_email: destinatario (es. 'me' o indirizzo email)
    - subject: oggetto dell'email
    - html_body: contenuto HTML
    """
    if to_email == 'me':
        to_email = GMAIL_SENDER_EMAIL

    # Costruisci il messaggio MIME
    msg = MIMEMultipart('alternative')
    msg['From'] = service.sender
    msg['To'] = to_email
    msg['Subject'] = subject

    # Versione testo (plain) e HTML
    plain_text = re.sub(r'<[^>]+>', '', html_body)  # Semplice conversione da HTML a testo
    part1 = MIMEText(plain_text, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        # Connessione SMTP a Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(service.sender, service.password)
            server.sendmail(service.sender, to_email, msg.as_string())
        logger.info(f"📧 Email inviata a {to_email}")
        return f"Email inviata a {to_email}"
    except Exception as e:
        logger.error(f"❌ Errore invio email: {e}")
        return f"Errore: {e}"

def get_email_details(service, msg_id):
    """
    Funzione dummy per compatibilità (non usata dall'agente di costi).
    """
    return {
        "id": msg_id,
        "sender": "dummy@example.com",
        "domain": "example.com",
        "subject": "Dummy",
        "internal_date": 0
    }

def get_email_details_adf(service, msg_id):
    """
    Funzione dummy per compatibilità (non usata dall'agente di costi).
    """
    return {
        "id": msg_id,
        "sender": "dummy@example.com",
        "subject": "Dummy",
        "body": "",
        "pipeline_name": None,
        "error": "",
        "internal_date": 0
    }

def mark_as_read(service, msg_id):
    """
    Funzione dummy per compatibilità (non usata dall'agente di costi).
    """
    logger.info(f"📌 Email {msg_id} marcata come letta (dummy).")
    return f"Email {msg_id} marcata come letta."

def send_report_email_legacy(service, to_email, subject, html_body):
    """
    Alias per send_report_email (compatibilità).
    """
    return send_report_email(service, to_email, subject, html_body)
