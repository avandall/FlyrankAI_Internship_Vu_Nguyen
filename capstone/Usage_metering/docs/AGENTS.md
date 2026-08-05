# AGENTS.md — Constitution cho dự án Usage Metering & Billing Engine

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Phải đảm bảo tính chính xác tuyệt đối trong mọi thay đổi liên quan đến tính toán Cost và lưu Usage Event.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [rules.md](rules.md), [plan.md](plan.md), [architecture.md](architecture.md) và [specs.md](specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một phase/item từ [WORK_BOARD.md](WORK_BOARD.md) mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [WORK_BOARD.md](WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [BLOCKED.md](BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách nợ kỹ thuật xử lý riêng.

## Hướng dẫn cho dự án này
- **Domain chính:** Usage Metering & Billing Engine, đảm bảo hệ thống SaaS có thể track bill, chặn quota và đồng bộ với Stripe (test mode).
- **Các thành phần ưu tiên:** 
  - **Exactly-once Metering:** Chặn tuyệt đối hiện tượng double-counting khi API retry bằng cách sử dụng `idempotency_key` lưu trực tiếp làm ràng buộc trong DB.
  - **Boundary Honesty:** Đếm chính xác quota API/AI token; khi chạm ngưỡng giới hạn (quota exceeded), phải báo `429` (nếu là Free) hoặc `402` (nếu là Pro).
  - **Token Cost Math:** Xử lý logic cộng trừ giá token AI với hằng số cấu hình. Tính toán Cost BẮT BUỘC sử dụng kiểu `Integer` (đơn vị micro-cents/cents).
  - **Stripe Webhook Sync:** Nhận webhook từ Stripe, kiểm tra chữ ký (`stripe-signature`), chặn event trùng (deduplication) rồi mới cập nhật DB.
- **Rủi ro cần cảnh giác:** Sai số thập phân khi tính tiền (float math error); Tính 2 lần (double-charge) do thiếu `idempotency_key`; Không verify chữ ký Stripe Webhook.
