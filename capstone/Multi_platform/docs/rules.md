# rules.md — Quy tắc phát triển cho Capstone - Multi-Platform Publisher

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Mọi logic liên quan đến network/API (gọi external server) đều phải được bọc trong block xử lý lỗi và retry.

## 2. Quy tắc miền riêng cho dự án Multi-Platform Publisher
- **Bảo vệ Adapter Layer:** Code chính (business logic/queue worker) không bao giờ được phép có lệnh `if platform == 'instagram'`. Mọi logic riêng biệt phải được giấu bên trong Adapter implement `SocialPublisher` interface.
- **Quy tắc Idempotency:** Trong mọi request `publish()`, bắt buộc phải tạo và truyền `idempotency_key` lên server.
- **Xử lý Rate Limit:** Không được phớt lờ lỗi `429`. Khi gặp lỗi này, queue worker phải đọc `Retry-After` header và reschedule job thay vì đánh dồn dập vào API.
- **Bảo mật tuyệt đối:** OAuth tokens lưu trong database PHẢI ĐƯỢC encrypt (AES-GCM) kèm IV ngẫu nhiên lưu cùng. Webhook payload PHẢI được verify HMAC signature trước khi cập nhật dữ liệu. Không verify = không trust = `400 Bad Request`.

## 3. Logging & Observability
- Ghi log rõ ràng cho các sự kiện: Enqueue, Publish Attempt, Timeout/Retry, Webhook Received, Signature Validation Failed.
- Che (mask) toàn bộ các phần rò rỉ của token/secrets trong quá trình ghi log.

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
