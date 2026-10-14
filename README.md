# ADY201m — Phân tích giá niêm yết xe đã qua sử dụng tại UAE

> **Trạng thái nhóm:** Đã có roster và phân công dự kiến. Repo online và bằng chứng đóng góp GitHub đang chờ kết nối đúng tài khoản.
>
> **Tên repository gợi ý:** `ady201m-uae-used-cars-analysis` (nên tạo Private để nhóm kiểm soát quyền truy cập).

## Tổng quan dự án

Dự án phân tích giá rao của 10.000 tin đăng xe đã qua sử dụng tại Các Tiểu vương quốc Ả Rập Thống nhất (UAE), trong khuôn khổ môn ADY201m — AI, Data Science with Python & SQL, Đại học FPT. Mỗi dòng dữ liệu đại diện cho một tin đăng. Trường `Price` được xem là giá niêm yết bằng AED, không phải giá giao dịch đã xác nhận.

## Vấn đề và mục tiêu

Người mua và người bán cần hiểu giá niêm yết thay đổi như thế nào theo đặc điểm xe và địa điểm. Phân tích này mô tả các mối liên hệ trong bộ dữ liệu; kết quả không khẳng định quan hệ nhân quả và không đại diện cho toàn bộ thị trường UAE.

Mục tiêu:

1. Khảo sát chất lượng dữ liệu, chuẩn hóa trường văn bản và giá trị thiếu đã biết.
2. Tạo cơ sở dữ liệu SQLite có các bảng chiều và viết truy vấn SQL để tổng hợp dữ liệu.
3. Phân tích giá theo hãng, kiểu thân xe, năm sản xuất, số km và tiểu vương quốc.
4. So sánh giá SUV và Sedan, sau đó đánh giá mô hình hồi quy baseline chỉ dùng năm sản xuất và số km.
5. Lưu quy trình, kết quả, biểu đồ và báo cáo để nhóm có thể kiểm tra và tái lập.

## Dữ liệu

- **Tên bộ dữ liệu:** *UAE Used Car Prices & Features (10K+ Listings)*.
- **Nguồn được ghi trong tài liệu dự án:** Ali Kalwar, Kaggle.
- **Giấy phép được ghi nhận:** CC BY-SA 4.0; giữ thông tin ghi công và điều khoản chia sẻ tương tự khi phân phối lại dữ liệu hoặc bản chuyển thể.
- **Tệp trong repo:** [`data/raw/uae_used_cars_10k.csv`](data/raw/uae_used_cars_10k.csv).
- **Kích thước:** 10.000 dòng, 12 cột: `Make`, `Model`, `Year`, `Price`, `Mileage`, `Body Type`, `Cylinders`, `Transmission`, `Fuel Type`, `Color`, `Location`, `Description`.
- **Ý nghĩa giá:** AED được rao trong tin đăng; không phải giá bán thực tế đã xác nhận.
- **Liên kết Kaggle chính xác:** Nhóm cần bổ sung URL trang dataset gốc nếu giảng viên yêu cầu liên kết trực tiếp. Không tự suy đoán URL.

## Công cụ và thư viện

Python; pandas; NumPy; SQLite và `sqlite3`; Jupyter Notebook; matplotlib; seaborn; Pillow (phương án xuất biểu đồ); pytest; python-docx và python-pptx để tạo tài liệu báo cáo/trình bày.

## Cấu trúc dự án

```text
repository-root/
├── data/
│   ├── raw/                 # CSV nguồn
│   ├── processed/           # Dữ liệu sạch, bảng tổng hợp và kết quả
│   └── bad_data/            # Ghi chú về dữ liệu bất thường
├── database/                # SQLite, schema.sql, queries.sql
├── notebooks/
│   ├── eda/                 # Làm sạch, phân tích, trực quan hóa
│   └── modeling/            # Hồi quy baseline
├── docs/
│   ├── figures/             # PNG/SVG
│   ├── Final_ADY201m_Report.docx
│   ├── Final_ADY201m_Report.md
│   ├── ADY201m_Project_Presentation.pptx
│   └── PROJECT_CHARTER.md
├── scripts/                 # Làm sạch, SQL/SQLite, phân tích, mô hình
├── tests/                   # Kiểm thử pipeline
├── .github/                 # Mẫu issue và pull request
├── CONTRIBUTING.md
├── TEAM.md
└── README.md
```

