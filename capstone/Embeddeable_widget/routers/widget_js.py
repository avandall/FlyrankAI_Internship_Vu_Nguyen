import json
from fastapi import APIRouter, Query, HTTPException, Response
from capstone.Embeddeable_widget.services.widget import WidgetService

router = APIRouter(tags=["Widget.js"])
widget_svc = WidgetService()

@router.get("/widget.js", response_class=Response)
async def serve_widget_js(
    id: str = Query(..., description="Widget ID"),
    v: int = Query(1, description="Widget version for cache-busting"),
):
    widget = widget_svc.get_widget(id)
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget {id} not found")

    config = {
        "widget_id": widget["widget_id"],
        "title": widget.get("title", "Contact Us"),
        "description": widget.get("description", ""),
        "button_text": widget.get("button_text", "Submit"),
        "primary_color": widget.get("primary_color", "#38BDF8"),
        "submit_url": "http://localhost:8002/api/public/submit",
    }

    js_content = f"""
/* FlyRank Widget v{v} — widget_id={id} */
(function() {{
  var config = {json.dumps(config)};
  
  function renderWidget() {{
    if (document.getElementById('flyrank-widget-' + config.widget_id)) return;
    
    var container = document.createElement('div');
    container.id = 'flyrank-widget-' + config.widget_id;
    container.style.cssText = [
      'font-family:Inter,system-ui,sans-serif',
      'max-width:420px',
      'background:#111827',
      'border:1px solid #1E293B',
      'border-radius:12px',
      'padding:1.5rem',
      'color:#F1F5F9',
      'box-shadow:0 25px 50px rgba(0,0,0,0.5)',
    ].join(';');
    
    container.innerHTML = [
      '<h3 style="margin:0 0 0.25rem;font-size:1.1rem;color:' + config.primary_color + '">' + config.title + '</h3>',
      config.description ? '<p style="margin:0 0 1rem;font-size:0.85rem;color:#64748B">' + config.description + '</p>' : '',
      '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
        '<input type="text" name="name" placeholder="Your name" style="' + inputStyle() + '" required/>',
        '<input type="email" name="email" placeholder="Email address" style="' + inputStyle() + '" required/>',
        '<textarea name="message" placeholder="Your message..." rows="3" style="' + inputStyle() + 'resize:vertical;"></textarea>',
        '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
        '<button type="submit" style="' + btnStyle(config.primary_color) + '">' + config.button_text + '</button>',
        '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.85rem"></div>',
      '</form>',
    ].join('');
    
    document.currentScript ? document.currentScript.parentNode.insertBefore(container, document.currentScript) 
      : document.body.appendChild(container);
  }}
  
  function inputStyle() {{
    return 'width:100%;background:#0D1421;border:1px solid #1E293B;border-radius:6px;color:#F1F5F9;padding:0.6rem;font-size:0.875rem;margin-bottom:0.5rem;box-sizing:border-box;font-family:inherit;';
  }}
  
  function btnStyle(color) {{
    return 'background:' + color + ';color:#000;border:none;border-radius:8px;padding:0.7rem 1.5rem;font-weight:600;font-size:0.9rem;cursor:pointer;width:100%;transition:opacity 0.2s;';
  }}
  
  window.flyrankSubmit = function(event, form) {{
    event.preventDefault();
    var statusEl = document.getElementById('flyrank-status-' + config.widget_id);
    statusEl.textContent = 'Sending...';
    statusEl.style.color = '#64748B';
    
    var data = {{widget_id: config.widget_id}};
    Array.from(new FormData(form)).forEach(function(e) {{ data[e[0]] = e[1]; }});
    
    fetch(config.submit_url, {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(data),
    }}).then(function(r) {{
      return r.json().then(function(d) {{ return {{ok: r.ok, data: d}}; }});
    }}).then(function(res) {{
      if (res.ok) {{
        form.style.display = 'none';
        statusEl.innerHTML = '<span style="color:#22D3A5">✅ Thank you! Your message was sent.</span>';
      }} else {{
        statusEl.innerHTML = '<span style="color:#F43F5E">❌ ' + (res.data.detail || 'Submission failed') + '</span>';
      }}
    }}).catch(function(err) {{
      statusEl.innerHTML = '<span style="color:#F43F5E">❌ Network error: ' + err.message + '</span>';
    }});
  }};
  
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', renderWidget);
  }} else {{
    renderWidget();
  }}
}})();
"""
    return Response(
        content=js_content,
        media_type="application/javascript",
        headers={
            "Cache-Control": f"public, max-age=3600, immutable",
            "X-Widget-Version": str(v),
            "X-Widget-ID": id,
        }
    )
