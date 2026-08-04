# prompt.md — Prompt chuẩn cho phiên làm việc mới

Hãy làm việc như một AI engineer trong dự án Capstone - Embeddable Widget & Lead-Capture Platform.

Yêu cầu:
1. Đọc [AGENTS.md](AGENTS.md), [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md).
2. Chọn đúng một mục chưa hoàn thành trong checklist.
3. Implement theo logical unit, không làm nhiều feature cùng lúc.
4. Sau khi viết code, chạy verification test/smoke check và ghi kết quả.
5. Nếu thành công thì đánh dấu checklist và commit; nếu không thì ghi blocker vào [docs/BLOCKED.md](docs/BLOCKED.md).

Context dự án:
- Xây dựng một widget JS có thể nhúng vào website bất kỳ, thu thập lead qua form, ghi lại sự kiện và chuyển dữ liệu sang backend/CRM.
- Các domain chính: widget_config, campaign, lead, event_log, webhook_delivery
- Rủi ro cần kiểm tra: Script bị chặn bởi CSP hoặc third-party blockers, Khả năng tương thích trên nhiều website, Nhạy cảm với dữ liệu người dùng và GDPR
