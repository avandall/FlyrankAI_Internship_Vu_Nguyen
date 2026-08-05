# rules.md — Quy tắc phát triển cho Capstone - Usage Metering

## 1. Nguyên tắc chung
- Hệ thống này quản lý tiền bạc: Mọi chi tiết liên quan đến Logic và Toán học phải được thiết kế phòng thủ và có Unit Test cứng (Pinned tests).
- Luôn dùng type hints và cấu trúc rõ ràng.

## 2. Quy tắc miền riêng cho dự án Usage Metering
- **Quy tắc Idempotency:** Trong mọi API Request sinh bill, phải bắt buộc client gửi kèm `idempotency_key`. Key này phải được map vào Database Schema (ví dụ `UNIQUE constraint`). Nếu `UNIQUE constraint` báo lỗi, return 200/cached response, tuyệt đối KHÔNG TẠO MỚI Event.
- **Tính toán tiền bạc:** Tiền được xử lý 100% bằng toán số nguyên (`Integer`). Ví dụ: $1.00 phải được lưu và cộng trừ dưới dạng 100 cents (hoặc micro-cents tuỳ thiết kế). Không bao giờ dùng `Float` để nhân chia cộng trừ tiền tệ.
- **Xác thực Webhook:** Stripe gửi webhook đến. Đầu tiên phải kiểm tra Stripe Signature SDK với biến môi trường `STRIPE_WEBHOOK_SECRET`. Nếu sai -> Reject `400`. Bắt buộc lưu trữ ID của webhook event đã xử lý để không xử lý lại (Deduplicate).
- **Status Codes:** Phải trung thực. API báo `429` (Quota exceeded) và `402` (Payment required) phải có JSON message giải thích rõ ràng tại sao user bị block.

## 3. Logging & Observability
- Phải log khi có hành động Deduplication (ví dụ: `Idempotency key XYZ already exists, skipping...` hoặc `Webhook event_id ABC already processed`).
- Log chi tiết các lỗi Webhook Signature để debug nhưng KHÔNG ĐƯỢC in log các secret keys.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit/phase từ `WORK_BOARD.md` mỗi phiên.
- Nếu test thất bại sau 2 lần, reset trạng thái về clean state và ghi blocker.
