"""
AI Image Engine — Automated Test Suite
Tests: schema validation, mismatch guard, matching accuracy, flagging, review API.
Run: python -m pytest capstone/AI_Image/tests/test_ai_image.py -v
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import pytest
from pathlib import Path

# Point tests at a temp DB so they don't pollute production data
os.environ['AI_IMAGE_TEST_DB'] = str(Path(__file__).parent / 'test_ai_image.db')

from capstone.AI_Image.core.database import init_db
from capstone.AI_Image.services.ingestion import ImageIngestionService
from capstone.AI_Image.services.matching import ContentMatchingEngine
from capstone.AI_Image.services.review import ReviewService
from capstone.AI_Image.core.config import SEED_IMAGES
from capstone.AI_Image.services.mismatch_guard import MismatchGuard
from capstone.AI_Image.utils import compute_embedding, cosine_similarity


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Redirect DB to tmp for each test."""
    import capstone.AI_Image.core.database as db
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db, 'DB_PATH', test_db)
    init_db()
    yield


@pytest.fixture
def ingestion():
    return ImageIngestionService()


@pytest.fixture
def matcher():
    return ContentMatchingEngine()


@pytest.fixture
def reviewer():
    return ReviewService()


# ═══════════════════════════════════════════════════════════════════════════
# 1. EMBEDDING & SIMILARITY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestEmbedding:
    def test_embedding_dimension(self):
        emb = compute_embedding("red fox in the forest", dim=64)
        assert len(emb) == 64

    def test_identical_texts_have_similarity_1(self):
        t = "a wild red fox running through snow"
        e1 = compute_embedding(t)
        e2 = compute_embedding(t)
        sim = cosine_similarity(e1, e2)
        assert abs(sim - 1.0) < 1e-6, f"Expected ~1.0, got {sim}"

    def test_different_texts_have_lower_similarity(self):
        e_fox = compute_embedding("red fox wildlife forest hunting")
        e_city = compute_embedding("urban cityscape skyscraper glass tower")
        sim = cosine_similarity(e_fox, e_city)
        assert sim < 0.7, f"Expected sim < 0.7 for unrelated texts, got {sim}"

    def test_embedding_is_normalized(self):
        emb = compute_embedding("test text here")
        mag = math.sqrt(sum(v**2 for v in emb))
        assert abs(mag - 1.0) < 0.01, f"Embedding not normalized: mag={mag}"


# ═══════════════════════════════════════════════════════════════════════════
# 2. INGESTION + SCHEMA VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestIngestion:
    def test_metadata_ingest_success(self, ingestion):
        result = ingestion.ingest_metadata({
            "image_id": "test_img_01", "filename": "fox.jpg",
            "file_size_bytes": 50000, "format": "jpg", "width": 800, "height": 600,
            "subject": "fox", "category": "animal",
            "attributes": ["wildlife", "fox"], "caption": "A red fox in the snow",
            "confidence_score": 0.95,
        })
        assert result["image_id"] == "test_img_01"
        assert result["is_flagged"] is False

    def test_low_confidence_image_is_flagged(self, ingestion):
        result = ingestion.ingest_metadata({
            "image_id": "test_blurry", "filename": "blurry.jpg",
            "file_size_bytes": 10000, "format": "jpg", "width": 200, "height": 200,
            "subject": "unknown", "category": "unknown",
            "attributes": [], "caption": "Unclear image",
            "confidence_score": 0.42,  # Below threshold of 0.70
        })
        assert result["is_flagged"] is True, "Image with confidence 0.42 should be flagged"

    def test_persisted_image_retrievable(self, ingestion):
        ingestion.ingest_metadata({
            "image_id": "p_img_01", "filename": "mountain.jpg",
            "file_size_bytes": 80000, "format": "jpg",
            "subject": "mountain", "category": "nature",
            "attributes": ["peak", "snow"], "caption": "Alpine mountain peak",
            "confidence_score": 0.90,
        })
        img = ingestion.get_image("p_img_01")
        assert img is not None
        assert img["subject"] == "mountain"

    def test_file_upload_pipeline(self, ingestion):
        """Test full file ingestion pipeline with synthetic file bytes."""
        # Create minimal JPEG-like bytes (not a valid JPEG, but tests pipeline)
        fake_bytes = b'\xff\xd8\xff\xe0' + b'\x00' * 100 + b'\xff\xd9'
        result = ingestion.ingest_from_file("fox_winter.jpg", fake_bytes, "img_upload_test")
        assert result["image_id"] == "img_upload_test"
        assert result["filename"] == "fox_winter.jpg"
        assert result["job_id"].startswith("job_")
        assert "confidence_score" in result


# ═══════════════════════════════════════════════════════════════════════════
# 3. MISMATCH GUARD TESTS — Core safety layer
# ═══════════════════════════════════════════════════════════════════════════

