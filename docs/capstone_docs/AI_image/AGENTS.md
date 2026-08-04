# AGENTS.md — Constitution cho dự án AI_image

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Không tự ý đổi architecture, API contract hoặc schema chính nếu chưa có approval.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một item từ checklist mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [docs/WORK_BOARD.md](docs/WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [docs/BLOCKED.md](docs/BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách debt xử lý riêng.

## Hướng dẫn cho dự án này
- Domain chính: Hệ thống hiểu hình ảnh, trích xuất ý nghĩa và so khớp nội dung
- Các thành phần cần ưu tiên: Ingestion Service: nhận file từ upload hoặc batch job, Preprocess: resize, normalize, metadata extraction, Vision/OCR Layer: OCR, captioning, object detection, Embedding Layer: vector representation và indexing, Search API: query by image/text, trả top-k results, scores, Review Queue: đánh dấu false positive và feedback loop
- Rủi ro cần cảnh giác: Độ chính xác OCR trên ảnh chất lượng thấp, Chi phí inference vision model, Nhập liệu không đồng nhất từ nhiều nguồn