## Công việc đã hoàn thành

- Đã kiểm tra 10.000 dòng và 12 cột; không có dòng trùng hoàn toàn trong CSV nguồn.
- Đã làm sạch và chuẩn hóa dữ liệu; 155 giá trị `Cylinders` thiếu/không rõ được giữ là thiếu. Có 9.869 giá trị `Location` có khoảng trắng thừa trong CSV thô.
- Đã tạo cơ sở dữ liệu SQLite gồm bảng tin đăng và các bảng chiều hãng, kiểu thân xe, tiểu vương quốc; có schema và truy vấn mẫu.
- Đã tạo thống kê mô tả, bảng giá theo nhóm, notebook, biểu đồ, báo cáo và bản trình bày.
- Giá trung bình là 245.234,51 AED; trung vị 102.766 AED; lớn nhất 14.686.975 AED.
- Trung vị SUV là 118.414 AED (n=4.607), Sedan là 70.287,50 AED (n=2.790); kiểm định Mann–Whitney U xấp xỉ cho p ≈ 1,44×10⁻⁷².
- Baseline hồi quy log-price dùng Year + Mileage có R² kiểm tra = −0,079 và MAE ≈ 193.896 AED; chưa phù hợp để định giá xe.

## Thành viên và phân công

Roster và phân công dự kiến nằm trong [`TEAM.md`](TEAM.md). Mỗi thành viên cần dùng tài khoản cá nhân để commit hoặc mở pull request; chỉ cập nhật bằng chứng sau khi hoạt động GitHub thực tế được ghi nhận.

| Vai trò | Trách nhiệm | Thành viên / GitHub username |
| --- | --- | --- |
| Dữ liệu và làm sạch | Nguồn, chất lượng, pipeline và data dictionary | Nguyễn Văn Tuấn — `TUANNV0301` (HE204537) |
| SQL và cơ sở dữ liệu | SQLite, schema, truy vấn và kiểm tra kết quả | Lê Huy Cường — `CuongLH02` (HE204406) |
| EDA, mô hình và báo cáo | Notebook, biểu đồ, baseline, báo cáo và slide | Đào Phương Vinh — `daophuongvinh4` (HE204851) |

Một thành viên có thể đảm nhận nhiều vai trò nếu quy mô nhóm nhỏ.

## Bằng chứng đóng góp

Chỉ ghi nhận đóng góp sau khi có commit hoặc pull request thực tế từ đúng tài khoản cá nhân. Bổ sung liên kết commit/PR và mô tả phần việc vào [`TEAM.md`](TEAM.md); không dùng tài khoản chung và không coi bảng phân công dự kiến là bằng chứng hoàn thành.

| Thành viên | Bằng chứng GitHub | Phần việc đã hoàn tất |
| --- | --- | --- |
| Nguyễn Văn Tuấn (`TUANNV0301`) | Chờ commit/PR | Chưa ghi nhận hoạt động GitHub |
| Lê Huy Cường (`CuongLH02`) | Chờ commit/PR | Chưa ghi nhận hoạt động GitHub |
| Đào Phương Vinh (`daophuongvinh4`) | Chờ commit/PR | Chưa ghi nhận hoạt động GitHub |

## Cài đặt và chạy lại

Tại thư mục gốc repository:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/database/database_setup.py
python scripts/clean/clean_cars.py
python scripts/analysis/generate_figures.py
python scripts/modeling/evaluate_models.py
pytest tests/ -v
jupyter lab
```

Mở notebook theo thứ tự trong `notebooks/eda/`, sau đó `notebooks/modeling/`. Hướng dẫn nhánh, commit và review nằm trong [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Giới hạn

Giá là giá rao chứ không phải giao dịch; dữ liệu tập trung nhiều ở Dubai; phân phối giá có ngoại lệ lớn; baseline chỉ dùng năm và số km, không có hãng/mẫu và nhiều đặc trưng khác. Diễn giải kết quả trong phạm vi bộ dữ liệu này.
