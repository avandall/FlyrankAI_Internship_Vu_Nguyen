# WORK_BOARD.md — Bảng trạng thái cho Capstone - AI Image Understanding & Content Matching Engine

## ✅ DONE
- [x] Khởi tạo harness docs và quy trình Ralph Loop cho dự án này.
- [x] Implemented Image Metadata validation schema and Ingestion Service with confidence threshold flagging (<0.70).
- [x] Built Content Matching Engine using Cosine Similarity for semantic matching.
- [x] Implemented Mismatch Guard with species mismatch blocking (Fox vs Wolf/Dog) and explicit reject reasons.
- [x] Built Human Review API feedback loop.
- [x] Passed 100% automated test suite (`pytest capstone/AI_Image/tests/test_ai_image.py`).

## 🟣 READY FOR REVIEW
- Tất cả các unit đã được verify và approve.

## 🟡 IN PROGRESS
- Chưa có task đang chạy.

## 🔴 TODO
- Xử lý batch job scale-out trong phase tiếp theo.

## 🛑 BLOCKED
- Không có blocker.
