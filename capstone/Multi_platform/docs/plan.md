# Multi-Platform Social Campaign Publisher - Implementation Plan

## 1. Project Mission
Build a robust background publishing system that turns a single blog post into a scheduled social media campaign across multiple platforms (e.g., Instagram, X). The focus is entirely on backend reliability: handling rate limits, network failures, ensuring exact-once publishing (idempotency) upon worker restarts, and securely processing status webhooks.

## 2. Core Architecture & Stack
- **Languages:** Node.js + Express OR Python + FastAPI
- **Target Platform:** A provided fake social platform server (acting as the real API).
- **Scheduling/Queues:** BullMQ + Redis (Node.js) or APScheduler (Python).
- **Image Processing:** `sharp` (Node.js) or `Pillow` (Python).
- **Security:** Node `crypto` or Python `cryptography` for token encryption and HMAC verification.

## 3. Key Components to Implement

### 3.1. Image Variant Pipeline
- **Processing:** Take a source image and generate correct variants per platform (e.g., 1080x1080 square for Instagram, 1600x900 landscape for X).
- **Requirements:** Ensure the correct dimensions and aspect ratio, keeping the main subject inside the "safe zone".

### 3.2. Platform-Tailored Caption Generation
- **Composition:** Assemble captions for each platform using reusable prompt fragments (brand voice, platform rules, content summary).
- **Rule:** Avoid duplicating identical prompts; compose them systematically.

### 3.3. Social Publishing Adapter Layer
- **Architecture:** Define a single `SocialPublisher` interface and implement at least two adapters (e.g., `FakeInstagramPublisher`, `FakeXPublisher`). The core application logic must only depend on the interface, not the specifics of the platform.
- **Idempotency:** Implement idempotency keys so that if a timeout occurs after the platform accepts the post, retrying the request does not double-post.
- **Rate-Limit Handling:** Honor `429 Too Many Requests` and `Retry-After` headers. The worker must back off and retry without hammering the API.
- **Token Security:** OAuth tokens must be stored encrypted at rest using random-IV encryption and never logged in plaintext.

### 3.4. Durable Scheduling System
- **Background Worker:** A reliable worker that picks up campaigns scheduled for the future.
- **Crash Recovery:** If the worker crashes mid-batch, it must be able to restart and resume without double-posting (relying on idempotency keys and transactional state).

### 3.5. Webhook-Based Status Tracking
- **Signature Verification:** The fake platform sends delivery events via webhooks. The system MUST verify the HMAC signature of the webhook.
- **Status Updates:** Only update campaign status (queued -> publishing -> published/failed) if the webhook signature is valid. Forged webhooks must be rejected with `400`.

## 4. Definition of Done (Checklist for AI implementation)
- [ ] Image pipeline produces correctly sized variants for at least two platforms.
- [ ] Adapter pattern is strictly used; the core app does not leak platform logic.
- [ ] OAuth tokens are encrypted at rest with a random IV.
- [ ] Publishing is strictly idempotent. A retried publish (due to timeout) yields exactly one post on the platform.
- [ ] `429` rate limits and `Retry-After` headers are correctly respected with backoff logic.
- [ ] Scheduler survives a mid-batch crash without creating duplicate posts.
- [ ] Webhook signatures are rigorously verified; forged requests are rejected.
- [ ] Automated tests cover rate limit behavior, crash recovery, idempotency, and webhook verification.
