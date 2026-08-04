# FlyRank Internship - Backend Track: Capstone Brief
## Multi-Platform Social Campaign Publisher

Tóm tắt và phân tích chi tiết yêu cầu đồ án Capstone dành cho Backend Track của FlyRank (Mức độ: **Medium-Hard**).

---

## 1. Tổng quan dự án (The Mission)

Bạn sẽ xây dựng một **Hệ thống Phát hành Chiến dịch Mạng xã hội Đa nền tảng (Multi-Platform Social Campaign Publisher)**.

* **Cách hoạt động:** Nhận một bài viết blog đã xuất bản, tự động chuyển đổi thành một chiến dịch truyền thông đa nền tảng hoàn chỉnh: cắt/chỉnh kích thước ảnh phù hợp cho từng nền tảng (Instagram, X,...), tạo caption theo phong cách riêng của từng mạng xã hội, lên lịch đăng bài và tự động xuất bản qua một hệ thống Publishers bền vững.
* **Thách thức cốt lõi:** Đây không chỉ là bài toán gọi API đơn thuần, mà là **Kỹ thuật xây dựng hệ thống chịu lỗi (Reliability Engineering)**. Bạn phải đảm bảo hệ thống sống sót trước các sự cố thực tế: Yêu cầu trùng lặp, lỗi mạng, dội Rate Limit, Worker bị crash giữa chừng. 
  * Gửi lại request (retry) **không bao giờ được tạo bài đăng trùng lặp** (Idempotency).
  * Đặt lịch đăng bài phải **sống sót qua các lần restart server**.
  * Trạng thái bài đăng chỉ chuyển sang `published` khi nhận được **Webhook đã được xác thực chữ ký (Signature Verification)**.
* **Môi trường giả lập (Sandbox-First):** Toàn bộ dự án sẽ chạy với một **Fake Social Platform Server** do FlyRank cung cấp (giả lập đầy đủ OAuth, Rate Limit 429, Retry-After, Idempotency Key, Signed Webhooks, Lỗi ngẫu nhiên). Tuyệt đối **không gọi API thật hay dùng tài khoản thật**.

---

## 2. Yêu cầu công nghệ & Quy tắc bắt buộc

* **Ngôn ngữ/Stack:** Node.js (Express) hoặc Python (FastAPI) + PostgreSQL / Redis + Docker.
* **Xử lý ảnh:** `sharp` (Node.js) hoặc `Pillow` (Python).
* **Xử lý Queue/Task Scheduler:** `BullMQ` + Redis (Node.js) hoặc `APScheduler` (Python).
* **Mã hóa:** Node `crypto` / `cryptography` (mã hóa Token bằng thuật toán AES-GCM với random IV).
* **Chi phí:** $0 (Chạy hoàn toàn ở môi trường Local/Docker).
* **GitHub:** Repository công khai độc lập (tên gợi ý: `flyrank-capstone-social-studio`). Tuyệt đối **không commit bí mật, API key hay token**.

---

## 3. Nội dung cần xây dựng (What You'll Build)

Hệ thống bao gồm 5 phần chính:

### 1. Image Variant Pipeline (Xử lý ảnh đa nền tảng)
* Từ 1 ảnh gốc, tạo ra các phiên bản ảnh chuẩn cho từng nền tảng (Instagram: $1080 	imes 1080$ tỷ lệ 1:1, X: $1600 	imes 900$ tỷ lệ 16:9).
* Đảm bảo đối tượng chính nằm trong "Safe Zone" (vùng an toàn không bị cắt mất).

### 2. Platform-Tailored Caption Generation (Tạo Caption theo nền tảng)
* Xây dựng prompt ghép từ các mảnh nhỏ tái sử dụng (Prompt Fragments: Shared Brand Voice + Platform Rules + Content Summary) thay vì copy-paste prompt.

### 3. Social Publishing Adapter Layer (Lớp Adapter xuất bản)
* Thiết kế một interface `SocialPublisher` chung và ít nhất 2 Adapter cho 2 nền tảng khác nhau (gửi tới Fake Server).
* Mỗi Adapter tự xử lý: Đọc Token đã mã hóa, Đăng bài Idempotent, Xử lý Rate Limit (429 + Retry-After) và Retry logic.

