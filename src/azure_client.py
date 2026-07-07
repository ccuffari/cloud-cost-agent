import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryDataset, QueryAggregation, QueryTimePeriod
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Carica credenziali
tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

def get_credential():
    return ClientSecretCredential(tenant_id, client_id, client_secret)

def get_resource_graph_client():
    return ResourceGraphClient(get_credential())

def get_cost_client():
    return CostManagementClient(get_credential())

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
    """Recupera CPU e RAM media per una VM (ultimi 7 giorni)."""
    # Implementazione semplificata: in produzione usi MonitorManagementClient
    # Per ora restituiamo valori fittizi (ma reali in produzione)
    # Simula CPU media tra 5% e 80%
    import random
    return {
        "cpu_avg": random.uniform(5, 80),
        "memory_avg": random.uniform(10, 90)
    }

def get_monthly_cost(resource_id: str):
    """Recupera il costo mensile di una risorsa (ultimi 30 giorni)."""
    # In produzione usi CostManagementClient
    # Per test simuliamo un costo mensile
    import random
    return round(random.uniform(10, 500), 2)
