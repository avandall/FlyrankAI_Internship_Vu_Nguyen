# rules.md — Quy tắc phát triển cho Capstone - Usage Metering & Billing Engine

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Không dùng try/except chung chung để nuốt lỗi; phải log lỗi cụ thể và có context.
- Tất cả giá trị tiền tệ phải được lưu bằng integer (cents/micro-units), tuyệt đối không dùng float.
- Mọi request và webhook phải có validation, deduplication và audit trail.

## 2. Quy tắc miền riêng cho dự án
- Usage event phải có idempotency key và chỉ được ghi đúng 1 lần cho cùng request.
- Quota check phải chạy trước khi xử lý; boundary đúng ở request thứ N và N+1.
- Trả về 429 khi quota exceeded và 402 khi cần upgrade hoặc account chưa thanh toán.
- Pricing engine phải đọc công thức từ config và tính đúng các loại token: input, cached input, output, reasoning.
- Stripe webhook phải verify HMAC và bỏ qua event trùng.

## 3. Logging & observability
- Log mỗi usage event với tenant id, plan id, usage amount, cost, quota status và webhook event id.
- Không log secret, webhook secret hoặc Stripe secret.
- Mọi lỗi từ Stripe hoặc external service phải có retry-safe handling.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit mỗi phiên, ví dụ: metering, quota, pricing hoặc webhook.
- Nếu test thất bại sau 2 lần, reset về trạng thái sạch và ghi blocker.
- Không refactor ngầm trong lúc làm feature mới; debt phải tách riêng.
