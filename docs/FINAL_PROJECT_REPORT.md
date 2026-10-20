# Báo cáo tổng kết đồ án

## Hệ thống thu thập và phân tích dữ liệu thời tiết, chất lượng không khí trên AWS

**Học phần:** Điện toán đám mây — lớp 261CLCO332779_05.

**Giảng viên hướng dẫn:** ThS. Huỳnh Xuân Phụng.

**Sinh viên thực hiện:** Nguyễn Tiến Sơn — 24110054; Trần Thị Ngọc Quyên — 24110051.

**Ngày cập nhật:** 20/10/2026. Các bộ số liệu giữ riêng ngày chốt và phạm vi kiểm chứng.

## Tóm tắt

Đồ án xây dựng một luồng xử lý dữ liệu môi trường cho TP. Hồ Chí Minh, Hà Nội và Đà Nẵng trên AWS Learner Lab. EventBridge kích hoạt Lambda; Lambda đọc cấu hình, gọi Open-Meteo, chuẩn hóa bản ghi, lưu NDJSON trên S3 và gửi thông báo vượt ngưỡng qua SNS. Glue Data Catalog và Athena cung cấp lớp truy vấn; các chương trình Python xuất CSV, phân tích, tạo biểu đồ và đánh giá dự báo. CloudWatch cung cấp log, metric và dashboard phục vụ đối chiếu vận hành.

Kết quả được trình bày theo bốn tuần, với các bộ dữ liệu và phiên bản mã được lưu riêng. Bản xuất tích lũy Tuần 3 ngày 19/10 có **641 bản ghi và 95 tệp JSON gốc**. Thực nghiệm Athena gồm **18 lượt truy vấn**; kỳ dự báo được đối chiếu đủ **144 giá trị**. Đợt kiểm chứng Tuần 4 nối được source đang triển khai, request thực thi, log, ba bản ghi S3 và SELECT tương ứng ở mỗi môi trường. Cả hai sinh viên đã xác nhận nhận email cảnh báo mới của đợt này. Template CloudFormation hiện tại khai báo **17 tài nguyên**, đã qua cfn-lint và AWS ValidateTemplate.

Ngày 20/10, hồ sơ bổ sung **hai stack CloudFormation CREATE_COMPLETE**, kiểm chứng Lambda/S3/Athena trên tài nguyên mới, **700 bản ghi và 115 JSON gốc**, **18 truy vấn Athena mới**, cùng **backtest ba cửa sổ lịch sử với 432 dự đoán và 18 dòng sai số**. Hai topic mới có thư thử kênh email đã được người nhận xác nhận. Chi tiết và nguồn nằm ở mục 7.3 và [báo cáo Tuần 4](../tuan_4/docs/FINAL_REPORT.md).

Tài liệu này tổng hợp kết quả toàn đồ án và giải thích ý nghĩa kỹ thuật. Báo cáo từng tuần tiếp tục giữ vai trò hồ sơ chi tiết theo đúng thời điểm chốt số liệu.

## 1. Mục tiêu và sản phẩm

| Mục tiêu | Sản phẩm và căn cứ đánh giá |
| --- | --- |
| Thu thập dữ liệu ba đô thị | [Source Lambda chính](../tuan_2/lambda/lambda_function.py), cấu hình lịch và các bản ghi đã lưu |
| Lưu dữ liệu có thể truy vết | NDJSON, CSV đủ 23 trường, danh mục object và SHA-256 trong [bản xuất ngày 19/10](../tuan_3/results/daily_update_2026_10_19/README.md) |
| Truy vấn và phân tích | SQL Athena, CSV, thống kê mô tả và biểu đồ trong [Tuần 1](../tuan_1/docs/FINAL_REPORT.md), [Tuần 2](../tuan_2/docs/FINAL_REPORT.md) và [Tuần 3](../tuan_3/docs/FINAL_REPORT.md) |
| Cảnh báo qua email | Điều kiện ngưỡng trong source, kết quả Publish và [xác nhận của hai người nhận](../tuan_4/results/verification_2026_10_19/recipient_confirmation.json) |
| Giải thích hiệu quả xử lý | So sánh ba cách tổ chức dữ liệu trên cùng đầu vào, giữ kết quả truy vấn tương đương |
| Đánh giá dự báo | Bản phát hành gốc, dữ liệu đối chiếu tải về sau, MAE/RMSE/Bias và biểu đồ |
| Kiểm chứng vận hành | [Đối chiếu request–log–metric–S3–Athena](../tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md), chi phí và bảo mật |
| Bàn giao và trình bày | Một template hạ tầng, hướng dẫn tái lập, worklog, checklist kết thúc Lab và yêu cầu video dưới 10 phút |

