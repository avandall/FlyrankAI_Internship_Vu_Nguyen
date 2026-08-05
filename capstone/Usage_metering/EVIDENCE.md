# EVIDENCE.md — Usage Metering & Billing Engine

## Checklist Completion Status

### ✅ Usage Tracking & Idempotency
- **Usage event ingestion**: `engine.py:QuotaService.check_and_consume()` processes `api_call` and `ai_tokens` events.
- **Idempotency key**: Deduplicates requests. If the same `idempotency_key` is passed, it returns the cached event without incrementing usage or charging again.
- **Persistent storage**: SQLite table `usage_events` records every billable action.

Test evidence:
```
PASSED TestIdempotency::test_same_key_returns_existing_event
PASSED TestIdempotency::test_duplicate_does_not_double_count_usage
PASSED TestIdempotency::test_different_keys_both_recorded
```

### ✅ Cost Calculation (Micro-cents)
- **Integer arithmetic**: Cost is calculated entirely in integers (micro-cents) to avoid float precision errors. 1 micro-cent = $0.00000001.
- **AI Token Pricing**: 
  - Input: 750 µ¢
  - Cached Input: 375 µ¢ (50% discount)
  - Output / Reasoning: 3000 µ¢
- **Formatting**: `micro_cents_to_display()` correctly converts back to USD string (e.g., 1,000,000 µ¢ = $0.01).

Test evidence:
```
PASSED TestCostCalculation::test_output_token_cost_is_integer
PASSED TestCostCalculation::test_input_token_price
PASSED TestCostCalculation::test_cached_input_is_50_percent_discount
PASSED TestCostCalculation::test_no_floats_in_calculation
PASSED TestCostCalculation::test_display_formatting
```

### ✅ Quota Enforcement (429 & 402)
- **HTTP 429 Too Many Requests**: Triggered when a tenant exceeds their plan's limits (`quota_api_calls` or `quota_ai_tokens`). Boundary conditions (e.g. 1000/1000 passes, 1001 fails) strictly tested.
- **HTTP 402 Payment Required**: Triggered if the tenant's subscription status is `canceled`, `past_due`, or `unpaid`.

Test evidence:
```
PASSED TestQuotaEnforcement::test_quota_check_before_limit_passes
PASSED TestQuotaEnforcement::test_quota_exceeded_raises_429_error
PASSED TestQuotaEnforcement::test_boundary_1000th_request_passes
PASSED TestQuotaEnforcement::test_1001th_request_fails
PASSED TestPaymentRequired::test_canceled_subscription_raises_402
```

### ✅ Stripe Webhook Handler (HMAC)
- **Signature verification**: `engine.py:StripeWebhookHandler.verify_signature()` uses HMAC-SHA256 to verify `Stripe-Signature` (format `t=timestamp,v1=signature`).
- **Events handled**: `checkout.session.completed` (upgrades plan), `customer.subscription.updated`, `customer.subscription.deleted` (downgrades to free).
- **Deduplication**: Records `stripe_event_id` in `stripe_events` table to ignore re-delivered hooks.

Test evidence:
```
PASSED TestStripeWebhook::test_valid_signature_checkout_completed
PASSED TestStripeWebhook::test_forged_signature_rejected
PASSED TestStripeWebhook::test_subscription_deleted_downgrades_to_free
PASSED TestStripeWebhook::test_duplicate_event_deduplicated
```

### ✅ Multi-Tenant Isolation
- **Tenant scoping**: All queries include `WHERE tenant_id=?`. Tenant A cannot see Tenant B's usage or invoice.

Test evidence:
```
PASSED TestMultiTenantIsolation::test_usage_is_scoped_to_tenant
PASSED TestMultiTenantIsolation::test_invoice_only_shows_own_events
```

## Test Run Output
```
==================== test session starts ====================
collected 23 items

capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_output_token_cost_is_integer PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_input_token_price PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_cached_input_is_50_percent_discount PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_output_token_price PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_reasoning_equals_output PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_no_floats_in_calculation PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_api_call_cost PASSED
capstone/Usage_metering/tests/test_metering.py::TestCostCalculation::test_display_formatting PASSED
capstone/Usage_metering/tests/test_metering.py::TestIdempotency::test_same_key_returns_existing_event PASSED
capstone/Usage_metering/tests/test_metering.py::TestIdempotency::test_duplicate_does_not_double_count_usage PASSED
capstone/Usage_metering/tests/test_metering.py::TestIdempotency::test_different_keys_both_recorded PASSED
capstone/Usage_metering/tests/test_metering.py::TestQuotaEnforcement::test_quota_check_before_limit_passes PASSED
capstone/Usage_metering/tests/test_metering.py::TestQuotaEnforcement::test_quota_exceeded_raises_429_error PASSED
capstone/Usage_metering/tests/test_metering.py::TestQuotaEnforcement::test_boundary_1000th_request_passes PASSED
capstone/Usage_metering/tests/test_metering.py::TestQuotaEnforcement::test_1001th_request_fails PASSED
capstone/Usage_metering/tests/test_metering.py::TestQuotaEnforcement::test_pro_plan_higher_quota PASSED
capstone/Usage_metering/tests/test_metering.py::TestPaymentRequired::test_canceled_subscription_raises_402 PASSED
capstone/Usage_metering/tests/test_metering.py::TestStripeWebhook::test_valid_signature_checkout_completed PASSED
capstone/Usage_metering/tests/test_metering.py::TestStripeWebhook::test_forged_signature_rejected PASSED
capstone/Usage_metering/tests/test_metering.py::TestStripeWebhook::test_subscription_deleted_downgrades_to_free PASSED
capstone/Usage_metering/tests/test_metering.py::TestStripeWebhook::test_duplicate_event_deduplicated PASSED
capstone/Usage_metering/tests/test_metering.py::TestMultiTenantIsolation::test_usage_is_scoped_to_tenant PASSED
capstone/Usage_metering/tests/test_metering.py::TestMultiTenantIsolation::test_invoice_only_shows_own_events PASSED

==================== 23 passed in 3.63s =====================
```
