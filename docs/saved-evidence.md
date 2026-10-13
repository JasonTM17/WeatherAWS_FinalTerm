# Minh chứng vận hành đã lưu

Hồ sơ này tổng hợp các kết quả dịch vụ đã lưu trong dự án. Các mã truy vấn, số dòng, thời gian và dung lượng quét được đối chiếu với CSV hiện dùng trong cả hai báo cáo.

[Mốc mã nguồn của hồ sơ](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/dbe7dd59fbde6f890126ce55241c0c6b0ea911c9) · [Dữ liệu minh chứng](saved-evidence.json) · [Kết quả Athena](../tuan_2/results/athena_queries/)

## Kết quả xử lý

| Hạng mục | Kết quả trong hồ sơ |
| --- | --- |
| Vùng dịch vụ | us-east-1 |
| Hàm Lambda | WeatherCollectorLambda; trạng thái Active |
| Cấu hình hàm | Python 3.12; 256 MB; giới hạn 60 giây |
| Phản hồi xử lý | Mã 200; 3 bản ghi thu thập |
| Thông báo | Hàm ghi nhận 2 cảnh báo gửi tới SNS |
| Đăng ký nhận email | pending confirmation trong hồ sơ; chưa xác nhận email được nhận |

## Truy vấn đã đối chiếu

| Truy vấn | Mã thực thi | Trạng thái | Dòng | Thời gian ms | Quét byte |
| --- | --- | --- | ---: | ---: | ---: |
| avg_aqi_by_city | c2fddbda-2bad-424f-b9f9-02773d5b3df4 | SUCCEEDED | 3 | 744 | 87250 |
| peak_pollution_hours | 8018524b-c34e-47ed-bb89-c05e7db88bd1 | SUCCEEDED | 24 | 936 | 87250 |
| aqi_category_distribution | ec8641a0-c706-45fb-bc8c-4f1d72d1978a | SUCCEEDED | 8 | 776 | 87250 |
| weather_correlation | 14bb410d-4725-45f3-bb5d-59ddf4c962cb | SUCCEEDED | 3 | 930 | 87250 |
| raw_weather_aqi_records | d67cd503-1d5a-487a-98dd-b46a111b2f43 | SUCCEEDED | 156 | 1192 | 87250 |

Bộ dữ liệu phân tích gồm 156 bản ghi và 52 mẫu cho mỗi đô thị. Số bản ghi của một lượt Lambda (3) và số bản ghi của tập phân tích tích lũy (156) là hai đại lượng khác nhau.

## Phạm vi xác nhận

Hồ sơ đã lưu ghi nhận lượt xử lý và các kết quả truy vấn tại mốc triển khai tương ứng. Mã nguồn đã được chỉnh sửa sau mốc đó; hồ sơ này không tự xác nhận một lần triển khai hoặc chạy mới của phiên bản hiện tại. Các bảng và biểu đồ tiếp tục dùng đúng CSV đã lưu.

Secrets Manager quản lý vị trí và ngưỡng cấu hình. Lời gọi Open-Meteo sử dụng API công khai; hồ sơ không chứa một khóa nhà cung cấp thực tế.
