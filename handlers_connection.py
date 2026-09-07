"""Connection management for Heap Connector."""
from __future__ import annotations
import uuid
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from heap_connector_client import HeapClient

def _mask(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 6:
        return "*" * len(v)
    return v[:2] + "*" * (len(v) - 4) + v[-2:]

async def get_connections_list(ctx) -> list[dict]:
    page = await ctx.store.query("connections")
    docs = page.data if hasattr(page, "data") else []
    conns = []
    for d in docs:
        data = d.data if hasattr(d, "data") else d
        doc_id = d.id if hasattr(d, "id") else data.get("id")
        data["_store_id"] = doc_id
        conns.append(data)
    return conns

async def resolve_client(ctx, connection_id: str = "") -> HeapClient:
    conns = await get_connections_list(ctx)
    if not conns:
        raise ValueError("No Heap connections configured. Use connect_heap_connector first.")
    conn = None
    if connection_id:
        for c in conns:
            if c.get("id") == connection_id:
                conn = c
                break
        if not conn:
            raise ValueError(f"Connection {connection_id} not found.")
    else:
        conn = conns[0]
    return HeapClient(
        app_id=conn.get("app_id", ""),
        base_url=conn.get("base_url", "")
    )

@chat.function("connect_heap_connector", "Connect Heap account via credentials.", action_type="write", chain_callable=True, event="heap-connector.connect_heap_connector", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_heap_connector(ctx, params: ConnectParams) -> ActionResult:
    client = HeapClient(app_id=params.app_id, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to connect to Heap: {res.get('error')}")
    
    cid = f"conn_{uuid.uuid4().hex[:8]}"
    label = params.label.strip() or f"Heap ({_mask(params.app_id)})"
    rec = {
        "id": cid,
        "label": label,
        "app_id": params.app_id,
        "masked_app_id": _mask(params.app_id),
        "base_url": params.base_url.rstrip("/"),
        "is_active": True
    }
    await ctx.store.create("connections", rec, id=cid)
    
    return ActionResult.success(
        {
            "id": cid,
            "label": label,
            "masked_app_id": _mask(params.app_id),
            "base_url": rec["base_url"],
            "is_active": True
        },
        summary=f"Connected Heap ({label})."
    )

@chat.function("list_connections", "List configured Heap connections.", action_type="read", chain_callable=True, event="heap-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    conns = await get_connections_list(ctx)
    records = []
    for c in conns:
        records.append({
            "id": c.get("id", ""),
            "label": c.get("label", ""),
            "masked_app_id": _mask(c.get("app_id", "")),
            "base_url": c.get("base_url", ""),
            "is_active": c.get("is_active", True)
        })
    return ActionResult.success({"connections": records, "total": len(records)}, summary=f"Found {len(records)} connection(s).")

@chat.function("disconnect_heap_connector", "Disconnect Heap account and delete stored credentials.", action_type="destructive", chain_callable=True, event="heap-connector.disconnect_heap_connector", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_heap_connector(ctx, params: ConnectionIdParams) -> ActionResult:
    conns = await get_connections_list(ctx)
    if not conns:
        return ActionResult.error("No active Heap connection to disconnect.")
    
    target_id = params.connection_id or conns[0].get("id")
    deleted = False
    for c in conns:
        if c.get("id") == target_id:
            store_id = c.get("_store_id") or c.get("id")
            await ctx.store.delete("connections", store_id)
            deleted = True
            break
            
    if not deleted and conns:
        store_id = conns[0].get("_store_id") or conns[0].get("id")
        await ctx.store.delete("connections", store_id)
        deleted = True

    return ActionResult.success({"success": True, "message": "Disconnected Heap connection."}, summary="Disconnected Heap connection.")
