"""
Multi-Platform Social Campaign Publisher — Test Suite
Tests: image variant dimensions, caption generation, idempotency,
rate limit handling, HMAC webhook verification, token encryption.
Run: python3 -m pytest capstone/Multi_platform/tests/test_multi_platform.py -v
"""
import sys, os, io, json, time, hmac, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    import capstone.Multi_platform.core.database as db
    from capstone.Multi_platform.core.database import init_db
    from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / "test_multi.db")
    init_db()
    # Also clear FakeSocialPlatformServer state
    FakeSocialPlatformServer._post_store.clear()
    FakeSocialPlatformServer._rate_counters.clear()
    yield


def make_minimal_jpeg(width=800, height=600) -> bytes:
    """Create a real minimal JPEG image for testing."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 1. IMAGE VARIANT PIPELINE — Correct dimensions per platform
# ═══════════════════════════════════════════════════════════════════════════

class TestImageVariantPipeline:
    def test_instagram_variant_is_1080x1080(self, tmp_path, monkeypatch):
        from capstone.Multi_platform.services.variants import ImageVariantPipeline, PLATFORM_SPECS
        pipeline = ImageVariantPipeline()
        monkeypatch.setattr(pipeline, 'OUTPUT_DIR', tmp_path / "variants")
        (tmp_path / "variants").mkdir()
        
        src_bytes = make_minimal_jpeg(1920, 1080)
        variants = pipeline.create_variants(src_bytes, "test_camp")
        
        assert "instagram" in variants
        ig = variants["instagram"]
        assert ig["width"] == 1080
        assert ig["height"] == 1080
        # Verify the actual file dimensions
        from PIL import Image
        img = Image.open(ig["path"])
        assert img.size == (1080, 1080), f"Expected 1080x1080, got {img.size}"

    def test_twitter_variant_is_1600x900(self, tmp_path, monkeypatch):
        from capstone.Multi_platform.services.variants import ImageVariantPipeline
        pipeline = ImageVariantPipeline()
        monkeypatch.setattr(pipeline, 'OUTPUT_DIR', tmp_path / "variants")
        (tmp_path / "variants").mkdir()
        
        src_bytes = make_minimal_jpeg(1920, 1080)
        variants = pipeline.create_variants(src_bytes, "test_camp")
        
        assert "twitter" in variants
        tw = variants["twitter"]
        assert tw["width"] == 1600
        assert tw["height"] == 900
        from PIL import Image
        img = Image.open(tw["path"])
        assert img.size == (1600, 900), f"Expected 1600x900, got {img.size}"

    def test_all_platforms_generate_variants(self, tmp_path, monkeypatch):
        from capstone.Multi_platform.services.variants import ImageVariantPipeline, PLATFORM_SPECS
        pipeline = ImageVariantPipeline()
        monkeypatch.setattr(pipeline, 'OUTPUT_DIR', tmp_path / "variants")
        (tmp_path / "variants").mkdir()
        
        src_bytes = make_minimal_jpeg(800, 600)
        variants = pipeline.create_variants(src_bytes, "camp_all")
        
        for platform in PLATFORM_SPECS:
            assert platform in variants, f"Variant for {platform} not generated"
            assert os.path.exists(variants[platform]["path"]), f"File missing: {variants[platform]['path']}"

    def test_portrait_image_handled(self, tmp_path, monkeypatch):
        """Portrait image (600x1200) should be cropped to fit each platform spec."""
        from capstone.Multi_platform.services.variants import ImageVariantPipeline
        pipeline = ImageVariantPipeline()
        monkeypatch.setattr(pipeline, 'OUTPUT_DIR', tmp_path / "variants")
        (tmp_path / "variants").mkdir()
        
        src_bytes = make_minimal_jpeg(600, 1200)  # Portrait
        variants = pipeline.create_variants(src_bytes, "portrait_test")
        
        from PIL import Image
        ig_img = Image.open(variants["instagram"]["path"])
        assert ig_img.size == (1080, 1080), "Instagram must always be 1080x1080"


# ═══════════════════════════════════════════════════════════════════════════
# 2. CAPTION GENERATION — Platform-tailored lengths
# ═══════════════════════════════════════════════════════════════════════════

class TestCaptionGeneration:
    def test_twitter_caption_max_280_chars(self):
        from capstone.Multi_platform.services.captions import CaptionGenerator
        gen = CaptionGenerator()
        caption = gen.generate("twitter", "A" * 500, "Long Post Title " * 20)
        assert len(caption) <= 280, f"Twitter caption too long: {len(caption)} chars"

    def test_instagram_caption_under_2200_chars(self):
        from capstone.Multi_platform.services.captions import CaptionGenerator
        gen = CaptionGenerator()
        caption = gen.generate("instagram", "Content " * 100, "Instagram Title")
        assert len(caption) <= 2200, f"Instagram caption too long: {len(caption)} chars"

    def test_instagram_has_hashtags(self):
        from capstone.Multi_platform.services.captions import CaptionGenerator
        gen = CaptionGenerator()
        caption = gen.generate("instagram", "Digital marketing strategy", "Marketing Guide")
        assert "#" in caption, "Instagram caption should contain hashtags"

    def test_captions_differ_per_platform(self):
        from capstone.Multi_platform.services.captions import CaptionGenerator
        gen = CaptionGenerator()
        title = "How AI is Changing SEO"
        content = "Artificial intelligence is transforming search engine optimization fundamentally."
        ig = gen.generate("instagram", content, title)
        tw = gen.generate("twitter", content, title)
        assert ig != tw, "Instagram and Twitter captions should be different"


# ═══════════════════════════════════════════════════════════════════════════
# 3. IDEMPOTENCY — Same campaign published twice → 1 post only
# ═══════════════════════════════════════════════════════════════════════════

class TestIdempotency:
    def test_publishing_twice_does_not_duplicate(self):
        """Core idempotency test: publish → publish again → only 1 post in FakeServer."""
        from capstone.Multi_platform.services.campaign import CampaignService
        from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer
        svc = CampaignService()
        camp = svc.create_campaign(
            "Test Campaign", "Content for idempotency test",
            ["instagram"], None
        )
        campaign_id = camp["campaign_id"]

        result1 = svc.publish_campaign(campaign_id)
        result2 = svc.publish_campaign(campaign_id)

        # Both calls should succeed
        assert result1["results"]["instagram"]["status"] in ("published",)
        assert result2["results"]["instagram"]["status"] == "already_published (idempotent)"

        # Only 1 post in FakeServer store
        import hashlib
        idem_key = hashlib.sha256(f"{campaign_id}:instagram".encode()).hexdigest()[:32]
        count = sum(1 for k in FakeSocialPlatformServer._post_store if k == idem_key)
        assert count == 1, f"Expected 1 post, found {count}"


# ═══════════════════════════════════════════════════════════════════════════
# 4. TOKEN ENCRYPTION — AES-GCM, never plaintext in storage
# ═══════════════════════════════════════════════════════════════════════════

class TestTokenEncryption:
    def test_encrypt_returns_base64(self):
        from capstone.Multi_platform.utils import encrypt_token
        import base64
        enc = encrypt_token("my_oauth_token_secret")
        # Should be valid base64
        decoded = base64.b64decode(enc.encode())
        assert len(decoded) >= 12, "Encrypted token too short"

    def test_encrypted_token_not_plaintext(self):
        from capstone.Multi_platform.utils import encrypt_token
        enc = encrypt_token("my_secret_token")
        assert "my_secret_token" not in enc, "Token must not appear in plaintext in encrypted form"

    def test_decrypt_round_trip(self):
        from capstone.Multi_platform.utils import encrypt_token, decrypt_token
        original = "super_secret_oauth_token_12345"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original, f"Decrypted value mismatch: {decrypted}"

    def test_different_encryptions_same_plaintext(self):
        """Each encryption should produce different ciphertext (random IV)."""
        from capstone.Multi_platform.utils import encrypt_token
        enc1 = encrypt_token("token123")
        enc2 = encrypt_token("token123")
        assert enc1 != enc2, "Two encryptions of same value should differ (random IV)"


# ═══════════════════════════════════════════════════════════════════════════
# 5. HMAC WEBHOOK VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class TestWebhookHMAC:
    def test_valid_signature_accepted(self):
        from capstone.Multi_platform.services.webhook import WebhookHandler, FakeSocialPlatformServer
        handler = WebhookHandler()
        payload = json.dumps({"event": "post.published", "post_id": "p123", "platform": "instagram"})
        signature = hmac.new(
            FakeSocialPlatformServer.WEBHOOK_SECRET.encode(),
            payload.encode(), hashlib.sha256
        ).hexdigest()
        valid, msg = handler.receive(payload, signature)
        assert valid is True, f"Valid webhook rejected: {msg}"

    def test_forged_signature_rejected(self):
        """Core security test: forged webhook MUST be rejected with False."""
        from capstone.Multi_platform.services.webhook import WebhookHandler
        handler = WebhookHandler()
        payload = json.dumps({"event": "post.published", "post_id": "p999"})
        forged_sig = "deadbeefdeadbeefdeadbeef"
        valid, msg = handler.receive(payload, forged_sig)
        assert valid is False, "Forged webhook must be rejected"
        assert "invalid" in msg.lower() or "rejected" in msg.lower()

    def test_duplicate_webhook_deduplicated(self):
        from capstone.Multi_platform.services.webhook import WebhookHandler, FakeSocialPlatformServer
        handler = WebhookHandler()
        payload = json.dumps({"event": "post.published", "post_id": "p_dedup", "platform": "twitter"})
        signature = hmac.new(
            FakeSocialPlatformServer.WEBHOOK_SECRET.encode(),
            payload.encode(), hashlib.sha256
        ).hexdigest()
        valid1, _ = handler.receive(payload, signature)
        valid2, msg2 = handler.receive(payload, signature)
        assert valid1 is True
        assert valid2 is True  # Duplicate is silently accepted
        assert "duplicate" in msg2.lower() or "already" in msg2.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 6. ADAPTER LAYER — Rate limit + retry logic
# ═══════════════════════════════════════════════════════════════════════════

class TestAdapterRateLimit:
    def test_rate_limit_triggers_429(self):
        from capstone.Multi_platform.services.fake_social import FakeSocialPlatformServer
        from capstone.Multi_platform.utils import encrypt_token
        enc = encrypt_token("test_token")
        
        # Fill rate limit (3 per 10s per platform)
        results = []
        for i in range(4):
            r = FakeSocialPlatformServer.publish_post(
                "instagram", "test_token", f"Caption {i}",
                None, f"idem_{i}"
            )
            results.append(r["status"])
        
        assert 429 in results, "Rate limit should trigger 429 on burst"
