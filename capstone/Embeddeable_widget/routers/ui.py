import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])

@router.get("/test-embed", response_class=HTMLResponse)
async def test_embed_page():
    return f"""<!DOCTYPE html>
<html>
<head><title>Customer Test Page — Widget Embed Demo</title>
<meta charset="UTF-8"/>
<style>
body{{font-family:Inter,sans-serif;background:#0B0F17;color:#F1F5F9;padding:2rem;}}
h1{{color:#38BDF8;}} .note{{background:#1E293B;padding:1rem;border-radius:8px;margin:1rem 0;font-size:0.85rem;}}
</style>
</head>
<body>
<h1>🌐 Customer Website Simulation</h1>
<div class="note">
  This page simulates a <strong>customer's external website</strong> that has embedded the FlyRank widget.
  The widget below is loaded via <code>&lt;script src="/widget.js?id=w_demo_flyrank"&gt;</code>.
  <br/><br/>
  For true cross-origin testing: open this file at a different port (e.g., python3 -m http.server 5500)
  and the widget will call back to localhost:8002 — testing real CORS.
</div>
<h2>Welcome to Demo Customer Blog</h2>
<p>This is a sample customer website. The contact widget below was embedded with a single script tag.</p>
<div id="widget-container" style="margin:2rem 0;max-width:420px">
  <script src="/widget.js?id=w_demo_flyrank&v=1"></script>
</div>
<h3>The embed code used:</h3>
<pre style="background:#1E293B;padding:1rem;border-radius:8px;font-size:0.85rem">&lt;script src="http://localhost:8002/widget.js?id=w_demo_flyrank&amp;v=1"&gt;&lt;/script&gt;</pre>
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
