# rules.md — Quy tắc phát triển cho Capstone - Embeddable Widget

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Mọi dữ liệu đầu vào (từ Public API) phải bị coi là untrusted và phải được schema validation cẩn thận.
- Các API trả về mã lỗi rõ ràng: `400` cho input sai, `429` cho rate limit, không bao giờ lộ `500` cho người dùng public.

## 2. Quy tắc miền riêng cho dự án Embeddable Widget
- **CORS Configuration:** Cực kỳ quan trọng. Preflight (`OPTIONS`) phải trả về headers đúng, không wildcard `*` cho các method/header quan trọng nếu không cần thiết.
- **Tenant Isolation:** Mọi query tới database trong Owner API PHẢI có kèm filter `tenant_id`.
- **Graceful Degradation:** Khi gọi External APIs (như Geo IP hoặc Email server), PHẢI bọc trong try/catch hoặc timeout. Nếu nó sập, main path (lưu form submission vào database) VẪN PHẢI THÀNH CÔNG.
- **Chống Spam & Rate Limit:** Bắt buộc áp dụng trước khi dữ liệu chạm tới database access layer.

## 3. Logging & Observability
- Log cảnh báo nếu rate limiter bị chạm ngưỡng (`429`).
- Log thông tin về fallback (ví dụ "Geo provider A failed, falling back to B").
- Không log các dữ liệu nhạy cảm hoặc PII nguyên bản từ payload.

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
