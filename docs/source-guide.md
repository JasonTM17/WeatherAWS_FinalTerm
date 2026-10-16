# Hướng dẫn đọc mã nguồn đồ án

Đề tài: thu thập và phân tích thời tiết, chất lượng không khí trên AWS. Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051), lớp 261CLCO332779_05.

## Thứ tự đọc

[Sơ đồ mã nguồn](repository-layout.md) xác định tệp chuẩn và các điểm vào dùng lại giữa hai tuần. [Danh mục SQL](../tuan_2/athena/README.md) nêu thứ tự tạo bảng và view; [danh mục dữ liệu](../tuan_2/results/README.md) phân biệt các bộ đầu vào đã lưu.

| Khu vực | Tệp chính | Trách nhiệm |
| --- | --- | --- |
| Thu thập | [Lambda](../tuan_2/lambda/lambda_function.py) | Đọc cấu hình, gọi Open-Meteo, chuẩn hóa bản ghi, cảnh báo SNS và lưu NDJSON trên S3 |
| Dịch vụ | [Python SDK](../tuan_2/scripts/aws_project.py) | Thiết lập S3, Secret, SNS, Lambda, EventBridge, Glue/Athena và CloudWatch |
| Lược đồ | [DDL Athena](../tuan_2/athena/create_table.sql) | 20 cột dữ liệu và ba khóa phân vùng year/month/day |
| Xuất dữ liệu | [Athena exporter](../tuan_2/scripts/athena_export.py) | Chờ truy vấn thành công, tải CSV đúng bytes, xử lý phân trang khi cần |
| Phân tích | [Bộ phân tích Tuần 2](../tuan_2/analytics/analyze_week2_accounts.py) | Giữ riêng hai bộ sinh viên, lọc thời gian, tính thống kê, đối chiếu và lưu nguồn |
| Biểu đồ | [Chương trình dựng hình](../tuan_2/analytics/generate_week2_charts.py) | 20 hình từ đúng các CSV phân tích |
| So sánh tuần | [Module đối chiếu trực tiếp](../tuan_2/analytics/weekly_comparison_charts.py) | Kiểm tra phạm vi đầu vào, dựng cột AQI và PM2.5 với cỡ mẫu, đơn vị rõ ràng |
| Kiểm tra | [Kiểm tra chức năng](../tuan_2/tests/) và [kiểm tra phân tích](../tuan_2/analytics/) | API/SDK giả lập và đối chiếu dữ liệu đã lưu, không gọi tài nguyên thật |

Các chương trình PowerShell trong `tuan_1/scripts` và `tuan_2/scripts` chuyển tham số tới chương trình Python chung. Tuần 1 dùng lại phần thiết lập nền tảng; mã Lambda và phân tích chính nằm tại Tuần 2. Bộ kiểm tra chức năng nằm trong `tuan_2/tests/`; các hồi quy phân tích nằm trong `tuan_2/analytics/`.

## Vì sao cấu hình này tạo ra các bảng kết quả

Thiết kế trong [aws_project.py](../tuan_2/scripts/aws_project.py) tạo bucket riêng theo tài khoản, chặn truy cập công khai, mã hóa đối tượng, đặt cấu hình ba đô thị và ngưỡng cảnh báo trong Secrets Manager, rồi nối EventBridge với Lambda, SNS và CloudWatch. Lambda được cấu hình Python 3.12, 256 MB và 60 giây. Đây là lựa chọn để lưu bản ghi riêng theo môi trường, chạy theo lịch và quan sát lỗi; số lịch thực tế của mỗi sinh viên được đọc từ metadata đã lưu, không suy ra từ tham số lịch mặc định trong source.

[lambda_function.py](../tuan_2/lambda/lambda_function.py) lấy dữ liệu khí tượng và chất lượng không khí bằng hai yêu cầu cho từng đô thị, chuẩn hóa 23 trường, gắn cả giờ UTC và giờ Việt Nam, rồi ghi NDJSON theo ngày UTC. Nhánh `backfill_hours` phục vụ chuỗi lịch sử; nhánh hiện tại kiểm tra AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³ để yêu cầu gửi thông báo. Giá trị mặc định 0 cho đầu vào không hợp lệ chỉ là quy tắc chuẩn hóa, nên bảng kiểm tra chất lượng dữ liệu không chứng minh API chưa từng thiếu số đo.

