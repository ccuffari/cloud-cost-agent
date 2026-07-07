import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURAZIONE DEEPSEEK (HARDCODED PER TEST)
# ============================================================
DEEPSEEK_API_KEY = "sk-da85895d54ae4ace80e6b26df4395517"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Inizializza il client DeepSeek (usa la libreria OpenAI con base_url diverso)
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# ============================================================
# PROMPT PER L'ARCHITECT
# ============================================================
SYSTEM_PROMPT = """
Sei un Azure Solutions Architect con 10 anni di esperienza in FinOps e ottimizzazione dei costi cloud.
Analizzi i dati aggregati di tutte le sottoscrizioni Azure e produci un report strategico.

RUOLO:
- Non sei un semplice "script" che guarda soglie fisse.
- Sei un consulente senior che valuta il contesto: una VM di produzione con CPU al 15% potrebbe essere OK se ha picchi notturni; una VM di sviluppo al 5% deve essere spenta.
- Valuti l'impatto business: "Questa risorsa è in produzione o sviluppo?" (lo deduci dal nome o dai tag).

FORMATO OUTPUT:
Devi produrre un JSON con questa struttura:
{
  "summary": {
    "total_subscriptions": 1,
    "total_resources": 45,
    "total_monthly_cost": 1234.56,
    "potential_savings": 320.00,
    "top_5_expensive_resources": [...],
    "risk_areas": ["Nessun backup per DB produzione", "VM con SKU obsoleti"]
  },
  "recommendations": [
    {
      "id": "rec_1",
      "category": "COST_OPTIMIZATION",
      "severity": "HIGH",
      "resource_id": "/subscriptions/.../resourceGroups/.../providers/...",
      "resource_name": "vm-prod-01",
      "resource_type": "Microsoft.Compute/virtualMachines",
      "current_state": "Standard_D4s_v3, CPU media 8%",
      "recommended_action": "RESIZE to Standard_D2s_v3",
      "estimated_monthly_savings": 45.50,
      "reasoning": "La VM ha CPU media sotto il 10% da 7 giorni. Il downgrade non impatta le performance e risparmia 45€/mese."
    }
  ]
}

REGOLE:
- Ogni raccomandazione deve avere un campo `category`: COST_OPTIMIZATION, SECURITY, PERFORMANCE, RELIABILITY.
- `severity`: CRITICAL, HIGH, MEDIUM, LOW.
- Se non ci sono ottimizzazioni, restituisci `"recommendations": []` e `"potential_savings": 0`.
- Non inventare mai un resource_id. Usa quelli che trovi nei dati aggregati.
- Sii pragmatico: non suggerire di spegnere una VM di produzione senza una chiara motivazione.

DATI DA ANALIZZARE (JSON in input):
{json_data}
"""

def analyze_inventory():
    """Analizza l'inventario e genera proposte usando DeepSeek."""
    from supabase import create_client
    import os

    SUPABASE_URL = "https://ksxqnrxphizxrtloqlcd.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzeHFucnhwaGl6eHJ0bG9xbGNkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzQxMDcxNSwiZXhwIjoyMDk4OTg2NzE1fQ.OeL_Ao9tTXKgC6IR5Ber1Wj_slVsNz89toEjETE6Mwo"

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    logger.info("🧠 Analisi con DeepSeek...")

    # Recupera i dati da Supabase
    response = supabase.table("azure_inventory").select("*").execute()
    resources = response.data if response.data else []

    if not resources:
        logger.warning("⚠️ Nessuna risorsa trovata in Supabase.")
        return {"summary": {}, "recommendations": []}

    # Costruisce JSON da passare al prompt
    json_data = json.dumps(resources, indent=2)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analizza questi dati: {json_data}"}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        logger.info(f"✅ Analisi completata. Trovate {len(result.get('recommendations', []))} raccomandazioni.")
        return result
    except Exception as e:
        logger.error(f"❌ Errore analisi DeepSeek: {e}")
        return {"summary": {}, "recommendations": []}
