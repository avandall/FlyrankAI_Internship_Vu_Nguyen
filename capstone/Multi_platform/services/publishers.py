import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from capstone.Multi_platform.core.database import get_db
from capstone.Multi_platform.utils import encrypt_token, decrypt_token
from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer

logger = logging.getLogger(__name__)

class SocialPublisher(ABC):
    platform: str

    @abstractmethod
    def publish(self, caption: str, image_path: Optional[str],
                idempotency_key: str) -> Tuple[bool, str, Optional[str]]:
        pass


class InstagramPublisherAdapter(SocialPublisher):
    platform = "instagram"

    def __init__(self, encrypted_token: str):
        self._encrypted_token = encrypted_token

    def publish(self, caption: str, image_path: Optional[str],
                idempotency_key: str) -> Tuple[bool, str, Optional[str]]:
        token = decrypt_token(self._encrypted_token)
        return self._publish_with_retry(caption, image_path, idempotency_key, token)

    def _publish_with_retry(self, caption, image_path, idem_key, token,
                             max_retries=3, backoff=1.0) -> Tuple[bool, str, Optional[str]]:
        for attempt in range(max_retries):
            result = FakeSocialPlatformServer.publish_post(
                self.platform, token, caption, image_path, idem_key
            )
            status = result["status"]
            if status in (200, 201):
                post_id = result["body"]["post_id"]
                return True, f"published (attempt {attempt+1})", post_id
            elif status == 429:
                retry_after = int(result.get("headers", {}).get("Retry-After", backoff))
                logger.warning(f"[{self.platform}] Rate limited. Waiting {retry_after}s")
                time.sleep(min(retry_after, 5))
                backoff *= 2
            elif status == 500:
                logger.warning(f"[{self.platform}] Server error, attempt {attempt+1}")
                time.sleep(backoff)
                backoff *= 2
            else:
                return False, f"Unexpected status {status}", None
        return False, "Max retries exceeded", None


class TwitterPublisherAdapter(SocialPublisher):
    platform = "twitter"

    def __init__(self, encrypted_token: str):
        self._encrypted_token = encrypted_token

    def publish(self, caption: str, image_path: Optional[str],
                idempotency_key: str) -> Tuple[bool, str, Optional[str]]:
        token = decrypt_token(self._encrypted_token)
        return self._publish_with_retry(caption, image_path, idempotency_key, token)

    def _publish_with_retry(self, caption, image_path, idem_key, token,
                             max_retries=3, backoff=1.0) -> Tuple[bool, str, Optional[str]]:
        for attempt in range(max_retries):
            result = FakeSocialPlatformServer.publish_post(
                self.platform, token, caption, image_path, idem_key
            )
            status = result["status"]
            if status in (200, 201):
                return True, f"published (attempt {attempt+1})", result["body"]["post_id"]
            elif status == 429:
                retry_after = int(result.get("headers", {}).get("Retry-After", backoff))
                time.sleep(min(retry_after, 5))
                backoff *= 2
            elif status == 500:
                time.sleep(backoff)
                backoff *= 2
            else:
                return False, f"Unexpected status {status}", None
        return False, "Max retries exceeded", None


class PublisherAdapterFactory:
    @staticmethod
    def get(platform: str) -> SocialPublisher:
        with get_db() as conn:
            row = conn.execute(
                "SELECT encrypted_token FROM platform_tokens WHERE platform=?", (platform,)
            ).fetchone()
        encrypted = row["encrypted_token"] if row else encrypt_token(f"demo_token_{platform}")

        adapters = {
            "instagram": InstagramPublisherAdapter(encrypted),
            "twitter": TwitterPublisherAdapter(encrypted),
        }
        if platform not in adapters:
            raise ValueError(f"No adapter for platform: {platform}")
        return adapters[platform]