[Bảng Athena](../tuan_2/athena/create_table.sql) khai báo 20 cột dữ liệu và ba khóa phân vùng. [Truy vấn raw Tuần 2](../tuan_2/athena/week2_analysis/raw_week2.sql) vừa lọc phân vùng vừa kiểm tra thời điểm UTC để khớp ranh giới UTC+7. Bởi vậy 27/57 dòng thuộc Tuần 2 được tách ra khỏi 204/231 dòng toàn bộ. Cặp [truy vấn chỉ lọc thời gian](../tuan_2/athena/week2_analysis/scan_week2_time_only.sql) và [truy vấn thêm phân vùng](../tuan_2/athena/week2_analysis/scan_week2_partition.sql) trả cùng số dòng nhưng có số byte quét khác nhau; thời gian thực thi được diễn giải theo từng lần đo.

[AthenaExporter](../tuan_2/scripts/athena_export.py) chỉ thay CSV đích sau khi truy vấn thành công và lấy được kết quả. [Bộ phân tích](../tuan_2/analytics/analyze_week2_accounts.py) đối chiếu bản ghi S3 với CSV Athena, giữ lượt ghi gốc của hai sinh viên riêng, tính trung bình và độ lệch chuẩn theo từng đô thị, rồi so với bảng SQL. Bộ phân tích cũng tạo [bảng theo đô thị và giờ](../tuan_2/results/week2_analysis/hourly_city.csv): 27 nhóm cho mỗi sinh viên từ 27/57 lượt ghi, và 21 nhóm cùng giờ được dùng để đối chiếu. [Chương trình dựng hình](../tuan_2/analytics/generate_week2_charts.py) dùng các CSV này và ghi đường dẫn nguồn trong manifest. Mối liên hệ từ quyết định trong mã đến các giá trị 9/19 lượt ghi mỗi đô thị, AQI Hà Nội 163,56/163,05 và mức giảm byte quét được giải thích đầy đủ tại Chương 6 của [báo cáo Tuần 2](../tuan_2/docs/FINAL_REPORT.md). Mức dự kiến 0,05 USD cho sinh viên Tiến Sơn và 0,03 USD cho sinh viên Ngọc Quyên do nhóm xác nhận; chúng không phải phép tính của mã nguồn hoặc giá trị Cost Explorer.

`export_metrics.py` là điểm vào tương thích để xuất năm truy vấn SELECT. Khi xuất kết quả mới, chỉ định `--output output/athena` để giữ riêng dữ liệu báo cáo đã lưu; điểm vào chính là `scripts/athena_export.py`. Các chương trình dựng hình ghi vào thư mục kết quả của tuần tương ứng, nên việc tái lập hình có thể làm thay đổi tệp PNG/manifest được Git theo dõi.

`generate_week2_charts.py` chỉ đọc dữ liệu và ghi hình khi gọi `main()` hoặc chạy trực tiếp tệp. Import module để kiểm tra hoặc dùng lại hàm sẽ không tạo hay thay hình báo cáo.

## Luồng dữ liệu và hợp đồng đầu vào

1. EventBridge gọi lambda_handler với sự kiện mặc định để thu thập hiện tại. Sự kiện có backfill_hours yêu cầu chuỗi lịch sử.
2. fetch_secrets đọc danh sách đô thị và ngưỡng. Khi dịch vụ trả lỗi, chương trình dùng cấu hình dự phòng ba đô thị.
3. fetch_city_data gọi API chất lượng không khí và thời tiết. Các phản hồi phải có khối current với ít nhất một trường đo được yêu cầu. fetch_historical_series yêu cầu khối hourly cùng danh sách thời gian không rỗng ở cả hai API, rồi ghép hai chuỗi bằng timestamp. Khối bị thiếu hoặc chỉ có metadata sẽ phát sinh lỗi; các trường đo có tên nhưng mang giá trị null vẫn dùng chính sách mặc định được nêu dưới đây.
4. safe_float/safe_int giữ số hợp lệ và dùng giá trị mặc định cho đầu vào không chuyển đổi được hoặc không hữu hạn. get_aqi_category trả Unknown khi AQI thiếu, không hợp lệ, không hữu hạn hoặc âm. Giá trị mặc định số 0 là chính sách chuẩn hóa của mã nguồn, không xác nhận API đã cung cấp một giá trị môi trường bằng 0.
5. Chế độ hiện tại phát cảnh báo khi AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³. Đây là ngưỡng cấu hình của dự án. Publish được chấp nhận không xác nhận người nhận đã đọc email.
6. save_records_to_s3 nhóm theo ngày UTC và ghi một dòng JSON cho mỗi bản ghi. timestamp_vn dùng để hiển thị giờ Việt Nam; khóa phân vùng vẫn theo UTC.
7. Nếu mọi đô thị thu thập thất bại, handler phát sinh lỗi. Nếu một phần thất bại, đầu ra giữ failed_cities và collection_status=partial, kèm số bản ghi và tệp đã lưu.

