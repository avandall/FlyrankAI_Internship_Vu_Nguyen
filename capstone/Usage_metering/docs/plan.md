# Usage Metering & Billing Engine - Implementation Plan

## 1. Project Mission
Build a highly precise metering and billing engine for a SaaS application. The system must accurately track customer usage (API calls, AI tokens), strictly enforce plan quotas at the boundaries, calculate costs based on complex AI token pricing rules, and integrate securely with Stripe (in test mode) for subscription management. Correctness is paramount to prevent double-charging or giving away free access.

## 2. Core Architecture & Stack
- **Languages:** Node.js + Express OR Python + FastAPI
- **Database:** PostgreSQL for robust transactional support.
- **Billing Integration:** Stripe (Test Mode only) + Stripe CLI for local webhook forwarding.

## 3. Key Components to Implement

### 3.1. Exactly-Once Usage Metering
- **Event Tracking:** Every billable action (e.g., a dummy `/generate` endpoint) must record a usage event (tenant, type, quantity, timestamp, idempotency key).
- **Idempotency:** Retried requests with the same idempotency key must absolutely NOT result in duplicate usage records. You must guarantee exactly-once metering.

### 3.2. Quota Enforcement
- **Boundary Logic:** Before allowing an action, calculate current usage + requested usage. Check it against the tenant's plan limits.
- **Honest Status Codes:** 
  - Return `429 Too Many Requests` when usage limits are exceeded.
  - Return `402 Payment Required` when payment/upgrade is required.
  - The API must return a clear message explaining why the request was blocked.

### 3.3. Cost Calculation (AI Token Pricing)
- **Complex Math:** Roll up monthly usage into a total cost using realistic AI pricing rules.
- **Rules:** 
  - Cached input tokens are priced cheaper than fresh input tokens.
  - Reasoning tokens count as output tokens (or must be handled according to specific pricing rules).
  - You cannot simply sum all token types together; they must be calculated separately based on pinned constants.
- **Data Types:** Money MUST be stored and calculated as integers (cents/micro-cents) to prevent floating-point precision errors.

### 3.4. Stripe Integration & Webhooks
- **Checkout Flow:** Implement a Stripe Checkout session to upgrade plans (e.g., Free to Pro).
- **Webhook Handling:** Receive webhooks (`checkout.session.completed`, `customer.subscription.updated/deleted`) from Stripe.
- **Security & Reliability:**
  - Verify the Stripe webhook signature using the webhook secret.
  - Deduplicate incoming webhook events (Stripe may send the same event twice).
  - Keep the local tenant plan and status perfectly synced with the Stripe source of truth.

## 4. Definition of Done (Checklist for AI implementation)
- [ ] Billable actions create exactly one usage event; idempotency keys prevent duplicate records under retries.
- [ ] Usage quota limits are strictly enforced.
- [ ] Requests exceeding quotas return appropriate `429` or `402` HTTP status codes.
- [ ] Cost calculation perfectly handles cached tokens, reasoning tokens, and output tokens using integer math.
- [ ] Stripe checkout successfully creates a subscription in test mode.
- [ ] Webhook handler verifies Stripe signatures and ignores duplicate events.
- [ ] Tenant data (subscriptions, usage events) is strictly isolated.
- [ ] Automated tests cover duplicate usage prevention, exact boundary conditions (at/over quota), token math, and invalid webhook rejection.