## 2. Kiến trúc và cơ sở lựa chọn

![Kiến trúc hệ thống](architecture.png)

*Hình 1. Kiến trúc thu thập, lưu trữ, truy vấn và cảnh báo. Trạng thái thực thi được đối chiếu bằng các hồ sơ kiểm chứng, tách với sơ đồ thiết kế.*

### 2.1. Vai trò của các thành phần

| Thành phần | Lý do sử dụng trong đồ án | Cách áp dụng và đánh giá |
| --- | --- | --- |
| EventBridge và Lambda | Tách lịch kích hoạt khỏi logic thu thập; phù hợp các lượt xử lý ngắn theo chu kỳ | Một lịch chuẩn cho mỗi môi trường; log và metric dùng để xác định lượt đã thực thi |
| Secrets Manager | Tách cấu hình vị trí và ngưỡng khỏi gói triển khai | Source đọc cấu hình lúc chạy; không đưa nội dung Secret hoặc khóa phiên vào repository |
| Amazon S3 | Giữ dữ liệu dạng tệp, hỗ trợ kiểm tra lại và truy vấn ngoài | NDJSON theo ngày UTC; mỗi bản xuất có danh mục object và hash |
| Glue Data Catalog và Athena | Dùng SQL trên dữ liệu S3, không cần xây dựng thêm máy chủ cơ sở dữ liệu cho bài thực hành | Lược đồ gồm 20 trường dữ liệu và ba khóa phân vùng; SQL lọc cả partition và timestamp khi cần |
| SNS email | Tách việc phát thông báo khỏi chức năng thu thập | Đếm Publish được chấp nhận và xác nhận email đến người nhận riêng |
| CloudWatch | Kết nối log ứng dụng với chỉ số vận hành | Đối chiếu request cụ thể, cùng chu kỳ metric và đúng môi trường |
| Python và GitHub Actions | Tái lập phép tính, kiểm tra cấu trúc hồ sơ và đóng gói source | Kết quả kiểm tra mã, lần triển khai và bằng chứng chạy AWS được dẫn riêng |

NDJSON giúp kiểm tra trực tiếp từng bản ghi và phù hợp đầu ra collector. Parquet được dùng trong thực nghiệm để đánh giá lợi ích đọc theo cột; dữ liệu raw ban đầu được giữ nguyên. Cách tổ chức này cho phép kiểm tra kết quả tối ưu từ cùng đầu vào, thay vì thay đổi dữ liệu rồi so sánh hai tập khác nhau.

### 2.2. Trình tự thực thi trong source

Trong chế độ realtime, `lambda_handler` đọc cấu hình, lần lượt gọi `fetch_city_data` cho từng đô thị, kiểm tra ngưỡng rồi gọi `send_sns_alert` khi cần. Sau vòng thu thập, `save_records_to_s3` ghi tập bản ghi đã thu được theo ngày UTC và handler trả về phần tổng hợp kết quả.

Điều kiện cảnh báo hiện tại là **US AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³**. Đây là ngưỡng cấu hình của ứng dụng. Phép so sánh có lấy dấu bằng; không thay bằng phép so sánh lớn hơn trong phần diễn giải. Tham số PM10 có trong cấu hình dự phòng nhưng không tham gia điều kiện gửi cảnh báo hiện tại.

Trong chế độ backfill, Lambda chỉ lấy các giờ lịch sử đã hoàn tất, lưu bản ghi và kiểm tra độ phủ theo từng đô thị. Chế độ này không phát SNS cho dữ liệu lịch sử. Nhờ vậy, việc bổ sung dữ liệu phục vụ phân tích không làm phát lại cảnh báo của các giờ trước.

### 2.3. Ý nghĩa của kết quả xử lý

| Thông tin | Ý nghĩa chính xác |
| --- | --- |
| `collection_status = complete` | Các đô thị cấu hình không bị ghi nhận lỗi thu thập; cần đọc cùng số bản ghi và tệp đã lưu |
| `collection_status = partial` | Có đô thị thu không thành công hoặc chuỗi lịch sử chưa đủ số giờ yêu cầu; các bản ghi đã thu vẫn được lưu |
| `alerts_sent` | Số thông điệp được SNS chấp nhận qua Publish, không tự xác nhận thư đã đến hộp thư |
| Lambda `Errors = 0` | Không có lỗi thực thi Lambda được ghi nhận trong chu kỳ metric đang xét; không thay thế kiểm tra kết quả nghiệp vụ |

