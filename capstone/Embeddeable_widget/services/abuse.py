import time
import threading
from collections import defaultdict
from typing import Tuple, Dict, List, Optional
from capstone.Embeddeable_widget.core.config import RATE_LIMIT_WINDOW_SECS

# Rate limit store: key=(ip, widget_id) → list of timestamps
_rate_store: Dict[str, List[float]] = defaultdict(list)
_rate_lock = threading.Lock()

class AbuseProtection:
    def check_rate_limit(self, ip: str, widget_id: str, limit: int) -> Tuple[bool, str]:
        """
        Sliding window rate limiter per (IP, widget_id).
        Returns (allowed, reason).
        """
        key = f"{ip}:{widget_id}"
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SECS

        with _rate_lock:
            # Remove expired timestamps
            _rate_store[key] = [t for t in _rate_store[key] if t > window_start]
            count = len(_rate_store[key])

            if count >= limit:
                return False, f"Rate limit exceeded: {count}/{limit} requests in {RATE_LIMIT_WINDOW_SECS}s window"

            _rate_store[key].append(now)
            return True, ""

    def check_honeypot(self, honeypot_field: Optional[str]) -> bool:
        """Returns True (is spam) if honeypot field is filled."""
        return bool(honeypot_field and honeypot_field.strip())
