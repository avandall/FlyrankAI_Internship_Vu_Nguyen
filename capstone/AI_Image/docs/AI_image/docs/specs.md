# specs.md — Spec checklist cho Capstone - AI Image Understanding & Content Matching Engine

## 1. Foundation & requirements
- [x] Xác định mục tiêu sản phẩm, phạm vi và quy tắc mismatch guard cho hệ thống.
- [x] Chuẩn hóa yêu cầu về dữ liệu ảnh, schema metadata và thiết kế cơ sở dữ liệu.
- [x] Tạo API contract cho ingestion, matching, review và background job.
- [x] Xác định quy tắc threshold, confidence score và reject reason cho mismatch guard.

## 2. Core implementation backlog
- [x] Xây dựng pipeline ingest ảnh từ thư viện mẫu (~50 ảnh) và lưu metadata đúng schema.
- [x] Triển khai Vision/OCR processing với validation schema, confidence flagging và retry policy.
- [x] Tạo embedding cho caption/description và xây dựng similarity search theo cosine similarity.
- [x] Cài đặt mismatch guard để chặn trường hợp fox/wolf/dog bị ghép sai và trả lời rõ lý do.
- [ ] Xây dựng background job xử lý batch, theo dõi cost per call và tiến độ xử lý.
- [x] Tạo review API để approve/reject suggestion và lưu lý do review.

## 3. Verification checklist
- [x] Smoke test cho flow happy path: ảnh phù hợp -> match thành công.
- [x] Test cho flow reject: wolf/fox mismatch bị chặn và trả reject reason.
- [x] Test cho trường hợp no confident match khi không có ảnh đủ tốt.
- [x] Test schema validation cho metadata và batch job.
- [x] Tài liệu, evidence và work board đã được cập nhật.