Source hiện gửi SNS trong vòng lặp trước khi ghi tập bản ghi vào S3. Hai thao tác thuộc hai dịch vụ riêng, nên đối chiếu cảnh báo và lưu trữ phải dựa trên kết quả của từng bước. Lỗi Publish được hàm gửi thông báo xử lý và trả về `False`; trạng thái thu thập `complete` không tự bảo đảm mọi cảnh báo đã gửi thành công.

Mã bản ghi và tên object có phần ngẫu nhiên để phân biệt các lần ghi. Cơ chế này không loại bỏ sự kiện gọi lại; khi đánh giá dữ liệu, báo cáo dùng đô thị–giờ và provenance để kiểm soát ảnh hưởng của mật độ lấy mẫu. Việc giữ một lịch chuẩn giúp tránh hai lịch cùng chủ động gọi một Lambda.

## 3. Dữ liệu và phương pháp đối chiếu

### 3.1. Hợp đồng dữ liệu

CSV raw giữ đủ **23 trường**, gồm nhận diện bản ghi, thời gian, vị trí, các đại lượng khí tượng và chất lượng không khí. Khi truy vấn, ba trường ngày phân vùng được lấy từ đường dẫn S3. UTC được dùng để tổ chức lưu trữ; UTC+7 được dùng để trình bày ngày báo cáo. Điều kiện SQL theo ngày Việt Nam cần quy đổi đúng mốc UTC, thay vì chỉ chọn partition cùng tên ngày.

`timestamp_utc` mô tả mốc thời gian của bản ghi; `collected_at` phục vụ truy vết lúc thu thập. Với chuỗi lịch sử, mốc của mô hình và ngày thu bổ sung có vai trò khác nhau. Bản ghi backfill chứng minh đã tải và lưu chuỗi đó, không được dùng để suy ra lịch tự động đã chạy ở từng giờ lịch sử.

Các hàm `safe_float` và `safe_int` có giá trị dự phòng bằng 0 khi đầu vào không hợp lệ. Vì vậy, một ô số 0 cần được đọc cùng cấu trúc phản hồi API, bản raw và kiểm tra chất lượng; không mặc định diễn giải mọi giá trị 0 là một phép đo môi trường hợp lệ. Cấu hình cũng có nhánh dự phòng khi đọc Secret thất bại. Log và cấu hình của lượt chạy là căn cứ xác định nhánh đã dùng.

### 3.2. Tổng hợp các bộ hồ sơ

| Hồ sơ | Quy mô đã lưu | Đơn vị và cách sử dụng |
| --- | --- | --- |
| Tuần 1 | 156 bản ghi, 52 bản ghi mỗi đô thị; năm truy vấn Athena, chín biểu đồ | Tập raw của báo cáo Tuần 1; các nhóm giờ không được diễn giải thành độ phủ liên tục cả tuần |
| Tuần 2 | Trong phạm vi tuần: sinh viên Tiến Sơn 27 dòng, sinh viên Ngọc Quyên 57 dòng; toàn bộ CSV tương ứng 204 và 231 dòng | Đối chiếu trên 21 nhóm đô thị–giờ chung; mỗi đô thị có bảy giờ chung |
| Tuần 3, bản xuất ngày 19/10 | Sinh viên Tiến Sơn 302 dòng/43 JSON; sinh viên Ngọc Quyên 339 dòng/52 JSON | Tổng tích lũy 641 dòng/95 JSON của bản xuất này |
| Dữ liệu riêng ngày 19/10 trong bản xuất Tuần 3 | Sinh viên Tiến Sơn 45 dòng; sinh viên Ngọc Quyên 42 dòng | Thống kê dùng cùng 14 giờ đã hoàn tất, tương ứng 42 bản ghi mỗi sinh viên |
| Kiểm chứng realtime Tuần 4 ngày 19/10 | Ba bản ghi mới mỗi môi trường, sáu bản ghi cho hai lượt | Đối chiếu đúng record_id của request kiểm chứng, không cộng vào số tích lũy của snapshot Tuần 3 đã chốt trước đó |
| Snapshot tích lũy ngày 20/10 | Sinh viên Tiến Sơn 331 dòng/53 JSON; sinh viên Ngọc Quyên 369 dòng/62 JSON | Tổng 700 dòng/115 JSON; có dữ liệu giao với snapshot cũ, không cộng hai bản xuất |
| Backtest lịch sử ngày 20/10 | 519 dòng lịch sử mô hình, 432 dự đoán, 18 dòng MAE/RMSE/Bias | Ba cửa sổ đích liên tiếp, train trước gốc; tách với bản dự báo đã phát hành |

