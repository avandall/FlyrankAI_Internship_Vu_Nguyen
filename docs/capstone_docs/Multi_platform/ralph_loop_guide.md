# ralph_loop_guide.md — Hướng dẫn chạy Ralph Loop cho Capstone - Multi-Platform Social Campaign Publisher

## Mục tiêu
Tự động hóa vòng lặp phát triển bằng các bước: đọc spec -> implement -> verify -> commit/block.

## Chuỗi thực hiện
1. Mở phiên mới và đọc [AGENTS.md](AGENTS.md).
2. Chọn đúng một checklist chưa hoàn thành từ [docs/specs.md](docs/specs.md).
3. Cập nhật hoặc bổ sung tài liệu nếu task làm ảnh hưởng đến architecture/rules.
4. Viết code và chạy smoke test.
5. Nếu pass, đánh dấu done; nếu fail, reset và ghi blocker.

## Cảnh báo riêng cho dự án
- Khác biệt format và giới hạn từng nền tảng
- Publish event có thể trễ hoặc fail
- Cần kiểm soát approval và bản quyền nội dung
