import requests
from typing import Tuple, Dict

class WebhookService:
    def deliver(self, webhook_url: str, payload: Dict) -> Tuple[bool, str]:
        """
        Delivers webhook. Returns (success, status_msg).
        SAFE SIDE EFFECT: caller must proceed even if this returns False.
        """
        try:
            resp = requests.post(
                webhook_url, json=payload,
                timeout=5,
                headers={"Content-Type": "application/json", "X-Widget-Event": "submission"}
            )
            if resp.status_code < 300:
                return True, f"delivered ({resp.status_code})"
            return False, f"http_{resp.status_code}"
        except Exception as e:
            return False, f"error: {str(e)}"