Các hàng trong bảng có phạm vi giao nhau hoặc thời điểm chốt khác nhau, nên không cộng thành một “tổng số mẫu toàn đồ án”. Số dòng lớn hơn cũng không tự thể hiện số giờ được quan sát nhiều hơn. Khi so sánh hai báo cáo dữ liệu, đơn vị đô thị–giờ được dùng để giảm ảnh hưởng của việc một môi trường có nhiều lượt thu trong cùng giờ.

Hai sinh viên sử dụng cùng tọa độ và cùng API mô hình. Giá trị AQI/PM2.5 bằng nhau tại một số giờ là kết quả có thể xuất hiện từ cùng đầu vào. Tỷ lệ AQI 100% trong một nhóm mẫu mô tả các bản ghi của nhóm đó, không tương đương 100% thời gian của cả tuần. Đây là cơ sở để giữ các biểu đồ đúng số liệu và giải thích rõ mẫu số.

Nguồn chi tiết: [Tuần 1](../tuan_1/docs/FINAL_REPORT.md), [Tuần 2](../tuan_2/docs/FINAL_REPORT.md), [bản xuất ngày 19/10](../tuan_3/results/daily_update_2026_10_19/README.md), [raw của hai lượt realtime](../tuan_4/results/verification_2026_10_19/README.md).

## 4. Phân tích chuyên sâu thực nghiệm Athena

### 4.1. Thiết kế đối chứng

Mỗi môi trường chạy ba phương án: JSON đăng ký phân vùng, JSON dùng partition projection và Parquet dùng partition projection. Mỗi phương án được chạy ba lần, tổng **18 lượt** cho hai môi trường. Đầu vào được đóng băng, kết quả tổng hợp được đối chiếu tương đương và không tái sử dụng kết quả truy vấn. Bảng dưới dùng trung vị để giảm ảnh hưởng của một lượt nhanh hoặc chậm riêng lẻ.

| Bộ báo cáo dữ liệu | Phương án | Byte quét | Thời gian engine, ms | Tổng thời gian, ms |
| --- | --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | JSON đăng ký phân vùng | 1.556 | 615 | 799 |
| Sinh viên Tiến Sơn | JSON projection | 1.556 | 537 | 746 |
| Sinh viên Tiến Sơn | Parquet projection | 302 | 452 | 619 |
| Sinh viên Ngọc Quyên | JSON đăng ký phân vùng | 11.243 | 572 | 756 |
| Sinh viên Ngọc Quyên | JSON projection | 11.243 | 431 | 606 |
| Sinh viên Ngọc Quyên | Parquet projection | 393 | 515 | 722 |

Nguồn: [tổng hợp sinh viên Tiến Sơn](../tuan_3/results/integration_2026_10_18/benchmark/default/summary.json), [tổng hợp sinh viên Ngọc Quyên](../tuan_3/results/integration_2026_10_18/benchmark/quyen/summary.json), [toàn bộ thực nghiệm](../tuan_3/results/integration_2026_10_18/benchmark/).

### 4.2. Diễn giải kết quả

**Định dạng và lượng quét.** So với JSON đăng ký phân vùng, Parquet giảm lượng quét **80,59%** trong bộ của sinh viên Tiến Sơn và **96,50%** trong bộ của sinh viên Ngọc Quyên. Tỷ lệ được tính bằng `(byte JSON − byte Parquet) / byte JSON × 100%`. Kết quả này chứng minh lợi ích về byte quét cho truy vấn thử nghiệm, không quy đổi trực tiếp thành phần trăm giảm hóa đơn tài khoản.

**Projection và thời gian.** Hai phương án JSON có cùng số byte quét, nhưng khác trung vị thời gian. Projection thay đổi cách xác định phân vùng; nó không tự chuyển dữ liệu sang định dạng cột hoặc làm giảm lượng nội dung cần đọc trong truy vấn này. Các số thời gian là quan sát của ba lần chạy mỗi phương án.

