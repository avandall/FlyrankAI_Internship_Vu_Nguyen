# specs.md — Spec checklist cho Capstone - Usage Metering & Billing Engine

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi và yêu cầu tính chính xác tuyệt đối cho billing.
- [x] Chuẩn hóa schema cho Tenant, Plan, Subscription, Usage Event và Invoice snapshot.
- [ ] Tạo API contract cho usage ingestion, quota check, usage report và webhook subscription.
- [ ] Xác định quy tắc idempotency, quota boundary và lưu trữ tiền tệ bằng integer.

## 2. Core implementation backlog
- [ ] Xây dựng usage metering với idempotency key và chống double-counting.
- [ ] Cài đặt quota enforcement trả về 429/402 đúng boundary và plan-based check.
- [ ] Tạo cost calculation cho input/cached input/output/reasoning tokens theo config.
- [ ] Tích hợp Stripe Checkout test mode và xử lý webhook checkout.session.completed / subscription.updated / subscription.deleted.
- [ ] Thêm audit trail, deduplication cho webhook và report endpoint cho usage/invoice.

## 3. Verification checklist
- [ ] Smoke test cho flow happy path: event -> quota OK -> cost tính đúng.
- [ ] Test duplicate request với cùng idempotency key không tạo event trùng.
- [ ] Test quota boundary: request thứ N và N+1 trả đúng 200/429/402.
- [ ] Test webhook giả mạo bị từ chối và event trùng bị bỏ qua.
- [ ] Test plan upgrade/ downgrade và sync status tenant đúng.
- [ ] Tài liệu, evidence và work board đã được cập nhật.
