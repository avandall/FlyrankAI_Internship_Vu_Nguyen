# TECH_DEBT.md — Nợ kỹ thuật cho Capstone - Multi-Platform Social Campaign Publisher

## 1. Các khoản nợ cần chú ý
| ID | Component | Mô tả | Status |
| :--- | :--- | :--- | :--- |
| DEBT-01 | Schema design | Có thể thay đổi khi tích hợp thực tế | OPEN |
| DEBT-02 | Logging | Cần thống nhất format và tracing | OPEN |
| DEBT-03 | Retry policy | Cần cấu hình rõ cho integration ngoài | OPEN |

## 2. Quy tắc xử lý
- Không refactor khi đang làm feature mới.
- Nếu phát hiện constraint lịch sử, ghi rõ và không sửa ngầm.
- Mỗi debt item phải có owner hoặc explicit next action.