**Byte quét và độ trễ là hai tiêu chí.** Ở bộ của sinh viên Ngọc Quyên, Parquet quét ít byte hơn nhưng engine mất 515 ms, cao hơn JSON projection 431 ms. Do đó, lựa chọn tối ưu cần xem đồng thời kết quả truy vấn, byte quét và thời gian; không kết luận Parquet luôn nhanh nhất từ một chỉ số riêng.

**Phạm vi so sánh.** Bộ đầu vào của sinh viên Tiến Sơn có 237 dòng, truy vấn chọn ba dòng ngày 18/10; bộ của sinh viên Ngọc Quyên có 273 dòng, truy vấn chọn 21 dòng ngày 16/10. Vì vậy, đối chứng hiệu quả thực hiện giữa các phương án trong từng môi trường. Không dùng chênh lệch byte giữa hai sinh viên để xếp hạng hiệu năng hai tài khoản.

## 5. Phân tích chuyên sâu dự báo

### 5.1. Quy trình đánh giá

Mã nguồn Tuần 3 đánh giá các phương pháp cơ sở gồm giữ giá trị cuối, lặp lại giá trị 24 giờ trước và trung bình trượt 24 giờ. Bản dự báo đã phát hành ngày 18/10 được giữ nguyên; các giá trị mô hình tải ngày 19/10 được dùng làm tập đối chiếu riêng. Cách tách này giúp tránh thay đổi dự báo sau khi đã có dữ liệu của kỳ đích.

Kỳ đã đối chiếu gồm **24 giờ đích × ba đô thị × hai chỉ số = 144 giá trị**, thuộc hai ngày 18/10 và 19/10. Bảng sau mô tả đúng kỳ phát hành này, với nguồn đối chiếu là dữ liệu mô hình CAMS tải về sau.

| Đô thị | Chỉ số | MAE | RMSE | Bias |
| --- | --- | ---: | ---: | ---: |
| TP. Hồ Chí Minh | US AQI, điểm | 10,221 | 10,617 | +10,221 |
| TP. Hồ Chí Minh | PM2.5, µg/m³ | 6,178 | 6,730 | +6,178 |
| Hà Nội | US AQI, điểm | 11,031 | 14,995 | −0,417 |
| Hà Nội | PM2.5, µg/m³ | 6,619 | 9,906 | −5,163 |
| Đà Nẵng | US AQI, điểm | 12,320 | 12,833 | +12,320 |
| Đà Nẵng | PM2.5, µg/m³ | 3,126 | 3,699 | −1,369 |

Nguồn: [CSV sáu bộ sai số](../tuan_3/results/forecast_followup_2026_10_19/comparison_metrics.csv) và [144 giá trị đối chiếu](../tuan_3/results/forecast_followup_2026_10_19/comparison.csv).

![Dự báo đã phát hành và mô hình đối chiếu](../tuan_3/results/forecast_followup_2026_10_19/issued_vs_later_model.png)

*Hình 2. Dự báo giữ nguyên theo bản phát hành và dữ liệu mô hình tải về sau của cùng kỳ đích.*

### 5.2. Ý nghĩa các đại lượng

Với sai số `e = dự báo − giá trị mô hình đối chiếu`, MAE là trung bình `|e|`, RMSE là căn bậc hai của trung bình `e²`, còn Bias là trung bình `e`. MAE và RMSE có cùng đơn vị với chỉ số; Bias dương biểu thị xu hướng dự báo cao hơn, Bias âm biểu thị xu hướng thấp hơn.

Tại Hà Nội, Bias AQI gần 0 nhưng MAE là 11,031 điểm và RMSE là 14,995 điểm. Sai số dương và âm có thể bù nhau trong trung bình; vì vậy Bias nhỏ không đủ để kết luận dự báo chính xác. RMSE cao hơn MAE cũng cho thấy các sai số lớn có ảnh hưởng đáng kể đến kết quả tổng hợp.

Đà Nẵng có MAE PM2.5 thấp nhất trong ba đô thị của kỳ này, trong khi MAE AQI lại cao nhất. AQI và PM2.5 có đơn vị và cách biểu diễn khác nhau, cần đánh giá từng chỉ số riêng. Không so sánh trực tiếp độ lớn MAE của hai chỉ số để kết luận chỉ số nào được dự báo tốt hơn.

