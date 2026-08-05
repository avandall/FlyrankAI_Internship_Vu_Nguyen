# Capstone - Multi-Platform Social Campaign Publisher

> Harness hub cho dự án Multi_platform. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop.

## 1. Tóm tắt sản phẩm
- Hệ thống backend bền bỉ (durable) biến một blog post thành một chiến dịch mạng xã hội trên nhiều nền tảng khác nhau.
- Đây là bài kiểm tra về kỹ năng xây dựng hệ thống chịu lỗi (Reliability engineering), không phải là bài toán gọi API thông thường. 

## 2. Mục tiêu cốt lõi
- **Kiến trúc Adapter (Adapter pattern):** Core application không bị phụ thuộc rò rỉ vào bất kỳ API của mạng xã hội cụ thể nào.
- **Tính lũy đẳng (Idempotency):** Worker retries không bao giờ tạo ra post bị trùng (double-posting).
- **Tôn trọng Rate Limit:** Bắt và xử lý mượt mà lỗi 429 cùng header `Retry-After`.
- **Durable Scheduling:** Background worker phải có khả năng tự phục hồi nếu bị crash mid-batch.
- **Bảo mật:** Verify webhook signature bằng HMAC, và lưu trữ OAuth tokens dạng mã hóa có IV ngẫu nhiên.

## 3. Các tài liệu chính
- [README.md](README.md): điểm vào cho toàn bộ harness.
- [AGENTS.md](AGENTS.md): luật vận hành cho AI agent.
- [plan.md](plan.md): kế hoạch triển khai và phân tầng thực hiện.
- [architecture.md](architecture.md): kiến trúc hệ thống và luồng dữ liệu.
- [specs.md](specs.md): đặc tả kỹ thuật, schema, và API endpoints.
- [rules.md](rules.md): quy định coding, logging và commit.
- [WORK_BOARD.md](WORK_BOARD.md): bảng trạng thái công việc (TODO, DONE).
- [TECH_DEBT.md](TECH_DEBT.md): nợ kỹ thuật và rủi ro.
- [BLOCKED.md](BLOCKED.md): log blocker và handbrake.
- [RALPH_LOOP.md](RALPH_LOOP.md): quy trình build-test-fix.

## 4. Luồng làm việc đề xuất
1. Đọc [AGENTS.md](AGENTS.md) và [rules.md](rules.md).
2. Chọn một item chưa hoàn thành từ [WORK_BOARD.md](WORK_BOARD.md).
3. Tham chiếu [architecture.md](architecture.md) và [specs.md](specs.md) để implement.
4. Xây dựng logic, chạy verification, ghi log và commit nếu thành công.
5. Nếu bị chặn, cập nhật [BLOCKED.md](BLOCKED.md) và dừng lại để human can thiệp.
