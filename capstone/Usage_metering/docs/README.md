# Capstone - Usage Metering & Billing Engine

> Harness hub cho dự án Usage_metering. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop.

## 1. Tóm tắt sản phẩm
- Hệ thống Metering & Billing cho ứng dụng SaaS để tính toán chính xác việc sử dụng tài nguyên (API/AI tokens), chặn quota khi hết giới hạn và đồng bộ gói cước với Stripe.
- Mục tiêu tối thượng của dự án là độ chính xác cực cao (Correctness), tuyệt đối không để xảy ra sai sót double-billing hoặc bỏ qua lỗi logic tính tiền.

## 2. Mục tiêu cốt lõi
- **Exactly-once Metering:** Theo dõi usage idempotent để ngăn chặn ghi nhận trùng lặp dù request có bị gửi lại (retries).
- **Quota Boundaries:** Trả về HTTP Code đúng (429/402) tại giới hạn gói cước theo logic đã định nghĩa.
- **Money Math:** Quy đổi Usage thành Cost chính xác bằng việc sử dụng `Integer` math, phân biệt input token, cached input token, và reasoning token.
- **Safe Stripe Integration (Test Mode):** Đồng bộ webhook Stripe thông qua việc kiểm tra HMAC Signature và loại bỏ webhook trùng lặp.

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
