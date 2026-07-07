import os
import logging
from datetime import datetime
from supabase import create_client
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ksxqnrxphizxrtloqlcd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzeHFucnhwaGl6eHJ0bG9xbGNkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzQxMDcxNSwiZXhwIjoyMDk4OTg2NzE1fQ.OeL_Ao9tTXKgC6IR5Ber1Wj_slVsNz89toEjETE6Mwo"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

AZURE_SUBSCRIPTION_ID = "9154481d-de4a-4a89-a60d-b0d000740638"
AZURE_RESOURCE_GROUP = "dph_rg"
AZURE_TENANT_ID = "43d04a32-4ce3-492a-9d6e-ba61b3e6882d"
AZURE_CLIENT_ID = "91453230-ac69-4ea4-93f0-d611299db661"
AZURE_CLIENT_SECRET = "zTW8Q~4z_zk6Nc0XD81Xg6vUHSlXTuoHOpIy6dn7"

def get_compute_client():
    return ComputeManagementClient(
        ClientSecretCredential(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET),
        AZURE_SUBSCRIPTION_ID
    )

def execute_approved_actions():
    """Esegue le azioni approvate."""
    response = supabase.table("azure_cost_proposals")\
        .select("*")\
        .eq("status", "APPROVED")\
        .is_("executed_at", "null")\
        .execute()
    proposals = response.data if response.data else []
    
    if not proposals:
        logger.info("✅ Nessuna azione approvata in sospeso.")
        return
    
    logger.info(f"⚡ Esecuzione di {len(proposals)} azioni approvate...")
    
    for p in proposals:
        proposal_id = p['id']
        resource_id = p['resource_id']
        action_type = p['action_type']
        resource_name = p['resource_name']
        
        try:
            if "RESIZE" in action_type:
                vm_name = resource_name
                new_sku = p.get('proposed_sku', 'Standard_D2s_v3')
                compute_client = get_compute_client()
                vm = compute_client.virtual_machines.get(AZURE_RESOURCE_GROUP, vm_name)
                vm.hardware_profile.vm_size = new_sku
                compute_client.virtual_machines.begin_update(AZURE_RESOURCE_GROUP, vm_name, vm)
                logger.info(f"✅ VM {vm_name} ridimensionata a {new_sku}")
            
            elif "STOP" in action_type:
                vm_name = resource_name
                compute_client = get_compute_client()
                compute_client.virtual_machines.begin_deallocate(AZURE_RESOURCE_GROUP, vm_name)
                logger.info(f"✅ VM {vm_name} fermata")
            
            # Segna come eseguito
            supabase.table("azure_cost_proposals").update({
                "status": "EXECUTED",
                "executed_at": datetime.now().isoformat(),
                "executed_success": True
            }).eq("id", proposal_id).execute()
            
        except Exception as e:
            logger.error(f"❌ Errore esecuzione proposta {proposal_id}: {e}")
            supabase.table("azure_cost_proposals").update({
                "status": "FAILED",
                "error_message": str(e)
            }).eq("id", proposal_id).execute()
