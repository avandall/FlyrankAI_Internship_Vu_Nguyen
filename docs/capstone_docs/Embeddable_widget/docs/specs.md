# specs.md — Spec checklist cho Capstone - Embeddable Widget & Lead-Capture Platform

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi và yêu cầu multi-tenant isolation.
- [x] Chuẩn hóa schema cho Widget, Submission, Event log và Webhook delivery.
- [ ] Tạo API contract cho widget management, embed snippet, submission và dashboard.
- [ ] Xác định quy tắc CORS, rate limiting, honeypot và enrichment fallback.

## 2. Core implementation backlog
- [ ] Xây dựng Widget Management API cho CRUD widget và phân quyền tenant isolation.
- [ ] Sinh script nhúng dạng `<script src=".../widget.js?id=...">` và phục vụ bundle versioned.
- [ ] Tạo public submission endpoint với CORS preflight, validation và lưu submission.
- [ ] Thêm abuse protection: rate limit theo IP/widget và honeypot chống spam.
- [ ] Cài đặt enrichment fallback chain cho IP geolocation và safe side effects cho email/webhook.
- [ ] Xây dựng owner dashboard API cho submissions và thống kê cơ bản.

## 3. Verification checklist
- [ ] Smoke test cho flow happy path: widget render và submission lưu thành công.
- [ ] Test cho CORS preflight và lỗi input trả về 4xx đúng JSON.
- [ ] Test rate limit 429 và honeypot chặn spam.
- [ ] Test fallback geolocation: A lỗi -> B thành công; cả hai lỗi -> vẫn lưu submission thành công.
- [ ] Test side effect lỗi: email/webhook lỗi không làm fail submission.
- [ ] Tài liệu, evidence và work board đã được cập nhật.