Nguồn đối chiếu là chuỗi mô hình có thể cập nhật hồi cứu, không phải số đo độc lập từ trạm quan trắc. Kết quả phản ánh mức độ phù hợp với chuỗi mô hình tải về sau trong kỳ đã phát hành. Hồ sơ giữ cả bản dự báo, dữ liệu đối chiếu và hash để phép đánh giá có thể kiểm tra lại.

## 6. Kiểm chứng hệ thống và khả năng truy vết

Ngày 19/10, mỗi môi trường được kiểm chứng bằng một lượt realtime. Đợt này không thay ngưỡng và không đổi lịch để tạo kết quả cảnh báo.

| Điểm đối chiếu | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Request realtime được kiểm chứng | 1 | 1 |
| Bản ghi của ba đô thị | 3 | 3 |
| Invocations trong chu kỳ kiểm chứng | 1 | 1 |
| Errors trong cùng chu kỳ | 0 | 0 |
| Publish được SNS chấp nhận | 1 | 1 |
| SELECT theo đúng record_id | Khớp | Khớp |
| Email mới | Người nhận đã xác nhận | Người nhận đã xác nhận |

Chuỗi đối chiếu gồm: hash source và gói triển khai → request → START/END/REPORT và Result → object S3 → CSV raw → SELECT chính xác. QueryExecutionId và số byte quét được lưu cùng lượt truy vấn. Cách kiểm tra này xác nhận dữ liệu phân tích thuộc đúng lượt thực thi đang được trình bày.

Kết luận về metric áp dụng cho chu kỳ chứa request kiểm chứng. Các chu kỳ khác không đủ cặp Invocations/Errors được giữ trong hồ sơ kỹ thuật; không mở rộng tỷ lệ 0% của chu kỳ kiểm chứng thành tỷ lệ lỗi của toàn bộ thời gian vận hành. Xác nhận email được bổ sung bằng [bản ghi người nhận](../tuan_4/results/verification_2026_10_19/recipient_confirmation.json), tách với trạng thái chờ xác nhận tại thời điểm chụp snapshot ban đầu.

Minh chứng đầy đủ: [bộ kiểm chứng Tuần 4](../tuan_4/results/verification_2026_10_19/README.md) và [báo cáo đối chiếu log–metric–S3](../tuan_4/docs/LOG_METRIC_S3_RECONCILIATION.md).

## 7. Chi phí, bảo mật và quản lý tài nguyên

### 7.1. Chi phí

Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated. Phép cộng dùng Decimal; bản hiển thị làm tròn đến cent.

| Sinh viên | Nhóm ngày/dịch vụ/loại ghi nhận | Tổng UnblendedCost gốc (USD) | Hiển thị đến cent (USD) |
| :--- | :---: | :---: | :---: |
| Sinh viên Tiến Sơn | 70 | -0,000000339 | 0,00 |
| Sinh viên Ngọc Quyên | 47 | 0,1364702401 | 0,14 |

Nguồn: [cost_summary.json](../tuan_4/results/cost/cost_summary.json), [117 dòng chi tiết](../tuan_4/results/cost/learner_lab_cost_breakdown.csv), [snapshot môi trường](../tuan_4/results/verification_2026_10_19/environment/). Kỳ chính xác trong cost_summary.json/cost.json là căn cứ của bảng; số liệu Estimated có thể được AWS cập nhật sau.

CSV có cả Usage và Credit. Tổng của sinh viên Tiến Sơn có trị tuyệt đối nhỏ hơn một cent nên hiển thị 0,00; giá trị gốc và các dòng âm được giữ nguyên. Không đổi âm thành số dương hoặc thay tổng API bằng mức dự kiến. Không suy ra một khoản Credit cụ thể chỉ từ dấu của tổng; xem từng nhóm để đối chiếu. Đây là chi phí tài khoản theo kỳ và nhóm dịch vụ, chưa phân bổ riêng theo tài nguyên đồ án. Chi tiết xem tại [Báo cáo chi phí](../tuan_4/docs/COST_REPORT.md).

Tối ưu được đánh giá theo số liệu cụ thể: byte quét và thời gian Athena, dung lượng object, lịch thu thập và phạm vi thử nghiệm. Checklist cuối phiên yêu cầu xuất dữ liệu, dừng đúng lịch thu thập khi kết thúc thực hành và thu hồi tài nguyên thử nghiệm theo phạm vi đã xác định.