### 4. Durable Scheduling System (Hệ thống đặt lịch bền vững)
* Đặt lịch đăng bài ("Đăng chiến dịch này vào 9:00 sáng mai"). Worker sẽ tự động lấy job ra xử lý đúng giờ.
* Nếu Server/Worker bị crash giữa chừng và khởi động lại, hệ thống phải **tiếp tục công việc an toàn mà không đăng trùng lặp bài**.

### 5. Webhook-Based Status Tracking (Cập nhật trạng thái qua Webhook)
* Nhận Webhook từ Fake Server tại `POST /webhook/social-delivery`.
* Xác thực chữ ký HMAC của Webhook. **Từ chối (400)** nếu chữ ký giả mạo hoặc bị chỉnh sửa. Chỉ cập nhật trạng thái chiến dịch (`queued` $ightarrow$ `publishing` $ightarrow$ `published` | `failed`) khi Webhook hợp lệ.

---

## 4. Danh sách mục cần hoàn thành (Definition of Done)

Lưu minh chứng vào file `EVIDENCE.md`:

- [ ] **Content Generation:** Ảnh biến thể đúng kích thước/tỷ lệ/safe zone; Caption được cấu thành từ các mảnh Prompt fragments.
- [ ] **Adapter Layer:** Áp dụng thiết kế Interface `SocialPublisher`; Token được mã hóa lưu trữ ở ổ đĩa (AES-GCM + random IV), không bao giờ ghi log thô.
- [ ] **Reliability:** Đăng bài tính đẳng tính (Idempotent): Bị lặp request hay timeout $ightarrow$ Chỉ có 1 bài duy nhất được tạo; Tự động tạm dừng (Backoff) khi dính Rate Limit `429 Retry-After`; Đặt lịch bền vững (Durable) không bị mất hay nhân đôi khi crash worker.
- [ ] **Status & Trust:** Xác thực chữ ký HMAC trên Webhook; Trạng thái cập nhật chuẩn xác theo chuẩn `SocialPostEntry`.
- [ ] **Tests & Documentation:** Automated tests kiểm tra kích thước ảnh, chống trùng bài, từ chối giả mạo webhook, xử lý rate limit; README + Diagram đầy đủ.

---

## 5. Các file bắt buộc trong Repo GitHub

1. `README.md`: Mô tả hệ thống, sơ đồ kiến trúc, hướng dẫn chạy app (`docker compose up`), ghi rõ hạn chế.
2. `capstone.yaml`: File cấu hình cho máy chấm bài tự động (`run`, `seed`, `test`, `base_url`...).
3. `EVIDENCE.md`: Chứa bằng chứng (output test, log, curl transcript) chứng minh bạn đã hoàn thành checklist.
4. `BUILDLOG.md`: Nhật ký sử dụng AI (AI đã giúp gì, làm sai ở đâu, bạn đã sửa gì).
5. `.env.example`: Danh sách biến môi trường mẫu.

---

## 6. Các giai đoạn thực hiện (Phases)

* **Phase 1: Design (~4-6h):** Thiết kế Interface `SocialPublisher`, quy định kích thước ảnh/voice rules từng platform, thiết kế ERD database & Token storage.
* **Phase 2: Content Generation (~8-12h):** Viết Pipeline xử lý ảnh (`sharp`/`Pillow`) và ghép Prompt tạo Caption.
* **Phase 3: Publishing System (~14-18h):** Viết Adapter Layer kết nối Fake Server, xử lý Idempotency Key, Rate limit 429 và mã hóa Token.
* **Phase 4: Production Reliability (~12-16h):** Xây dựng Durable Scheduler (BullMQ/APScheduler), xác thực chữ ký Webhook HMAC, viết Tests và hoàn thiện EVIDENCE.md.
* **Phase 5: Demo Prep (~2-3h):** Chuẩn bị demo: Đặt lịch đăng bài, tua thời gian, bấm nút đăng 5 lần liên tục (chứng minh chỉ có 1 bài ra đời), gửi Webhook giả mạo bị chặn.