# rules.md — Quy tắc phát triển cho Capstone - Multi-Platform Social Campaign Publisher

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Không dùng try/except chung chung để nuốt lỗi; phải log lỗi cụ thể và có context.
- Mọi dữ liệu publish job phải có schema validation, trạng thái rõ và audit trail.
- Tất cả integration ngoài như fake platform hoặc webhook phải có retry, backoff và idempotency key.

## 2. Quy tắc miền riêng cho dự án
- Publish phải là idempotent: cùng request lặp lại không tạo nhiều post trùng.
- Scheduler phải bền vững qua restart worker; job không được mất hoặc nhân đôi.
- Webhook status update chỉ được chấp nhận nếu signature hợp lệ bằng HMAC.
- Tạo ảnh và caption phải phân biệt theo từng nền tảng (Instagram/X/LinkedIn/Facebook).
- Trạng thái campaign phải đi tuần tự: queued -> publishing -> published/failed.

## 3. Logging & observability
- Ghi log cho từng job: campaign id, platform, schedule time, attempt count, retry-after, error code, webhook status.
- Không log token nhạy cảm hay signature thô.
- Nếu platform trả 429, phải xử lý Retry-After đúng cách.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit mỗi phiên, ví dụ: image variant, prompt composer, adapter, scheduler hoặc webhook.
- Nếu test thất bại sau 2 lần, reset về trạng thái sạch và ghi blocker.
- Không refactor ngầm trong lúc làm feature mới; debt phải tách riêng.
