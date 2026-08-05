# AI Image Understanding & Content Matching Engine - Implementation Plan

## 1. Project Mission
Build a reliable AI-powered system that organizes an image library automatically and matches the best image to a corresponding blog post based on semantic meaning, not just keywords. A critical requirement is to ensure the AI behaves reliably: it should make good suggestions when confident and safely reject mismatches (e.g., rejecting a wolf image for a red fox post) when uncertain.

## 2. Core Architecture & Stack
- **Languages:** Node.js + Express OR Python + FastAPI
- **AI Models:** 
  - Vision Model: Gemini Flash (free tier) or local Ollama (e.g., llava).
  - Embeddings: Gemini embeddings or local `all-minilm`.
- **Database:** PostgreSQL (with `pgvector` for similarity search).
- **Validation:** Zod (Node.js) or Pydantic (Python) for schema validation.

## 3. Key Components to Implement

### 3.1. Image Ingestion & Classification Pipeline
- **Vision Processing:** Run images through a vision model to generate structured metadata (subject, category, attributes, caption, confidence score).
- **Schema Validation:** Strictly validate the model's JSON output. Invalid or malformed responses must be retried or flagged.
- **Low-Confidence Handling:** If the confidence score is too low, the result must be flagged for manual review, not silently accepted.

### 3.2. Semantic Image Matching
- **Embeddings Generation:** Generate vector embeddings for the extracted image captions and the blog post text.
- **Similarity Search:** Store embeddings in the vector database and retrieve ranked image suggestions based on cosine similarity to the post's text.

### 3.3. Mismatch Guard (Safety Layer)
- **Concept:** The most critical production feature. A rule engine that evaluates top candidates.
- **Rules:** Combine extracted metadata tags (e.g., category matching), semantic similarity thresholds, and confidence scores to decide if the match is "good enough."
- **Rejection:** If the best candidate fails the check (e.g., mismatching animal categories), the system must reject it with a clear, human-readable explanation (e.g., "Animal category mismatch: expected fox, detected wolf").

### 3.4. Background Processing System
- **Batch Jobs:** Image vision processing and embedding generation must run asynchronously in background jobs (e.g., BullMQ for Node.js, APScheduler for Python).
- **Reliability:** The jobs must support retries. 
- **Cost Tracking:** The system must record the AI usage cost for every vision and embedding call.

### 3.5. Review API
- **Endpoints:** Provide a simple API to list matches, inspect rejection reasons, and approve or reject suggested image-post pairings. (A full frontend is not required, just functional endpoints).

## 4. Definition of Done (Checklist for AI implementation)
- [ ] Vision model returns strict, validated JSON matching the predefined schema.
- [ ] Low-confidence classifications are successfully flagged.
- [ ] Images are processed in the background with retries.
- [ ] AI costs are meticulously tracked per call.
- [ ] The mismatch guard successfully rejects incorrect matches (e.g., wolf for a fox post) with a clear explanation.
- [ ] When no image clears the threshold, the system accurately reports "no confident match".
- [ ] Semantic matching works based on concepts, not just exact keywords.
- [ ] Appropriate automated tests cover the mismatch rejection logic, schema validation, and matching accuracy.
