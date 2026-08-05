# Project Queue

File này là nguồn theo dõi chung cho toàn bộ chuỗi capstone projects. AI cần đọc file này trước khi bắt đầu session để biết project nào đang được ưu tiên, project nào đã hoàn tất, và project nào cần làm tiếp.

## Quy tắc sử dụng
- Mỗi session chỉ làm một project.
- Chỉ chuyển sang project tiếp theo sau khi project hiện tại đã được verify và handoff xong.
- Nếu project bị block, ghi rõ blocker và không tự chuyển sang project khác cho đến khi có hướng dẫn.
- Implement dự án trực tiếp vào capstone/Tênproject tách rời mỗi dự án theo folder tạo sẵn.

## Danh sách project
- Trong capstone có 4 thư mục project tương ứng, mỗi thư mục đã có docs để đọc:
- [x] AI_image — capstone/AI_Image — Status: refactored ✅ — Postgres + pgvector/JSONB, real Groq Vision AI, Ollama Embeddings, Redis Background jobs, Dark Mode UI
- [x] Embeddable_widget — capstone/Embeddeable_widget — Status: refactored ✅ — Postgres, Async GeoIP, Redis Rate Limiting, Cross-origin Widget
- [x] Multi_platform — capstone/Multi_platform — Status: refactored ✅ — Postgres, Async/Await, Redis Durable Scheduler, Async Webhooks
- [x] Usage_metering — capstone/Usage_metering — Status: refactored ✅ — Postgres + Transactions, Integer Cost math, Idempotency, Stripe Async HMAC

## Cập nhật trạng thái
Khi một project hoàn thành hoặc bị block, cập nhật checklist theo mẫu:
- [x] Project đã hoàn tất
- [ ] Project vẫn đang chờ
- [/] Project đang làm hiện tại
- [!] Project bị block

Ví dụ:
- [/] AI_image — capstone/AI_image — Status: in-progress — Next: implement next task
- [x] Embeddable_widget — capstone/Embeddable_widget — Status: completed — Next: done
- [!] Multi_platform — capstone/Multi_platform — Status: blocked — Next: wait for clarification

## Handoff mẫu
```md
## Handoff
- Project: <tên project>
- Status: completed / blocked / partial
- Verified evidence: <command và kết quả>
- Next project: <project tiếp theo>
```
