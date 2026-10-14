# Dữ liệu và phương pháp phân tích

## Bộ báo cáo Tuần 1

[CSV của báo cáo Tuần 1](../tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051/) gồm 156 bản ghi/52 mẫu mỗi đô thị, bốn bảng tổng hợp và chỉ số truy vấn. Bộ này giữ nguyên các giá trị trong báo cáo và Excel Tuần 1. Mỗi đô thị có 52 mốc giờ liên tiếp, được gom thành 24 nhóm giờ trong ngày. Có 51 dòng lịch sử nạp bổ sung trước ranh giới Tuần 1 và 105 dòng trong ranh giới tuần theo UTC+7; bộ 156 dòng là phạm vi của lần xuất dùng làm báo cáo. Các chương trình dựng hình Tuần 1 đọc bản sao cùng dữ liệu tại [athena_queries](../tuan_2/results/athena_queries/); vai trò các thư mục được giải thích trong [danh mục dữ liệu](../tuan_2/results/README.md).

## Bộ dữ liệu mới Tuần 2

[Kết quả Athena](../tuan_2/results/week2_live/) được lưu riêng trong hai bộ báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên. Tổng raw là 204/231, mẫu thuộc Tuần 2 là 27/57. Tuần được lọc theo UTC+7, timestamp môi trường dạng không có múi giờ được hiểu là UTC; các thời điểm dịch vụ có múi giờ được đổi về UTC trước khi lọc.

[Tệp raw và metadata nguồn](../tuan_2/results/week2_evidence/) giữ đủ tệp raw có thể đọc được, danh sách/hash đối tượng, trạng thái tài nguyên, điểm CloudWatch, dòng REPORT đã trích, lịch sử truy vấn và chi phí theo dịch vụ. Credentials, nội dung secret, endpoint email, URL tải có chữ ký và log thô được loại khỏi bộ công khai.

## Phép tính

- Phân tích riêng từng bộ báo cáo dữ liệu; 144 quan trắc lịch sử cùng đô thị và thời điểm xuất hiện trong cả hai bộ có giá trị tương ứng bằng nhau, nên giữ riêng cỡ mẫu khi trình bày.
- Trung bình và SD tính trên các bản ghi trong cùng đô thị/bộ dữ liệu; SD dùng n−1.
- Q1, trung vị, Q3 và P95 dùng nội suy tuyến tính. Không gọi SD là khoảng tin cậy.
- Các tỷ lệ dùng số mẫu cùng đô thị/bộ dữ liệu làm mẫu số; không diễn giải thành tỷ lệ thời gian toàn tuần.
- Đối chiếu ghép trung bình của cùng thành phố/giờ, 21 nhóm (7 giờ mỗi đô thị), với trọng số mỗi giờ bằng nhau.
- Pearson và Spearman giữ kèm n; Spearman dùng hạng trung bình khi nhiều giá trị bằng nhau. Mẫu chuỗi ngắn không chứng minh nhân quả.
- Giá trị NULL/không hữu hạn được kiểm tra riêng; số 0 giữ nguyên và đếm riêng.
- Errors > Invocations khiến tỷ lệ lỗi không xác định. Không thay dữ liệu bằng 0 hoặc tạo phần trăm vượt 100%.
- Cost Explorer giữ số tiền gốc, đơn vị và cờ Estimated; số liệu môi trường AWS của từng sinh viên không được gọi là chi phí riêng dự án.

## Tệp kết quả

[27 CSV phân tích](../tuan_2/results/week2_analysis/) có bảng phân bố, giờ/ngày, cấp AQI, vượt ngưỡng, tương quan, so sánh ghép giờ, chất lượng, vận hành, query metrics, chi phí và đối chiếu với báo cáo Tuần 1. [Manifest hình](../tuan_2/results/week2_charts/chart_manifest.json) chỉ rõ CSV nguồn của cả 20 hình. Word và Excel nhúng cùng các ảnh, bên cạnh dữ liệu và các công thức tổng hợp trong Excel.

[Thống kê bổ sung Tuần 1](../tuan_2/results/charts/week1_extended_statistics.csv) tính trên đúng 156 dòng của bộ báo cáo đã lưu, gồm 52 mẫu mỗi đô thị. Năm hình bổ sung mô tả nồng độ bụi, khí tượng, phân bố, các cặp nhiệt độ–PM2.5 và hiệu năng truy vấn; [manifest Tuần 1](../tuan_2/results/charts/week1_chart_manifest.json) giữ các mảng vẽ và hash nguồn.

[matched_hour_summary.csv](../tuan_2/results/week2_analysis/matched_hour_summary.csv) tổng hợp bảy giờ chung cho mỗi đô thị với mỗi giờ cùng trọng số. AQI, PM2.5 và PM10 bằng nhau trước khi làm tròn trong cả 21 nhóm; Hình 3.8 trình bày mức thực tế, bảng kèm chênh lệch khí tượng. Phạm vi này khác trung bình toàn bộ 9/19 mẫu Tuần 2.

[week1_week2_extended_comparison.csv](../tuan_2/results/week2_analysis/week1_week2_extended_comparison.csv) giữ số đếm, mẫu số, tỷ lệ cấp AQI và Pearson khí tượng–PM2.5 của bộ Tuần 1 cùng hai mẫu Tuần 2. Hai hình đối chiếu mới sử dụng trực tiếp bảng này. Chạy `generate_week2_charts.py` tạo các hình và hai CSV bổ sung sau bộ 25 CSV nền tảng của `analyze_week2_accounts.py`.

### Đối chiếu số liệu chi phí

