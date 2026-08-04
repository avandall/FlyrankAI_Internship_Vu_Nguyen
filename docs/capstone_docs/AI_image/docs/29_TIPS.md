# 29_TIPS.md — Cẩm nang vận hành cho Capstone - AI Image Understanding & Content Matching Engine

## 1. Tập trung vào product contract
- Đảm bảo API/behavior của feature khớp với yêu cầu nghiệp vụ.
- Không thêm layer phức tạp mà không có nhu cầu rõ ràng.

## 2. Tài liệu phải đi cùng code
- Khi thay đổi workflow, cập nhật [docs/architecture.md](architecture.md) và [docs/specs.md](specs.md).

## 3. Verification không thể bỏ qua
- Sau mỗi thay đổi, chạy smoke test hoặc unit test cho logic cốt lõi.
- Nếu có service ngoài, kiểm tra timeout, retry và fallback.

## 4. Khi gặp blocker
- Dừng, ghi chi tiết vào [docs/BLOCKED.md](BLOCKED.md), không lặp vô hạn.

## 5. Dự án cụ thể
- Domain chính: Hệ thống hiểu hình ảnh, trích xuất ý nghĩa và so khớp nội dung
- Rủi ro cần ưu tiên trong loop: Độ chính xác OCR trên ảnh chất lượng thấp, Chi phí inference vision model, Nhập liệu không đồng nhất từ nhiều nguồn
