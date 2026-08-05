# rules.md — Quy tắc phát triển cho Capstone - Embeddable Widget & Lead-Capture Platform

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Không dùng try/except chung chung để nuốt lỗi; phải log lỗi cụ thể với context.
- Mọi request/response phải có validation rõ ràng và tránh dữ liệu thô không kiểm soát.
- Public API phải luôn có CORS, rate limit và error contract chuẩn.

## 2. Quy tắc miền riêng cho dự án
- Widget phải có tenant isolation nghiêm ngặt: tenant A không được xem/sửa widget tenant B.
- Public submission endpoint phải validate input chặt chẽ và trả về 4xx đúng cho lỗi dữ liệu.
- Honeypot và rate limit là bắt buộc để chống spam và abuse.
- IP geolocation phải dùng fallback chain: Provider A -> Provider B -> no location, nhưng submission vẫn lưu thành công.
- Side effects như email/webhook phải là safe side effect: lỗi không làm fail submission.

## 3. Logging & observability
- Log mỗi submission với widget id, request id, IP hash, status, enrichment result và side effect status.
- Không log secret, API key hoặc dữ liệu nhạy cảm thô.
- Mọi lỗi bên ngoài cần có retry/fallback nhưng không làm crash request.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit mỗi phiên, ví dụ: widget CRUD, submission API, abuse protection hoặc dashboard.
- Nếu test thất bại sau 2 lần, reset về trạng thái sạch và ghi blocker.
- Không refactor ngầm trong lúc làm feature mới; debt phải tách riêng.
