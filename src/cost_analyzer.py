import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# Carica DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)

# Il Prompt (definito sopra)
SYSTEM_PROMPT = """
Sei un Azure Solutions Architect con 10 anni di esperienza in FinOps...
"""  # Inserisci il prompt completo qui

def analyze_inventory():
    """Analizza l'inventario e genera proposte."""
    logger.info("🧠 Analisi con DeepSeek...")
    
    # Recupera tutti i dati da Supabase (o da Azure direttamente)
    response = supabase.table("azure_inventory").select("*").execute()
    resources = response.data if response.data else []
    
    if not resources:
        logger.warning("⚠️ Nessuna risorsa trovata.")
        return []
    
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
        return result
    except Exception as e:
        logger.error(f"❌ Errore analisi: {e}")
        return {"summary": {}, "recommendations": []}
