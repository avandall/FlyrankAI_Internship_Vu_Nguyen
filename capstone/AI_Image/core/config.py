from typing import Dict, List

CONFIDENCE_THRESHOLD = 0.70
SIMILARITY_THRESHOLD = 0.60

# ─── Mismatch Guard taxonomy rules ──────────────────────────────────────────
# Maps (target_subject_keyword → rejected_candidate_keywords)
MISMATCH_RULES: Dict[str, List[str]] = {
    "fox": ["wolf", "dog", "coyote"],
    "cat": ["lion", "tiger", "cheetah", "leopard"],
    "eagle": ["hawk", "vulture", "owl"],
}

# Reverse alias resolution — semantic synonyms map to canonical subjects
SUBJECT_ALIASES: Dict[str, str] = {
    "red fox": "fox", "vulpes vulpes": "fox", "wild fox": "fox",
    "grey wolf": "wolf", "gray wolf": "wolf",
    "golden retriever": "dog", "labrador": "dog",
    "kitten": "cat", "kitty": "cat",
}

# ─── Demo seed data (50 images for full capstone demo) ──────────────────────
SEED_IMAGES = [
    {
        "image_id": "img_fox_01", "filename": "red_fox_snow.jpg",
        "file_size_bytes": 124000, "format": "jpg", "width": 1024, "height": 768,
        "subject": "fox", "category": "animal",
        "attributes": ["wildlife", "fox", "red fox", "vulpes", "snow", "nature", "forest", "predator", "mammal", "hunting"],
        "caption": "A wild red fox Vulpes vulpes standing gracefully in the forest snow, hunting for food in winter. The fox is a cunning solitary predator with distinctive russet orange fur and a bushy tail.",
        "confidence_score": 0.95,
    },
    {
        "image_id": "img_wolf_01", "filename": "grey_wolf_woods.jpg",
        "file_size_bytes": 145000, "format": "jpg", "width": 1024, "height": 768,
        "subject": "wolf", "category": "animal",
        "attributes": ["wildlife", "wolf", "grey wolf", "predator", "forest", "pack", "howling", "carnivore"],
        "caption": "A grey wolf standing alert in the dense forest, eyes scanning for prey. Wolves are powerful apex predators that hunt in organized packs across boreal forests.",
        "confidence_score": 0.91,
    },
    {
        "image_id": "img_dog_01", "filename": "golden_retriever_park.jpg",
        "file_size_bytes": 110000, "format": "jpg", "width": 800, "height": 600,
        "subject": "dog", "category": "animal",
        "attributes": ["pet", "dog", "canine", "park", "friendly"],
        "caption": "A friendly golden retriever playing fetch in a sunny park",
        "confidence_score": 0.94,
    },
    {
        "image_id": "img_mountain_01", "filename": "alpine_mountain_peak.jpg",
        "file_size_bytes": 230000, "format": "jpg", "width": 1920, "height": 1080,
        "subject": "mountain", "category": "nature",
        "attributes": ["mountain", "alpine", "snow", "peak", "landscape", "hiking", "summit", "elevation", "wilderness"],
        "caption": "A majestic alpine mountain peak covered in snow at dawn, offering breathtaking views of the surrounding wilderness. Ideal for hiking and mountaineering enthusiasts seeking high elevation adventure.",
        "confidence_score": 0.93,
    },
    {
        "image_id": "img_ocean_01", "filename": "ocean_waves_coast.jpg",
        "file_size_bytes": 190000, "format": "jpg", "width": 1920, "height": 1080,
        "subject": "ocean", "category": "nature",
        "attributes": ["ocean", "waves", "coast", "sea", "water"],
        "caption": "Ocean waves crashing against a rocky coastline at sunset",
        "confidence_score": 0.92,
    },
    {
        "image_id": "img_low_conf", "filename": "blurry_shadow.jpg",
        "file_size_bytes": 35000, "format": "jpg", "width": 400, "height": 300,
        "subject": "unknown", "category": "unknown",
        "attributes": ["blurry", "unclear"],
        "caption": "Unclear shape in dim lighting, content unidentifiable",
        "confidence_score": 0.40,  # Will be flagged
    },
]
