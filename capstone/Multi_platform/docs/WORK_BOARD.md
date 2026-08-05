# WORK_BOARD.md — Bảng trạng thái cho Capstone - Multi-Platform Publisher

## ✅ DONE
- [x] Khởi tạo harness docs, architecture, specs, và plan cho dự án.

## 🟣 READY FOR REVIEW
- Chưa có unit nào hoàn thành.

## 🟡 IN PROGRESS
- Chưa có task đang chạy.

## 🔴 TODO
- [ ] **Phase 1: Design & Models** - Thiết lập DB Schema (Campaigns, Posts, Tokens, Statuses) và interface `SocialPublisher`.
- [ ] **Phase 2: Content Generation** - Viết pipeline xử lý ảnh (Resize crop: 1080x1080 cho IG, 1600x900 cho X) và Caption composer.
- [ ] **Phase 3: Publishing System (Adapter Layer)** - Viết ít nhất 2 adapters (FakeInstagram, FakeX). Cài đặt idempotency key logic và retry-after backoff (chống spam). Thêm tính năng encrypt tokens.
- [ ] **Phase 4: Production Reliability** - Thiết lập Durable Scheduler (queue worker có tính năng crash recovery) và Webhook receiver (xác thực HMAC signature để update status).
- [ ] **Phase 5: Demo Prep** - Rehearse chạy worker test idempotency (publish 2 lần nhưng chỉ tạo 1 post), và gửi forged webhook để show 400 rejection.

## 🛑 BLOCKED
- Không có blocker.
