# WORK_BOARD.md — Bảng trạng thái cho Capstone - AI Image Understanding

## ✅ DONE
- [x] Khởi tạo harness docs, architecture, specs, và plan cho dự án.

## 🟣 READY FOR REVIEW
- Chưa có unit nào hoàn thành.

## 🟡 IN PROGRESS
- Chưa có task đang chạy.

## 🔴 TODO
- [ ] **Phase 1: Design & Setup** - Thiết lập Database Schema (PostgreSQL/pgvector), Image metadata schema (Zod/Pydantic).
- [ ] **Phase 2: Image Pipeline** - Tạo Background Worker gọi Vision API, schema validation, flag low-confidence, cost tracking.
- [ ] **Phase 3: Matching Engine** - Tạo API embeddings cho posts và images, thực hiện Similarity Search, và viết Mismatch Guard rules.
- [ ] **Phase 4: Production Layer** - Viết Review API (approve/reject matches), chuẩn bị Evaluation dataset, viết automated tests.
- [ ] **Phase 5: Demo Prep** - Seed data (50 images), test refusal case (bắt buộc Mismatch Guard chặn hình ảnh "wolf" cho bài "fox").

## 🛑 BLOCKED
- Không có blocker.
