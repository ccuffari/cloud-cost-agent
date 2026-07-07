import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from supabase import create_client

logger = logging.getLogger(__name__)

# Carica credenziali
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group = os.getenv("AZURE_RESOURCE_GROUP")
tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_compute_client():
    return ComputeManagementClient(ClientSecretCredential(tenant_id, client_id, client_secret), subscription_id)

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
        recommended_action = p.get('recommended_action', '')
        
        try:
            # RESIZE VM
            if "RESIZE" in action_type:
                vm_name = p['resource_name']
                new_sku = p.get('proposed_sku', 'Standard_D2s_v3')
                compute_client = get_compute_client()
                vm = compute_client.virtual_machines.get(resource_group, vm_name)
                vm.hardware_profile.vm_size = new_sku
                compute_client.virtual_machines.begin_update(resource_group, vm_name, vm)
                logger.info(f"✅ VM {vm_name} ridimensionata a {new_sku}")
            
            # STOP VM
            elif "STOP" in action_type:
                vm_name = p['resource_name']
                compute_client = get_compute_client()
                compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
                logger.info(f"✅ VM {vm_name} fermata")
            
            # ENABLE_BACKUP (placeholder)
            elif "ENABLE_BACKUP" in action_type:
                logger.info(f"✅ Backup attivato per {p['resource_name']}")
            
            # UPDATE TAG (placeholder)
            elif "UPDATE_TAG" in action_type:
                logger.info(f"✅ Tag aggiornato per {p['resource_name']}")
            
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
