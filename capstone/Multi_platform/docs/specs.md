# Technical Specifications: Multi-Platform Social Campaign Publisher

## 1. Database Schema (PostgreSQL)

### `campaigns`
- `id` (UUID, PK)
- `source_post_id` (String)
- `status` (Enum: `DRAFT`, `SCHEDULED`, `PUBLISHING`, `COMPLETED`, `FAILED`)
- `scheduled_for` (Timestamp)

### `social_posts`
- `id` (UUID, PK)
- `campaign_id` (UUID, FK to campaigns)
- `platform` (Enum: `INSTAGRAM`, `X`)
- `caption` (Text)
- `image_path` (String)
- `status` (Enum: `QUEUED`, `PUBLISHING`, `PUBLISHED`, `FAILED`)
- `idempotency_key` (UUID) - Generated at creation.
- `platform_post_id` (String, nullable) - Populated via webhook.

### `platform_tokens`
- `id` (UUID, PK)
- `platform` (String)
- `encrypted_token` (String) - Encrypted at rest.
- `iv` (String) - Initialization vector for decryption.

## 2. Image Variant Specifications
- **Instagram:** 1080x1080 pixels (1:1 aspect ratio).
- **X (Twitter):** 1600x900 pixels (16:9 aspect ratio).
- **Safe Zone:** The main subject must be preserved during cropping (use center gravity or smart crop).

## 3. Adapter Interface
All platforms must implement this interface:
```typescript
interface SocialPublisher {
  publish(
    content: string, 
    mediaPath: string, 
    idempotencyKey: string
  ): Promise<PublishResult>;
}
```

## 4. Reliability Rules
1. **Idempotency:** When the worker calls `FakeInstagramPublisher`, it passes the `idempotency_key`. If the fake server timeouts, the worker retries with the *same* key.
2. **Rate Limiting:** If the fake server returns `429`, the worker must read the `Retry-After` header (seconds or HTTP date), pause the job, and reschedule it exactly after that duration.
3. **Crash Recovery:** BullMQ / APScheduler stores job state in Redis/Postgres. If the Node/Python process dies, the job remains in the `active` or `queued` state and is picked up when the process restarts.

## 5. Webhook Security Spec
- **Endpoint:** `POST /webhook/social-delivery`
- **Header:** `X-Signature-256`
- **Validation:** 
  1. Compute HMAC SHA-256 of the raw request body using the shared webhook secret.
  2. Compare computed signature with `X-Signature-256` using a constant-time string comparison to prevent timing attacks.
  3. If invalid, drop request and return `400 Bad Request`.
  4. If valid, locate the `social_posts` row and update the status.

## 6. Task Implementation Checklist
- [ ] **Task 1:** Setup Database Schema (campaigns, social_posts, platform_tokens).
- [ ] **Task 2:** Implement Image Variant Pipeline (Resize/crop: IG 1080x1080, X 1600x900).
- [ ] **Task 3:** Setup Encryption for OAuth Tokens (AES-GCM with random IV).
- [ ] **Task 4:** Implement `SocialPublisher` Interface and Adapters (FakeInstagram, FakeX).
- [ ] **Task 5:** Build Idempotency Logic in Adapters (Retrying with the same key).
- [ ] **Task 6:** Implement Rate Limit Handling (Pause/Backoff honoring `Retry-After`).
- [ ] **Task 7:** Set up Durable Scheduling Worker (Crash recovery).
- [ ] **Task 8:** Implement Webhook Security Verification (HMAC SHA-256 validation).
- [ ] **Task 9:** Write Automated Tests for HMAC verification and idempotency duplicate blocking.
