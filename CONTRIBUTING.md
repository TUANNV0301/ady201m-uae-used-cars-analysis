# Hướng dẫn cộng tác

## Quy trình làm việc

1. Clone repository và tạo nhánh riêng: `feature/<ten-cong-viec>` hoặc `fix/<ten-loi>`.
2. Chỉ chỉnh các tệp liên quan đến phần được phân công; không ghi đè dữ liệu nguồn.
3. Commit bằng tài khoản cá nhân, với thông điệp ngắn mô tả thay đổi, ví dụ `feat: add emirate price summary`.
4. Mở pull request về nhánh `main`, nêu mục đích, tệp thay đổi, cách kiểm tra và người phụ trách.
5. Một thành viên khác review trước khi merge. Cập nhật bảng bằng chứng trong `TEAM.md` sau khi PR được merge hoặc commit được xác nhận.

## Quy ước dữ liệu và phân tích

- Giữ bản CSV nguồn trong `data/raw/`; lưu kết quả sinh ra trong `data/processed/`.
- Ghi rõ giả định, xử lý thiếu/ngoại lệ và nguồn dữ liệu trong notebook hoặc tài liệu.
- Không diễn giải tương quan thành quan hệ nhân quả; gọi `Price` là giá niêm yết.
- Không đưa mật khẩu, token, `.env` hoặc dữ liệu cá nhân vào Git.
- Trước khi đề xuất kết quả mới, chạy lại script liên quan và kiểm tra thay đổi đầu ra.
