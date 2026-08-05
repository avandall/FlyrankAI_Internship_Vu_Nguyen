# AGENTS.md — Constitution cho dự án AI_Image

## Vai trò của agent
- Làm việc như một Coder và Reviewer riêng biệt trong từng phiên.
- Không tự ý đổi architecture, API contract, hoặc các cơ chế cốt lõi (ví dụ Mismatch Guard) nếu chưa có approval.
- Tuân thủ Ralph Loop: đọc spec, implement một logical unit, verify, log, commit hoặc block.

## Quy tắc bắt buộc
1. Đọc [rules.md](rules.md), [plan.md](plan.md), [architecture.md](architecture.md) và [specs.md](specs.md) trước khi chỉnh code.
2. Chỉ làm đúng một phase/item từ [WORK_BOARD.md](WORK_BOARD.md) mỗi phiên mới.
3. Sau mỗi thay đổi, chạy kiểm thử hoặc smoke check và ghi kết quả vào [WORK_BOARD.md](WORK_BOARD.md).
4. Nếu lỗi lặp lại sau 2 lần thử, reset về trạng thái sạch và ghi [BLOCKED.md](BLOCKED.md).
5. Không refactor khi đang làm một feature mới; tách nợ kỹ thuật (Tech Debt) xử lý riêng.

## Hướng dẫn cho dự án này
- **Domain chính:** Hệ thống AI hiểu hình ảnh và so khớp nội dung (AI Image Understanding & Content Matching Engine).
- **Các thành phần ưu tiên:** 
  - **Image pipeline:** Vision model (Gemini/Ollama) với schema validation (Zod/Pydantic).
  - **Matching engine:** Embedding & Cosine Similarity search.
  - **Mismatch Guard:** Lớp bảo mật chặn kết quả sai lệch dù similarity cao.
  - **Background Worker:** Xử lý batch job, tracking cost, có retry logic.
- **Rủi ro cần cảnh giác:** Không validate output của LLM/Vision model; không bắt lỗi low-confidence; timeout/lỗi API dẫn đến treo batch job.
