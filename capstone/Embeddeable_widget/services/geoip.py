import httpx
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class GeoIPService:
    """
    Enrichment fallback chain using async HTTP client:
    Provider A: ip-api.com
    Provider B: ipapi.co
    """

    async def lookup(self, ip: str) -> Dict[str, Optional[str]]:
        empty = {"country": None, "city": None, "region": None, "provider": None}
        
        if not ip or ip in ("127.0.0.1", "localhost", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
            return {**empty, "country": "Local", "city": "Local", "region": "Local", "provider": "skip_private_ip"}
        
        async with httpx.AsyncClient(timeout=3.0) as client:
            # --- Provider A ---
            try:
                resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName")
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        return {
                            "country": data.get("country"),
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "provider": "ip-api.com",
                        }
            except Exception as e:
                logger.warning(f"GeoIP Provider A failed: {e}")

            # --- Provider B ---
            try:
                resp = await client.get(f"https://ipapi.co/{ip}/json/", headers={"User-Agent": "widget-capstone"})
                if resp.status_code == 200:
                    data = resp.json()
                    if not data.get("error"):
                        return {
                            "country": data.get("country_name"),
                            "city": data.get("city"),
                            "region": data.get("region"),
                            "provider": "ipapi.co",
                        }
            except Exception as e:
                logger.warning(f"GeoIP Provider B failed: {e}")

        logger.warning(f"Both GeoIP providers failed for {ip}. Saving without geo.")
        return empty
