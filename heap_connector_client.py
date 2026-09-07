"""HTTP client for Heap Analytics API."""
from __future__ import annotations
import httpx
import time
from typing import Any, Optional

DEFAULT_BASE = "https://heapanalytics.com"

class HeapClient:
    def __init__(self, app_id: str, base_url: str = ""):
        self.app_id = app_id.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Heap-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        """Verify App ID against Heap Server-Side API via a harmless ping event."""
        if not self.app_id:
            return {"status": "error", "error": "Heap App ID / Environment ID is required."}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/track",
                    headers=self.headers,
                    json={
                        "app_id": self.app_id,
                        "identity": "imperal_verification@bluebeeweb.com",
                        "event": "$ping",
                        "properties": {
                            "source": "imperal_connector_validation",
                            "tested_at": int(time.time())
                        }
                    }
                )
                if resp.status_code == 200:
                    return {
                        "status": "ok",
                        "app_id_valid": True,
                        "ingestion_status": "operational",
                        "app_id": self.app_id
                    }
                return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def track_event(self, identity: str, event_name: str, properties: Optional[dict[str, Any]] = None) -> bool:
        """Send a server-side event to Heap."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/track",
                headers=self.headers,
                json={
                    "app_id": self.app_id,
                    "identity": identity,
                    "event": event_name,
                    "properties": properties or {}
                }
            )
            return resp.status_code == 200

    async def list_events(self, limit: int = 20) -> list[dict[str, Any]]:
        """List tracked events reference in Heap."""
        return [{
            "id": "heap_autocapture",
            "name": "Heap Autocapture & Server-side Events",
            "status": "active",
            "description": f"Heap active environment {self.app_id}. Autocaptures web/mobile events and receives server-side events via /api/track."
        }]

    async def get_event(self, event_id: str) -> dict[str, Any]:
        """Retrieve details of an event reference."""
        return {
            "id": event_id,
            "name": event_id,
            "status": "active",
            "app_id": self.app_id,
            "ingestion_url": f"{self.base_url}/api/track"
        }
