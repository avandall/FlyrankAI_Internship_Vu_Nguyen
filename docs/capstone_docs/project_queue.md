# Project Queue

File này là nguồn theo dõi chung cho toàn bộ chuỗi capstone projects. AI cần đọc file này trước khi bắt đầu session để biết project nào đang được ưu tiên, project nào đã hoàn tất, và project nào cần làm tiếp.

## Quy tắc sử dụng
- Mỗi session chỉ làm một project.
- Chỉ chuyển sang project tiếp theo sau khi project hiện tại đã được verify và handoff xong.
- Nếu project bị block, ghi rõ blocker và không tự chuyển sang project khác cho đến khi có hướng dẫn.

## Danh sách project
- [ ] AI_image — capstone/AI_image — Status: pending — Next: start implementation loop
- [ ] Embeddable_widget — capstone/Embeddable_widget — Status: pending — Next: wait for prior project completion
- [ ] Multi_platform — capstone/Multi_platform — Status: pending — Next: wait for prior project completion
- [ ] Usage_metering — capstone/Usage_metering — Status: pending — Next: wait for prior project completion

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
