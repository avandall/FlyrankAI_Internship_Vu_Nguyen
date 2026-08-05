# AGENTS.md — Constitution cho dự án Multi_platform

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
- Domain chính: Hệ thống xuất bản chiến dịch đa nền tảng
- Các thành phần cần ưu tiên: Campaign Planner: định nghĩa message, assets, target audience, Content Adapter: chuyển nội dung sang định dạng từng nền tảng, Scheduler: lên lịch publish theo timezone, Publisher Adapters: wrapper cho từng kênh, Audit Layer: log, approval, retry và status tracking
- Rủi ro cần cảnh giác: Khác biệt format và giới hạn từng nền tảng, Publish event có thể trễ hoặc fail, Cần kiểm soát approval và bản quyền nội dung
