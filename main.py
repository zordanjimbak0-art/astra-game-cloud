#!/usr/bin/env python3
"""
ASTRA GAME CLOUD VAULT - WEB SERVER & PORTAL v3.0
Chunked Upload Engine + Volume Storage + Catalog Browser
Mounted Volume: /vault_storage
Komandan: MUHAMAD DAFFA CAHYA | TCG 7B - PNJ
"""
import os
import json
import hashlib
import shutil
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, send_from_directory, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))
# Disable default request size limit for chunked uploads
app.config["MAX_CONTENT_LENGTH"] = None

STORAGE_DIR = "/vault_storage" if os.path.exists("/vault_storage") else os.path.join(os.path.dirname(__file__), "vault_storage")
CHUNKS_DIR  = os.path.join(STORAGE_DIR, ".chunks")
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)

CATALOG_FILE = os.path.join(os.path.dirname(__file__), "game_catalog.json")
if os.path.exists(CATALOG_FILE):
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        CATALOG_DATA = json.load(f)
else:
    CATALOG_DATA = {"games": {}}

# ─── PORTAL HTML ─────────────────────────────────────────────────────────────
HTML_PORTAL = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASTRA GAME CLOUD VAULT</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Rajdhani', sans-serif; background: #080b10; color: #c9d1d9; min-height: 100vh; }
  .header { background: linear-gradient(180deg, rgba(31,111,235,0.2) 0%, rgba(8,11,16,0.95) 100%); border-bottom: 1px solid rgba(88,166,255,0.3); padding: 30px 20px 20px; text-align: center; }
  .header h1 { font-family: 'Orbitron', sans-serif; font-size: 2rem; letter-spacing: 2px; color: #58a6ff; text-shadow: 0 0 15px rgba(88,166,255,0.5); }
  .container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }
  .stats-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 25px; }
  .stat-card { background: #111622; border: 1px solid #21262d; border-radius: 10px; padding: 16px; text-align: center; }
  .stat-val { font-family: 'Orbitron', sans-serif; font-size: 1.6rem; font-weight: 700; color: #388bfd; }
  .stat-lbl { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
  .section-title { font-family: 'Orbitron', sans-serif; font-size: 1.1rem; color: #e6edf3; margin: 20px 0 15px; display: flex; align-items: center; gap: 10px; }
  .section-title::after { content: ''; flex: 1; height: 1px; background: #21262d; }
  .game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; }
  .game-card { background: #111622; border: 1px solid #30363d; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.25s; }
  .game-card:hover { border-color: #58a6ff; transform: translateY(-3px); box-shadow: 0 6px 20px rgba(31,111,235,0.25); }
  .game-title { font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 8px; }
  .game-meta { font-size: 0.85rem; color: #8b949e; margin-bottom: 12px; display: flex; justify-content: space-between; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }
  .badge-cloud { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.4); }
  .badge-ssd   { background: rgba(31,111,235,0.15); color: #58a6ff; border: 1px solid rgba(88,166,255,0.4); }
  .badge-hdd   { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.4); }
  .badge-upload { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.4); }
  .btn { display: block; width: 100%; padding: 9px; border: none; border-radius: 6px; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; font-weight: 700; cursor: pointer; text-align: center; }
  .btn-cloud { background: linear-gradient(135deg, #238636, #2ea043); color: #fff; }
  .btn-ssd   { background: linear-gradient(135deg, #1f6feb, #388bfd); color: #fff; }
  .upload-box { background: #111622; border: 2px dashed #30363d; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 20px; }
  .upload-box:hover { border-color: #58a6ff; }
  .progress-bar { width: 100%; background: #21262d; border-radius: 4px; height: 8px; margin-top: 10px; overflow: hidden; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, #1f6feb, #3fb950); transition: width 0.3s; }
  .dot-online { display: inline-block; width: 10px; height: 10px; background: #3fb950; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px #3fb950; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
  .vault-files { background: #111622; border: 1px solid #21262d; border-radius: 10px; padding: 16px; margin-top: 15px; }
  .file-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #21262d; font-size: 0.9rem; }
  .file-row:last-child { border: none; }
  .footer { text-align: center; padding: 30px 20px; color: #8b949e; font-size: 0.8rem; border-top: 1px solid #21262d; margin-top: 40px; }
</style>
</head>
<body>
<div class="header">
  <h1>🎮 ASTRA GAME CLOUD VAULT</h1>
  <p><span class="dot-online"></span>CLOUD REPOSITORY ACTIVE — Terpisah dari Sistem Akademik PNJ</p>
  <p style="font-size:0.85rem;color:#58a6ff;margin-top:4px;">Komandan: MUHAMAD DAFFA CAHYA | TCG 7B | Ryzen 5 5600 · RX 580</p>
</div>

<div class="container">
  <div class="stats-bar">
    <div class="stat-card">
      <div class="stat-val" style="color:#3fb950;">ONLINE</div>
      <div class="stat-lbl">Cloud Vault</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ total_games }}</div>
      <div class="stat-lbl">Game Terindeks</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ "%.1f"|format(total_size) }} GB</div>
      <div class="stat-lbl">Total Katalog</div>
    </div>
    <div class="stat-card">
      <div class="stat-val" style="color:#3fb950;">{{ vault_count }}</div>
      <div class="stat-lbl">File di Vault</div>
    </div>
    <div class="stat-card">
      <div class="stat-val" style="color:#d29922;">{{ "%.2f"|format(vault_size_gb) }} GB</div>
      <div class="stat-lbl">Vault Storage</div>
    </div>
  </div>

  <!-- VAULT FILE LIST -->
  {% if vault_files %}
  <div class="section-title">☁️ FILE TERSIMPAN DI CLOUD VAULT</div>
  <div class="vault-files">
    {% for f in vault_files %}
    <div class="file-row">
      <span>📦 {{ f.name }}</span>
      <span style="color:#8b949e;">{{ f.size_mb }} MB</span>
      <a href="/api/download/{{ f.name }}" style="color:#58a6ff;font-size:0.8rem;">⬇ Download</a>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <div class="section-title">🕹️ KATALOG GAME — {{ total_games }} Game Terindeks</div>
  <div class="game-grid">
    {% for game in games %}
    <div class="game-card">
      <div>
        <div class="game-title">{{ game.title }}</div>
        <div class="game-meta">
          <span>📦 {{ "%.2f"|format(game.size_gb) }} GB</span>
          <span>
            {% if game.cloud_url %}
            <span class="badge badge-cloud">☁ IN VAULT</span>
            {% elif game.is_offloaded or game.is_mirrored_on_hdd %}
            <span class="badge badge-hdd">HDD Offloaded</span>
            {% else %}
            <span class="badge badge-ssd">SSD Active</span>
            {% endif %}
          </span>
        </div>
      </div>
      <div>
        {% if game.cloud_url %}
        <a href="{{ game.cloud_url }}" class="btn btn-cloud">☁️ DOWNLOAD FROM VAULT</a>
        {% else %}
        <button class="btn btn-ssd" onclick="alert('Buka via ASTRA GAME LAUNCHER di desktop Komandan.')">▶️ LAUNCH LOCAL</button>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>

  <div class="footer">
    <p>ASTRA GAME CLOUD VAULT v3.0 • Terpisah Penuh Dari Sistem Akademik PNJ • Cloud 24/7</p>
    <p style="margin-top:6px;">
      <a href="/api/games" style="color:#58a6ff;">JSON API</a> •
      <a href="/api/storage" style="color:#58a6ff;">Storage Stats</a> •
      <a href="/health" style="color:#58a6ff;">Health</a>
    </p>
  </div>
</div>
</body>
</html>"""

# ─── ROUTES ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    games_list = list(CATALOG_DATA.get("games", {}).values())
    games_list.sort(key=lambda x: x.get("size_gb", 0), reverse=True)
    total_size = sum(g.get("size_gb", 0) for g in games_list)
    # Vault file list
    vault_files = []
    vault_bytes = 0
    if os.path.exists(STORAGE_DIR):
        for f in os.listdir(STORAGE_DIR):
            fp = os.path.join(STORAGE_DIR, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                vault_bytes += sz
                vault_files.append({"name": f, "size_mb": round(sz / (1024*1024), 2)})
    return render_template_string(
        HTML_PORTAL,
        games=games_list,
        total_games=len(games_list),
        total_size=total_size,
        vault_files=sorted(vault_files, key=lambda x: x["size_mb"], reverse=True),
        vault_count=len(vault_files),
        vault_size_gb=round(vault_bytes / (1024**3), 2),
    )

# ─── CHUNKED UPLOAD: Initiate ─────────────────────────────────────────────────
@app.route("/api/upload/init", methods=["POST"])
def upload_init():
    data = request.json
    filename  = secure_filename(data.get("filename", "file"))
    total_chunks = int(data.get("total_chunks", 1))
    file_size = int(data.get("file_size", 0))
    upload_id = hashlib.md5(f"{filename}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
    # Buat folder sementara untuk chunks
    chunk_folder = os.path.join(CHUNKS_DIR, upload_id)
    os.makedirs(chunk_folder, exist_ok=True)
    # Simpan metadata
    meta = {"filename": filename, "total_chunks": total_chunks, "file_size": file_size, "received": 0}
    with open(os.path.join(chunk_folder, "meta.json"), "w") as f:
        json.dump(meta, f)
    return jsonify({"upload_id": upload_id, "filename": filename, "total_chunks": total_chunks})

# ─── CHUNKED UPLOAD: Upload Chunk ─────────────────────────────────────────────
@app.route("/api/upload/chunk", methods=["POST"])
def upload_chunk():
    try:
        upload_id   = request.form.get("upload_id")
        chunk_index = int(request.form.get("chunk_index", 0))
        chunk_file  = request.files.get("chunk")
        if not upload_id or not chunk_file:
            return jsonify({"error": "Missing upload_id or chunk"}), 400
        chunk_folder = os.path.join(CHUNKS_DIR, upload_id)
        if not os.path.exists(chunk_folder):
            # Auto-recreate jika folder hilang (Railway restart)
            os.makedirs(chunk_folder, exist_ok=True)
            return jsonify({"error": "Session expired, re-init required"}), 410
        chunk_path = os.path.join(chunk_folder, f"chunk_{chunk_index:06d}")
        # Stream langsung ke disk, hindari memory buffer besar
        chunk_file.save(chunk_path)
        chunk_size = os.path.getsize(chunk_path)
        return jsonify({"status": "ok", "chunk": chunk_index, "size": chunk_size})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()[:500]}), 500

# ─── CHUNKED UPLOAD: Finalize ─────────────────────────────────────────────────
@app.route("/api/upload/finalize", methods=["POST"])
def upload_finalize():
    try:
        data      = request.get_json(force=True) or {}
        upload_id = data.get("upload_id")
        if not upload_id:
            return jsonify({"error": "Missing upload_id"}), 400
        chunk_folder = os.path.join(CHUNKS_DIR, upload_id)
        if not os.path.exists(chunk_folder):
            return jsonify({"error": f"Invalid upload_id: {upload_id}"}), 404
        meta_path = os.path.join(chunk_folder, "meta.json")
        with open(meta_path, "r") as f:
            meta = json.load(f)
        filename  = meta["filename"]
        dest_path = os.path.join(STORAGE_DIR, filename)
        # Sort & merge semua chunks
        chunks = sorted(
            [f for f in os.listdir(chunk_folder) if f.startswith("chunk_")],
            key=lambda x: int(x.split("_")[1])
        )
        if not chunks:
            return jsonify({"error": "No chunks found"}), 400
        with open(dest_path, "wb") as out:
            for chunk_name in chunks:
                chunk_path = os.path.join(chunk_folder, chunk_name)
                with open(chunk_path, "rb") as c:
                    shutil.copyfileobj(c, out)
        # Bersihkan temp folder
        shutil.rmtree(chunk_folder, ignore_errors=True)
        final_size = os.path.getsize(dest_path)
        return jsonify({
            "status": "complete",
            "filename": filename,
            "size_bytes": final_size,
            "size_gb": round(final_size / (1024**3), 3),
            "download_url": f"/api/download/{filename}"
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# ─── SIMPLE UPLOAD (backward compat, small files) ─────────────────────────────
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No filename"}), 400
    filename  = secure_filename(file.filename)
    dest_path = os.path.join(STORAGE_DIR, filename)
    file.save(dest_path)
    size = os.path.getsize(dest_path)
    return jsonify({"status": "success", "filename": filename, "size_bytes": size,
                    "download_url": f"/api/download/{filename}"})

# ─── DOWNLOAD ─────────────────────────────────────────────────────────────────
@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(STORAGE_DIR, secure_filename(filename), as_attachment=True)

# ─── STORAGE STATS ────────────────────────────────────────────────────────────
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
                files.append({"name": f, "size_mb": round(sz / (1024*1024), 2),
                               "download_url": f"/api/download/{f}"})
    return jsonify({"status": "online", "storage_path": STORAGE_DIR,
                    "files_count": len(files), "total_size_gb": round(total_bytes / (1024**3), 3),
                    "files": sorted(files, key=lambda x: x["size_mb"], reverse=True)})

@app.route("/api/games")
def api_games():
    return jsonify({"status": "online", "service": "Astra Game Cloud Vault",
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_games": len(CATALOG_DATA.get("games", {})),
                    "games": CATALOG_DATA.get("games", {})})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Astra Game Cloud Vault v3.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "storage_active": os.path.exists(STORAGE_DIR)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
