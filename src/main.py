import os
import logging
import json
from datetime import datetime
from src.data_aggregator import aggregate_and_save
from src.cost_analyzer import analyze_inventory
from src.email_builder import build_azure_style_email
from src.executor import execute_approved_actions
from src.gmail_client import get_gmail_service, send_report_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Avvio Azure Cost Optimization Agent...")
    
    # 1. Estrai dati da Azure e salva su Supabase
    aggregate_and_save()
    
    # 2. Analizza con DeepSeek e genera proposte
    analysis_result = analyze_inventory()
    
    # 3. Salva proposte su Supabase (status PENDING)
    recommendations = analysis_result.get('recommendations', [])
    from supabase import create_client
    SUPABASE_URL = "https://ksxqnrxphizxrtloqlcd.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzeHFucnhwaGl6eHJ0bG9xbGNkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzQxMDcxNSwiZXhwIjoyMDk4OTg2NzE1fQ.OeL_Ao9tTXKgC6IR5Ber1Wj_slVsNz89toEjETE6Mwo"
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    for rec in recommendations:
        # Controlla se esiste già una proposta per questa risorsa
        existing = supabase.table("azure_cost_proposals").select("id").eq("resource_id", rec.get('resource_id')).eq("status", "PENDING").execute()
        if existing.data and len(existing.data) > 0:
            logger.info(f"⏩ Proposta già esistente per {rec.get('resource_name')}")
            continue

        data = {
            "resource_id": rec.get('resource_id'),
            "resource_name": rec.get('resource_name'),
            "action_type": rec.get('recommended_action', 'UNKNOWN'),
            "current_state": rec.get('current_state', ''),
            "proposed_sku": rec.get('proposed_sku'),
            "estimated_monthly_savings": rec.get('estimated_monthly_savings', 0),
            "reasoning": rec.get('reasoning', ''),
            "severity": rec.get('severity', 'MEDIUM'),
            "category": rec.get('category', 'COST_OPTIMIZATION'),
            "status": "PENDING"
        }
        supabase.table("azure_cost_proposals").insert(data).execute()
        logger.info(f"💡 Proposta creata per {rec.get('resource_name')}")

    # 4. Costruisci email
    APPROVAL_SERVER_URL = os.getenv("APPROVAL_SERVER_URL", "https://fn-approval-server.azurewebsites.net")
    html_body = build_azure_style_email(analysis_result, APPROVAL_SERVER_URL)
    
    # 5. Invia email
    service = get_gmail_service()
    send_report_email(
        service,
        os.getenv("GMAIL_RECIPIENT", "me"),
        f"☁️ Azure Cost Report - {datetime.now().strftime('%Y-%m-%d')}",
        html_body
    )
    logger.info("📧 Email inviata.")
    
    # 6. Esegui azioni già approvate (dal giorno prima)
    execute_approved_actions()
    
    logger.info("🏁 Elaborazione completata.")

if __name__ == "__main__":
    main()
