# FlyRank Internship - Backend Track: Capstone Brief
## Embeddable Widget & Lead-Capture Platform

Tóm tắt và dịch chi tiết yêu cầu đồ án Capstone dành cho Backend Track của FlyRank.

---

## 1. Tổng quan dự án (The Mission)

Bạn sẽ xây dựng một **Nền tảng Widget nhúng & Thu thập thông tin khách hàng (Embeddable Widget & Lead-Capture Platform)**.

* **Cách hoạt động:** Khách hàng (Widget Owner) sử dụng ứng dụng của bạn để tạo form/widget (signup form, contact form, popover CTA). Hệ thống cấp cho họ 1 đoạn mã `<script>` duy nhất. Họ dán đoạn mã này vào trang web bất kỳ. Khi người dùng truy cập trang web đó và điền form, dữ liệu sẽ gửi về Backend của bạn, trải qua các bước: **Xác thực (Validation) $ightarrow$ Lọc Spam/Chống nghẽn $ightarrow$ Làm giàu dữ liệu (Geo IP) $ightarrow$ Lưu trữ $ightarrow$ Hiển thị trên Dashboard**.
* **Thách thức cốt lõi:** Nhận request từ trình duyệt web bên ngoài mà bạn không kiểm soát. Bạn phải suy nghĩ như một Backend Engineer thật sự cho môi trường Internet mở (xử lý CORS, rate limiting, bảo mật, hạ cấp tính năng khi gọi dịch vụ ngoài bị lỗi).

---

## 2. Yêu cầu công nghệ & Quy tắc bắt buộc

* **Ngôn ngữ/Stack:** Node.js (Express) hoặc Python (FastAPI) + PostgreSQL (Docker).
* **Chi phí:** $0 (Chỉ sử dụng các công cụ miễn phí, không nhập thẻ tín dụng).
* **Môi trường demo/test:** Không cần mua CDN hay domain. "Trang web khách hàng" chỉ cần là một file HTML tĩnh chạy ở origin/port khác với Backend (ví dụ Backend chạy port 3000, trang test HTML chạy port 5500).
* **GitHub:** Tạo 1 repository công khai riêng (tên gợi ý: `flyrank-capstone-widget-platform`). Tuyệt đối **không commit các API key / mật khẩu / file `.env`**.

---

## 3. Nội dung cần xây dựng (What You'll Build)

Hệ thống bao gồm 5 phần chính:

### 1. Widget Management API (API quản lý Widget)
* Cho phép Admin/Khách hàng đăng nhập, tạo/sửa/xóa Widget (loại form, tiêu đề, các trường dữ liệu, giao diện, nút bấm).
* Đảm bảo **Multi-tenant isolation**: Khách hàng A không bao giờ xem hay sửa được Widget của khách hàng B.

### 2. Embed Snippet Generation (Tạo đoạn mã nhúng)
* Sinh ra mã nhúng dạng:
  ```html
  <script src="https://your-domain.com/widget.js?id=abc123"></script>
  ```

### 3. Cached Widget Delivery (Phục vụ Widget nhanh chóng)
* Trả về file JavaScript nhúng và cấu hình (config) của Widget với các HTTP Cache Header phù hợp.

### 4. Public Submission Endpoint (API nhận dữ liệu form)
* Nhận request từ các website bên ngoài gửi về.
* Cấu hình **CORS** chính xác (bao gồm cả request preflight `OPTIONS`).
* Kiểm tra, validate dữ liệu đầu vào. Trả về mã lỗi `4xx` thích hợp nếu dữ liệu sai/quá dung lượng, tuyệt đối không bị dính lỗi server `500`.

### 5. Chống lạm dụng, Làm giàu dữ liệu & Tác dụng phụ an toàn (Protection, Enrichment & Safe Side Effects)
* **Abuse Protection:** Giới hạn số lượng request (Rate limiting) theo IP/Widget và thêm cơ chế chống spam (ví dụ: trường ẩn `honeypot`).
* **Enrichment Fallback Chain:** Lấy thông tin vị trí từ IP qua Provider A (`ip-api.com`) $ightarrow$ nếu lỗi thì chuyển sang Provider B (`ipapi.co`). Nếu cả 2 đều lỗi/sập, **vẫn lưu dữ liệu thành công** (không có thông tin vị trí) chứ không được báo lỗi cho người dùng.
* **Safe Side Effects:** Gửi email/webhook xác nhận sau khi lưu form. Nếu việc gửi email/webhook bị lỗi, **submission vẫn phải báo thành công**.

### 6. Owner Dashboard API
* Các API trả về danh sách submissions và thống kê cơ bản (số lượng theo thời gian, thống kê theo widget, biểu đồ địa lý).

---

## 4. Danh sách mục cần hoàn thành (Definition of Done)

Lưu minh chứng cho mỗi ô checklist vào file `EVIDENCE.md`:

- [ ] **Widget Management:** CRUD có xác thực, cách ly multi-tenant giữa các user, tạo được script nhúng.
- [ ] **Widget Delivery:** Endpoint config có HTTP Cache Header, file `.js` trả về dưới dạng versioned bundle, widget render được trên trang HTML ở origin khác.
- [ ] **Public Submission API:** CORS hoạt động tốt (có preflight), validate input chặt chẽ (lỗi trả về JSON 4xx), lưu trữ thành công submission.
- [ ] **Abuse Protection:** Rate limit trả về `429` khi bị dội request nhanh; Bắt được spam bằng `honeypot`.
- [ ] **Enrichment & Safe Side Effects:** Test chuỗi fallback IP Geo (A sập $ightarrow$ B trả lời; cả A và B sập $ightarrow$ vẫn lưu thành công); Email/webhook lỗi không làm chết request submission.
- [ ] **Tests & Documentation:** Có Automated tests kiểm tra các trường hợp quan trọng trên; README có sơ đồ kiến trúc + hướng dẫn cài đặt.

---

## 5. Các file bắt buộc trong Repo GitHub

1. `README.md`: Mô tả hệ thống, sơ đồ kiến trúc, hướng dẫn chạy app (`docker compose up`), ghi rõ hạn chế.
2. `capstone.yaml`: File cấu hình cho máy chấm bài tự động (chứa lệnh run, seed, test, base_url...).
3. `EVIDENCE.md`: Chứa bằng chứng (output test, log, curl transcript) chứng minh bạn đã làm xong từng mục trong Checklist.
4. `BUILDLOG.md`: Nhật ký sử dụng AI (AI đã giúp gì, AI làm sai chỗ nào, bạn đã sửa gì).
5. `.env.example`: Danh sách các biến môi trường mẫu.

---

## 6. Các giai đoạn thực hiện (Phases)

* **Phase 1: Design (~4-6h):** Thiết kế database model (Widget, Submission), flow nhúng script, API contract, viết file tài liệu thiết kế.
* **Phase 2: The Hardened Submission Path (~14-20h):** Làm API nhận form submission + CORS + Validate + Rate limit + Honeypot + IP Geo Fallback + Email side effect.
* **Phase 3: Delivery, Dashboard & Proof (~12-16h):** Viết file JS nhúng, API config (có Cache), trang HTML test (origin khác), API Dashboard, viết Unit/Integration Tests.
* **Phase 4: Demo Prep (~2-3h):** Chuẩn bị dữ liệu mẫu và tập dượt demo kịch bản lỗi.