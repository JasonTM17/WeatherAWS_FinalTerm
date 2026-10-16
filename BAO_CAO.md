# Báo cáo bổ sung tiến độ Tuần 2

**Học phần:** Điện toán đám mây · **Lớp học phần:** 261CLCO332779_05
**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng
**Sinh viên:** Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051)

Repo là hồ sơ chính để xem tiến độ, dữ liệu, mã nguồn và minh chứng. [Hồ sơ chi tiết Tuần 2](tuan_2/README.md) là trang cần mở khi xem phần Tuần 2; trang này tổng hợp các mục và dẫn tới tài liệu nguồn.

- [Repository GitHub](https://github.com/JasonTM17/WeatherAWS_FinalTerm)
- [Hồ sơ Tuần 1](tuan_1/README.md)
- [Hồ sơ Tuần 2](tuan_2/README.md)
- [Worklog tổng hợp dạng CSV](worklog.csv) · [Diễn giải worklog](docs/WORKLOG.md)
- [Mã nguồn và commit theo thành phần](docs/components.md)
- [Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md)

## 1. Phân công và thời lượng

| Sinh viên | Phụ trách chính | Tuần 1 | Tuần 2 | Tổng |
| --- | --- | ---: | ---: | ---: |
| Nguyễn Tiến Sơn (24110054) | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | 9,5 giờ | 10,0 giờ | 19,5 giờ |
| Trần Thị Ngọc Quyên (24110051) | Glue, Athena, xuất CSV, biểu đồ và đối chiếu dữ liệu | 9,0 giờ | 9,5 giờ | 18,5 giờ |
| Cả hai sinh viên | Kiến trúc, tích hợp, đối chiếu và hoàn thiện hồ sơ | 18,5 giờ | 19,5 giờ | 38,0 giờ |

Số giờ được xác nhận theo tuần; worklog không tự chia nhỏ theo ngày hoặc đầu việc. Danh sách sản phẩm và đường dẫn đối chiếu có trong [worklog chi tiết](docs/WORKLOG.md).

## 2. Kết quả dữ liệu Tuần 2

Bảng dưới đây dùng **bộ dữ liệu đã lưu cùng báo cáo Tuần 2**: 27 lượt ghi của sinh viên Tiến Sơn và 57 lượt ghi của sinh viên Ngọc Quyên. Các thống kê theo đô thị và biểu đồ trong hồ sơ Tuần 2 đều truy về bộ này.

| Đô thị | AQI trung bình · Tiến Sơn | AQI trung bình · Ngọc Quyên | PM2.5 trung bình · Tiến Sơn (µg/m³) | PM2.5 trung bình · Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Nguồn: [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv). Xem [phân bố cấp AQI](tuan_2/results/week2_analysis/category_distribution.csv), [raw Tuần 2](tuan_2/results/week2_analysis/raw_week2_both_accounts.csv) và [các biểu đồ cùng manifest nguồn](tuan_2/results/week2_charts/).

Một đợt đọc AWS riêng ngày 16/10/2026 ghi nhận 39 lượt Tuần 2 của sinh viên Tiến Sơn và 75 lượt của sinh viên Ngọc Quyên qua 14 truy vấn SELECT. Bộ mới được lưu riêng tại [hồ sơ kiểm chứng](tuan_2/results/review_2026_10_16/README.md), không thay thế hay gộp vào bộ 27/57 đã dùng trong báo cáo. Các lượt thỏa ngưỡng trong dữ liệu không tự chứng minh thư cảnh báo đã được gửi hoặc nhận.

## 3. Mã nguồn và cách tạo kết quả

[Mã nguồn hiện tại](tuan_2/) gồm hàm thu thập, truy vấn, xuất CSV, phân tích và dựng biểu đồ. [Hướng dẫn mã nguồn](docs/source-guide.md) giải thích vai trò từng phần và cách tái lập các kết quả từ dữ liệu đã lưu.

Đợt kiểm chứng AWS ngày 16/10 cho thấy mã hàm Lambda đang chạy khác mã hiện có trong repo. Vì vậy, hồ sơ mô tả mã nguồn và cấu hình đã đọc được; không khẳng định các thay đổi trong repo đã được triển khai lên hai môi trường.

## 4. Đường dẫn mã nguồn và commit

[Mục lục thành phần](docs/components.md) liên kết mã nguồn trên GitHub và commit liên quan cho Lambda, lịch EventBridge, S3, Secrets Manager, SNS, Glue, Athena, xuất CSV, phân tích, biểu đồ và công cụ kiểm tra hồ sơ.

## 5. Kế hoạch tiếp theo và hồ sơ Tuần 1

[Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md) nêu đầu việc tích hợp, kiểm tra lịch, tối ưu lưu trữ và truy vấn, giám sát, xác minh cảnh báo và tiêu chí nghiệm thu. Đây là kế hoạch; giờ thực hiện và kết quả Tuần 3 sẽ được ghi khi có minh chứng.

[Hồ sơ Tuần 1](tuan_1/README.md) lưu nền tảng dữ liệu gồm 156 lượt ghi, 52 lượt mỗi đô thị, cùng CSV, biểu đồ và worklog Tuần 1. Báo cáo chi tiết và tệp dữ liệu được liên kết trong trang này.

## Kiểm tra repo

[GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions) chạy kiểm tra tính nhất quán của worklog, danh mục CSV, hồ sơ AWS đã lưu, mã nguồn và phân tích dữ liệu. Lệnh kiểm tra tại máy và điều kiện tái lập được ghi ở [README](README.md).
