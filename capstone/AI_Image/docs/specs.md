# Technical Specifications: AI Image Understanding & Content Matching Engine

## 1. Database Schema (PostgreSQL)

### `images`
- `id` (UUID, PK)
- `url` (String) - Path to the image (e.g., Unsplash/Pexels URL or local path).
- `status` (Enum: `PENDING`, `PROCESSED`, `NEEDS_REVIEW`, `FAILED`)
- `created_at` (Timestamp)

### `image_metadata`
- `image_id` (UUID, FK to images)
- `subject` (String)
- `category` (String)
- `attributes` (Array of Strings)
- `caption` (Text)
- `confidence` (Float, 0.0 to 1.0)

### `image_embeddings`
- `image_id` (UUID, FK to images)
- `embedding` (Vector) - Using `pgvector`

### `posts`
- `id` (UUID, PK)
- `content` (Text)
- `embedding` (Vector)

### `reviews` (Optional, for API)
- `id` (UUID, PK)
- `post_id` (UUID)
- `image_id` (UUID)
- `status` (Enum: `APPROVED`, `REJECTED`)
- `reason` (Text, nullable)

## 2. API Endpoints

### `GET /posts/:id/images`
- **Purpose:** Fetches ranked image suggestions for a specific blog post.
- **Query Params:** `limit` (default: 5)
- **Response:**
  - `200 OK`: Returns an array of suggested images, ranked by semantic similarity.
  - Returns `[]` if the Mismatch Guard rejects all top candidates, with an explanation.

### `POST /images/review`
- **Purpose:** Approves or rejects a suggested pairing.
- **Body:**
  ```json
  {
    "post_id": "uuid",
    "image_id": "uuid",
    "action": "APPROVE" | "REJECT"
  }
  ```

## 3. Metadata JSON Schema (Zod/Pydantic)
The AI model MUST return JSON conforming to this schema.
```json
{
  "type": "object",
  "properties": {
    "subject": { "type": "string" },
    "category": { "type": "string" },
    "attributes": { 
      "type": "array", 
      "items": { "type": "string" } 
    },
    "caption": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
  },
  "required": ["subject", "category", "attributes", "caption", "confidence"]
}
```

## 4. Mismatch Guard Rules
The mismatch guard evaluates a candidate image against the target post.
1. **Semantic Similarity Threshold:** The cosine similarity between the image caption vector and the post text vector must be `>= 0.75` (configurable).
2. **Category Agreement:** The system compares the detected `category` from the image metadata against keywords in the post (e.g., if post is exclusively about "foxes", an image categorized as "wolf" is rejected).
3. **Confidence Gate:** If the model's confidence was `< 0.8`, the image is automatically excluded from auto-suggestions unless manually approved.

## 5. Task Implementation Checklist
- [ ] **Task 1:** Setup Database Schema (images, image_metadata, image_embeddings, posts, reviews).
- [ ] **Task 2:** Implement Metadata JSON Schema using Zod/Pydantic.
- [ ] **Task 3:** Build Vision Model Ingestion (Flag low-confidence `< 0.8`).
- [ ] **Task 4:** Build Embedding logic & Cosine Similarity search (`pgvector`).
- [ ] **Task 5:** Implement Mismatch Guard Rules (Similarity Threshold, Category Agreement).
- [ ] **Task 6:** Build `GET /posts/:id/images` API.
- [ ] **Task 7:** Build `POST /images/review` API.
- [ ] **Task 8:** Write Automated Tests for Mismatch Guard and schema validation.
