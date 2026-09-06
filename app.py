"""Extension declaration, capabilities, health check for Heap Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "heap-connector",
    version="0.1.0",
    display_name="Heap",
    icon="icon.svg",
    capabilities=["heap:manage"],
    description="Official Imperal connector for Heap (C30. Email Marketing & Newsletter). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("heap_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Heap connection(s) configured." if count else "Not connected yet."
    }
