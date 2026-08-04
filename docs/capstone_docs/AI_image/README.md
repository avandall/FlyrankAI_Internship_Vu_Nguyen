# Capstone - AI Image Understanding & Content Matching Engine

> Harness hub cho dự án AI_image. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop cho dự án này.

## 1. Tóm tắt sản phẩm
- Hệ thống hiểu hình ảnh, trích xuất ý nghĩa và so khớp nội dung
- Xây dựng pipeline nhận ảnh, trích xuất metadata và ngữ nghĩa, tạo embedding cho nội dung hình ảnh, rồi cho phép tìm kiếm/so khớp và ranking kết quả.

## 2. Mục tiêu cốt lõi
- Nhận diện và chuẩn hóa hình ảnh đầu vào từ nhiều nguồn
- Trích xuất OCR, caption, tags và metadata ngữ cảnh
- Tạo embedding vector và thực hiện similarity search
- Cung cấp API và UI để xem kết quả matching cùng confidence score

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
- Thư mục dự án hiện tại: [capstone/AI_image](../../capstone/AI_image)
- Tài liệu tham khảo: [docs/capstone_docs](../../docs/capstone_docs)
