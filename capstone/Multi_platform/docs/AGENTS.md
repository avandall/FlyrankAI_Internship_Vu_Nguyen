# AGENTS.md — Constitution cho dự án Multi-Platform Social Campaign Publisher

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Không tự ý đổi architecture (như phá vỡ Adapter pattern) hoặc bỏ qua bảo mật (OAuth token encryption, Webhook Signature Verification) nếu chưa có approval.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [rules.md](rules.md), [plan.md](plan.md), [architecture.md](architecture.md) và [specs.md](specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một phase/item từ [WORK_BOARD.md](WORK_BOARD.md) mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [WORK_BOARD.md](WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [BLOCKED.md](BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách nợ kỹ thuật xử lý riêng.

## Hướng dẫn cho dự án này
- **Domain chính:** Nền tảng xuất bản chiến dịch mạng xã hội (Multi-Platform Publisher) có tính bền bỉ và xử lý background an toàn.
- **Các thành phần ưu tiên:** 
  - **Adapter Architecture:** `SocialPublisher` interface và nhiều implementation (Instagram, X). Core app không bao giờ biết chi tiết của từng platform.
  - **Durable Scheduling & Idempotency:** Queue worker phải chịu được crash mid-batch. Retry timeout không bao giờ được tạo ra duplicate post (dùng idempotency key).
  - **Rate Limit Handling:** Tôn trọng `429` và `Retry-After`, worker phải backoff thay vì spam API.
  - **Webhook Trust:** Chỉ đổi trạng thái campaign sang "published" nếu Webhook payload pass bước xác thực HMAC SHA256 signature.
- **Rủi ro cần cảnh giác:** Lưu token dạng plaintext; Double-posting khi mạng chập chờn; Tin tưởng webhook mà không xác thực chữ ký.
