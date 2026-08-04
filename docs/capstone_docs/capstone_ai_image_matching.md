# FlyRank Internship - Backend Track: Capstone Brief
## AI Image Understanding & Content Matching Engine

Tóm tắt và phân tích chi tiết yêu cầu đồ án Capstone dành cho Backend Track của FlyRank (Mức độ: **Medium**).

---

## 1. Tổng quan dự án (The Mission)

Bạn sẽ xây dựng một **Hệ thống Hiểu hình ảnh AI & Ghép nối Nội dung (AI Image Understanding & Content Matching Engine)**.

* **Cách hoạt động:** Hệ thống quét qua một thư viện hình ảnh (~50 ảnh), sử dụng AI Vision để tự động phân tích/gán tag/mô tả ngữ nghĩa cho từng ảnh. Sau đó, hệ thống ghép nối ảnh phù hợp nhất với một bài viết blog (dựa trên ý nghĩa nội dung chứ không dựa vào tên file hay keyword).
* **Hành vi mong muốn:**
  * Bài viết về **cáo đỏ (red fox)** $ightarrow$ Tìm ra ảnh **cáo đỏ**.
  * Ảnh **chó sói (wolf)** có ngoại hình tương tự $ightarrow$ **Từ chối (Reject)**.
  * Ảnh **chó nhà (dog)** chung chung $ightarrow$ Điểm xếp hạng thấp.
  * Nếu không có ảnh nào đủ phù hợp $ightarrow$ Hệ thống báo **"Không có ảnh phù hợp" (No confident match)** thay vì đoán mò.
* **Thách thức cốt lõi (Core Innovation):** **Chốt chặn từ chối (Mismatch Guard)**. Đây là lớp bảo mật kết hợp giữa Tag extracted, Ngưỡng tương đồng ngữ nghĩa (Similarity Threshold) và Điểm tin cậy (Confidence Score) để quyết định xem một gợi ý có đủ tốt hay không và từ chối khi không đạt chuẩn.

---

## 2. Yêu cầu công nghệ & Quy tắc bắt buộc

* **Ngôn ngữ/Stack:** Node.js (Express) hoặc Python (FastAPI) + PostgreSQL (với `pgvector` hoặc lưu mảng vector) + Docker.
* **AI Stack (Chi phí $0):**
  * *Cloud:* Gemini Flash API (Miễn phí qua Google AI Studio).
  * *Local (Offline):* Ollama (mô hình vision như `llava`, `moondream` và embedding `all-minilm`).
* **Dữ liệu mẫu:** Tải bộ dataset khoảng ~50 ảnh miễn phí bản quyền (từ Unsplash / Pexels).
* **GitHub:** Repository riêng biệt, công khai từ ngày đầu (tên gợi ý: `flyrank-capstone-image-relevance`). Tuyệt đối **không commit API key hay `.env`**.

---

## 3. Nội dung cần xây dựng (What You'll Build)

Hệ thống bao gồm 5 phần chính:

### 1. Image Ingestion & Classification (Phân tích & Phân loại ảnh)
* Quét toàn bộ thư viện ảnh qua Vision Model để trích xuất JSON metadata có cấu trúc (Subject, Category, Attributes, Caption, Confidence).
* Validate dữ liệu bằng Schema (dùng `Zod` đối với Node.js hoặc `Pydantic` đối với Python).
* Kết quả có điểm tin cậy thấp (`confidence`) sẽ bị đánh cờ (flagged) thay vì chấp nhận ngầm.

### 2. Semantic Image Matching (Ghép nối ngữ nghĩa)
* Tạo Embeddings cho phần mô tả ảnh (`caption`) và nội dung bài viết blog (`post text`).
* Lưu trữ vector và tìm kiếm độ tương đồng (Cosine similarity).
* Khả năng khớp khái niệm tương đương (ví dụ: "red fox", "Vulpes vulpes", "wild fox" đều ghép khớp ngữ nghĩa).

