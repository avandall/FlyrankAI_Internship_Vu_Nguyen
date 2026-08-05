"""
Pydantic schemas for AI Image Understanding & Content Matching Engine.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class ImageMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_id: str = Field(..., description="Unique identifier for the image")
    filename: str = Field(..., description="Image filename")
    file_size_bytes: int = Field(..., gt=0, description="File size in bytes")
    format: str = Field(..., description="Image format (png, jpg, jpeg, webp)")
    dimensions: Dict[str, int] = Field(..., description="Image dimensions with width and height")
    subject: str = Field(..., description="Primary subject of the image (e.g. red fox, wolf, dog)")
    category: str = Field(..., description="Broader category (e.g. animal, landscape, urban)")
    attributes: List[str] = Field(default_factory=list, description="Extracted tags/attributes")
    caption: str = Field(..., description="Semantic text caption for the image")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Vision model confidence score")
    is_flagged: bool = Field(default=False, description="Flagged if confidence is below threshold")


class PostContent(BaseModel):
    post_id: str = Field(..., description="Unique post ID")
    title: str = Field(..., description="Post title")
    text: str = Field(..., description="Full post text or excerpt")
    target_subject: Optional[str] = Field(None, description="Target subject expected (e.g. fox)")
    target_category: Optional[str] = Field(None, description="Target category expected (e.g. animal)")


class MatchCandidate(BaseModel):
    image_id: str
    filename: str
    caption: str
    similarity_score: float
    confidence_score: float
    subject: str
    category: str


class MatchResult(BaseModel):
    status: str = Field(..., description="MATCHED, REJECTED, or NO_CONFIDENT_MATCH")
    matched_image: Optional[MatchCandidate] = None
    all_candidates: List[MatchCandidate] = Field(default_factory=list)
    reject_reason: Optional[str] = None
    confidence_score: float = 0.0


class ReviewSubmission(BaseModel):
    suggestion_id: str
    approved: bool
    review_reason: str
    reviewer: str = "human_editor"
