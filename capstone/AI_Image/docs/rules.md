# rules.md — Quy tắc phát triển cho Capstone - AI Image Understanding

## 1. Nguyên tắc chung
- Luôn dùng type hints và cấu trúc rõ ràng cho function, class, DTO và API payload.
- Không dùng try/except chung chung để nuốt lỗi; phải log lỗi cụ thể kèm context.
- Phải có schema validation tại biên giới của hệ thống (Boundary validation).

## 2. Quy tắc miền riêng cho dự án AI_Image
- **Không bao giờ tin tưởng output của Model AI:** Mọi response từ Vision Model (Gemini/Ollama) phải được validate qua Zod/Pydantic schema. Lỗi parse JSON phải trigger retry.
- **Low Confidence Flag:** Nếu model trả về confidence < mức quy định, dữ liệu không được tự động approve, phải flag trạng thái `NEEDS_REVIEW`.
- **Mismatch Guard là bắt buộc:** Kết quả trả về cho user phải luôn đi qua Mismatch Guard. Tuyệt đối không trả về kết quả chỉ dựa trên Similarity Score cao mà bỏ qua kiểm tra tags/logic.
- **Background Jobs:** Tác vụ gọi LLM/Vision/Embedding phải nằm trong background queue (không block HTTP request), phải có cơ chế retry an toàn.
- **Cost Tracking:** Ghi lại metadata cost cho mỗi token/call gửi lên API.

## 3. Logging & Observability
- Log rõ input image ID, bài viết liên quan, cost API, và reject reason nếu Mismatch Guard kích hoạt.
- Ghi nhận trạng thái batch job (Success, Retry, Failed) với thông tin error stack cụ thể.

## 4. Commit standard
```text
<type>(<scope>): <summary>

- Why: <nguyên nhân>
- What: <file và logic đã đổi>
- Verification: <test/smoke check đã chạy>
```

## 5. Ralph Loop guardrails
- Chỉ làm một logical unit/phase từ `WORK_BOARD.md` mỗi phiên.
- Nếu test thất bại sau 2 lần, reset trạng thái về clean state và ghi blocker.