### 3. The Mismatch Guard (Chốt chặn chống ghép sai)
* Lớp kiểm soát an toàn quyết định xem ứng viên tốt nhất có đủ điều kiện không.
* Kết hợp kiểm tra Tag/Category, Threshold điểm tương đồng và Confidence score.
* Báo lý do rõ ràng khi từ chối (Ví dụ: *"Animal category mismatch: expected fox, detected wolf"*).

### 4. Background Processing System (Hệ thống xử lý chạy ngầm)
* Xử lý gọi Vision Model và tạo Vector Embedding thông qua Batch Jobs bất đồng bộ.
* Tự động thử lại khi lỗi (Retries), theo dõi tiến độ và **ghi nhận chi phí trên mỗi lượt gọi AI (Cost tracking per call)**.

### 5. Review API (Workflow duyệt kết quả)
* Cung cấp endpoint cho phép con người kiểm tra, duyệt (Approve) hoặc từ chối (Reject) các gợi ý ảnh, cũng như xem lý do tại sao hệ thống chọn hoặc từ chối ảnh đó.

---

## 4. Danh sách mục cần hoàn thành (Definition of Done)

Lưu minh chứng cho mỗi ô checklist vào file `EVIDENCE.md`:

- [ ] **AI Processing:** Vision model trả về JSON đúng Schema; Kết quả `confidence` thấp bị đánh cờ; Xử lý batch job có retry; Ghi nhận chi phí (cost) từng lượt gọi API.
- [ ] **Matching System:** Lưu trữ Vector Embeddings bài viết & hình ảnh; Trả về danh sách xếp hạng theo độ tương đồng ngữ nghĩa.
- [ ] **Safety Layer (Mismatch Guard):** Từ chối ghép sai (chứng minh kịch bản Sói - Cáo bị chặn); Trả về lý do từ chối dễ hiểu; Báo "No confident match" khi không có ảnh đạt ngưỡng.
- [ ] **Backend:** Thiết kế DB đầy đủ cho Image, Tag, Embedding, Post, Suggestion, Review; Endpoint API đầy đủ và được validate.
- [ ] **Quality & Documentation:** Automated tests cho schema validation, mismatch rejection, matching accuracy; Đo lường chỉ số **Top-1 Precision** trên bộ đánh giá mẫu (ghi vào README).

---

## 5. Các file bắt buộc trong Repo GitHub

1. `README.md`: Mô tả hệ thống, sơ đồ kiến trúc, hướng dẫn chạy app (`docker compose up`), báo cáo chỉ số Top-1 Precision và hạn chế.
2. `capstone.yaml`: File cấu hình cho máy chấm bài tự động (`run`, `seed`, `test`, `base_url`...).
3. `EVIDENCE.md`: Chứa bằng chứng (output test, log, curl transcript) chứng minh bạn đã hoàn thành checklist § 6.
4. `BUILDLOG.md`: Nhật ký sử dụng AI (AI đã giúp gì, làm sai ở đâu, bạn đã sửa gì).
5. `.env.example`: Danh sách biến môi trường mẫu.

---

## 6. Các giai đoạn thực hiện (Phases)

* **Phase 1: Design (~4-6h):** Thiết kế Schema cho metadata ảnh, quy tắc Mismatch Guard, Database ERD, thu thập bộ dữ liệu ~50 ảnh.
* **Phase 2: Image Understanding Pipeline (~10-14h):** Viết Batch job xử lý Vision Model, validate Zod/Pydantic, retry và ghi nhận chi phí.
* **Phase 3: Matching Engine (~12-16h):** Tạo Embeddings, viết Similarity Search, cài đặt Mismatch Guard kèm giải thích lý do từ chối.
* **Phase 4: Production (~8-12h):** Xây dựng Review API, chạy bộ Evaluation test đo Top-1 Precision, hoàn thiện tài liệu & EVIDENCE.md.
* **Phase 5: Demo Prep (~2-3h):** Chuẩn bị dữ liệu demo, tập dượt kịch bản "Chặn Sói ghép Cáo" và kịch bản "Không có ảnh phù hợp".