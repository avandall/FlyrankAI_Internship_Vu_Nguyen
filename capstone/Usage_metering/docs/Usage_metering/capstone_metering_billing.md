# FlyRank Internship - Backend Track: Capstone Brief
## Usage Metering & Billing Engine

Tóm tắt và phân tích chi tiết yêu cầu đồ án Capstone dành cho Backend Track của FlyRank (Mức độ: **Medium** - *Được khuyến nghị nhất cho thực tập sinh mới*).

---

## 1. Tổng quan dự án (The Mission)

Bạn sẽ xây dựng một **Hệ thống Đo lường Mức độ Sử dụng & Tính cước (Usage Metering & Billing Engine)** - dịch vụ lõi mà mọi sản phẩm SaaS đều cần có.

* **Nhiệm vụ cốt lõi:** Trả lời 3 câu hỏi lớn của một hệ thống SaaS:
  1. *Khách hàng đã sử dụng bao nhiêu tài nguyên?* (API calls, AI tokens)
  2. *Họ phải trả bao nhiêu tiền?* (Tính toán chi phí dựa trên các quy tắc giá token phức tạp)
  3. *Họ đã chạm hạn mức (Quota) của gói dịch vụ chưa?* (Chặn request nếu vượt quá giới hạn)
* **Thách thức kỹ thuật:** **Tính chính xác tuyệt đối (Absolute Correctness)**. 
  * Gửi lại request do lỗi mạng không bao giờ được phép ghi nhận gấp đôi (Double-counting).
  * Webhook nhận trùng lặp không được làm thay đổi trạng thái gói dịch vụ 2 lần.
  * Phản hồi chính xác ở điểm ranh giới Quota (ví dụ: request thứ 1,000 và 1,001).
* **Môi trường thanh toán:** Sử dụng **Stripe Test Mode** + **Stripe CLI** ($0, không cần thẻ tín dụng thật, không phát sinh chi phí).

---

## 2. Yêu cầu công nghệ & Quy tắc bắt buộc

* **Ngôn ngữ/Stack:** Node.js (Express) hoặc Python (FastAPI) + PostgreSQL + Docker.
* **Thanh toán:** Stripe API (Test mode) + Stripe CLI (để listen và trigger webhook ở môi trường local).
* **Quy tắc tính toán tiền tệ:** Lưu trữ tiền tệ dạng **Số nguyên (Integer - Cents/Micro-units)**, tuyệt đối **không dùng số thực (Float)** để tránh lỗi làm tròn.
* **Môi trường AI:** Mô phỏng số lượng token ngẫu nhiên/nhập tay (không bắt buộc phải gọi model AI thật).
* **GitHub:** Repository công khai độc lập (tên gợi ý: `flyrank-capstone-metering-billing`). Tuyệt đối **không commit Stripe Secret Key hay Webhook Secret (`whsec`)**.

---

## 3. Nội dung cần xây dựng (What You'll Build)

Hệ thống được chia làm 4 thành phần chính:

### 1. Usage Metering (Đo lường mức độ sử dụng)
* Mỗi hành động tính phí (Billable action) sẽ ghi lại một `usage_event` gắn với Khách hàng/Tenant.
* Đảm bảo tính **Đẳng tính (Idempotency)**: Cùng request + cùng `idempotency_key` $ightarrow$ Chỉ ghi nhận đúng **1 event**.

### 2. Quota Enforcement (Kiểm soát hạn mức gói)
* Trước khi xử lý hành động, kiểm tra: `Usage hiện tại` + `Usage yêu cầu` $\le$ `Hạn mức của Plan`.
* Trả về HTTP Status Code chuẩn xác:
  * **429 Too Many Requests**: Khi vượt quá hạn mức sử dụng (Quota exceeded).
  * **402 Payment Required**: Khi cần nâng cấp gói hoặc tài khoản chưa thanh toán.

### 3. Cost Calculation (Tính toán chi phí)
* Quy đổi tài nguyên sử dụng thành tiền mặt.
* Áp dụng quy tắc giá AI Token chuẩn thực tế:
  * Input tokens, Cached input tokens (giá rẻ hơn), Output tokens và Reasoning tokens (tính giá như Output tokens).
  * Không thể cộng gộp trực tiếp các loại token lại với nhau mà phải nhân theo công thức cố định quy định trong file config.

### 4. Stripe Subscription Integration (Tích hợp đăng ký Stripe)
* Tạo luồng Checkout (Free $ightarrow$ Pro).
* Xây dựng Webhook Endpoint xử lý các sự kiện: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`.
* Bắt buộc: **Xác thực chữ ký HMAC Webhook**, **Chống xử lý lặp sự kiện (Deduplication)** và **Đồng bộ trạng thái Plan trong DB**.

---

## 4. Danh sách mục cần hoàn thành (Definition of Done)

Lưu minh chứng vào file `EVIDENCE.md`:

- [ ] **Metering:** Ghi nhận chính xác 1 event cho mỗi hành động (chống ghi trùng bằng `idempotency_key`); Có automated test chứng minh không bị double-counting.
- [ ] **Quotas:** Kiểm tra quota trước khi xử lý; Trả về chuẩn mã lỗi `429` / `402` khi vượt hạn mức.
- [ ] **Cost Calculation:** Tổng hợp được chi phí sử dụng theo tháng; Tính đúng giá các loại AI token (Cached input, Reasoning); Giá được cố định trong file config và có unit test bao phủ.
- [ ] **Stripe Integration:** Chạy hoàn chỉnh luồng Stripe Checkout (Test mode); Webhook xác thực chữ ký, bỏ qua event trùng và cập nhật đúng Plan/Status của Tenant.
- [ ] **Data Model & Tests:** DB thiết kế cách ly dữ liệu Multi-tenant; Test suite bao phủ boundary cases, duplicate requests, webhook giả mạo.

---

## 5. Các file bắt buộc trong Repo GitHub

1. `README.md`: Mô tả hệ thống, sơ đồ kiến trúc, hướng dẫn chạy app (`docker compose up`), ghi rõ hạn chế.
2. `capstone.yaml`: File cấu hình cho máy chấm bài tự động (`run`, `seed`, `test`, `base_url`...).
3. `EVIDENCE.md`: Chứa bằng chứng (output test, log, curl transcript) chứng minh bạn đã hoàn thành checklist § 6.
4. `BUILDLOG.md`: Nhật ký sử dụng AI (AI đã giúp gì, làm sai ở đâu, bạn đã sửa gì).
5. `.env.example`: Danh sách biến môi trường mẫu.

---

## 6. Các giai đoạn thực hiện (Phases)

* **Phase 1: Design (~4-6h):** Thiết kế ERD Database (Tenants, Plans, Subscriptions, Usage Events), chiến lược Idempotency Key và API Contract.
* **Phase 2: Core Billing Logic (~9-13h):** Viết logic Metering idempotency + Quota check trả về mã `429`/`402` + Unit tests chống ghi duplicate.
* **Phase 3: Stripe Integration (~8-12h):** Dùng Stripe CLI cấu hình luồng Checkout (Test mode), viết Webhook handler có HMAC Verification & Deduplication.
* **Phase 4: Cost & Finalization (~7-10h):** Cài đặt công thức tính chi phí AI token, kiểm tra chỉ số tổng hợp qua GET `/usage`, hoàn thiện tài liệu & EVIDENCE.md.
* **Phase 5: Demo Prep (~2-3h):** Chuẩn bị tenant gần chạm hạn mức, demo vượt limit (429), retry lặp request (chống double-count), nâng cấp Stripe Checkout live.