# Capstone - Embeddable Widget & Lead-Capture Platform

> Harness hub cho dự án Embeddable_widget. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop.

## 1. Tóm tắt sản phẩm
- Hệ thống nền tảng cho phép khách hàng tạo các widget thu thập lead (form) và nhúng vào website bất kỳ bằng một thẻ `<script>`.
- Hệ thống backend public phải chịu được các luồng request từ internet, đảm bảo bảo mật và tính sẵn sàng cao.

## 2. Mục tiêu cốt lõi
- **Public API an toàn:** Xử lý Cross-Origin Resource Sharing (CORS) đúng cách.
- **Cách ly dữ liệu:** Đảm bảo Tenant Isolation trong thiết kế cơ sở dữ liệu.
- **Chống lạm dụng (Abuse Protection):** Rate limiting cho mỗi IP và tính năng chặn Spam.
- **Graceful Degradation:** Tích hợp chuỗi Enrichment (Geo) có fallback, và Side effects (Email) không được phép làm đứt gãy luồng ghi dữ liệu chính.
- **Giao nhận bộ mã:** Serve JavaScript bundle và config nhanh chóng qua bộ nhớ đệm (Caching headers).

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