Chi phí trong bảng báo cáo được làm tròn đến cent; dữ liệu Cost Explorer gốc được giữ nguyên. Đối chiếu từng nhóm dịch vụ bằng số thập phân chính xác cho tổng −0,0000000764 USD của sinh viên Tiến Sơn và 0,0267146366 USD của sinh viên Ngọc Quyên, lần lượt hiển thị 0,00 USD và 0,03 USD. Số âm đã nằm trong các chuỗi Amount của phản hồi JSON, không phát sinh từ việc cộng tổng hoặc làm tròn ở báo cáo.

| Bộ báo cáo dữ liệu | AWS Secrets Manager (USD) | Amazon CloudWatch (USD) | Amazon S3 (USD) | Tổng UnblendedCost (USD) | Hiển thị đến cent (USD) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | −0,0000000608 | −0,0000000156 | 0 | −0,0000000764 | 0,00 |
| Sinh viên Ngọc Quyên | 0,0210227416 | 0,0056163440 | 0,0000755510 | 0,0267146366 | 0,03 |

Mức chi phí dự kiến cho phần thực hành của sinh viên Tiến Sơn trong Tuần 2 là **0,05 USD**, do nhóm đề xuất. Bảng 5.4 của báo cáo trình bày mức này ở cột dự kiến và đặt số Cost Explorer làm tròn trong một cột riêng. Mức dự kiến không phải giá trị trả về từ Cost Explorer và không thay thế dữ liệu ghi nhận trong CSV.

Các dịch vụ khác trong phạm vi đã xuất có giá trị 0; cả hai kết quả có cờ Estimated. Phản hồi nhóm theo SERVICE và không có RECORD_TYPE, nên không xác định được các mục âm này là credit, refund hay một loại điều chỉnh khác. Không dùng độ lớn rất nhỏ của số âm để kết luận nguyên nhân là lỗi làm tròn. Mức 0,00 USD trong bảng là độ chính xác trình bày, không chứng minh dự án miễn phí hoặc số tiền trên hóa đơn bằng 0.

AWS phân biệt số liệu Cost Explorer với hóa đơn, có thể có khác biệt do thời điểm cập nhật, độ chi tiết, làm tròn và cách phản ánh khoản hoàn tiền. Đây là mô tả chung của dịch vụ, không phải bằng chứng về nguyên nhân trong hai bộ dữ liệu này. Xem [tài liệu AWS Billing](https://docs.aws.amazon.com/us_en/awsaccountbilling/latest/aboutv2/differences-billing-data-cost-explorer-data.html) và [GetCostAndUsage về nhóm RECORD_TYPE](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetCostAndUsage.html).

## Hai phạm vi đối chiếu tuần

- [submitted_week1_comparison.csv](../tuan_2/results/week2_analysis/submitted_week1_comparison.csv) giữ bộ 156 dòng của báo cáo Tuần 1 làm mốc (52 mẫu/đô thị), so với mẫu Tuần 2 riêng từng nguồn (9/19). Bảng 3.10 và 3.11 trong báo cáo dùng phép này cho AQI và PM2.5. Chênh lệch tính từ trung bình chưa làm tròn; tệp manifest lưu hash của bộ mốc.
- [weekly_comparison.csv](../tuan_2/results/week2_analysis/weekly_comparison.csv) lọc hai tuần từ cùng lần xuất mới, nên có 42/41 mẫu Tuần 1 và 9/19 mẫu Tuần 2 mỗi đô thị. Bảng 3.12 và Hình 3.14 dùng riêng phạm vi này. Sheet So_sanh_tuan trong Excel giữ cả hai bảng nguồn.
- Các bộ có thời gian và độ phủ khác nhau; không xem chênh lệch trung bình mẫu là xu hướng của toàn bộ bảy ngày hoặc so sánh cùng thời điểm. Trong lần xuất mới, 144/156 dòng trong bộ của sinh viên Tiến Sơn và 156/156 dòng trong bộ của sinh viên Ngọc Quyên có cùng thành phố, timestamp với bộ cũ; các giá trị cảm biến tương ứng bằng nhau.

Dữ liệu chất lượng không khí được cung cấp qua [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), dựa trên CAMS. Bộ API đã lưu không được coi là phép đo trực tiếp tại một trạm.

Hai hình đối chiếu trực tiếp AQI và PM2.5 (Hình 3.12 và 3.13) dùng submitted_week1_comparison.csv, mốc 52 mẫu/đô thị của báo cáo Tuần 1 và mẫu Tuần 2 riêng 9/19. Word và Excel nhúng cùng tệp PNG; manifest ghi cả dãy số dùng cho từng cột.

## Dữ liệu gốc trong báo cáo Tuần 2

Mục 2.8 đối chiếu 27/57 dòng Tuần 2 với 204/231 dòng toàn bộ và trích sáu bản ghi gốc. Phụ lục dữ liệu gốc trình bày đủ 84 dòng Tuần 2, mỗi dòng đủ 23 trường qua hai bảng nối bằng mã TS/NQ; city là giá trị cố định trong tiêu đề nhóm. Timestamp, định danh và giá trị số giữ nguyên chuỗi từ CSV. Mức dự kiến 0,05 USD và số liệu Cost Explorer không thuộc dữ liệu cảm biến. Xem [báo cáo đầy đủ](../tuan_2/docs/FINAL_REPORT.md), [CSV của sinh viên Tiến Sơn](../tuan_2/results/week2_live/default/raw_week2.csv) và [CSV của sinh viên Ngọc Quyên](../tuan_2/results/week2_live/quyen/raw_week2.csv).
