import os
import time
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])

@router.get("/test-embed", response_class=HTMLResponse)
async def test_embed_page(id: str = Query("w_demo_flyrank", description="Widget ID to embed")):
    v = int(time.time())
    return f"""<!DOCTYPE html>
<html>
<head>
<title>Customer Test Page — Widget Embed Demo</title>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
body {{ font-family: Inter, system-ui, sans-serif; background: #0B0F17; color: #F1F5F9; padding: 2rem; max-width: 900px; margin: 0 auto; line-height: 1.5; }}
h1 {{ color: #38BDF8; margin-bottom: 0.5rem; }}
.note {{ background: #1E293B; border-left: 4px solid #38BDF8; padding: 1rem; border-radius: 8px; margin: 1rem 0; font-size: 0.88rem; }}
.control-panel {{ background: #141A26; border: 1px solid #232D3F; padding: 1.25rem; border-radius: 10px; margin-bottom: 2rem; }}
.control-row {{ display: flex; gap: 0.75rem; margin-top: 0.5rem; }}
input {{ flex: 1; background: #0D1421; border: 1px solid #232D3F; border-radius: 6px; color: #FFF; padding: 0.65rem 0.8rem; font-size: 0.9rem; font-family: inherit; }}
button {{ background: #38BDF8; color: #000; border: none; font-weight: 600; padding: 0.65rem 1.25rem; border-radius: 6px; cursor: pointer; white-space: nowrap; }}
button:hover {{ opacity: 0.9; }}
pre {{ background: #0D1421; border: 1px solid #232D3F; padding: 1rem; border-radius: 8px; font-size: 0.82rem; color: #38BDF8; overflow-x: auto; }}
</style>
</head>
<body>
<h1>🌐 Customer Website Simulation</h1>
<p class="text-muted">Simulates an external customer website embedding your widget via <code>&lt;script&gt;</code>.</p>

<!-- INTERACTIVE WIDGET SELECTOR -->
<div class="control-panel">
  <strong style="color:#F1F5F9;font-size:0.95rem">🧪 Test Any Custom Widget Script:</strong>
  <div class="control-row">
    <input id="custom-widget-id" type="text" value="{id}" placeholder="Enter Widget ID (e.g. w_12345 or paste script)" />
    <button onclick="loadCustomWidget()">🚀 Render This Widget</button>
  </div>
  <p style="font-size:0.78rem;color:#94A3B8;margin-top:0.5rem">
    Current active widget ID: <code style="color:#38BDF8">{id}</code>
  </p>
</div>

<div class="note">
  <strong>How it works:</strong> The script tag below calls <code>/widget.js?id={id}</code>. 
  When a visitor submits the form below, the data is validated, enriched with Geo-IP, and stored in PostgreSQL!
</div>

<h2>Welcome to Customer Blog</h2>
<p style="color:#94A3B8;margin-bottom:1.5rem">Sample customer page containing the embedded form widget:</p>

<div id="widget-container" style="margin:2rem 0;max-width:420px">
  <script src="/widget.js?id={id}&v={v}"></script>
</div>

<h3>Current Embed Code Used:</h3>
<pre id="current-code">&lt;script src="http://localhost:8000/widget.js?id={id}&amp;v=1"&gt;&lt;/script&gt;</pre>

<script>
function loadCustomWidget() {{
  var val = document.getElementById('custom-widget-id').value.trim();
  if (!val) return;
  // If user pasted full script tag, extract id parameter
  var match = val.match(/id=([a-zA-Z0-9_-]+)/);
  var targetId = match ? match[1] : val;
  window.location.href = '/test-embed?id=' + encodeURIComponent(targetId);
}}
</script>
</body>
</html>"""

@router.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Widget Platform v2 running. See /docs for API.</h1>"
