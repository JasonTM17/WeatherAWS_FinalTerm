# Sơ đồ source và tệp chuẩn

## Cách tổ chức

Repository trình bày theo tuần học. Tuần 1 giữ hồ sơ nền tảng và bộ báo cáo đã nộp; Tuần 2 chứa bộ source dùng chung, dữ liệu của hai sinh viên và phân tích bổ sung. Việc gọi lại module chuẩn giúp hai tuần dùng cùng cách triển khai và kiểm tra.

```text
WeatherAWS_FinalTerm/
  README.md                  Điểm bắt đầu và liên kết báo cáo
  docs/                      Tài liệu chung, kiến trúc, phương pháp, nhật ký
  tuan_1/
    README.md
    docs/                    Báo cáo Word/PDF/Excel, CSV, phân công, nhật ký
    scripts/                 Hai script nền tảng gọi SDK dùng chung
  tuan_2/
    README.md
    lambda/                  Một chương trình thu thập chuẩn
    scripts/                 SDK, bộ xuất CSV và các điểm vào PowerShell
    athena/                  Một bảng gốc, một view, năm SELECT, 12 SELECT Tuần 2
    analytics/               Phân tích, dựng hình và hồi quy phân tích
    tests/                   Bốn module kiểm tra chức năng chuẩn
    docs/                    Báo cáo Word/PDF/Excel và nhật ký Tuần 2
    results/                 Bộ đầu vào, kết quả và metadata đã lưu
```

## Tệp chuẩn và điểm vào dùng lại

| Chức năng | Tệp chuẩn | Điểm vào dùng lại |
| --- | --- | --- |
| Thu thập | [lambda_function.py](../tuan_2/lambda/lambda_function.py) | EventBridge gọi `lambda_handler` |
| Quản lý dịch vụ | [aws_project.py](../tuan_2/scripts/aws_project.py) | Các `.ps1` ở hai tuần chuyển tham số tới SDK |
| Xuất năm SELECT | [athena_export.py](../tuan_2/scripts/athena_export.py) | `export_csv.ps1`, `export_metrics.py`; `export_raw_records.py` xuất riêng raw |
| Lược đồ | [Danh mục Athena](../tuan_2/athena/README.md) | SDK đọc đúng một DDL bảng gốc và một DDL view |
| Bốn hình Tuần 1 | [generate_charts.py](../tuan_2/analytics/generate_charts.py) | Đọc `results/athena_queries/` |
| Phân tích Tuần 2 | [analyze_week2_accounts.py](../tuan_2/analytics/analyze_week2_accounts.py) | Đọc CSV và hồ sơ nguồn của từng sinh viên |
| 18 hình Tuần 2 | [generate_week2_charts.py](../tuan_2/analytics/generate_week2_charts.py) | Đọc `results/week2_analysis/`; dùng helper so sánh tuần |
| Kiểm tra chức năng | [tuan_2/tests/](../tuan_2/tests/) | Bốn module kiểm tra Lambda, SDK, CSV và biểu đồ |

`lambda` được giữ làm tên thư mục chứa gói triển khai, không dùng làm tên Python package để import. Chạy các chương trình bằng đường dẫn tệp từ thư mục gốc, như [hướng dẫn source](source-guide.md).

## Dữ liệu và tệp tạo ra

[Danh mục kết quả](../tuan_2/results/README.md) giải thích từng tập dữ liệu, các bản sao cùng số liệu và đường từ CSV tới hình. Báo cáo Word/PDF/Excel là sản phẩm nộp; bản Markdown `FINAL_REPORT.md` giúp đọc nội dung trên GitHub. Hình PNG dùng trong báo cáo vẫn được theo dõi để có thể xem mà không cần chạy Python.

Các lượt xuất tùy chọn nên ghi vào `output/`, được Git bỏ qua. Cache Python, tệp tạm Office, gói triển khai Lambda và thư mục làm báo cáo tạm cũng được bỏ qua. Tệp CSV ZIP cũ được giữ ở máy; repo cung cấp thư mục CSV đã giải nén để xem trực tiếp.

## Phụ thuộc và kiểm tra

- [tuan_2/analytics/requirements.txt](../tuan_2/analytics/requirements.txt): boto3, NumPy và Matplotlib để chạy SDK, phân tích, biểu đồ và các kiểm tra chức năng.
- `tuan_2/lambda/requirements.txt`: boto3 để phát triển cục bộ; runtime Lambda cung cấp SDK và các thư viện chuẩn được source sử dụng.
- Các lệnh kiểm tra nằm trong [hướng dẫn đọc source](source-guide.md). Kiểm tra SDK/API giả lập xác nhận cách xử lý cục bộ; phạm vi vận hành được đối chiếu riêng từ hồ sơ dữ liệu đã lưu.

[Trở về tài liệu dự án](README.md) · [Nhật ký và số giờ](WORKLOG.md)
