import json
from datetime import datetime

def build_azure_style_email(analysis_result, approval_base_url):
    """Costruisce un'email HTML in stile Azure."""
    summary = analysis_result.get('summary', {})
    recommendations = analysis_result.get('recommendations', [])
    
    # CSS Azure Style
    css = """
    <style>
        body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px; }
        .header { background: linear-gradient(135deg, #0078D4, #005A9E); color: white; padding: 20px; border-radius: 6px 6px 0 0; margin: -30px -30px 20px -30px; padding-left: 30px; }
        .header h1 { margin: 0; font-weight: 300; font-size: 24px; }
        .header small { opacity: 0.8; font-size: 14px; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
        .summary-card { background: #f0f2f5; padding: 15px; border-radius: 6px; text-align: center; border-left: 4px solid #0078D4; }
        .summary-card .number { font-size: 24px; font-weight: 600; color: #0078D4; }
        .summary-card .label { font-size: 13px; color: #666; margin-top: 4px; }
        .savings { color: #107C10; font-weight: bold; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th { background: #0078D4; color: white; padding: 10px; text-align: left; font-weight: 500; }
        .table td { padding: 10px; border-bottom: 1px solid #e5e5e5; }
        .table tr:hover { background: #f5f8fa; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .badge-critical { background: #a80000; color: white; }
        .badge-high { background: #d83b01; color: white; }
        .badge-medium { background: #ffb900; color: #333; }
        .badge-low { background: #107C10; color: white; }
        .btn { display: inline-block; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: 600; font-size: 13px; }
        .btn-approve { background: #107C10; color: white; }
        .btn-reject { background: #a80000; color: white; }
        .btn-approve-all { background: #0078D4; color: white; padding: 12px 24px; font-size: 16px; }
        .footer { margin-top: 30px; color: #999; font-size: 12px; border-top: 1px solid #ddd; padding-top: 15px; }
        .tag { display: inline-block; background: #e5e5e5; padding: 2px 8px; border-radius: 3px; font-size: 11px; color: #333; }
    </style>
    """
    
    # Summary Cards
    total_resources = summary.get('total_resources', 0)
    total_cost = summary.get('total_monthly_cost', 0)
    potential_savings = summary.get('potential_savings', 0)
    risk_areas = summary.get('risk_areas', [])
    
    summary_html = f"""
    <div class="summary-grid">
        <div class="summary-card">
            <div class="number">{total_resources}</div>
            <div class="label">Totale Risorse</div>
        </div>
        <div class="summary-card">
            <div class="number">€{total_cost:.2f}</div>
            <div class="label">Costo Mensile</div>
        </div>
        <div class="summary-card" style="border-left-color: #107C10;">
            <div class="number savings">€{potential_savings:.2f}</div>
            <div class="label">Risparmio Potenziale</div>
        </div>
        <div class="summary-card" style="border-left-color: #d83b01;">
            <div class="number">{len(risk_areas)}</div>
            <div class="label">Aree di Rischio</div>
        </div>
    </div>
    """
    
    # Tabella raccomandazioni
    rows = ""
    for rec in recommendations[:20]:  # Limita a 20 per email
        rec_id = rec.get('id', '')
        category = rec.get('category', 'COST_OPTIMIZATION')
        severity = rec.get('severity', 'MEDIUM')
        resource_name = rec.get('resource_name', 'N/A')
        resource_type = rec.get('resource_type', 'N/A').split('/')[-1]
        current_state = rec.get('current_state', '')
        recommended_action = rec.get('recommended_action', '')
        savings = rec.get('estimated_monthly_savings', 0)
        reasoning = rec.get('reasoning', '')
        
        # Genera token JWT per approvazione
        token = jwt.encode(
            {"proposal_id": rec_id, "exp": datetime.utcnow() + timedelta(hours=48)},
            JWT_SECRET_KEY,
            algorithm="HS256"
        )
        approve_link = f"{approval_base_url}/approve/cost/{token}"
        reject_link = f"{approval_base_url}/reject/cost/{token}"
        
        badge_class = f"badge-{severity.lower()}"
        rows += f"""
        <tr>
            <td><b>{resource_name}</b><br><span class="tag">{resource_type}</span></td>
            <td>{current_state}</td>
            <td><span class="badge {badge_class}">{severity}</span></td>
            <td><b>{recommended_action}</b><br><small>{reasoning[:80]}...</small></td>
            <td style="color:#107C10; font-weight:bold;">€{savings:.2f}</td>
            <td>
                <a href="{approve_link}" class="btn btn-approve">✅ Approva</a>
                <a href="{reject_link}" class="btn btn-reject">❌ Rifiuta</a>
            </td>
        </tr>
        """
    
    table_html = f"""
    <table class="table">
        <tr>
            <th>Risorsa</th>
            <th>Stato Attuale</th>
            <th>Severità</th>
            <th>Azione Proposta</th>
            <th>Risparmio</th>
            <th>Approvazione</th>
        </tr>
        {rows}
    </table>
    """
    
    # Assemble HTML
    html = f"""
    <html>
    <head>{css}</head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☁️ Azure Cost Optimization Report</h1>
                <small>{datetime.now().strftime('%A, %d %B %Y - %H:%M')}</small>
            </div>
            
            {summary_html}
            
            <div style="margin: 20px 0; text-align: center;">
                <a href="{approval_base_url}/approve/all/cost" class="btn btn-approve-all" style="background:#0078D4; color:white; padding:12px 30px; border-radius:4px; text-decoration:none; font-weight:bold;">
                    ✅ APPROVA TUTTE LE PROPOSTE
                </a>
            </div>
            
            <h2 style="margin-top:30px;">📋 Raccomandazioni</h2>
            {table_html if rows else '<p>✅ Nessuna azione necessaria. Tutte le risorse sono ottimizzate.</p>'}
            
            <div class="footer">
                <p>Questo report è stato generato automaticamente dal <b>Azure Cost Optimization Agent</b>.</p>
                <p>I link di approvazione scadono tra 48 ore.</p>
                <p style="color:#0078D4;">Azure Cost Agent v2.0</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