Ở chế độ lịch sử, `timestamp_utc` là thời điểm dữ liệu từ API, `timestamp_vn` là thời điểm đó cộng bảy giờ và `collected_at` là thời điểm chương trình tiếp nhận chuỗi dữ liệu. Timestamp không kèm múi giờ được hiểu là UTC; timestamp có offset được chuyển về UTC trước khi xác định phân vùng. Ở chế độ hiện tại, mã đang dùng thời điểm thu thập để gắn `timestamp_utc`/`timestamp_vn`; các trường này không lưu riêng thời gian cập nhật `current.time` của API.

Mã hiện tại đã sửa việc gán `collected_at` bằng thời điểm dữ liệu lịch sử và việc thay offset trực tiếp bằng UTC. Các bản ghi trong CSV đã lưu giữ nguyên giá trị của phiên bản đã tạo ra chúng; không sửa hồi tố metadata hoặc thời gian để làm giống mã mới. Hai hồi quy kiểm tra riêng thời điểm thu thập và chuyển ngày/phân vùng khi timestamp có offset. Commit `36c9b39` đã được triển khai lên cả hai Lambda; module tải lại khớp source, lượt lịch sử xác nhận `collected_at` thực tế và các lượt hiện tại ghi S3, phát SNS thành công. Chi tiết và giới hạn xác nhận nằm trong [minh chứng triển khai](deployment-verification.md).

