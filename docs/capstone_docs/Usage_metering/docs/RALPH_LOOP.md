# RALPH_LOOP.md — Quy trình tự động cho Capstone - Usage Metering & Billing Engine

## 1. Chuỗi hoạt động
1. Mở phiên mới và đọc AGENTS, rules và specs.
2. Chọn đúng một item chưa hoàn thành.
3. Implement theo logical unit.
4. Chạy verification và log kết quả.
5. Nếu thành công: commit và đánh dấu done.
6. Nếu thất bại sau 2 lần: reset và ghi blocker.

## 2. Exit code
- 0: success
- 1: retry needed
- 2: blocked

## 3. Logging và status update
- Mỗi iteration phải có log riêng.
- Sau mỗi session thành công, cập nhật WORK_BOARD và specs.
