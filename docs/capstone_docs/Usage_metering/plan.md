# plan.md — Kế hoạch triển khai cho Capstone - Usage Metering & Billing Engine

## 1. Phân tích sản phẩm
Xây dựng engine dùng để ghi nhận usage event, tính quota và tổng tiền theo từng billing rule, đồng thời hỗ trợ báo cáo và reconciliation.

## 2. Phân tầng thực hiện
### Phase A — Foundation
- Xác định schema dữ liệu đầu vào, output, idempotency và trạng thái nghiệp vụ.
- Định nghĩa các API contract cho service chính.
- Thiết lập logging, tracing và error taxonomy.

### Phase B — Core workflow
- Triển khai thành phần nghiệp vụ chính: Event Collector: nhận usage event từ client/service, Metering Service: aggregate theo tenant, plan và time window.
- Đảm bảo flow xử lý từ đầu vào đến kết quả đầu ra có thể test được.
- Tách middleware cho validation, retry và non-blocking notification.

### Phase C — Delivery and monitoring
- Tạo endpoint/UX và report layer cho người dùng/ops.
- Thêm audit log, health checks và alerting cho lỗi publish/billing/ingest.
- Viết verification checklist trước khi commit.

## 3. Các logical unit cần ưu tiên
- [ ] Định nghĩa schema event usage và billing rule
- [ ] Triển khai aggregation và quota calculation
- [ ] Tạo endpoint báo cáo usage và invoice preview
- [ ] Thêm audit trail và retry-safe billing job
- [ ] Cung cấp cảnh báo cho overage và plan renewal

## 4. Done definition
- [ ] Code đã chạy smoke test hoặc unit test phù hợp.
- [ ] Tài liệu và spec được cập nhật.
- [ ] Commit có verification rõ ràng.
