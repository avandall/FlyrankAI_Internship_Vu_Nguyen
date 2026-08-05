# WORK_BOARD.md — Bảng trạng thái cho Capstone - Usage Metering

## ✅ DONE
- [x] Khởi tạo harness docs, architecture, specs, và plan cho dự án.

## 🟣 READY FOR REVIEW
- Chưa có unit nào hoàn thành.

## 🟡 IN PROGRESS
- Chưa có task đang chạy.

## 🔴 TODO
- [ ] **Phase 1: Design & API Contract** - Thiết kế DB schema cho Tenants, Plans, Subscriptions, Usage Events. Định nghĩa cơ chế idempotency.
- [ ] **Phase 2: Core Billing Logic (Metering & Quotas)** - Xây dựng Dummy API sinh Usage Event (có chống trùng lặp bằng Idempotency Key). Cài đặt logic chặn Quota với mã lỗi trung thực `429` / `402`.
- [ ] **Phase 3: Stripe Integration** - Code webhook handler (Checkout session completed). Xác thực chữ ký bằng thư viện SDK và deduplicate Stripe Events.
- [ ] **Phase 4: Cost Math & Rollups** - Xây dựng endpoint `GET /usage` rollup toàn bộ events. Tính tiền bằng toán `Integer` và quy tắc phân loại Token. Viết test pinned cho Cost Math.
- [ ] **Phase 5: Demo Prep** - Seed 1 user sát ngưỡng Quota. Chạy kịch bản gọi API hit quota `429`. Replay request báo duplicate thành công. Stripe trigger test.

## 🛑 BLOCKED
- Không có blocker.
