# WORK_BOARD.md — Bảng trạng thái cho Capstone - Embeddable Widget

## ✅ DONE
- [x] Khởi tạo harness docs, architecture, specs, và plan cho dự án.

## 🟣 READY FOR REVIEW
- Chưa có unit nào hoàn thành.

## 🟡 IN PROGRESS
- Chưa có task đang chạy.

## 🔴 TODO
- [ ] **Phase 1: Design & API Setup** - Xây dựng DB (Tenants, Widgets, Submissions) đảm bảo tenant isolation; Viết Management API CRUD cơ bản.
- [ ] **Phase 2: Delivery & Config** - Tạo public endpoint serve widget JS và config nhỏ với Cache-Control chuẩn (max-age, public).
- [ ] **Phase 3: The Hardened Submission API** - Xây dựng endpoint nhận submission: cấu hình CORS, Payload Validation.
- [ ] **Phase 4: Abuse Protection** - Tích hợp Rate Limiting (429) và Spam Control (Honeypot).
- [ ] **Phase 5: Degradation & Side Effects** - Code chuỗi Geo IP Fallback và asynchronous email logging (nếu lỗi email không rớt request chính).
- [ ] **Phase 6: Demo Prep** - Chạy 1 trang HTML ở local port khác, nhúng script, test CORS, test gửi lỗi, test 429.

## 🛑 BLOCKED
- Không có blocker.
