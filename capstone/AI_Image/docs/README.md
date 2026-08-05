# Capstone - AI Image Understanding & Content Matching Engine

> Harness hub cho dự án AI_Image. Đây là bộ tài liệu vận hành cho Ralph Loop, tập trung vào product goals, implementation plan và verification loop cho dự án này.

## 1. Tóm tắt sản phẩm
- Xây dựng hệ thống tự động hiểu thư viện hình ảnh và so khớp ảnh phù hợp nhất cho bài viết blog.
- Yêu cầu AI hoạt động đáng tin cậy ở môi trường production: đưa ra gợi ý tốt khi độ tự tin cao và từ chối an toàn (kèm lý do) khi có sự sai lệch (Mismatch).

## 2. Mục tiêu cốt lõi
- Xử lý hình ảnh qua Vision API bằng background job, trích xuất siêu dữ liệu JSON có cấu trúc (validated).
- Nhúng (embed) nội dung ảnh và bài viết để tìm kiếm ngữ nghĩa (Semantic search).
- Xây dựng **Mismatch Guard** kết hợp tags, similarity threshold và confidence score để ngăn chặn gợi ý sai.
- Tracking API costs cho mọi lời gọi AI.

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
