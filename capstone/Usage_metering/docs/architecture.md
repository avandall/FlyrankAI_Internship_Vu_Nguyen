# Architecture: Usage Metering & Billing Engine

## 1. System Overview

This system handles the intersection of application usage and money. The architecture is intentionally small but designed for absolute correctness: exactly-once metering, precise mathematical rollups, and strict synchronization with an external payment provider (Stripe).

```mermaid
graph TD
    %% Metering Path
    subgraph Billable Action (The Write Path)
        CLI[Client Request] --> API[Billable API]
        API --> METER[Meter Service]
        METER -->|Idempotency Key| DEDUP{Is Duplicate?}
        DEDUP -->|Yes| RETURN[Return Original Result]
        DEDUP -->|No| STORE_EVENT[(Usage Events DB)]
        STORE_EVENT --> QUOTA[Quota Check]
        QUOTA -->|Exceeded| REJECT[429 / 402 Reject]
        QUOTA -->|Allowed| ALLOW[Execute Action]
    end

    %% Read Path
    subgraph Dashboard (The Read Path)
        GET_U[GET /usage] --> ROLLUP[Rollup Engine]
        ROLLUP --> STORE_EVENT
        ROLLUP --> CONST[Pricing Constants]
        ROLLUP -->|Math| RES[{Used, Limit, Cost}]
    end

    %% Stripe Path
    subgraph Stripe Integration (The Sync Path)
        STRIPE[Stripe Test Mode] -->|POST /webhooks| WH[Webhook Handler]
        WH --> VERIFY_SIG[Verify Signature]
        VERIFY_SIG --> DEDUP_WH[Deduplicate Event]
        DEDUP_WH --> UPDATE[(Tenant Plan DB)]
    end
```

## 2. Core Components

### 2.1. Metering Engine
- **Role:** Records every billable action reliably.
- **Mechanism:** Requires the client to pass an `idempotency_key`. The engine attempts to insert the usage event with this key (usually via a unique constraint in the DB). If the insert fails due to a constraint violation, the engine knows this is a retry of an already-processed action and safely ignores it, preventing double-billing.

### 2.2. Quota Enforcer
- **Role:** Gatekeeper for API actions.
- **Mechanism:** Before executing any expensive/billable action, it sums up the tenant's current usage for the cycle and compares it against their plan limits.
- **Boundaries:** It handles the exact boundary meticulously. If a user has 1,000 calls and requests 1 more, it must reject with `429 Too Many Requests` or `402 Payment Required` depending on business logic, with a clear error message.

### 2.3. Rollup & Math Engine
- **Role:** Translates raw events into money.
- **Mechanism:** Extracts token counts (input, cached input, reasoning, output) and applies pinned pricing constants. It strictly uses integer math (e.g., storing all costs as micro-cents) to avoid floating-point inaccuracies.

### 2.4. Stripe Synchronization Layer
- **Role:** Keeps the local database truth aligned with Stripe.
- **Mechanism:** The application does not manage credit cards or recurring schedules; Stripe does. The app listens for Stripe webhooks (`checkout.session.completed`, `customer.subscription.updated`).
- **Security:** Webhooks are verified using Stripe's official libraries to check the `stripe-signature` header against a local webhook secret (`whsec_...`). Unverified payloads are dropped immediately.
