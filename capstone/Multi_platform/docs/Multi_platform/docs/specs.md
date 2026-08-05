# specs.md — Spec checklist cho Capstone - Multi-Platform Social Campaign Publisher

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi sandbox và yêu cầu reliability engineering.
- [x] Chuẩn hóa schema cho Campaign, Content Variant, Platform Adapter, Schedule Job và Publish Event.
- [x] Tạo API contract cho campaign creation, publish request, webhook status update và scheduler.
- [x] Xác định quy tắc idempotency, retry-after, durable scheduling và HMAC webhook verification.

## 2. Core implementation backlog
- [x] Tạo pipeline xử lý ảnh đa nền tảng và tạo variant đúng kích thước/tỷ lệ/safe zone.
- [x] Xây dựng content generation pipeline từ prompt fragments cho từng platform.
- [x] Thiết kế interface SocialPublisher và ít nhất 2 adapter cho 2 nền tảng khác nhau.
- [ ] Tạo hệ thống scheduler bền vững cho publish theo thời gian đã định.
- [x] Xử lý webhook signed status update và cập nhật trạng thái campaign đúng quy trình.
- [x] Thêm audit log, retry policy và chống publish trùng lặp.

## 3. Verification checklist
- [x] Smoke test cho flow happy path: campaign -> variant -> queued -> published.
- [x] Test idempotency: retry hoặc duplicate request không tạo nhiều post trùng.
- [x] Test rate limit 429 Retry-After và backoff logic.
- [x] Test webhook giả mạo bị từ chối với 400.
- [x] Test crash/restart worker không làm mất hoặc nhân đôi job.
- [x] Tài liệu, evidence và work board đã được cập nhật.
