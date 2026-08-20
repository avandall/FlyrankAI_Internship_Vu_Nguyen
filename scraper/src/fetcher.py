import time
import hashlib
from pathlib import Path
import requests
from src.config import USER_AGENT, REQUEST_TIMEOUT, POLITE_DELAY, CACHE_DIR

class PoliteFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.cache_hits = 0
        self.pages_fetched = 0

    def _get_cache_path(self, url: str) -> Path:
        # Tạo tên file cache an toàn từ hash của URL
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return CACHE_DIR / f"{url_hash}.html"

    def fetch(self, url: str, retry_on_5xx: bool = True) -> tuple[str, bool]:
        """
        Returns: (html_content, is_cache_hit)
        """
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            self.cache_hits += 1
            content = cache_path.read_text(encoding="utf-8")
            print(f"[CACHE HIT] {url} ({len(content)} bytes)")
            return content, True

        # Rate limit trước khi gửi live request
        time.sleep(POLITE_DELAY)

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                # Không retry 404 hoặc 403
                if response.status_code in [403, 404]:
                    raise ValueError(f"HTTP {response.status_code}: Not found or Forbidden ({url})")
                # Retry 1 lần nếu 5xx
                if retry_on_5xx and 500 <= response.status_code < 600:
                    time.sleep(1.0)
                    response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    if response.status_code != 200:
                        raise ValueError(f"HTTP {response.status_code} after retry ({url})")
                else:
                    raise ValueError(f"HTTP {response.status_code} error ({url})")

            html_content = response.text
            cache_path.write_text(html_content, encoding="utf-8")
            self.pages_fetched += 1
            print(f"[FETCH] {url} ({len(html_content)} bytes)")
            return html_content, False

        except requests.RequestException as e:
            raise RuntimeError(f"Network error on {url}: {e}")