# specs.md — Spec checklist cho Capstone - Embeddable Widget & Lead-Capture Platform

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi và yêu cầu multi-tenant isolation.
- [x] Chuẩn hóa schema cho Widget, Submission, Event log và Webhook delivery.
- [x] Tạo API contract cho widget management, embed snippet, submission và dashboard.
- [x] Xác định quy tắc CORS, rate limiting, honeypot và enrichment fallback.

## 2. Core implementation backlog
- [x] Xây dựng Widget Management API cho CRUD widget và phân quyền tenant isolation.
- [x] Sinh script nhúng dạng `<script src=".../widget.js?id=...">` và phục vụ bundle versioned.
- [x] Tạo public submission endpoint với CORS preflight, validation và lưu submission.
- [x] Thêm abuse protection: rate limit theo IP/widget và honeypot chống spam.
- [x] Cài đặt enrichment fallback chain cho IP geolocation và safe side effects cho email/webhook.
- [x] Xây dựng owner dashboard API cho submissions và thống kê cơ bản.

## 3. Verification checklist
- [x] Smoke test cho flow happy path: widget render và submission lưu thành công.
- [x] Test cho CORS preflight và lỗi input trả về 4xx đúng JSON.
- [x] Test rate limit 429 và honeypot chặn spam.
- [x] Test fallback geolocation: A lỗi -> B thành công; cả hai lỗi -> vẫn lưu submission thành công.
- [x] Test side effect lỗi: email/webhook lỗi không làm fail submission.
- [x] Tài liệu, evidence và work board đã được cập nhật.
