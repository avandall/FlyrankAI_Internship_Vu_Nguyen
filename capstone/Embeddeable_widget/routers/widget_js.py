import json
from fastapi import APIRouter, Query, HTTPException, Response, Request
from capstone.Embeddeable_widget.services.widget import WidgetService

router = APIRouter(tags=["Widget.js"])
widget_svc = WidgetService()

@router.get("/widget.js", response_class=Response)
async def serve_widget_js(
    request: Request,
    id: str = Query(..., description="Widget ID"),
    v: int = Query(1, description="Widget version for cache-busting"),
):
    widget = await widget_svc.get_widget(id)
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget {id} not found")

    base_url = str(request.base_url).rstrip("/")
    config = {
        "widget_id": widget["widget_id"],
        "form_type": widget.get("form_type", "contact"),
        "title": widget.get("title") or ("Contact Us" if widget.get("form_type") == "contact" else ("Join Newsletter" if widget.get("form_type") == "signup" else "Quick Chat & Feedback")),
        "description": widget.get("description", ""),
        "button_text": widget.get("button_text", "Submit"),
        "primary_color": widget.get("primary_color", "#38BDF8"),
        "submit_url": f"{base_url}/api/public/submit",
    }

    js_content = f"""
/* FlyRank Widget v{v} — type={config['form_type']} — widget_id={id} */
(function() {{
  var config = {json.dumps(config)};
  
  function renderWidget() {{
    if (document.getElementById('flyrank-widget-' + config.widget_id)) return;
    
    var container = document.createElement('div');
    container.id = 'flyrank-widget-' + config.widget_id;
    
    if (config.form_type === 'popover') {{
      // Floating Bottom-Right Popover Widget
      container.style.cssText = [
        'position:fixed',
        'bottom:24px',
        'right:24px',
        'z-index:999999',
        'font-family:Inter,system-ui,sans-serif',
      ].join(';');

      container.innerHTML = [
        '<div id="flyrank-popover-card-' + config.widget_id + '" style="display:none;width:340px;background:#111827;border:1px solid #1E293B;border-radius:16px;padding:1.25rem;color:#F1F5F9;box-shadow:0 25px 50px rgba(0,0,0,0.6);margin-bottom:12px;">',
          '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">',
            '<h3 style="margin:0;font-size:1.05rem;color:' + config.primary_color + '">💬 ' + config.title + '</h3>',
            '<button onclick="toggleFlyrankPopover(\'' + config.widget_id + '\')" style="background:none;border:none;color:#94A3B8;font-size:1.2rem;cursor:pointer;padding:0">&times;</button>',
          '</div>',
          config.description ? '<p style="margin:0 0 1rem;font-size:0.8rem;color:#64748B">' + config.description + '</p>' : '',
          '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
            '<input type="text" name="name" placeholder="Your name" style="' + inputStyle() + '" required/>',
            '<input type="email" name="email" placeholder="Email address" style="' + inputStyle() + '" required/>',
            '<textarea name="message" placeholder="How can we help?" rows="2" style="' + inputStyle() + 'resize:none;"></textarea>',
            '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
            '<button type="submit" style="' + btnStyle(config.primary_color) + '">' + config.button_text + '</button>',
            '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.8rem"></div>',
          '</form>',
        '</div>',
        '<button onclick="toggleFlyrankPopover(\'' + config.widget_id + '\')" style="background:' + config.primary_color + ';color:#000;border:none;border-radius:50px;padding:0.75rem 1.25rem;font-weight:700;font-size:0.9rem;cursor:pointer;box-shadow:0 10px 25px rgba(0,0,0,0.4);display:flex;align-items:center;gap:0.5rem">',
          '<span>💬</span> <span>' + config.title + '</span>',
        '</button>',
      ].join('');
      document.body.appendChild(container);

    }} else if (config.form_type === 'signup') {{
      // Newsletter / Quick Email Signup Form
      container.style.cssText = [
        'font-family:Inter,system-ui,sans-serif',
        'max-width:440px',
        'background:#0D1421',
        'border:1px solid #1E293B',
        'border-radius:12px',
        'padding:1.25rem',
        'color:#F1F5F9',
        'box-shadow:0 15px 30px rgba(0,0,0,0.3)',
      ].join(';');

      container.innerHTML = [
        '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem">',
          '<span style="font-size:0.75rem;font-weight:700;background:rgba(56,189,248,0.15);color:' + config.primary_color + ';padding:0.15rem 0.5rem;border-radius:12px">📩 NEWSLETTER</span>',
        '</div>',
        '<h3 style="margin:0 0 0.25rem;font-size:1.1rem;color:#F8FAFC">' + config.title + '</h3>',
        config.description ? '<p style="margin:0 0 1rem;font-size:0.85rem;color:#64748B">' + config.description + '</p>' : '',
        '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
          '<div style="display:flex;gap:0.5rem">',
            '<input type="email" name="email" placeholder="Enter your email" style="' + inputStyle() + 'margin-bottom:0;" required/>',
            '<button type="submit" style="' + btnStyle(config.primary_color) + 'width:auto;white-space:nowrap;">' + config.button_text + '</button>',
          '</div>',
          '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
          '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.85rem"></div>',
        '</form>',
      ].join('');

      injectContainer(container);

    }} else {{
      // Standard Contact Form (default)
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
        '<h3 style="margin:0 0 0.25rem;font-size:1.1rem;color:' + config.primary_color + '">📝 ' + config.title + '</h3>',
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

      injectContainer(container);
    }}
  }}

  function injectContainer(container) {{
    if (document.currentScript && document.currentScript.parentNode) {{
      document.currentScript.parentNode.insertBefore(container, document.currentScript);
    }} else {{
      document.body.appendChild(container);
    }}
  }}
  
  function inputStyle() {{
    return 'width:100%;background:#0D1421;border:1px solid #1E293B;border-radius:6px;color:#F1F5F9;padding:0.6rem;font-size:0.875rem;margin-bottom:0.5rem;box-sizing:border-box;font-family:inherit;';
  }}
  
  function btnStyle(color) {{
    return 'background:' + color + ';color:#000;border:none;border-radius:8px;padding:0.7rem 1.5rem;font-weight:600;font-size:0.9rem;cursor:pointer;width:100%;transition:opacity 0.2s;';
  }}

  window.toggleFlyrankPopover = function(id) {{
    var card = document.getElementById('flyrank-popover-card-' + id);
    if (card) {{
      card.style.display = (card.style.display === 'none' || !card.style.display) ? 'block' : 'none';
    }}
  }};
  
  window.flyrankSubmit = function(event, form) {{
    event.preventDefault();
    var statusEl = document.getElementById('flyrank-status-' + config.widget_id);
    statusEl.textContent = 'Sending...';
    statusEl.style.color = '#64748B';
    
    var data = {{widget_id: config.widget_id}};
    Array.from(new FormData(form)).forEach(function(e) {{ data[e[0]] = e[1]; }});
    
    function handleRes(res) {{
      if (res.ok) {{
        form.style.display = 'none';
        statusEl.innerHTML = '<span style="color:#22D3A5">✅ Thank you! Your submission was received.</span>';
      }} else {{
        statusEl.innerHTML = '<span style="color:#F43F5E">❌ ' + (res.data.detail || 'Submission failed') + '</span>';
      }}
    }}

    function doFetch(url) {{
      return fetch(url, {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(data),
      }}).then(function(r) {{
        return r.json().then(function(d) {{ return {{ok: r.ok, data: d}}; }});
      }});
    }}

    doFetch(config.submit_url)
      .then(handleRes)
      .catch(function() {{
        doFetch('/api/public/submit')
          .then(handleRes)
          .catch(function(err) {{
            statusEl.innerHTML = '<span style="color:#F43F5E">❌ Network error: ' + err.message + '</span>';
          }});
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
            "Cache-Control": f"no-cache",
            "X-Widget-Version": str(v),
            "X-Widget-ID": id,
        }
    )
