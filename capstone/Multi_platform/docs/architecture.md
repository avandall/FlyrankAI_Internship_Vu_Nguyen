# Architecture: Multi-Platform Social Campaign Publisher

## 1. System Overview

This system turns a source blog post into multiple platform-specific social media posts. The architecture is heavily focused on the Adapter pattern to abstract away platform differences, and durable queues to handle the unreliability of networks.

```mermaid
graph TD
    %% Content Generation
    subgraph Content Generation
        BP[Blog Post] --> CC[Caption Composer]
        BP --> IVP[Image Variant Pipeline]
        CC -->|Platform Fragments| C_IG[Instagram Caption]
        CC -->|Platform Fragments| C_X[X Caption]
        IVP -->|1080x1080| I_IG[Instagram Image]
        IVP -->|1600x900| I_X[X Image]
    end

    %% Scheduling and Adapters
    subgraph Durable Publishing Engine
        C_IG & I_IG --> CAM[Campaign Created]
        C_X & I_X --> CAM
        CAM -->|Scheduled Time| Q[Durable Queue]
        Q -->|Wakeup| WORKER[Publish Worker]
        WORKER --> ADAPT{SocialPublisher Interface}
        
        ADAPT -->|Token + Idempotency Key| API_IG[Fake Instagram Adapter]
        ADAPT -->|Token + Idempotency Key| API_X[Fake X Adapter]
    end

    %% Webhook Trust
    subgraph Status Tracking
        API_IG & API_X -.->|Async Network| FAKE[Fake Social Platform]
        FAKE -->|POST /webhook| WH_REC[Webhook Receiver]
        WH_REC -->|Verify Signature| VERIFY{Valid?}
        VERIFY -->|Yes| DB[(Campaign DB)]
        VERIFY -->|No| REJECT[400 Bad Request]
    end
```

## 2. Core Components

### 2.1. Image Variant Pipeline
- **Role:** Ensures media strictly conforms to platform specifications.
- **Mechanism:** Takes a source image, applies crop, resize, and safe-zone logic dynamically based on the target platform's requirements.

### 2.2. Social Publisher Adapter Layer
- **Role:** Hides the chaotic, varied APIs of social networks behind one clean internal interface.
- **Mechanism:** Implements a single interface (e.g., `publish(content, media, idempotencyKey)`). Both Instagram and X adapters implement this. Adding LinkedIn later would just mean adding a new adapter class without touching the core publishing loop.

### 2.3. Durable Scheduler
- **Role:** Ensures campaigns publish exactly on time, and survive server restarts.
- **Mechanism:** A persistent job store (e.g., Redis via BullMQ, or Postgres via APScheduler). If the worker crashes while processing a batch, the jobs remain in the queue and are retried upon restart.

### 2.4. Idempotency & Rate Limit Engine
- **Role:** Prevents double-posting.
- **Mechanism:** Every outbound request to a social network includes a unique idempotency key. If a request times out, the worker retries with the *same* key. The fake platform recognizes the key and returns the cached success response instead of creating a second post.
- **Rate Limits:** If the adapter encounters a `429`, it reads the `Retry-After` header, puts the job to sleep for that exact duration, and requeues it.

### 2.5. Webhook Trust Boundary
- **Role:** Maintains accurate campaign status.
- **Mechanism:** We never trust our own outgoing request for final status. A post is only marked `published` when the platform tells us via an HMAC-signed webhook. The receiver calculates the expected signature and compares it; if they mismatch, the payload is forged and immediately dropped.
