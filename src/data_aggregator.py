import os
import logging
from supabase import create_client
from src.azure_client import get_all_resources_with_metrics, get_vm_metrics, get_monthly_cost

logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ksxqnrxphizxrtloqlcd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzeHFucnhwaGl6eHJ0bG9xbGNkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzQxMDcxNSwiZXhwIjoyMDk4OTg2NzE1fQ.OeL_Ao9tTXKgC6IR5Ber1Wj_slVsNz89toEjETE6Mwo"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def aggregate_and_save():
    """Estrae dati da Azure e li salva su Supabase."""
    logger.info("🔄 Inizio aggregazione dati Azure...")
    
    resources = get_all_resources_with_metrics()
    
    for r in resources:
        resource_id = r.get('id')
        resource_name = r.get('name')
        resource_type = r.get('type')
        location = r.get('location')
        tags = r.get('tags', {})
        subscription_id = r.get('subscriptionId')
        resource_group = r.get('resourceGroup')
        
        # Arricchisce con metriche e costi
        metrics = {}
        monthly_cost = 0.0
        if "virtualMachines" in resource_type:
            metrics = get_vm_metrics(resource_id, resource_name)
            monthly_cost = get_monthly_cost(resource_id)
        
        # Salva su Supabase (tabella azure_inventory)
        data = {
            "resource_id": resource_id,
            "resource_name": resource_name,
            "resource_type": resource_type,
            "location": location,
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "tags": tags,
            "metrics": metrics,
            "monthly_cost": monthly_cost,
            "last_updated": datetime.now().isoformat()
        }
        supabase.table("azure_inventory").upsert(data, on_conflict="resource_id").execute()
    
    logger.info(f"✅ Aggiornate {len(resources)} risorse su Supabase.")
