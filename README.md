# Hệ thống thu thập, lưu trữ và phân tích dữ liệu thời tiết và chất lượng không khí

Đồ án thực hành học phần **Điện toán đám mây**: xây dựng luồng thu thập dữ liệu thời tiết và chất lượng không khí từ API công khai, lưu bản ghi thô trên Amazon S3, truy vấn bằng Amazon Athena, sau đó tổng hợp kết quả thành CSV và biểu đồ có thể đối chiếu với dữ liệu đầu vào.

| Thông tin | Chi tiết |
| --- | --- |
| Học phần | Điện toán đám mây, Cloud – Đợt 1, năm học 2026–2027 |
| Lớp | 261CLCO332779_05 |
| Giảng viên hướng dẫn | ThS. Huỳnh Xuân Phụng |
| Sinh viên thực hiện | Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051) |
| Khu vực dữ liệu | TP. Hồ Chí Minh, Hà Nội và Đà Nẵng |
| Nguồn dữ liệu | [Open-Meteo Weather API](https://open-meteo.com/en/docs) và [Air Quality API](https://open-meteo.com/en/docs/air-quality-api) |

## Điều hướng nhanh

| Nội dung | Tài liệu hoặc dữ liệu |
| --- | --- |
| Hồ sơ Tuần 1 | [Trang Tuần 1](tuan_1/README.md) · [PDF](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.pdf) · [Word](tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_24110054_24110051.docx) · [Excel](tuan_1/docs/Bao_cao_tuan_1_Du_lieu_Athena_24110054_24110051.xlsx) |
| CSV Tuần 1 | [Sáu CSV đã dùng trong báo cáo](tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/) · [Chín biểu đồ](tuan_2/results/charts/) |
| Hồ sơ Tuần 2 | [Trang Tuần 2](tuan_2/README.md) · [PDF](tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.pdf) · [Word](tuan_2/docs/Bao_cao_Tuan_2_24110054_24110051.docx) · [Excel](tuan_2/docs/Du_lieu_phan_tich_Tuan_2_24110054_24110051.xlsx) |
| CSV và hình Tuần 2 | [CSV Athena đã lưu](tuan_2/results/week2_live/) · [27 bảng phân tích](tuan_2/results/week2_analysis/) · [20 biểu đồ](tuan_2/results/week2_charts/) · [Raw và metadata](tuan_2/results/week2_evidence/) |
| Phân công và thời gian | [Worklog tổng hợp](docs/WORKLOG.md) · [CSV worklog](worklog.csv) |
| Kiến trúc và mã nguồn | [Sơ đồ kiến trúc](docs/architecture.md) · [Hướng dẫn đọc mã](docs/source-guide.md) · [Cấu trúc repository](docs/repository-layout.md) · [Chỉ mục thành phần và commit](docs/components.md) |
| Phương pháp và kiểm chứng | [Phân tích dữ liệu](docs/data-analysis.md) · [Vận hành](docs/operation.md) · [Danh mục CSV và SHA-256](docs/csv_catalog.csv) |
| AWS và kế hoạch tiếp theo | [Snapshot AWS ngày 16/10/2026](tuan_2/results/review_2026_10_16/README.md) · [Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md) |

[Phạm vi](#mục-tiêu-và-phạm-vi) · [Luồng xử lý](#luồng-xử-lý-dữ-liệu) · [Mô hình và phương pháp](#mô-hình-dữ-liệu-và-phương-pháp) · [Kết quả từng tuần](#kết-quả-theo-tuần) · [Mã nguồn](#cấu-trúc-mã-nguồn) · [Cài đặt và kiểm tra](#cài-đặt-và-kiểm-tra) · [Giới hạn minh chứng](#giới-hạn-và-cách-diễn-giải)

## Mục tiêu và phạm vi

Dự án trình bày một quy trình xử lý dữ liệu đầu-cuối ở quy mô học phần:

- Thu thập các trường thời tiết và chất lượng không khí cho ba đô thị từ Open-Meteo.
- Lưu kết quả thu thập ở định dạng NDJSON trên S3, tổ chức theo ngày để có thể truy vấn theo phân vùng.
- Dùng Glue Data Catalog và Athena để đọc dữ liệu, lọc theo thời gian và xuất kết quả truy vấn.
- Dùng Python để kiểm tra dữ liệu, tính thống kê mô tả, ghép các khung giờ có thể so sánh và tạo biểu đồ.
- Ghi nhận cấu hình cảnh báo theo ngưỡng của đồ án bằng SNS và theo dõi các chỉ số Lambda bằng CloudWatch.

Repository gồm mã nguồn, truy vấn SQL, nhật ký công việc, các bộ dữ liệu đã lưu, báo cáo Word/PDF/Excel và biểu đồ. Các đầu ra được tách theo từng mốc để người đọc truy vết từ bản ghi gốc, qua kết quả truy vấn và bảng phân tích, đến CSV nguồn của từng biểu đồ.

Dự án **không** coi dữ liệu API là phép đo trực tiếp tại trạm, không xem một mẫu ngắn là đại diện cho toàn bộ tuần và không suy luận quan hệ nhân quả từ tương quan. Các giới hạn cụ thể được nêu ở [phần diễn giải dữ liệu](#giới-hạn-và-cách-diễn-giải) và trong [tài liệu phương pháp](docs/data-analysis.md).

## Luồng xử lý dữ liệu

![Sơ đồ kiến trúc hệ thống](docs/architecture.png)

| Bước | Thành phần | Trách nhiệm và đầu ra |
| --- | --- | --- |
| 1 | EventBridge | Phát sự kiện theo lịch để gọi hàm thu thập. Cấu hình trong mã nguồn dùng lịch định kỳ một giờ; trạng thái thực tế được ghi riêng trong snapshot AWS. |
| 2 | Secrets Manager | Cung cấp cấu hình cần cho tiến trình như danh sách đô thị và ngưỡng cảnh báo; giá trị Secret không được lưu trong repository. |
| 3 | Lambda và Open-Meteo | Gọi API thời tiết và API chất lượng không khí cho từng đô thị, kiểm tra cấu trúc phản hồi, chuẩn hóa trường dữ liệu và tính cấp AQI. |
| 4 | Amazon S3 | Lưu bản ghi JSON theo dòng (NDJSON). Khóa phân vùng năm/tháng/ngày được xác định theo UTC; thời gian Việt Nam được giữ riêng để trình bày. |
| 5 | Glue Data Catalog và Athena | Đăng ký lược đồ/phân vùng, chạy SQL trên dữ liệu gốc và trả kết quả truy vấn CSV. Truy vấn theo tuần dùng cả điều kiện phân vùng và mốc timestamp. |
| 6 | Các chương trình Python | Đọc dữ liệu gốc và kết quả truy vấn đã lưu, đối chiếu số dòng, tính thống kê, lưu CSV phân tích và tạo PNG. Manifest biểu đồ ghi nhận bảng đầu vào. |
| 7 | SNS và CloudWatch | SNS tiếp nhận thông điệp khi dữ liệu vượt ngưỡng cấu hình. CloudWatch lưu metric và trạng thái alarm; phản hồi Publish không tự xác nhận email đã được nhận. |

### Một số quyết định thiết kế

- **Phân vùng theo UTC:** giữ đường dẫn S3 ổn định giữa các môi trường. Khi báo cáo dùng tuần theo UTC+7, SQL chuyển mốc thời gian tương ứng và kiểm tra timestamp bên cạnh điều kiện partition.
- **Giữ dữ liệu gốc và bảng dẫn xuất riêng:** số lượt ghi ban đầu không bị thay bằng số liệu tổng hợp. Bảng theo giờ và biểu đồ là đầu ra dẫn xuất, có thể truy vết về CSV nguồn tương ứng.
- **Ghi nhận thu thập một phần:** nếu chỉ một số đô thị thất bại, phản hồi có trạng thái `partial` và danh sách đô thị lỗi; lỗi toàn bộ được báo riêng thay vì trình bày như một lần thu thập đủ.
- **Bảo vệ CSV cũ khi xuất lỗi:** Athena exporter chỉ thay tệp đích khi truy vấn thành công và kết quả đọc được; lỗi hoặc timeout không ghi đè bản CSV trước đó.
- **So sánh theo thời điểm ghép được:** với Tuần 2, mỗi bộ dữ liệu được gom theo đô thị và giờ UTC trước khi ghép. Cách này cho mỗi giờ cùng trọng số, trong khi vẫn giữ nguyên các lượt ghi ban đầu trong dữ liệu gốc.
- **Theo dõi nguồn của biểu đồ:** manifest ghi tên CSV và dữ liệu dùng cho từng hình, giúp so sánh hình trong Word với bảng CSV thay vì dựng hai kết quả độc lập.

Chi tiết về xử lý lỗi API, timeout theo thời gian Lambda còn lại, xuất CSV và các hàm tính thống kê nằm trong [hướng dẫn đọc mã nguồn](docs/source-guide.md).

## Mô hình dữ liệu và phương pháp

### Trường dữ liệu và mốc thời gian

Bản ghi thu thập có 23 trường đầu ra. Lược đồ Athena gồm 20 cột dữ liệu cùng ba khóa phân vùng `year`, `month`, `day`. Các trường mô tả đô thị/tọa độ, timestamp UTC và giờ địa phương, chỉ số thời tiết, chất ô nhiễm, US AQI/cấp AQI và thông tin thu thập.

Mốc thời gian chất lượng không khí từ API không kèm múi giờ được diễn giải là UTC. Thời gian có offset trong metadata dịch vụ được đổi về UTC trước khi lọc. Phạm vi tuần dùng UTC+7: bộ Tuần 2 lọc từ **12/10/2026 00:00** đến trước **19/10/2026 00:00**, nhưng các bản ghi đã lưu trong mẫu chỉ nằm ở hai ngày 13–14/10.

### Quy tắc tổng hợp

- Thống kê mô tả theo lượt ghi tính trung bình và độ lệch chuẩn mẫu với mẫu số `n−1` trong từng đô thị và từng bộ dữ liệu.
- Bảng đối chiếu trực tiếp gộp theo đô thị–giờ UTC trước, sau đó so sánh các giờ cùng xuất hiện. Trong bộ Tuần 2 đã lưu, có 27 nhóm giờ ở mỗi sinh viên và 21 nhóm ghép được, tức bảy giờ cho mỗi đô thị.
- Nhiều lượt ghi trong cùng đô thị–giờ được giữ nguyên trong tệp dữ liệu gốc. Việc tính trung bình theo giờ chỉ áp dụng cho bảng đối chiếu theo giờ; không xóa hay làm giảm số dòng gốc.
- Các phân vị sử dụng nội suy tuyến tính. Tương quan Pearson/Spearman mô tả tập mẫu; kích thước mẫu và cách xử lý giá trị bằng nhau được lưu trong các bảng liên quan.
- Tỷ lệ vượt ngưỡng dùng số lượt trong cùng đô thị/bộ dữ liệu làm mẫu số. Tỷ lệ này không phải tỷ lệ thời gian của cả tuần.
- Giá trị không hợp lệ/không hữu hạn được xử lý theo chính sách chuẩn hóa của mã nguồn. Một số trường số có giá trị mặc định bằng 0; vì vậy số 0 trong dữ liệu dẫn xuất không tự chứng minh API đã trả về phép đo bằng 0.
- Nếu tổng Errors trong cửa sổ CloudWatch lớn hơn Invocations, tỷ lệ lỗi không được tính. Báo cáo giữ trạng thái chưa xác định thay vì tạo tỷ lệ vượt 100%.

### Chi phí

Mức dự kiến cho phần thực hành Tuần 2 được sinh viên xác nhận riêng: **0,05 USD** cho sinh viên Tiến Sơn và **0,03 USD** cho sinh viên Ngọc Quyên. Đây không phải kết quả do mã phân tích tự tính. Cost Explorer trả số ước tính hiển thị đến cent lần lượt **0,00 USD** và **0,03 USD**; CSV vẫn giữ giá trị gốc, đơn vị và cờ Estimated. Hai loại số liệu không được cộng gộp hay coi là cùng một nguồn. Xem [giải thích phương pháp và chi phí](docs/data-analysis.md).

## Kết quả theo tuần

### Tuần 1: nền tảng và bộ dữ liệu ban đầu

Bộ CSV dùng trong báo cáo có **156 dòng**, tương ứng **52 dòng cho mỗi đô thị**, cùng sáu CSV báo cáo và chín biểu đồ. Trong 156 dòng của snapshot này, **51 dòng là dữ liệu lịch sử trước ranh giới tuần** và **105 dòng nằm trong ranh giới Tuần 1 theo UTC+7**. Vì vậy, con số 156 mô tả bộ đầu vào đã nộp, không có nghĩa cả 156 lượt đều được thu trong tuần.

- [Trang hồ sơ Tuần 1](tuan_1/README.md) giải thích mục tiêu, phạm vi, bảng kết quả và nguồn CSV.
- [CSV gốc và bảng truy vấn](tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/) là bộ được dùng để lập báo cáo.
- [Chín hình Tuần 1](tuan_2/results/charts/) có manifest và các bảng mở rộng tương ứng.
- Worklog ghi **9,5 giờ** cho sinh viên Tiến Sơn và **9,0 giờ** cho sinh viên Ngọc Quyên.

### Tuần 2: hai bộ báo cáo dữ liệu

Tuần 2 giữ riêng bộ dữ liệu của **sinh viên Tiến Sơn** và **sinh viên Ngọc Quyên**. Trong bộ báo cáo đã lưu, sinh viên Tiến Sơn có 204 dòng toàn bộ, trong đó 27 dòng thuộc phạm vi Tuần 2; sinh viên Ngọc Quyên có 231 dòng toàn bộ, trong đó 57 dòng thuộc phạm vi Tuần 2. Khi gom theo đô thị–giờ UTC, mỗi bộ có 27 nhóm. Các tệp dữ liệu gốc vẫn giữ nguyên cả 27 và 57 lượt ghi; phép so sánh trực tiếp dùng 21 nhóm giờ chung.

Kết quả dưới đây lấy từ **bộ báo cáo đã lưu 27/57**, không lấy từ lần đọc AWS mới ngày 16/10. Mỗi sinh viên có mẫu ở hai ngày và chín khung giờ; không suy rộng thành số liệu đủ bảy ngày.

| Đô thị | AQI trung bình – sinh viên Tiến Sơn | AQI trung bình – sinh viên Ngọc Quyên | PM2.5 trung bình – sinh viên Tiến Sơn (µg/m³) | PM2.5 trung bình – sinh viên Ngọc Quyên (µg/m³) |
| --- | ---: | ---: | ---: | ---: |
| TP. Hồ Chí Minh | 78,00 | 79,05 | 23,38 | 22,92 |
| Hà Nội | 163,56 | 163,05 | 76,66 | 75,11 |
| Đà Nẵng | 35,44 | 35,37 | 6,38 | 6,46 |

Nguồn: [city_statistics.csv](tuan_2/results/week2_analysis/city_statistics.csv). Trong mẫu đã lưu, AQI trung bình ở Hà Nội cao nhất; phân loại tương ứng trong bộ mẫu là Unhealthy ở Hà Nội, Moderate tại TP. Hồ Chí Minh và Good ở Đà Nẵng. Phân loại/tỷ lệ được tính trên mẫu từng đô thị, không phải tuyên bố về chất lượng không khí cả tuần.

![AQI trung bình theo đô thị trong bộ Tuần 2 đã lưu](tuan_2/results/week2_charts/02_aqi_city.png)

Các đầu ra chi tiết gồm [27 CSV phân tích](tuan_2/results/week2_analysis/), [20 biểu đồ có manifest nguồn](tuan_2/results/week2_charts/), [CSV truy vấn Athena](tuan_2/results/week2_live/) và [dữ liệu gốc/metadata](tuan_2/results/week2_evidence/). Báo cáo Tuần 2 có phụ lục **84 dòng dữ liệu gốc** trong phạm vi tuần, chia thành hai bảng theo từng sinh viên.

### Phân công và thời gian đã xác nhận

| Sinh viên | Phần việc chính | Tuần 1 | Tuần 2 | Tổng |
| --- | --- | ---: | ---: | ---: |
| Nguyễn Tiến Sơn (24110054) | S3, Secrets Manager, Lambda và SNS; phối hợp lịch và giám sát | 9,5 giờ | 10,0 giờ | 19,5 giờ |
| Trần Thị Ngọc Quyên (24110051) | Glue, Athena, xuất CSV, biểu đồ và đối chiếu dữ liệu | 9,0 giờ | 9,5 giờ | 18,5 giờ |
| Cả hai sinh viên | Kiến trúc, tích hợp và hoàn thiện hồ sơ | 18,5 giờ | 19,5 giờ | 38,0 giờ |

Số giờ là tổng theo tuần đã được xác nhận; không chia ngược thành giờ từng ngày từ lịch sử commit. Đối chiếu công việc và sản phẩm tại [worklog có minh chứng](docs/WORKLOG.md).

## Snapshot AWS ngày 16/10/2026

Đây là lần đọc trạng thái riêng, không thay đầu vào của báo cáo và biểu đồ Tuần 2 đã lưu. Hồ sơ ghi 13 nhóm kiểm tra metadata cho mỗi sinh viên và **14/14 truy vấn SELECT thành công**.

| Hạng mục đọc được | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| CSV toàn bộ / thuộc Tuần 2 | 216 / 39 dòng | 249 / 75 dòng |
| Lambda | Active, Python 3.12, 256 MB, timeout 60 giây | Active, Python 3.12, 256 MB, timeout 60 giây |
| Mã Lambda trên AWS so với mã nguồn trong repository | Khác | Khác |
| S3 và Glue | AES256, chặn truy cập công khai; 6 phân vùng Glue | AES256, chặn truy cập công khai; 6 phân vùng Glue |
| Lịch EventBridge đang bật | 1 | 2 |
| SNS | 1 đăng ký email đã xác nhận | 2 đăng ký email đã xác nhận |
| CloudWatch Alarm | INSUFFICIENT_DATA | INSUFFICIENT_DATA |

Trong cửa sổ metric đã truy vấn, tổng Errors lớn hơn tổng Invocations; nguyên nhân chưa được kết luận và không tính tỷ lệ lỗi. Đợt đọc chỉ kiểm tra metadata và truy vấn SELECT, **không triển khai mã mới, không đổi lịch và không gọi thử Lambda**. Đăng ký email đã xác nhận không đồng nghĩa có minh chứng email cảnh báo đã đến hộp thư. Xem [manifest và kết quả chi tiết](tuan_2/results/review_2026_10_16/README.md).

## Cấu trúc mã nguồn

| Đường dẫn | Vai trò |
| --- | --- |
| [docs/](docs/README.md) | Kiến trúc, phương pháp, worklog, hướng dẫn mã nguồn, cấu trúc repo và kế hoạch |
| [tuan_1/](tuan_1/README.md) | Hồ sơ Tuần 1, báo cáo, CSV đã nộp và cách đọc các biểu đồ |
| [tuan_2/lambda/](tuan_2/lambda/lambda_function.py) | Lambda lấy dữ liệu, chuẩn hóa bản ghi, phân loại AQI, lưu S3 và yêu cầu phát cảnh báo |
| [tuan_2/scripts/](tuan_2/scripts/) | Python SDK cho cấu hình dịch vụ, Athena exporter, bộ thu thập snapshot và kiểm tra repository |
| [tuan_2/athena/](tuan_2/athena/README.md) | DDL, view và SQL phân tích dữ liệu gốc theo thành phố, giờ, ngày và phân vùng |
| [tuan_2/analytics/](tuan_2/analytics/) | Phân tích hai bộ dữ liệu, tạo bảng CSV và dựng biểu đồ theo manifest |
| [tuan_2/tests/](tuan_2/tests/) | Kiểm tra Lambda, SDK, CSV, dữ liệu và hồ sơ lưu cục bộ |
| [tuan_2/results/](tuan_2/results/README.md) | CSV gốc/tổng hợp, hình, metadata và phân tách các mốc dữ liệu |
| [.github/workflows/](.github/workflows/verify-repository.yml) | Quy trình CI để kiểm tra tính nhất quán của repository |

Điểm vào phân tích và tệp có trách nhiệm chi tiết được liệt kê trong [chỉ mục mã nguồn](docs/components.md) và [hướng dẫn đọc mã nguồn](docs/source-guide.md).

## Cài đặt và kiểm tra

Yêu cầu Python **3.12 trở lên**. Các kiểm tra cục bộ bên dưới dùng dữ liệu đã lưu; không cần thông tin đăng nhập AWS.

Cài dependencies từ gốc repository:

    python -m pip install -r tuan_2/analytics/requirements.txt

Kiểm tra tính nhất quán của CSV catalog, worklog và các hồ sơ:

    python tuan_2/scripts/repository_audit.py --check

Chạy các bộ kiểm tra chức năng và phân tích:

    python -m unittest discover -s tuan_2/tests -v
    python -m unittest discover -s tuan_2/analytics -p "test_*.py" -v

Xuất lại dữ liệu từ các CSV đã lưu trong chế độ offline vào thư mục riêng:

    python tuan_2/scripts/athena_export.py --offline --output output/csv

Để phân tích hoặc dựng biểu đồ từ đầu, xem [hướng dẫn tái lập và các điểm vào](docs/source-guide.md). Các chương trình tạo bảng/hình ghi vào thư mục kết quả có theo dõi bằng Git; hãy dùng bản sao làm việc và kiểm tra phần thay đổi trước khi thay thế các tệp kết quả đã lưu. Thao tác với dịch vụ AWS cần phiên Boto3 hợp lệ được cấu hình bên ngoài repository; xem [hướng dẫn vận hành](docs/operation.md). Quy trình CI được khai báo trong [.github/workflows/verify-repository.yml](.github/workflows/verify-repository.yml); trạng thái từng lần chạy xem tại [GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions).

## Giới hạn và cách diễn giải

- Dữ liệu chất lượng không khí từ Open-Meteo dựa trên mô hình CAMS; đây không phải phép đo tại trạm quan trắc cụ thể.
- Bộ Tuần 2 đã lưu chỉ có dữ liệu ở hai ngày và chín khung giờ. Tỷ lệ, trung bình và tương quan trong báo cáo mô tả đúng mẫu đã lưu, không đại diện cho toàn tuần hoặc xu hướng dài hạn.
- Các ngưỡng AQI và PM2.5 là cấu hình của đồ án. SNS nhận thông điệp hoặc có đăng ký đã xác nhận không chứng minh email được gửi tới, nhận hoặc đọc.
- Snapshot ngày 16/10 ghi nhận hai Alarm đang INSUFFICIENT_DATA và mã Lambda trên AWS khác mã nguồn hiện tại; không tuyên bố mã trong repository đã được triển khai.
- Cost Explorer có cờ Estimated; số hiển thị không thay cho hóa đơn cuối cùng. Mức dự kiến do sinh viên xác nhận được báo riêng.
- Giá trị thiếu/không chuyển đổi được có thể đi qua chính sách mặc định của mã nguồn. Khi diễn giải số 0, hãy đối chiếu dữ liệu gốc, quy tắc chuẩn hóa và bảng chất lượng dữ liệu.
- Tương quan không chứng minh quan hệ nhân quả. Mẫu ít và thời điểm lấy mẫu khác nhau cần được nêu cùng mọi kết luận so sánh.

## Tài liệu chi tiết

- [Hồ sơ và kết quả Tuần 1](tuan_1/README.md)
- [Hồ sơ và kết quả Tuần 2](tuan_2/README.md)
- [Kiến trúc hệ thống](docs/architecture.md)
- [Dữ liệu và phương pháp phân tích](docs/data-analysis.md)
- [Hướng dẫn đọc mã nguồn](docs/source-guide.md)
- [Cài đặt và vận hành](docs/operation.md)
- [Nhật ký công việc](docs/WORKLOG.md)
- [Danh mục CSV, số dòng và SHA-256](docs/csv_catalog.csv)
- [Kế hoạch Tuần 3](docs/WEEK_3_PLAN.md)

Repository công khai: [JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).
