# Embeddable Widget & Lead-Capture Platform - Implementation Plan

## 1. Project Mission
Build a robust platform that allows customers to define a widget (like a signup or contact form) and embed it on their own websites using a single `<script>` tag. The backend must handle unauthenticated, cross-origin traffic from the public internet, validating input, blocking spam, gracefully enriching data, and serving the widget configuration quickly.

## 2. Core Architecture & Stack
- **Languages:** Node.js + Express OR Python + FastAPI
- **Database:** PostgreSQL (tenant-isolated data models).
- **Environment:** Must run entirely on `localhost` utilizing different ports or `file://` protocols to simulate cross-origin requests.
- **External Services (Mocked/Free):** Geo IP APIs (ip-api.com, ipapi.co), local email catcher (Mailpit or console log).

## 3. Key Components to Implement

### 3.1. Widget Management API (Authenticated)
- **CRUD Operations:** Authenticated endpoints for customers (tenants) to create and manage their widgets (type, fields, display options).
- **Tenant Isolation:** A tenant must absolutely never be able to read or modify another tenant's widgets or submissions.

### 3.2. Widget Delivery & Embed Snippet
- **Snippet Generation:** Return the single line of `<script>` tag for the customer.
- **Fast, Cached Delivery:** Serve the widget configuration and JavaScript bundle with proper HTTP cache headers (e.g., `Cache-Control`).
- **Versioning:** The widget JavaScript bundle must be versioned (e.g., cache-busted via URL or query param).

### 3.3. Public Submission Endpoint (Hardened)
- **CORS Handling:** The endpoint receives cross-origin requests. It must correctly handle `OPTIONS` preflight requests and proper CORS headers.
- **Input Validation:** Validate every submitted field. Malformed or oversized payloads must be rejected with clean `4xx` errors (never a `500`).

### 3.4. Abuse Protection
- **Rate Limiting:** Implement rate limiting per IP address and/or per widget (returning `429 Too Many Requests`).
- **Spam Control:** Implement at least one anti-spam measure (e.g., a honeypot field, a token, or heuristic validation).

### 3.5. Enrichment & Safe Side Effects
- **Geo Enrichment Fallback Chain:** Enrich the submission with Geo IP data. If primary provider A fails, fallback to provider B. If both fail, the submission *must still succeed* (just without geo data).
- **Safe Side Effects:** Trigger an email/webhook notification after a successful save. If the email delivery fails, it must *not* break the main submission request. (Degrade gracefully).

### 3.6. Owner Dashboard API
- **Analytics:** Provide basic endpoints for the owner to view submission counts over time, stats per widget, and geographic breakdown.

## 4. Definition of Done (Checklist for AI implementation)
- [ ] Strict multi-tenant isolation enforced at the database/API level.
- [ ] Public config and JS bundle served with correct cache headers.
- [ ] Cross-origin (CORS) submissions work successfully, including preflight handling.
- [ ] Validation correctly rejects bad payloads with `4xx` responses.
- [ ] Rate limiter effectively stops bursts, returning `429`.
- [ ] Spam control successfully drops bot-like submissions.
- [ ] Geo enrichment degrades gracefully when providers fail; main submission is untouched.
- [ ] Failing side effects (email) do not prevent the row from being saved.
- [ ] Automated tests cover CORS, rate limiting, provider fallback, and invalid payload scenarios.
