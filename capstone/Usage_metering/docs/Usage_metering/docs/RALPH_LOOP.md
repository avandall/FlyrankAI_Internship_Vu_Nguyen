# RALPH_LOOP.md — Quy trình tự động cho Capstone - Usage Metering & Billing Engine

## 1. Chuỗi hoạt động
1. Mở phiên mới và đọc AGENTS, rules và specs.
2. Chọn đúng một item chưa hoàn thành.
3. Engineer implement theo logical unit.
4. Reviewer đọc patch, kiểm tra chất lượng code, rule compliance và test coverage.
5. Nếu reviewer chấp thuận: chạy verification và log kết quả.
6. Nếu reviewer từ chối: engineer sửa lại theo feedback, lặp lại vòng review tối đa 2 lần.
7. Nếu thành công: commit và đánh dấu done.
8. Nếu thất bại sau 2 lần: reset và ghi blocker.

## 2. Vai trò trong loop
- Engineer: chịu trách nhiệm implement, test và sửa lỗi.
- Reviewer: chịu trách nhiệm phản biện chất lượng code, phát hiện logic sai, missing edge case, violation rule và thiếu evidence.

## 3. Quy tắc đối chất
- Reviewer không được chỉ nói chung chung; phải nêu rõ file, logic và lý do.
- Engineer phải trả lời từng feedback bằng patch hoặc bằng lý do đã bỏ qua.
- Chỉ khi cả hai bên đồng ý và verification pass thì mới được commit.

## 4. Exit code
- 0: success
- 1: retry needed
- 2: blocked

## 5. Logging và status update
- Mỗi iteration phải có log riêng cho engineer và reviewer.
- Sau mỗi session thành công, cập nhật WORK_BOARD, specs và evidence.
