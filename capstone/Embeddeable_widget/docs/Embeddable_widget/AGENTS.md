# AGENTS.md — Constitution cho dự án Embeddable_widget

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Không tự ý đổi architecture, API contract hoặc schema chính nếu chưa có approval.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một item từ checklist mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [docs/WORK_BOARD.md](docs/WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [docs/BLOCKED.md](docs/BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách debt xử lý riêng.

## Hướng dẫn cho dự án này
- Domain chính: Widget nhúng được và hệ thống thu thập lead
- Các thành phần cần ưu tiên: Widget Loader: tải script và cấu hình từ server, UI Layer: modal, banner, inline form, Event Tracking: click/submit/abandon analytics, Lead API: lưu lead, normalize dữ liệu, gửi webhook, Notification Layer: email/slack/webhook cho lead mới, Privacy Layer: consent, hashing và dữ liệu tối thiểu
- Rủi ro cần cảnh giác: Script bị chặn bởi CSP hoặc third-party blockers, Khả năng tương thích trên nhiều website, Nhạy cảm với dữ liệu người dùng và GDPR
