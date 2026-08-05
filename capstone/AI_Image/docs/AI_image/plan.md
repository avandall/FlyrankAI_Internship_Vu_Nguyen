# plan.md — Kế hoạch triển khai cho Capstone - AI Image Understanding & Content Matching Engine

## 1. Phân tích sản phẩm
Xây dựng pipeline nhận ảnh, trích xuất metadata và ngữ nghĩa, tạo embedding cho nội dung hình ảnh, rồi cho phép tìm kiếm/so khớp và ranking kết quả.

## 2. Phân tầng thực hiện
### Phase A — Foundation
- Xác định schema dữ liệu đầu vào, output, idempotency và trạng thái nghiệp vụ.
- Định nghĩa các API contract cho service chính.
- Thiết lập logging, tracing và error taxonomy.

### Phase B — Core workflow
- Triển khai thành phần nghiệp vụ chính: Ingestion Service: nhận file từ upload hoặc batch job, Preprocess: resize, normalize, metadata extraction.
- Đảm bảo flow xử lý từ đầu vào đến kết quả đầu ra có thể test được.
- Tách middleware cho validation, retry và non-blocking notification.

### Phase C — Delivery and monitoring
- Tạo endpoint/UX và report layer cho người dùng/ops.
- Thêm audit log, health checks và alerting cho lỗi publish/billing/ingest.
- Viết verification checklist trước khi commit.

## 3. Các logical unit cần ưu tiên
- [ ] Xây dựng pipeline ingest ảnh và lưu metadata chuẩn
- [ ] Triển khai OCR/vision extraction với fallback và retry policy
- [ ] Tạo embedding cho hình ảnh và xây dựng similarity search
- [ ] Cung cấp endpoint so khớp nội dung và scoring
- [ ] Thêm review workflow và logging chất lượng cho mỗi lần match

## 4. Done definition
- [ ] Code đã chạy smoke test hoặc unit test phù hợp.
- [ ] Tài liệu và spec được cập nhật.
- [ ] Commit có verification rõ ràng.
