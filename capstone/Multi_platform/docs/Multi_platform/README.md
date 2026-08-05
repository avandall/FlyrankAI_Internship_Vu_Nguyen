# Capstone - Multi-Platform Social Campaign Publisher

> Harness hub cho dự án Multi_platform. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop cho dự án này.

## 1. Tóm tắt sản phẩm
- Hệ thống xuất bản chiến dịch đa nền tảng
- Xây dựng hệ thống giúp tạo bản nội dung, biến đổi theo từng nền tảng, lên lịch đăng, review và theo dõi trạng thái publish.

## 2. Mục tiêu cốt lõi
- Tạo campaign và draft nội dung theo template
- Biến đổi nội dung cho từng nền tảng như Instagram, X, LinkedIn, Facebook
- Lên lịch publish và theo dõi state approval
- Cung cấp audit log và rollback khi publish thất bại

## 3. Các tài liệu chính
- [README.md](README.md): điểm vào cho toàn bộ harness.
- [AGENTS.md](AGENTS.md): luật vận hành cho AI agent.
- [plan.md](plan.md): kế hoạch triển khai và phân tầng thực hiện.
- [prompt.md](prompt.md): prompt chuẩn cho agent làm việc trong phiên mới.
- [docs/architecture.md](docs/architecture.md): kiến trúc hệ thống và mapping sang code.
- [docs/rules.md](docs/rules.md): quy định coding, logging và commit.
- [docs/specs.md](docs/specs.md): backlog theo logical unit và checklist done.
- [docs/WORK_BOARD.md](docs/WORK_BOARD.md): trạng thái làm việc.
- [docs/TECH_DEBT.md](docs/TECH_DEBT.md): nợ kỹ thuật và rủi ro.
- [docs/BLOCKED.md](docs/BLOCKED.md): log blocker và handbrake.
- [docs/RALPH_LOOP.md](docs/RALPH_LOOP.md): quy trình build-test-fix.
- [ralph_loop_guide.md](ralph_loop_guide.md): hướng dẫn vận hành vòng lặp hàng ngày.

## 4. Luồng làm việc đề xuất
1. Đọc [AGENTS.md](AGENTS.md) và [docs/rules.md](docs/rules.md).
2. Chọn một item chưa hoàn thành từ [docs/specs.md](docs/specs.md).
3. Xây dựng logic, chạy verification, ghi log và commit nếu thành công.
4. Nếu bị chặn, cập nhật [docs/BLOCKED.md](docs/BLOCKED.md) và dừng lại để human can thiệp.

## 5. Vùng làm việc chính
- Thư mục dự án hiện tại: [capstone/Multi_platform](../../capstone/Multi_platform)
- Tài liệu tham khảo: [docs/capstone_docs](../../docs/capstone_docs)
