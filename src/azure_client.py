import os
import logging
import random
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions

logger = logging.getLogger(__name__)

# ============================================================
# CREDENZIALI AZURE (HARDCODED PER TEST)
# ============================================================
AZURE_SUBSCRIPTION_ID = "9154481d-de4a-4a89-a60d-b0d000740638"
AZURE_TENANT_ID = "43d04a32-4ce3-492a-9d6e-ba61b3e6882d"
AZURE_CLIENT_ID = "91453230-ac69-4ea4-93f0-d611299db661"
AZURE_CLIENT_SECRET = "zTW8Q~4z_zk6Nc0XD81Xg6vUHSlXTuoHOpIy6dn7"

def get_credential():
    return ClientSecretCredential(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)

def get_resource_graph_client():
    return ResourceGraphClient(get_credential())

def query_azure_resource_graph(query: str):
    """Esegue una query su Azure Resource Graph."""
    client = get_resource_graph_client()
    request = QueryRequest(
        query=query,
        options=QueryRequestOptions(result_format="objectArray")
    )
    response = client.resources(request)
    return response.data

def get_all_resources_with_metrics():
    """Recupera TUTTE le risorse con metriche di base."""
    logger.info("📊 Estrazione risorse da Azure Resource Graph...")
    
    query = """
    resources
    | where type in (
        'Microsoft.Compute/virtualMachines',
        'Microsoft.Sql/servers/databases',
        'Microsoft.Storage/storageAccounts',
        'Microsoft.Web/sites',
        'Microsoft.ContainerService/managedClusters'
    )
    | project 
        subscriptionId,
        resourceGroup,
        id,
        name,
        type,
        location,
        tags,
        properties
    """
    
    resources = query_azure_resource_graph(query)
    logger.info(f"✅ Trovate {len(resources)} risorse.")
    return resources

def get_vm_metrics(vm_id: str, vm_name: str):
    """Recupera CPU e RAM media per una VM (simulato per test)."""
    return {
        "cpu_avg": random.uniform(5, 80),
        "memory_avg": random.uniform(10, 90)
    }

def get_monthly_cost(resource_id: str):
    """Recupera il costo mensile di una risorsa (simulato per test)."""
    return round(random.uniform(10, 500), 2)
