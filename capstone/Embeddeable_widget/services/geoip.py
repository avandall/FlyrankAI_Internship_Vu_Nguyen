import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class GeoIPService:
    """
    Enrichment fallback chain:
    Provider A: ip-api.com (primary, free, no key required)
    Provider B: ipapi.co (fallback, free, no key required)
    If both fail: submission saved with geo=None (no error raised)
    """

    def lookup(self, ip: str) -> Dict[str, Optional[str]]:
        empty = {"country": None, "city": None, "region": None, "provider": None}
        
        # Skip private/loopback IPs
        if not ip or ip in ("127.0.0.1", "localhost", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
            return {**empty, "country": "Local", "city": "Local", "region": "Local", "provider": "skip_private_ip"}
        
        # --- Provider A: ip-api.com ---
        try:
            resp = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName",
                timeout=3
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    logger.info(f"GeoIP via ip-api.com for {ip}")
                    return {
                        "country": data.get("country"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "provider": "ip-api.com",
                    }
        except Exception as e:
            logger.warning(f"GeoIP Provider A (ip-api.com) failed: {e}")

        # --- Provider B: ipapi.co fallback ---
        try:
            resp = requests.get(
                f"https://ipapi.co/{ip}/json/",
                timeout=3,
                headers={"User-Agent": "widget-capstone/1.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("error"):
                    logger.info(f"GeoIP via ipapi.co for {ip}")
                    return {
                        "country": data.get("country_name"),
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "provider": "ipapi.co",
                    }
        except Exception as e:
            logger.warning(f"GeoIP Provider B (ipapi.co) failed: {e}")

        # --- Both failed: safe fallback (submission still saved) ---
        logger.warning(f"Both GeoIP providers failed for {ip}. Saving submission without geo.")
        return empty
