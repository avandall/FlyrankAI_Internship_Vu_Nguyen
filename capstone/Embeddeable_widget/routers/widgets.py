from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from capstone.Embeddeable_widget.services.widget import WidgetService
from capstone.Embeddeable_widget.core.dependencies import require_tenant

router = APIRouter(prefix="/api", tags=["Widgets"])
widget_svc = WidgetService()

@router.get("/widget/{widget_id}/config")
async def get_widget_config(widget_id: str):
    widget = await widget_svc.get_widget(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    embed = await widget_svc.generate_embed_snippet(widget_id)
    return JSONResponse(
        content={"config": widget, "embed_snippet": embed},
        headers={"Cache-Control": "public, max-age=60"},
    )

@router.get("/widgets")
async def list_widgets(tenant: dict = Depends(require_tenant)):
    widgets = await widget_svc.get_for_tenant(tenant["tenant_id"])
    return {"tenant_id": tenant["tenant_id"], "widgets": widgets}

@router.post("/widgets", status_code=201)
async def create_widget(body: dict, tenant: dict = Depends(require_tenant)):
    widget = await widget_svc.create_widget(tenant["tenant_id"], body)
    embed = await widget_svc.generate_embed_snippet(widget["widget_id"])
    return {"widget": widget, "embed_snippet": embed}

@router.put("/widgets/{widget_id}")
async def update_widget(widget_id: str, body: dict, tenant: dict = Depends(require_tenant)):
    widget = await widget_svc.update_widget(widget_id, tenant["tenant_id"], body)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or access denied")
    return {"widget": widget}

@router.delete("/widgets/{widget_id}")
async def delete_widget(widget_id: str, tenant: dict = Depends(require_tenant)):
    ok = await widget_svc.delete_widget(widget_id, tenant["tenant_id"])
    if not ok:
        raise HTTPException(status_code=404, detail="Widget not found or access denied")
    return {"status": "deleted", "widget_id": widget_id}
