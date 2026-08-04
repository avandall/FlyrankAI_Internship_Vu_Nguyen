# plan.md — Kế hoạch triển khai cho Capstone - Embeddable Widget & Lead-Capture Platform

## 1. Phân tích sản phẩm
Xây dựng một widget JS có thể nhúng vào website bất kỳ, thu thập lead qua form, ghi lại sự kiện và chuyển dữ liệu sang backend/CRM.

## 2. Phân tầng thực hiện
### Phase A — Foundation
- Xác định schema dữ liệu đầu vào, output, idempotency và trạng thái nghiệp vụ.
- Định nghĩa các API contract cho service chính.
- Thiết lập logging, tracing và error taxonomy.

### Phase B — Core workflow
- Triển khai thành phần nghiệp vụ chính: Widget Loader: tải script và cấu hình từ server, UI Layer: modal, banner, inline form.
- Đảm bảo flow xử lý từ đầu vào đến kết quả đầu ra có thể test được.
- Tách middleware cho validation, retry và non-blocking notification.

### Phase C — Delivery and monitoring
- Tạo endpoint/UX và report layer cho người dùng/ops.
- Thêm audit log, health checks và alerting cho lỗi publish/billing/ingest.
- Viết verification checklist trước khi commit.

## 3. Các logical unit cần ưu tiên
- [ ] Thiết kế widget script và cấu hình nhúng
- [ ] Triển khai form capture với validation và honeypot
- [ ] Ghi nhận event tracking và conversion funnel
- [ ] Tạo API lưu lead và gửi webhook cho CRM
- [ ] Thêm privacy-safe logging và consent handling

## 4. Done definition
- [ ] Code đã chạy smoke test hoặc unit test phù hợp.
- [ ] Tài liệu và spec được cập nhật.
- [ ] Commit có verification rõ ràng.
