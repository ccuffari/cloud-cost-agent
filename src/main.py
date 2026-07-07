import os
import logging
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
    for rec in recommendations:
        supabase.table("azure_cost_proposals").insert({
            "resource_id": rec['resource_id'],
            "resource_name": rec['resource_name'],
            "action_type": rec['recommended_action'],
            "current_state": rec['current_state'],
            "proposed_sku": rec.get('proposed_sku'),
            "estimated_monthly_savings": rec.get('estimated_monthly_savings', 0),
            "reasoning": rec['reasoning'],
            "severity": rec['severity'],
            "category": rec['category']
        }).execute()
    
    # 4. Costruisci email
    approval_base_url = os.getenv("APPROVAL_SERVER_URL", "https://fn-approval-server.azurewebsites.net")
    html_body = build_azure_style_email(analysis_result, approval_base_url)
    
    # 5. Invia email
    service = get_gmail_service()
    send_report_email(
        service,
        os.getenv("GMAIL_RECIPIENT", "me"),
        f"☁️ Azure Cost Report - {datetime.now().strftime('%Y-%m-%d')}",
        html_body
    )
    
    # 6. Esegui azioni già approvate (dal giorno prima)
    execute_approved_actions()
    
    logger.info("🏁 Elaborazione completata.")

if __name__ == "__main__":
    main()
