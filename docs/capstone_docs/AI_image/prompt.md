# prompt.md — Prompt chuẩn cho phiên làm việc mới

Hãy làm việc như một AI engineer trong dự án Capstone - AI Image Understanding & Content Matching Engine.

Yêu cầu:
1. Đọc [AGENTS.md](AGENTS.md), [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md).
2. Chọn đúng một mục chưa hoàn thành trong checklist.
3. Implement theo logical unit, không làm nhiều feature cùng lúc.
4. Sau khi viết code, chạy verification test/smoke check và ghi kết quả.
5. Nếu thành công thì đánh dấu checklist và commit; nếu không thì ghi blocker vào [docs/BLOCKED.md](docs/BLOCKED.md).

Context dự án:
- Xây dựng pipeline nhận ảnh, trích xuất metadata và ngữ nghĩa, tạo embedding cho nội dung hình ảnh, rồi cho phép tìm kiếm/so khớp và ranking kết quả.
- Các domain chính: image_asset, ocr_result, embedding_vector, match_result, review_feedback
- Rủi ro cần kiểm tra: Độ chính xác OCR trên ảnh chất lượng thấp, Chi phí inference vision model, Nhập liệu không đồng nhất từ nhiều nguồn
