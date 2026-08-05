# Technical Specifications: Embeddable Widget & Lead-Capture Platform

## 1. Database Schema (PostgreSQL)

### `tenants`
- `id` (UUID, PK)
- `name` (String)
- `api_key_hash` (String, for auth)

### `widgets`
- `id` (UUID, PK)
- `tenant_id` (UUID, FK to tenants) - **Critical for isolation**
- `type` (Enum: `SIGNUP`, `CTA`, `POPOVER`)
- `title` (String)
- `fields` (JSONB) - Defines the form fields.
- `allowed_origins` (Array of Strings) - For CORS validation.

### `submissions`
- `id` (UUID, PK)
- `widget_id` (UUID, FK to widgets)
- `tenant_id` (UUID, FK to tenants)
- `payload` (JSONB)
- `ip_address` (String)
- `geo_country` (String, nullable)
- `geo_city` (String, nullable)
- `created_at` (Timestamp)

## 2. API Endpoints

### 2.1. Widget Management (Authenticated)
- `POST /api/widgets` - Create a new widget. Requires valid tenant auth.
- `GET /api/widgets` - List widgets for the authenticated tenant.
- `PUT /api/widgets/:id` - Update widget config.

### 2.2. Widget Delivery (Public, Cached)
- `GET /cdn/widgets/:id/config`
  - **Headers Required:** `Cache-Control: public, max-age=300`
  - **Response:** Small JSON payload with widget configuration.

### 2.3. Public Submission Endpoint
- `POST /api/submit/:widget_id`
  - **CORS:** Must respond to `OPTIONS`. Must check `Origin` against `widgets.allowed_origins`.
  - **Rate Limiting:** `429 Too Many Requests` if > 10 requests per minute per IP.
  - **Validation:** `400 Bad Request` if payload doesn't match widget fields, or if body > 50kb.
  - **Spam:** Reject silently (return 200, don't store) if honeypot field is filled.

## 3. Graceful Degradation Chain Logic

### Geo Enrichment
1. Attempt `ip-api.com`. Timeout: 2s.
2. On fail/timeout, attempt `ipapi.co`. Timeout: 2s.
3. On fail/timeout, proceed with `geo_country = null`.

### Side Effects (Email/Webhook)
- Executed asynchronously AFTER the database `INSERT` commits.
- Wrapped in a generic try/catch.
- If it fails, log the error. DO NOT return a 500 to the submitter.

## 4. Task Implementation Checklist
- [ ] **Task 1:** Setup Database Schema (tenants, widgets, submissions) with strict tenant isolation.
- [ ] **Task 2:** Build Widget Management API (CRUD operations for authenticated tenants).
- [ ] **Task 3:** Build Widget Delivery API (`GET /cdn/widgets/:id/config` with Cache-Control).
- [ ] **Task 4:** Implement Public Submission Endpoint (`POST /api/submit/:widget_id`) with CORS and Preflight (`OPTIONS`).
- [ ] **Task 5:** Add Payload Validation (e.g., 400 Bad Request for bad input/size).
- [ ] **Task 6:** Add Rate Limiting (429) & Spam Control (Honeypot).
- [ ] **Task 7:** Implement Geo Enrichment Fallback Chain (Graceful degradation).
- [ ] **Task 8:** Implement Safe Side Effects (Async Email/Webhook wrapper).
- [ ] **Task 9:** Write Automated Tests for CORS, rate limiting, and fallback scenarios.
