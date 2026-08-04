# plan.md — Kế hoạch triển khai cho Capstone - Multi-Platform Social Campaign Publisher

## 1. Phân tích sản phẩm
Xây dựng hệ thống giúp tạo bản nội dung, biến đổi theo từng nền tảng, lên lịch đăng, review và theo dõi trạng thái publish.

## 2. Phân tầng thực hiện
### Phase A — Foundation
- Xác định schema dữ liệu đầu vào, output, idempotency và trạng thái nghiệp vụ.
- Định nghĩa các API contract cho service chính.
- Thiết lập logging, tracing và error taxonomy.

### Phase B — Core workflow
- Triển khai thành phần nghiệp vụ chính: Campaign Planner: định nghĩa message, assets, target audience, Content Adapter: chuyển nội dung sang định dạng từng nền tảng.
- Đảm bảo flow xử lý từ đầu vào đến kết quả đầu ra có thể test được.
- Tách middleware cho validation, retry và non-blocking notification.

### Phase C — Delivery and monitoring
- Tạo endpoint/UX và report layer cho người dùng/ops.
- Thêm audit log, health checks và alerting cho lỗi publish/billing/ingest.
- Viết verification checklist trước khi commit.

## 3. Các logical unit cần ưu tiên
- [ ] Định nghĩa model campaign và draft content
- [ ] Triển khai adapter cho từng nền tảng publishing
- [ ] Tạo scheduler và trạng thái approval workflow
- [ ] Thêm audit log và retry policy cho publish thất bại
- [ ] Cung cấp dashboard trạng thái thực thi chiến dịch

## 4. Done definition
- [ ] Code đã chạy smoke test hoặc unit test phù hợp.
- [ ] Tài liệu và spec được cập nhật.
- [ ] Commit có verification rõ ràng.