Khi được gọi trong Lambda, thời gian chờ HTTP được tính lại trước mỗi request: tối đa 15 giây và không vượt thời gian còn lại trừ 10 giây dành cho kết thúc/lưu dữ liệu. Khi không còn thời gian thu thập, chương trình dừng các request tiếp theo và giữ các đô thị đã thu thập để lưu một phần. Gọi helper trực tiếp với context=None giữ mức chờ 15 giây. Đây là cơ chế điều chỉnh timeout theo thời gian còn lại; thời gian DNS, đọc phản hồi và các lượt gọi SDK/S3 vẫn phụ thuộc dịch vụ, nên không phải bảo đảm thời hạn tuyệt đối cho toàn bộ invocation. Tham khảo [Lambda context](https://docs.aws.amazon.com/lambda/latest/dg/python-context.html) về thời gian còn lại và [urllib.request](https://docs.python.org/3.12/library/urllib.request.html) về phạm vi timeout của thao tác kết nối.

## Xuất CSV và thống kê

- AthenaExporter chỉ thay tệp đích sau khi truy vấn thành công và đọc được kết quả. Chờ quá thời hạn sẽ yêu cầu dừng truy vấn; lỗi thực thi không ghi đè tệp CSV cũ.
- CSV được kiểm tra UTF-8, header có tên cột không rỗng và duy nhất, dấu nháy hợp lệ và số ô khớp số cột. Kết quả không có dòng dữ liệu vẫn hợp lệ nếu có header; trường chứa xuống dòng được đọc theo quy tắc CSV. Bytes của tệp hợp lệ được giữ nguyên khi xuất.
- Tham số --database được áp dụng đồng thời vào ngữ cảnh thực thi và tên cơ sở dữ liệu trong cả năm mẫu SELECT. Mặc định giữ nguyên nội dung SQL đã lưu; tên tùy chọn được bao bằng dấu nháy kép và thoát dấu nháy bên trong theo cú pháp định danh SELECT của [Athena](https://docs.aws.amazon.com/athena/latest/ug/reserved-words.html).
- Nếu tải S3 bị AccessDenied hoặc NoSuchKey, exporter đọc GetQueryResults theo NextToken; giữ vị trí cột, trường NULL rỗng và một hàng tiêu đề.
- Chế độ offline sao chép bộ đã lưu và ghi manifest là saved-snapshot. Chế độ này không được trình bày như truy vấn mới.
- Tuần 2 lọc theo ranh giới tuần UTC+7, rồi quy đổi timestamp_utc về UTC. Trung bình và SD dùng riêng mẫu từng sinh viên/đô thị; SD có mẫu số n−1. Phân vị nội suy tuyến tính; Spearman dùng hạng trung bình khi các giá trị bằng nhau.
- Tương quan chỉ dùng những bản ghi có cả hai biến hữu hạn trong cùng một quan trắc. Số mẫu của từng hệ số là số cặp hợp lệ; không lọc riêng hai cột rồi ghép theo vị trí còn lại.
- submitted_week1_comparison.csv dùng đúng 156 dòng của bộ báo cáo Tuần 1, gồm dữ liệu lịch sử nạp bổ sung. Hai hình mới dùng mốc chung 52 mẫu/đô thị, so với 9/19 mẫu Tuần 2. weekly_comparison.csv là phép lọc từ lần xuất mới, có mốc 42/41 mẫu; hai phạm vi được trình bày riêng.
- Module biểu đồ từ chối thiếu hàng đô thị, lặp khóa sinh viên/đô thị, sai phạm vi, số không hữu hạn và mốc Tuần 1 khác nhau giữa hai bộ sinh viên. Manifest giữ các giá trị thực sự dùng cho cột của hai hình mới.

## Cách kiểm tra và tái lập

Chạy từ thư mục gốc với Python 3.12 trở lên:

```powershell
python -m pip install -r tuan_2/analytics/requirements.txt
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v
python tuan_2/analytics/analyze_week2_accounts.py
python tuan_2/analytics/generate_week1_supplement.py
python tuan_2/analytics/generate_week2_charts.py
```

Matplotlib tối thiểu 3.9 vì mã nguồn dùng tick_labels trong boxplot; tham số này xuất hiện từ phiên bản 3.9 theo [tài liệu Matplotlib](https://matplotlib.org/3.9.2/api/_as_gen/matplotlib.axes.Axes.boxplot.html). Hướng dẫn thao tác tài nguyên nằm trong [vận hành](operation.md).

## Kiểm tra hồ sơ repository

[repository_audit.py](../tuan_2/scripts/repository_audit.py) đối chiếu tổng giờ theo tuần, đường dẫn worklog và Markdown, cấu trúc toàn bộ CSV, danh mục hash và kết quả SQL mới với raw. [Bộ thu thập minh chứng](../tuan_2/scripts/collect_repository_evidence.py) dùng SDK đọc cấu hình và chạy SELECT vào thư mục mới, không triển khai hoặc gọi Lambda. Xem [đợt đọc ngày 16/10](../tuan_2/results/review_2026_10_16/README.md).

```powershell
python tuan_2/scripts/repository_audit.py --check
```

Các lệnh trên chạy năm module kiểm tra chức năng và hồ sơ trong `tuan_2/tests`, cùng bộ kiểm tra phân tích trong `tuan_2/analytics`. Kết quả theo từng commit được ghi tại [GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions); cấu hình nằm trong [workflow](../.github/workflows/verify-repository.yml). Các hồi quy riêng của hồ sơ nằm trong [test_repository_evidence.py](../tuan_2/tests/test_repository_evidence.py).

## Phạm vi minh chứng

Kiểm tra cục bộ dùng SDK/API giả lập và dữ liệu đã lưu. Nó xác nhận nhánh xử lý và phép tính, không chứng minh mã nguồn vừa được triển khai lên AWS. Bộ báo cáo giữ nguyên số liệu gốc.

Lịch thu thập, Alarm và tổng metric có phạm vi thời gian khác nhau. Errors lớn hơn Invocations được giữ nguyên, tỷ lệ lỗi không xác định. Dữ liệu mô hình API và mẫu ngắn không chứng minh xu hướng toàn tuần hoặc quan hệ nhân quả. Không công bố credentials, nội dung Secret, endpoint email hay log thực thi thô trong mã nguồn.
