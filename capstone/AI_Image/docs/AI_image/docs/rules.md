# rules.md — Quy tắc phát triển cho Capstone - AI Image Understanding & Content Matching Engine

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Không dùng try/except chung chung để nuốt lỗi; phải log lỗi cụ thể kèm context.
- Mọi dữ liệu đầu vào/đầu ra phải có schema validation và sample payload lưu kèm.
- Khi làm việc với model AI hoặc batch job, phải có fallback, retry và cost tracking.

## 2. Quy tắc miền riêng cho dự án
- Dữ liệu ảnh phải được validate trước khi đưa vào pipeline: định dạng, kích thước, dung lượng, metadata.
- Mỗi kết quả OCR/vision phải có confidence score và flag trạng thái thấp/mismatch.
- Mismatch guard là phần bảo mật cốt lõi: không được phép bỏ qua threshold và reject reason.
- Khi ghép ảnh với blog post, phải ưu tiên semantic similarity hơn tên file hoặc keyword.
- Hệ thống phải có ít nhất 3 lớp kiểm tra: schema validation, similarity threshold, review feedback.

## 3. Logging & observability
- Log mỗi bước: ingestion, preprocessing, vision output, embedding, match result, review action.
- Ghi rõ input id, image id, confidence score, reject reason và cost per call.
- Nếu AI call fail, phải có retry và fallback logic, không được để batch job silent fail.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit mỗi phiên, ví dụ: schema, ingestion, matching, review.
- Nếu test thất bại sau 2 lần, reset trạng thái về clean state và ghi blocker.
- Không refactor ngầm khi đang xử lý một feature mới; debt phải tách riêng.
