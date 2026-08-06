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
  var config = {json.dumps(config)};  function hexToRgba(hex, opacity) {{
    hex = (hex || '#38BDF8').replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(function(h) {{ return h + h; }}).join('');
    var r = parseInt(hex.substring(0, 2), 16) || 56;
    var g = parseInt(hex.substring(2, 4), 16) || 189;
    var b = parseInt(hex.substring(4, 6), 16) || 248;
    return 'rgba(' + r + ',' + g + ',' + b + ',' + opacity + ')';
  }}

  function renderWidget() {{
    if (document.getElementById('flyrank-widget-' + config.widget_id)) return;
    
    var container = document.createElement('div');
    container.id = 'flyrank-widget-' + config.widget_id;
    var color = config.primary_color || '#38BDF8';
    var colorGlow = hexToRgba(color, 0.25);
    var colorBadgeBg = hexToRgba(color, 0.15);
    
    if (config.form_type === 'popover') {{
      // 1. Floating Bottom-Right Popover Widget
      container.style.cssText = [
        'position:fixed',
        'bottom:24px',
        'right:24px',
        'z-index:999999',
        'font-family:Inter,system-ui,sans-serif',
      ].join(';');

      container.innerHTML = [
        '<div id="flyrank-popover-card-' + config.widget_id + '" style="display:block;width:340px;background:#111827;border:1px solid ' + hexToRgba(color, 0.4) + ';border-top:3px solid ' + color + ';border-radius:16px;padding:1.25rem;color:#F1F5F9;box-shadow:0 20px 40px rgba(0,0,0,0.7), 0 0 20px ' + colorGlow + ';margin-bottom:12px;">',
          '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">',
            '<h3 style="margin:0;font-size:1.05rem;font-weight:700;color:' + color + '">💬 ' + config.title + '</h3>',
            '<button onclick="toggleFlyrankPopover(\\\'' + config.widget_id + '\\\')" style="background:none;border:none;color:#94A3B8;font-size:1.2rem;cursor:pointer;padding:0;line-height:1">&times;</button>',
          '</div>',
          config.description ? '<p style="margin:0 0 1rem;font-size:0.8rem;color:#94A3B8;line-height:1.4">' + config.description + '</p>' : '',
          '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
            '<input type="text" name="name" placeholder="Your name" style="' + inputStyle(color) + '" required/>',
            '<input type="email" name="email" placeholder="Email address" style="' + inputStyle(color) + '" required/>',
            '<textarea name="message" placeholder="How can we help?" rows="2" style="' + inputStyle(color) + 'resize:none;"></textarea>',
            '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
            '<button type="submit" style="' + btnStyle(color) + '">' + config.button_text + '</button>',
            '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.8rem"></div>',
          '</form>',
        '</div>',
        '<div style="display:flex;justify-content:flex-end">',
          '<button onclick="toggleFlyrankPopover(\\\'' + config.widget_id + '\\\')" style="background:' + color + ';color:#000;border:none;border-radius:50px;padding:0.75rem 1.25rem;font-weight:700;font-size:0.9rem;cursor:pointer;box-shadow:0 10px 25px ' + hexToRgba(color, 0.45) + ';display:flex;align-items:center;gap:0.5rem;transition:transform 0.2s">',
            '<span>💬</span> <span>' + config.title + '</span>',
          '</button>',
        '</div>',
      ].join('');
      injectContainer(container);

    }} else if (config.form_type === 'signup') {{
      // 2. Newsletter / Quick Email Signup Form
      container.style.cssText = [
        'font-family:Inter,system-ui,sans-serif',
        'max-width:460px',
        'background:#0D1421',
        'border:1px solid ' + hexToRgba(color, 0.35),
        'border-top:3px solid ' + color,
        'border-radius:12px',
        'padding:1.25rem',
        'color:#F1F5F9',
        'box-shadow:0 15px 30px rgba(0,0,0,0.4), 0 0 15px ' + colorGlow,
      ].join(';');

      container.innerHTML = [
        '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem">',
          '<span style="font-size:0.75rem;font-weight:700;background:' + colorBadgeBg + ';color:' + color + ';border:1px solid ' + hexToRgba(color, 0.3) + ';padding:0.2rem 0.6rem;border-radius:20px">📩 NEWSLETTER</span>',
        '</div>',
        '<h3 style="margin:0 0 0.3rem;font-size:1.15rem;font-weight:700;color:#F8FAFC">' + config.title + '</h3>',
        config.description ? '<p style="margin:0 0 1rem;font-size:0.85rem;color:#94A3B8;line-height:1.4">' + config.description + '</p>' : '',
        '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
          '<div style="display:flex;gap:0.5rem">',
            '<input type="email" name="email" placeholder="Enter your email address..." style="' + inputStyle(color) + 'margin-bottom:0;" required/>',
            '<button type="submit" style="' + btnStyle(color) + 'width:auto;white-space:nowrap;padding:0.6rem 1.25rem;">' + config.button_text + '</button>',
          '</div>',
          '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
          '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.85rem"></div>',
        '</form>',
      ].join('');

      injectContainer(container);

    }} else {{
      // 3. Standard Contact Form (default)
      container.style.cssText = [
        'font-family:Inter,system-ui,sans-serif',
        'max-width:420px',
        'background:#111827',
        'border:1px solid ' + hexToRgba(color, 0.35),
        'border-top:3px solid ' + color,
        'border-radius:12px',
        'padding:1.5rem',
        'color:#F1F5F9',
        'box-shadow:0 25px 50px rgba(0,0,0,0.5), 0 0 20px ' + colorGlow,
      ].join(';');
      
      container.innerHTML = [
        '<h3 style="margin:0 0 0.3rem;font-size:1.15rem;font-weight:700;color:' + color + '">📝 ' + config.title + '</h3>',
        config.description ? '<p style="margin:0 0 1rem;font-size:0.85rem;color:#94A3B8;line-height:1.4">' + config.description + '</p>' : '',
        '<form id="flyrank-form-' + config.widget_id + '" onsubmit="flyrankSubmit(event, this)">',
          '<input type="text" name="name" placeholder="Your name" style="' + inputStyle(color) + '" required/>',
          '<input type="email" name="email" placeholder="Email address" style="' + inputStyle(color) + '" required/>',
          '<textarea name="message" placeholder="Your message..." rows="3" style="' + inputStyle(color) + 'resize:vertical;"></textarea>',
          '<input type="text" name="_hp_field" style="display:none" tabindex="-1" autocomplete="off"/>',
          '<button type="submit" style="' + btnStyle(color) + '">' + config.button_text + '</button>',
          '<div id="flyrank-status-' + config.widget_id + '" style="margin-top:0.5rem;font-size:0.85rem"></div>',
        '</form>',
      ].join('');

      injectContainer(container);
    }}

    // Attach focus ring highlights for input elements
    setTimeout(function() {{
      var form = document.getElementById('flyrank-form-' + config.widget_id);
      if (form) {{
        var inputs = form.querySelectorAll('input:not([type="hidden"]):not([style*="display:none"]), textarea');
        inputs.forEach(function(inp) {{
          inp.addEventListener('focus', function() {{
            inp.style.borderColor = color;
            inp.style.boxShadow = '0 0 0 2px ' + hexToRgba(color, 0.25);
          }});
          inp.addEventListener('blur', function() {{
            inp.style.borderColor = '#1E293B';
            inp.style.boxShadow = 'none';
          }});
        }});
      }}
    }}, 100);
  }}

  function injectContainer(container) {{
    var targetEl = document.getElementById('widget-embed-zone') || document.getElementById('widget-container');
    if (targetEl) {{
      targetEl.appendChild(container);
      return;
    }}
    var scriptTag = document.currentScript;
    if (!scriptTag) {{
      var scripts = document.getElementsByTagName('script');
      for (var i = scripts.length - 1; i >= 0; i--) {{
        var src = scripts[i].src || '';
        if (src.indexOf('widget.js') !== -1 && src.indexOf('id=' + config.widget_id) !== -1) {{
          scriptTag = scripts[i];
          break;
        }}
      }}
    }}
    if (scriptTag && scriptTag.parentNode) {{
      scriptTag.parentNode.insertBefore(container, scriptTag);
    }} else {{
      document.body.appendChild(container);
    }}
  }}
  
  function inputStyle(color) {{
    return 'width:100%;background:#0D1421;border:1px solid #1E293B;border-radius:6px;color:#F1F5F9;padding:0.6rem;font-size:0.875rem;margin-bottom:0.5rem;box-sizing:border-box;font-family:inherit;outline:none;transition:all 0.2s;';
  }}
  
  function btnStyle(color) {{
    return 'background:' + color + ';color:#000;border:none;border-radius:8px;padding:0.75rem 1.5rem;font-weight:700;font-size:0.9rem;cursor:pointer;width:100%;transition:all 0.2s;box-shadow:0 4px 14px ' + hexToRgba(color, 0.35) + ';';
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