class TestMismatchGuard:
    def test_wolf_rejected_for_fox_post(self):
        """Core scenario: Fox article must NOT match Wolf image."""
        guard = MismatchGuard()
        is_valid, reason = guard.evaluate(
            target_subject="fox", target_category="animal",
            candidate_subject="wolf", candidate_category="animal",
            similarity=0.85, confidence=0.91,
        )
        assert is_valid is False, "Wolf should be REJECTED for fox article"
        assert "mismatch" in reason.lower() or "wolf" in reason.lower()

    def test_fox_matches_fox(self):
        """Fox article should ACCEPT fox image."""
        guard = MismatchGuard()
        is_valid, reason = guard.evaluate(
            target_subject="fox", target_category="animal",
            candidate_subject="fox", candidate_category="animal",
            similarity=0.88, confidence=0.95,
        )
        assert is_valid is True, f"Fox should match fox, but got: {reason}"

    def test_low_similarity_rejected(self):
        """Similarity below 0.60 should be rejected."""
        guard = MismatchGuard()
        is_valid, reason = guard.evaluate(
            target_subject=None, target_category=None,
            candidate_subject="cat", candidate_category="animal",
            similarity=0.35, confidence=0.9,
        )
        assert is_valid is False
        assert "0.35" in reason or "threshold" in reason.lower()

    def test_flagged_image_rejected(self):
        """Flagged images (low confidence) should be blocked."""
        guard = MismatchGuard()
        is_valid, reason = guard.evaluate(
            target_subject="fox", target_category="animal",
            candidate_subject="fox", candidate_category="animal",
            similarity=0.90, confidence=0.40,  # Confidence below 0.70 threshold
        )
        assert is_valid is False
        assert "confidence" in reason.lower() or "0.40" in reason

    def test_category_mismatch_rejected(self):
        """Urban image rejected for animal category request."""
        guard = MismatchGuard()
        is_valid, reason = guard.evaluate(
            target_subject=None, target_category="animal",
            candidate_subject="cityscape", candidate_category="urban",
            similarity=0.65, confidence=0.90,
        )
        assert is_valid is False
        assert "category" in reason.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONTENT MATCHING ACCURACY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestContentMatching:
    @pytest.fixture(autouse=True)
    def seed_images(self, ingestion):
        for seed in SEED_IMAGES:
            ingestion.ingest_metadata(seed)

    def test_fox_post_matches_fox_image(self, matcher):
        result = matcher.match_post(
            post_id="test_fox",
            title="The Red Fox: Master of Survival",
            text="The red fox Vulpes vulpes is a cunning predator of the forest hunting alone",
            target_subject="fox",
            target_category="animal",
        )
        assert result["status"] == "MATCHED", f"Expected MATCHED, got {result['status']}: {result.get('reject_reason')}"
        assert result["matched_image"]["subject"] == "fox"

    def test_wolf_is_blocked_for_fox_post(self, matcher):
        """Wolf image must be rejected when fox is expected (Mismatch Guard)."""
        # Temporarily ingest only wolf image to force it as top candidate
        svc = ImageIngestionService()
        svc.ingest_metadata({
            "image_id": "wolf_only", "filename": "wolf_forest.jpg",
            "file_size_bytes": 100000, "format": "jpg",
            "subject": "wolf", "category": "animal",
            "attributes": ["wolf", "forest", "predator"],
            "caption": "A grey wolf standing in the forest",
            "confidence_score": 0.92,
        })
        result = matcher.match_post(
            post_id="test_wolf_block",
            title="Red Fox Life in Northern Forests",
            text="foxes are solitary animals that hunt alone unlike wolves",
            target_subject="fox",  # Explicitly asking for fox
            target_category="animal",
        )
        # Wolf should be blocked by Mismatch Guard
        if result["status"] == "MATCHED":
            assert result["matched_image"]["subject"] == "fox", \
                "If matched, must be fox NOT wolf"

    def test_no_match_returned_for_unrelated_content(self, matcher):
        result = matcher.match_post(
            post_id="test_quantum",
            title="Quantum Computing Breakthroughs",
            text="Superconducting qubits and quantum entanglement in modern processors",
            target_category="technology",  # No tech images in library
        )
        assert result["status"] in ("NO_CONFIDENT_MATCH", "REJECTED"), \
            f"Unrelated content should not match: {result['status']}"

    def test_ranked_candidates_ordered_by_similarity(self, matcher):
        result = matcher.match_post(
            post_id="test_rank",
            title="Animal Wildlife Photography",
            text="Wildlife animals in natural habitats forest snow nature",
        )
        if result.get("all_candidates"):
            scores = [c["similarity_score"] for c in result["all_candidates"]]
            assert scores == sorted(scores, reverse=True), "Candidates must be sorted by similarity DESC"


# ═══════════════════════════════════════════════════════════════════════════
# 5. REVIEW API TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestReviewAPI:
    def test_submit_approval(self, reviewer):
        result = reviewer.submit_review("img_fox_01", "post_001", approved=True)
        assert result["approved"] is True
        assert result["review_id"].startswith("rev_")

    def test_submit_rejection_with_reason(self, reviewer):
        result = reviewer.submit_review(
            "img_wolf_01", "post_001", approved=False,
            reject_reason="Wrong animal suggested for fox article"
        )
        assert result["approved"] is False
        assert "fox" in result["reject_reason"]

    def test_precision_metric_calculated(self, reviewer):
        reviewer.submit_review("img_fox_01", "post_001", approved=True)
        reviewer.submit_review("img_wolf_01", "post_002", approved=True)
        reviewer.submit_review("img_dog_01", "post_003", approved=False)
        metrics = reviewer.get_top1_precision()
        assert metrics["total_reviews"] == 3
        assert metrics["approved"] == 2
        assert abs(metrics["top1_precision"] - 2/3) < 0.01


# ═══════════════════════════════════════════════════════════════════════════
# 6. IDEMPOTENCY — Same image_id overwritten safely
# ═══════════════════════════════════════════════════════════════════════════

class TestIdempotency:
    def test_duplicate_ingest_does_not_create_duplicates(self, ingestion):
        meta = {
            "image_id": "idem_img_01", "filename": "fox.jpg",
            "file_size_bytes": 50000, "format": "jpg",
            "subject": "fox", "category": "animal",
            "attributes": ["fox"], "caption": "Red fox",
            "confidence_score": 0.92,
        }
        ingestion.ingest_metadata(meta)
        ingestion.ingest_metadata(meta)  # Ingest same ID again
        images = [i for i in ingestion.get_all_images() if i["image_id"] == "idem_img_01"]
        assert len(images) == 1, "Duplicate ingest should not create extra records"
