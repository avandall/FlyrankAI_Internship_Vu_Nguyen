# specs.md — Spec checklist cho Capstone - Usage Metering & Billing Engine

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi và yêu cầu tính chính xác tuyệt đối cho billing.
- [x] Chuẩn hóa schema cho Tenant, Plan, Subscription, Usage Event và Invoice snapshot.
- [x] Tạo API contract cho usage ingestion, quota check, usage report và webhook subscription.
- [x] Xác định quy tắc idempotency, quota boundary và lưu trữ tiền tệ bằng integer.

## 2. Core implementation backlog
- [x] Xây dựng usage metering với idempotency key và chống double-counting.
- [x] Cài đặt quota enforcement trả về 429/402 đúng boundary và plan-based check.
- [x] Tạo cost calculation cho input/cached input/output/reasoning tokens theo config.
- [x] Tích hợp Stripe Checkout test mode và xử lý webhook checkout.session.completed / subscription.updated / subscription.deleted.
- [x] Thêm audit trail, deduplication cho webhook và report endpoint cho usage/invoice.

## 3. Verification checklist
- [x] Smoke test cho flow happy path: event -> quota OK -> cost tính đúng.
- [x] Test duplicate request với cùng idempotency key không tạo event trùng.
- [x] Test quota boundary: request thứ N và N+1 trả đúng 200/429/402.
- [x] Test webhook giả mạo bị từ chối và event trùng bị bỏ qua.
- [x] Test plan upgrade/ downgrade và sync status tenant đúng.
- [x] Tài liệu, evidence và work board đã được cập nhật.
