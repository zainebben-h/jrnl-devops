#!/usr/bin/env python3
"""
Script de monitoring Docker simplifié pour jrnl
"""

import subprocess
import datetime
import re

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Erreur: {e}"

def get_container_info():
    """Récupère les informations des conteneurs"""
    cmd = "docker ps --format \"{{.Names}}|{{.Status}}|{{.Image}}\""
    output = run_command(cmd)
    
    containers = []
    if output and "Erreur" not in output:
        for line in output.split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 3:
                    containers.append({
                        'name': parts[0],
                        'status': parts[1],
                        'image': parts[2]
                    })
    return containers

def get_simple_stats():
    """Récupère les stats de manière simplifiée"""
    cmd = "docker stats --no-stream --format \"table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\""
    output = run_command(cmd)
    return output

def get_logs(container_name="jrnl-container"):
    """Récupère les logs"""
    cmd = f'docker logs --tail 50 {container_name} 2>&1'
    output = run_command(cmd)
    if not output or "No such container" in output:
        output = "Aucun log disponible - Le conteneur n'est pas en cours d'exécution"
    return output

def generate_dashboard():
    """Génère le dashboard HTML"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get container info
    containers = get_container_info()
    
    # Get stats
    stats_output = get_simple_stats()
    
    # Parse stats into HTML table rows
    stats_rows = ""
    if stats_output and "NAME" in stats_output:
        lines = stats_output.split('\n')[1:]  # Skip header
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    stats_rows += f"""
                    <tr>
                        <td>{parts[0]}</td>
                        <td>{parts[1]}</td>
                        <td>{parts[2]} / {parts[3]}</td>
                        <td>{parts[4]}</td>
                    </tr>
                    """
    
    if not stats_rows:
        stats_rows = "<tr><td colspan='4'>Aucun conteneur en cours d'exécution</td></tr>"
    
    # Get logs
    logs = get_logs()
    
    # Container status cards
    container_cards = ""
    if containers:
        for c in containers:
            container_cards += f"""
            <div class="status-card">
                <h3>📦 {c['name']}</h3>
                <p><strong>Status:</strong> <span class="status running">✓ {c['status']}</span></p>
                <p><strong>Image:</strong> {c['image']}</p>
            </div>
            """
    else:
        container_cards = """
        <div class="status-card">
            <h3>⚠️ Aucun conteneur actif</h3>
            <p>Démarrez un conteneur avec: <code>docker-compose up -d</code></p>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Monitoring - jrnl DevOps</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                padding: 20px;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            header {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            
            h1 {{
                color: #667eea;
                margin-bottom: 10px;
            }}
            
            .timestamp {{
                color: #666;
                font-size: 14px;
            }}
            
            .dashboard {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .card h2 {{
                color: #667eea;
                margin-bottom: 20px;
                font-size: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            .status-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }}
            
            .status-card h3 {{
                margin-bottom: 10px;
                color: #667eea;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            th {{
                background-color: #f5f5f5;
                font-weight: 600;
                color: #667eea;
            }}
            
            tr:hover {{
                background-color: #f9f9f9;
            }}
            
            .logs {{
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.6;
                overflow-x: auto;
                max-height: 400px;
                overflow-y: auto;
            }}
            
            .status {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            
            .status.running {{
                background-color: #4caf50;
                color: white;
            }}
            
            .refresh-btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
            }}
            
            .refresh-btn:hover {{
                background: #5568d3;
            }}
            
            code {{
                background: #e0e0e0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Dashboard Monitoring - jrnl DevOps</h1>
                <p class="timestamp">Dernière mise à jour: {timestamp}</p>
                <button class="refresh-btn" onclick="location.reload()">🔄 Actualiser</button>
            </header>
            
            <div class="dashboard">
                <div class="card">
                    <h2>🐳 Conteneurs Actifs</h2>
                    {container_cards}
                </div>
                
                <div class="card">
                    <h2>📈 Métriques des Conteneurs</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Conteneur</th>
                                <th>CPU</th>
                                <th>Mémoire</th>
                                <th>% Mémoire</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="card">
                    <h2>📋 Logs du Conteneur</h2>
                    <div class="logs">
                        <pre>{logs}</pre>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    print("🔍 Collecte des métriques Docker...")
    
    # Generate dashboard
    html = generate_dashboard()
    
    # Save to file
    output_file = "dashboard.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard généré: {output_file}")
    print(f"📂 Ouvrez {output_file} dans votre navigateur")
    
    # Show quick info
    containers = get_container_info()
    if containers:
        print("\n📦 Conteneurs actifs:")
        for c in containers:
            print(f"  - {c['name']} ({c['status']})")
    else:
        print("\n⚠️  Aucun conteneur actif")
        print("💡 Démarrez avec: docker-compose up -d")

if __name__ == "__main__":
    main()