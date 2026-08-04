# prompt.md — Prompt chuẩn cho phiên làm việc mới

Hãy làm việc như một AI engineer trong dự án Capstone - Usage Metering & Billing Engine.

Yêu cầu:
1. Đọc [AGENTS.md](AGENTS.md), [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md).
2. Chọn đúng một mục chưa hoàn thành trong checklist.
3. Implement theo logical unit, không làm nhiều feature cùng lúc.
4. Sau khi viết code, chạy verification test/smoke check và ghi kết quả.
5. Nếu thành công thì đánh dấu checklist và commit; nếu không thì ghi blocker vào [docs/BLOCKED.md](docs/BLOCKED.md).

Context dự án:
- Xây dựng engine dùng để ghi nhận usage event, tính quota và tổng tiền theo từng billing rule, đồng thời hỗ trợ báo cáo và reconciliation.
- Các domain chính: usage_event, metering_window, plan_rule, invoice, billing_audit
- Rủi ro cần kiểm tra: Sai lệch đếm usage do event trùng hoặc bỏ sót, Phức tạp khi có nhiều plan và discount rule, Yêu cầu reconcile đúng thời điểm billing