### 7.2. Bảo mật và hạ tầng

Hai bucket hiện hữu có đủ bốn thiết lập Block Public Access, mã hóa mặc định AES256 và không ghi nhận public policy/public ACL trong đợt đọc cấu hình. Versioning của bucket hiện hữu chưa bật; template mới khai báo bật versioning. Quyền đọc IAM policy của LabRole không được môi trường cấp cho lần kiểm chứng, nên [policy mẫu](../tuan_4/infrastructure/collector-policy.example.json) được trình bày như thiết kế quyền theo tài nguyên cho collector, không gọi là effective permissions đã xác nhận của LabRole.

[Template CloudFormation chính](../tuan_4/infrastructure/weather-stack.json) gồm 17 tài nguyên ứng dụng, dùng artifact đóng gói từ source collector chính và execution role của Lab. Lịch mới khởi tạo ở trạng thái DISABLED; chính sách Retain giữ các tài nguyên chứa dữ liệu được chỉ định. Bản hiện tại đã qua cfn-lint và AWS ValidateTemplate ở cả hai môi trường. Ngày 20/10, hai stack **weather-w4-son/weather-w4-quyen** đã đạt **CREATE_COMPLETE**, mã Lambda đúng source, mỗi hàm thu đủ ba đô thị và SELECT khớp bốn trường đã chọn trong database/workgroup mới. [Events, hash, raw và truy vấn](../tuan_4/results/advanced_live_2026_10_20/README.md) ghi lại triển khai thực tế sau bước ValidateTemplate.

Công cụ quản lý phiên kiểm tra account/function/rule/target trước khi pause hoặc restore, lưu trạng thái khôi phục và đọc lại kết quả. Kiểm thử cục bộ bao phủ các tình huống phục hồi; ngày 20/10 đã thực hiện pause rồi restore trên cả hai môi trường và đọc lại ENABLED → DISABLED → ENABLED, binding không đổi. [Minh chứng thao tác thật](../tuan_4/results/advanced_live_2026_10_20/session/) được lưu riêng; hai lịch của stack mới vẫn DISABLED. [Checklist kết thúc phiên](../tuan_4/docs/SESSION_CHECKLIST.md) là căn cứ thao tác sau khi hoàn tất quay demo và xuất minh chứng.

### 7.3. Kết quả nâng cao bổ sung ngày 20/10

- **Dữ liệu:** [snapshot mới](../tuan_4/results/advanced_live_2026_10_20/snapshot/) giữ 331/369 bản ghi, 53/62 JSON nguyên byte, tổng 700 bản ghi và 115 JSON.
- **Athena:** [18 lượt đo mới](../tuan_4/results/advanced_live_2026_10_20/benchmark/) có parity, không result reuse; lọc ngày 20/10 với ba bản ghi mỗi sinh viên. Median JSON Projection là 1.558 byte, Parquet 302 byte (giảm 80,62%). Median tổng JSON Projection/Parquet là 647/682 ms của sinh viên Tiến Sơn và 640/647 ms của sinh viên Ngọc Quyên. Ít byte hơn không đồng nghĩa thời gian tổng nhỏ hơn.
- **Backtest:** [ba cửa sổ lịch sử](../tuan_4/results/backtest_2026_10_20/README.md), mỗi cửa sổ dùng 24 giờ train trước gốc và 24 giờ đích; MA24 cố định, 432 dự đoán và 18 dòng sai số. Đây là hồi cứu chuỗi mô hình, tách riêng kỳ dự báo đã phát hành ở mục 5.
- **SNS và bảo mật:** topic mới đã confirmed, cả hai người nhận xác nhận thư thử kênh; dữ liệu trong lượt E2E mới dưới ngưỡng nên 0 cảnh báo. Hai bucket mới được đọc lại BPA, AES256, versioning Enabled, ownership và HTTPS-only. [Hồ sơ stack/email](../tuan_4/results/advanced_live_2026_10_20/README.md) giữ các bằng chứng tương ứng.

## 8. Đối chiếu yêu cầu tổng kết và bàn giao

