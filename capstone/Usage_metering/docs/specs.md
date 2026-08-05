# Technical Specifications: Usage Metering & Billing Engine

## 1. Database Schema (PostgreSQL)

### `tenants`
- `id` (UUID, PK)
- `stripe_customer_id` (String, nullable)

### `plans`
- `id` (String, PK) - e.g., `free`, `pro`
- `api_call_limit` (Integer)
- `ai_token_limit` (Integer)

### `subscriptions`
- `id` (UUID, PK)
- `tenant_id` (UUID, FK to tenants)
- `plan_id` (String, FK to plans)
- `status` (String) - e.g., `active`, `past_due`

### `usage_events`
- `id` (UUID, PK)
- `tenant_id` (UUID, FK to tenants)
- `idempotency_key` (String, UNIQUE) - **Crucial for exactly-once**
- `type` (Enum: `API_CALL`, `AI_TOKENS`)
- `quantity` (Integer)
- `details` (JSONB) - e.g., `{"input": 100, "cached_input": 50, "output": 200, "reasoning": 50}`
- `created_at` (Timestamp)

## 2. API Endpoints

### `POST /generate` (Dummy Billable Endpoint)
- **Headers:** `Idempotency-Key` (UUID), `Tenant-ID`
- **Behavior:**
  1. Check quota. If usage >= limit, return `429` (Free tier) or `402` (Pro tier past limit).
  2. Attempt to insert `usage_event`. 
  3. Catch `unique_violation` on `idempotency_key`. If caught, return `200` with the cached original response (simulated).
  4. Execute dummy AI generation and return.

### `GET /usage`
- **Behavior:** Rolls up usage for the current billing cycle. Returns `{ used_api, limit_api, used_tokens, limit_tokens, total_cost_cents }`.

## 3. Pricing Math Rules
Prices are pinned in config (e.g., micro-cents per token).
- `input_cost = input_tokens * config.INPUT_PRICE`
- `cached_input_cost = cached_tokens * config.CACHED_INPUT_PRICE`
- `output_cost = output_tokens * config.OUTPUT_PRICE`
- `reasoning_cost = reasoning_tokens * config.OUTPUT_PRICE` (Reasoning tokens are billed at the output rate).
- `total_cost = (input_cost + cached_input_cost + output_cost + reasoning_cost) / 1000` (Convert to cents, rounding safely).

## 4. Stripe Webhook Handling
- **Endpoint:** `POST /webhooks/stripe`
- **Verification:** Use the official Stripe SDK (`stripe.webhooks.constructEvent`) to verify the `stripe-signature` header using `STRIPE_WEBHOOK_SECRET`.
- **Idempotency:** Track processed Stripe Event IDs in a `processed_webhooks` table to ignore duplicate deliveries from Stripe.
- **Events to handle:**
  - `checkout.session.completed`: Upgrade tenant plan to Pro.
  - `customer.subscription.updated` / `deleted`: Sync tenant plan status.

## 5. Task Implementation Checklist
- [ ] **Task 1:** Setup Database Schema (tenants, plans, subscriptions, usage_events).
- [ ] **Task 2:** Build Idempotency constraint (`UNIQUE` on `idempotency_key` in usage_events).
- [ ] **Task 3:** Implement Dummy Billable Endpoint (`POST /generate`) simulating idempotency handling.
- [ ] **Task 4:** Implement Quota Enforcement rules (Return `429` / `402` accurately at boundaries).
- [ ] **Task 5:** Implement Pricing Math Logic (Integer math, logic for cached vs reasoning tokens).
- [ ] **Task 6:** Build Usage Rollup Endpoint (`GET /usage`).
- [ ] **Task 7:** Implement Stripe Webhook Verification (Using Stripe SDK `constructEvent`).
- [ ] **Task 8:** Build Webhook Deduplication logic (Ignore processed events).
- [ ] **Task 9:** Write Pinned Tests for token Cost Math.
