# AGENTS.md — Constitution cho dự án Usage_metering

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
- Domain chính: Engine đo usage, quota và billing
- Các thành phần cần ưu tiên: Event Collector: nhận usage event từ client/service, Metering Service: aggregate theo tenant, plan và time window, Pricing Rules: tính phí và overage, Billing Service: tạo invoice preview và post-billing events, Reconciliation & Audit: theo dõi mismatch và failed invoice jobs
- Rủi ro cần cảnh giác: Sai lệch đếm usage do event trùng hoặc bỏ sót, Phức tạp khi có nhiều plan và discount rule, Yêu cầu reconcile đúng thời điểm billing