| Nội dung | Kết quả trong hồ sơ | Trạng thái bàn giao |
| --- | --- | --- |
| Báo cáo Tuần 1–3, dữ liệu, phân công | Có báo cáo theo tuần, CSV, biểu đồ, source và nhật ký | Đã lưu và liên kết trên repository |
| Kiểm chứng tổng thể | Hai request realtime có source, log, S3, Athena, SNS và xác nhận email | Đã kiểm chứng trong phạm vi đợt ngày 19/10 |
| Đối chiếu log–metric–S3 | Có bảng theo request và chu kỳ metric tương ứng | Đã tổng hợp |
| Báo cáo chi phí và rà soát bảo mật | Có dữ liệu gốc, kỳ tính, kết quả đọc cấu hình và phân biệt thiết kế hạ tầng | Đã tổng hợp |
| Một template CloudFormation | Bản 17 tài nguyên, artifact đúng version/hash | Hai stack CREATE_COMPLETE và E2E trên tài nguyên mới ngày 20/10 |
| Quản lý tài nguyên cuối Lab | Có công cụ preview/pause/restore, kiểm thử và checklist | Thực hiện thao tác kết thúc phiên sau demo và xuất minh chứng |
| Video không quá 10 phút | Trình bày luồng xử lý, kết quả phân tích và kiểm chứng vận hành | Cần quay, kiểm tra thời lượng và bổ sung đường dẫn video thực tế |
| Nhật ký công việc | Tổng theo tuần đã xác nhận: 78 giờ | Đã lưu CSV và bảng phân công |

Video thực tế là sản phẩm cần hoàn tất trước khi nộp gói cuối theo yêu cầu giảng viên. Nội dung trình bày sử dụng đúng dữ liệu của lượt được kiểm chứng; hồ sơ ngày 19/10 được giới thiệu theo ngày đã lưu. Đường dẫn video được bổ sung sau khi kiểm tra thời lượng và quyền xem.

## 9. Phân công và kết luận toàn đồ án

Sinh viên Tiến Sơn phụ trách S3, Secrets Manager, Lambda, SNS, lịch thu thập và giám sát. Sinh viên Ngọc Quyên phụ trách Glue, Athena, xuất CSV, phân tích và đối chiếu báo cáo. Hai sinh viên cùng tích hợp, rà soát và chuẩn bị bảo vệ. Tổng theo tuần đã xác nhận là **39,5 giờ của sinh viên Tiến Sơn và 38,5 giờ của sinh viên Ngọc Quyên, tổng 78,0 giờ**. [Nhật ký](WORKLOG.md) và [CSV giờ công](../worklog.csv) liên kết thời gian với sản phẩm từng tuần.

Đồ án đã xây dựng và kiểm chứng được luồng thu thập, lưu trữ, truy vấn và cảnh báo qua email trên hai môi trường thực hành. Giá trị của kết quả nằm ở khả năng truy vết từ source và request tới bản ghi, truy vấn và biểu đồ; mỗi kết luận đều gắn với tập dữ liệu và kỳ kiểm chứng cụ thể.

Về phân tích, thực nghiệm Athena chỉ ra lợi ích giảm byte quét của Parquet, đồng thời cho thấy cần đo thêm thời gian để lựa chọn phương án phù hợp. Phần dự báo hình thành được quy trình phát hành, giữ nguyên dự báo và đánh giá đủ kỳ bằng nhiều thước đo. Về vận hành, hồ sơ kết nối log–metric–S3–Athena và tách việc SNS chấp nhận thông điệp với email người nhận đã xác nhận.

Các nội dung có thể phát triển sau đồ án gồm đánh giá nhiều kỳ dự báo trên dữ liệu mới, phân bổ chi phí theo tài nguyên và bổ sung cơ chế kiểm soát sự kiện gọi lại khi mở rộng vận hành. Đây là hướng phát triển tiếp từ kết quả hiện có. Hồ sơ bàn giao hiện tại tập trung vào source, dữ liệu, phép kiểm chứng và quy trình trình bày có thể đối chiếu.

## 10. Liên kết đọc và sao chép

- **Repository:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm](https://github.com/JasonTM17/WeatherAWS_FinalTerm).
- **Tổng kết toàn đồ án:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/FINAL_PROJECT_REPORT.md).
- **Danh mục đầy đủ báo cáo, dữ liệu và commit:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/docs/EVIDENCE_INDEX.md).
- **Báo cáo kiểm chứng Tuần 4:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/tuan_4/docs/FINAL_REPORT.md).
- **Nội dung và liên kết nộp báo cáo:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/BAO_CAO.md](https://github.com/JasonTM17/WeatherAWS_FinalTerm/blob/main/BAO_CAO.md).
