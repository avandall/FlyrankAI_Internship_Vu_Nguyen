# AGENTS.md — Constitution cho dự án Embeddable Widget

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Không tự ý đổi architecture, schema chính hoặc thiết lập bỏ qua bảo mật (ví dụ tắt CORS, tắt rate limit) nếu chưa có approval.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [rules.md](rules.md), [plan.md](plan.md), [architecture.md](architecture.md) và [specs.md](specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một phase/item từ [WORK_BOARD.md](WORK_BOARD.md) mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [WORK_BOARD.md](WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [BLOCKED.md](BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách nợ kỹ thuật xử lý riêng.

## Hướng dẫn cho dự án này
- **Domain chính:** Nền tảng Widget nhúng (Embeddable Widget & Lead-Capture) tiếp nhận public request từ internet.
- **Các thành phần ưu tiên:** 
  - **Widget Delivery:** Serve script và config qua CDN pattern (cached, public, versioned).
  - **Submission Endpoint:** Phải chịu tải từ public origin, có CORS chuẩn (kể cả preflight).
  - **Abuse Protection:** Bắt buộc có Rate Limiting (chặn IP spam với lỗi 429) và Honeypot spam control.
  - **Graceful Degradation:** Chuỗi Enrichment (Geo IP A -> B) và Safe side effects (Email); nếu fail cũng KHÔNG làm rớt request chính của khách.
- **Rủi ro cần cảnh giác:** Mở CORS bừa bãi; Trust payload từ client; Lỗi phụ (như gửi email) làm rớt việc lưu DB.
