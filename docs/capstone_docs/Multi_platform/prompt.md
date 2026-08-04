# prompt.md — Prompt chuẩn cho phiên làm việc mới

Hãy làm việc như một AI engineer trong dự án Capstone - Multi-Platform Social Campaign Publisher.

Yêu cầu:
1. Đọc [AGENTS.md](AGENTS.md), [docs/rules.md](docs/rules.md) và [docs/specs.md](docs/specs.md).
2. Chọn đúng một mục chưa hoàn thành trong checklist.
3. Implement theo logical unit, không làm nhiều feature cùng lúc.
4. Sau khi viết code, chạy verification test/smoke check và ghi kết quả.
5. Nếu thành công thì đánh dấu checklist và commit; nếu không thì ghi blocker vào [docs/BLOCKED.md](docs/BLOCKED.md).

Context dự án:
- Xây dựng hệ thống giúp tạo bản nội dung, biến đổi theo từng nền tảng, lên lịch đăng, review và theo dõi trạng thái publish.
- Các domain chính: campaign, content_variant, platform_adapter, schedule_job, publish_event
- Rủi ro cần kiểm tra: Khác biệt format và giới hạn từng nền tảng, Publish event có thể trễ hoặc fail, Cần kiểm soát approval và bản quyền nội dung
