import httpx
import logging
import json
from typing import Tuple

logger = logging.getLogger(__name__)

class WebhookService:
    async def deliver(self, url: str, payload: dict) -> Tuple[bool, str]:
        """
        Deliver webhook asynchronously. Safe side effect that won't crash main thread.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return True, ""
        except Exception as e:
            logger.error(f"Webhook delivery failed to {url}: {e}")
            return False, str(e)
