# ralph_loop_guide.md — Hướng dẫn chạy Ralph Loop cho Capstone - Usage Metering & Billing Engine

## Mục tiêu
Tự động hóa vòng lặp phát triển bằng các bước: đọc spec -> implement -> verify -> commit/block.

## Chuỗi thực hiện
1. Mở phiên mới và đọc [AGENTS.md](AGENTS.md).
2. Chọn đúng một checklist chưa hoàn thành từ [docs/specs.md](docs/specs.md).
3. Cập nhật hoặc bổ sung tài liệu nếu task làm ảnh hưởng đến architecture/rules.
4. Viết code và chạy smoke test.
5. Nếu pass, đánh dấu done; nếu fail, reset và ghi blocker.

## Cảnh báo riêng cho dự án
- Sai lệch đếm usage do event trùng hoặc bỏ sót
- Phức tạp khi có nhiều plan và discount rule
- Yêu cầu reconcile đúng thời điểm billing
