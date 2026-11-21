#!/usr/bin/env python3
"""
ASTRA GAME CLOUD VAULT - WEB SERVER & PORTAL v2.0
Central Cloud Game Repository, Chunked Upload Engine & Browser Hub
Mounted Volume: /vault_storage
Komandan: MUHAMAD DAFFA CAHYA | TCG 7B — PNJ
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))

STORAGE_DIR = "/vault_storage" if os.path.exists("/vault_storage") else os.path.join(os.path.dirname(__file__), "vault_storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

CATALOG_FILE = os.path.join(os.path.dirname(__file__), "game_catalog.json")
if os.path.exists(CATALOG_FILE):
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        CATALOG_DATA = json.load(f)
else:
    CATALOG_DATA = {"games": {}}

HTML_PORTAL = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASTRA GAME CLOUD VAULT</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Rajdhani', sans-serif;
    background: #080b10;
    color: #c9d1d9;
    min-height: 100vh;
    overflow-x: hidden;
  }
  .header {
    background: linear-gradient(180deg, rgba(31,111,235,0.2) 0%, rgba(8,11,16,0.95) 100%);
    border-bottom: 1px solid rgba(88,166,255,0.3);
    padding: 30px 20px 20px;
    text-align: center;
  }
  .header h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    letter-spacing: 2px;
    color: #58a6ff;
    text-shadow: 0 0 15px rgba(88,166,255,0.5);
  }
  .header p {
    color: #8b949e;
    font-size: 1rem;
    margin-top: 6px;
    letter-spacing: 1px;
  }
  .container {
    max-width: 1200px;
    margin: 25px auto;
    padding: 0 20px;
  }
  .stats-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
  }
  .stat-card {
    background: #111622;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }
  .stat-val {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #388bfd;
  }
  .stat-lbl {
    font-size: 0.85rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
  }
  .section-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.2rem;
    color: #e6edf3;
    margin: 20px 0 15px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #21262d;
  }
  .game-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  .game-card {
    background: #111622;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px;
    transition: all 0.25s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .game-card:hover {
    border-color: #58a6ff;
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(31,111,235,0.25);
  }
  .game-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
  }
  .game-meta {
    font-size: 0.9rem;
    color: #8b949e;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
  }
  .badge-ssd { background: rgba(31,111,235,0.2); color: #58a6ff; border: 1px solid rgba(88,166,255,0.3); }
  .badge-hdd { background: rgba(210,153,34,0.2); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }
  .badge-mirror { background: rgba(46,160,67,0.2); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
  .btn-play {
    display: block;
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
    color: #ffffff;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    text-align: center;
    border: none;
    border-radius: 6px;
    text-decoration: none;
    cursor: pointer;
  }
  .footer {
    text-align: center;
    padding: 40px 20px;
    color: #8b949e;
    font-size: 0.85rem;
    border-top: 1px solid #21262d;
    margin-top: 40px;
  }
  .dot-online {
    display: inline-block;
    width: 10px;
    height: 10px;
    background: #3fb950;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 10px #3fb950;
  }
</style>
</head>
<body>

<div class="header">
  <h1>🎮 ASTRA GAME CLOUD VAULT</h1>
  <p><span class="dot-online"></span>CLOUD REPOSITORY & ZERO-BLOAT LAUNCHER</p>
  <p style="font-size: 0.85rem; color: #58a6ff; margin-top: 4px;">Komandan: MUHAMAD DAFFA CAHYA | Hardware Profile: R5 5600, RX 580</p>
</div>

<div class="container">
  <div class="stats-bar">
    <div class="stat-card">
      <div class="stat-val" style="color:#3fb950;">ONLINE</div>
      <div class="stat-lbl">Cloud Vault Status</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ total_games }}</div>
      <div class="stat-lbl">Game Terindeks</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ "%.1f"|format(total_size) }} GB</div>
      <div class="stat-lbl">Total Katalog Game</div>
    </div>
    <div class="stat-card">
      <div class="stat-val" style="color:#238636;">{{ stored_files_count }}</div>
      <div class="stat-lbl">Cloud Vault Stashed</div>
    </div>
  </div>

  <div class="section-title">🕹️ SEMUA GAME DALAM ASTRA CLOUD VAULT</div>

  <div class="game-grid">
    {% for game in games %}
    <div class="game-card">
      <div>
        <div class="game-title">{{ game.title }}</div>
        <div class="game-meta">
          <span>📦 {{ "%.2f"|format(game.size_gb) }} GB</span>
          <span>
            {% if game.is_offloaded or game.is_mirrored_on_hdd %}
            <span class="badge badge-mirror">HDD Offloaded</span>
            {% else %}
            <span class="badge badge-ssd">SSD Active</span>
            {% endif %}
          </span>
        </div>
      </div>
      <div>
        <button class="btn-play" onclick="alert('Game terdaftar di Astra Cloud Vault! Buka dari desktop Komandan via ASTRA GAME LAUNCHER.')">▶️ READY TO LAUNCH</button>
      </div>
    </div>
    {% endfor %}
  </div>

  <div class="footer">
    <p>ASTRA GAME CLOUD VAULT • Terpisah Penuh Dari Sistem Akademik • Cloud 24/7</p>
    <p style="margin-top: 6px;"><a href="/api/games" style="color:#58a6ff; text-decoration:none;">JSON API Endpoint</a> • <a href="/api/storage" style="color:#58a6ff; text-decoration:none;">Storage Stats</a> • <a href="/health" style="color:#58a6ff; text-decoration:none;">Health Check</a></p>
  </div>
</div>

</body>
</html>"""

@app.route("/")
def index():
    games_list = list(CATALOG_DATA.get("games", {}).values())
    games_list.sort(key=lambda x: x.get("size_gb", 0), reverse=True)
    total_size = sum(g.get("size_gb", 0) for g in games_list)
    stored_files = os.listdir(STORAGE_DIR) if os.path.exists(STORAGE_DIR) else []
    return render_template_string(
        HTML_PORTAL,
        games=games_list,
        total_games=len(games_list),
        total_size=total_size,
        stored_files_count=len(stored_files)
    )

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    dest_path = os.path.join(STORAGE_DIR, filename)
    file.save(dest_path)
    file_size = os.path.getsize(dest_path)
    return jsonify({
        "status": "success",
        "filename": filename,
        "size_bytes": file_size,
        "path": dest_path
    })

@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(STORAGE_DIR, secure_filename(filename), as_attachment=True)

@app.route("/api/storage", methods=["GET"])
def storage_info():
    files = []
    total_bytes = 0
    if os.path.exists(STORAGE_DIR):
        for f in os.listdir(STORAGE_DIR):
            fp = os.path.join(STORAGE_DIR, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                total_bytes += sz
                files.append({"name": f, "size_mb": round(sz / (1024*1024), 2)})
    return jsonify({
        "status": "online",
        "storage_path": STORAGE_DIR,
        "files_count": len(files),
        "total_size_gb": round(total_bytes / (1024**3), 2),
        "files": files
    })

@app.route("/api/games")
def api_games():
    return jsonify({
        "status": "online",
        "service": "Astra Game Cloud Vault",
        "timestamp": datetime.utcnow().isoformat(),
        "total_games": len(CATALOG_DATA.get("games", {})),
        "games": CATALOG_DATA.get("games", {})
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "Astra Game Cloud Vault",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
