# Nhật ký kỹ thuật và kế hoạch công việc Tuần 3

**Nguyễn Tiến Sơn — MSSV 24110054 · Trần Thị Ngọc Quyên — MSSV 24110051**

**Kỳ báo cáo:** 19–25/10/2026, múi giờ Việt Nam (UTC+7).

**Mốc chuẩn bị đã có minh chứng:** 18/10/2026.

## 1. Phạm vi và cách ghi nhận

Nhật ký liên kết công việc với mã nguồn, dữ liệu và kết quả kiểm chứng để giảng viên có thể đối chiếu trực tiếp. Phân công kế thừa [bảng thành phần của dự án](../../docs/components.md): sinh viên Tiến Sơn phụ trách thu thập, cấu hình, giám sát và triển khai; sinh viên Ngọc Quyên phụ trách dữ liệu, Athena và phân tích. Hai sinh viên cùng rà soát kết quả và hoàn thiện báo cáo.

Các thao tác có minh chứng ngày 18/10 được ghi tại mục 2 như một mốc chuẩn bị. Mục 3 là **kế hoạch 20,0 giờ**, chưa phải số giờ đã thực hiện. Cột giờ thực tế để **“Chờ xác nhận”** và chưa được cộng vào [nhật ký Tuần 1–2](../../docs/WORKLOG.md), có tổng **38,0 giờ** đã xác nhận. Thời gian chạy AWS, thời điểm commit và thời gian kiểm thử không được dùng thay số giờ làm việc của sinh viên.

## 2. Nhật ký chuẩn bị ngày 18/10/2026

Các giờ bên dưới là thời điểm của commit hoặc kết quả hệ thống, không phải giờ bắt đầu/kết thúc ca làm của sinh viên. Trách nhiệm rà soát được ghi theo phân công của dự án.

| Mốc ngày 18/10, UTC+7 | Công việc và kết quả đã lưu | Phụ trách rà soát | Minh chứng trực tiếp |
| --- | --- | --- | --- |
| Trước mốc tích hợp 12:44 | Đọc trạng thái Lambda, lịch gọi và dữ liệu S3; lưu 237 bản ghi của sinh viên Tiến Sơn và 273 bản ghi của sinh viên Ngọc Quyên. Bảy nhóm kiểm tra chất lượng đã khai báo không phát hiện lỗi; chưa có bản ghi thuộc lịch 19–25/10. | Sinh viên Tiến Sơn: trạng thái triển khai; sinh viên Ngọc Quyên: dữ liệu và chất lượng | [Snapshot sinh viên Tiến Sơn](../results/integration_2026_10_18/snapshot/default/) · [Snapshot sinh viên Ngọc Quyên](../results/integration_2026_10_18/snapshot/quyen/) |
| Mốc commit 12:44 | Hoàn thiện công cụ tích hợp, thử nghiệm Athena và bộ đánh giá dự báo. Thực hiện 18 truy vấn trên ba cách lưu/khai báo trong hai môi trường; kết quả tổng hợp khớp đầu vào. Tạo Dashboard riêng và lưu metric cùng ảnh AWS. | Sinh viên Ngọc Quyên: Athena và dự báo; sinh viên Tiến Sơn: Dashboard và triển khai | [Commit 0b26858](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e) · [18 lượt truy vấn](../results/integration_2026_10_18/benchmark/) · [Dashboard](../results/integration_2026_10_18/dashboard/) |
| Mốc commit 12:48 và hai lượt CD tiếp theo | Sửa metadata và phương thức lưu ZIP để artifact Windows/Linux khớp byte. Hai workflow CD cập nhật mã thành công; gói tải lại từ AWS khớp artifact và cấu hình được giữ nguyên. Xóa secrets tạm sau kiểm chứng. | Sinh viên Tiến Sơn | [Commit c28da19](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356) · [CD sinh viên Tiến Sơn](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450) · [CD sinh viên Ngọc Quyên](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) · [Hồ sơ đọc lại và dọn secrets](../results/cd_2026_10_18/) |
| Mốc commit 12:56 | Bổ sung hồ sơ CD và biểu thức Dashboard chỉ tính tỷ lệ khi bộ đếm đầy đủ, hợp lệ. Giữ nguyên số đo Errors cao hơn Invocations để tiếp tục đối chiếu; chưa xác định nguyên nhân. | Sinh viên Tiến Sơn | [Commit 86a064c](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/86a064cdc5c13e3046b0291a2ac866f6e55872ef) · [431 dòng metric và ảnh AWS](../results/monitoring_2026_10_18/) |
| Đối chiếu bổ sung và lượt theo lịch 13:15 | Cấu hình hai Metric Filters trong mỗi môi trường; kiểm tra mẫu khớp/không khớp và đọc lại cấu hình. Đối chiếu GetMetricData với GetMetricStatistics. Lượt tự động của sinh viên Tiến Sơn thu đủ ba đô thị, ba bản ghi khớp S3 và tạo một điểm ResultLogLines. Không có mẫu vượt ngưỡng, số cảnh báo bằng 0 đúng điều kiện. | Sinh viên Tiến Sơn; sinh viên Ngọc Quyên đối chiếu raw | [Commit 65b4550](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/65b4550cc8a8d34b1a77449a2650c86df2dc18d3) · [Metric Filters và log–S3](../results/operations_2026_10_18/) · [Lượt theo lịch của sinh viên Tiến Sơn](../results/operations_2026_10_18/scheduled_followup/collections/default/) |
| Cùng đợt đối chiếu cấu hình | Sửa định dạng JSON của cấu hình sinh viên Ngọc Quyên trong Secrets Manager; kiểm tra các trường vận hành không đổi, giữ phiên bản trước và đọc lại phiên bản mới. Lượt 12:51 có trước lần sửa, vì vậy chưa dùng lượt đó để kết luận cấu hình sau sửa đã chạy đạt. | Sinh viên Tiến Sơn; sinh viên Ngọc Quyên rà soát môi trường của mình | [Biên bản sửa định dạng, không chứa giá trị Secret](../results/operations_2026_10_18/configuration-format-repair.json) · [Lượt trước sửa của sinh viên Ngọc Quyên](../results/operations_2026_10_18/scheduled_followup/collections/quyen/) |
| Mốc commit 13:28 | Sửa thời điểm phát hành dự báo sau khi phát hiện sáu dòng của bản đầu có giờ đích trước lúc lấy nguồn. Bản bổ sung có 522 dòng lịch sử mô hình, 432 dòng đánh giá giữ lại và 144 giá trị cho 24 giờ đích sau phát hành. Bộ hồi quy Tuần 3 có 32 trường hợp; CI của commit thành công. | Sinh viên Ngọc Quyên; hai sinh viên đối chiếu báo cáo | [Commit cf05203](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/cf05203c2e599ab0eddfb90216fdfb54ff126b90) · [Dữ liệu và biểu đồ dự báo](../results/forecast_issued_2026_10_18/) · [CI của commit](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39104190458) |
| Lượt theo lịch 13:51; quan sát metric đến 13:52 | Kiểm chứng sinh viên Ngọc Quyên sau sửa JSON: log hoàn tất, ba đô thị/ba bản ghi khớp S3, 0 cảnh báo phù hợp với raw dưới ngưỡng. Có một điểm ResultLogLines mới; truy vấn cửa sổ quanh lượt này không thấy thông báo đọc Secret thất bại. | Sinh viên Tiến Sơn: vận hành; sinh viên Ngọc Quyên: raw và ngưỡng | [Hồ sơ sau sửa](../results/post_repair_2026_10_18/README.md) · [CSV đối chiếu](../results/post_repair_2026_10_18/collection_check/quyen/collection_checks.csv) · [Raw](../results/post_repair_2026_10_18/collection_check/quyen/raw_verified.csv) · [Ảnh metric AWS](../results/post_repair_2026_10_18/cloudwatch_log_metrics.png) |

Các thư mục kết quả là những mốc chụp riêng. Chẳng hạn, snapshot đầu có 273 bản ghi của sinh viên Ngọc Quyên, snapshot vận hành sau có 276 bản ghi. Đây là cập nhật theo thời điểm thu thập; không cộng các snapshot thành những quan sát độc lập. Tương tự, các cửa sổ metric có thể chồng lên nhau.

**Rà soát bổ sung ngày 18/10:** tính lại tổng hợp từ raw cho đủ 18 truy vấn Athena, đối chiếu các trung vị đã báo cáo và toàn bộ 432 dòng đánh giá của mỗi mốc dự báo; các giá trị khớp. Phát hiện và sửa nhánh xử lý lỗi của công cụ triển khai để ghi trạng thái thất bại khi không nhận được xác nhận cập nhật hoặc không đọc được RevisionId hiện tại. Hai hồi quy mới thất bại trước sửa và đạt sau sửa; cả bảy kiểm tra tập trung vào triển khai/khôi phục đạt. Không triển khai lại Lambda và không gây lỗi lên AWS thật trong lần rà soát này.

## 3. Kế hoạch thực hiện và theo dõi thời gian

Ngày và thời lượng dưới đây là **dự kiến phân bổ cho tuần 19–25/10**, tập trung rà soát sản phẩm chuẩn bị và bổ sung quan sát trong tuần. Khi ghi giờ thực tế, cần thêm ngày làm, kết quả và minh chứng tương ứng. Không ghi lại công việc chuẩn bị ngày 18/10 thành công việc đã làm trong một ngày tương lai.

| Mã | Ngày dự kiến | Sinh viên phụ trách | Công việc dự kiến và sản phẩm bàn giao | Tiêu chí hoàn thành | Giờ dự kiến | Giờ thực tế |
| --- | --- | --- | --- | --- | ---: | --- |
| W3-01 | 19/10 | Sinh viên Tiến Sơn | Rà soát phiên bản Lambda sau CD, hash gói, trạng thái, cấu hình và phương án khôi phục; bổ sung mốc đọc lại khi có thay đổi. | Hash khớp bản phát hành; có biên bản trạng thái/cấu hình và đường dẫn gói khôi phục được bảo vệ. | 2,0 | Chờ xác nhận |
| W3-02 | 19–20/10 | Sinh viên Tiến Sơn | Theo dõi các lượt thực sự chạy theo lịch trong phiên Lab; đối chiếu log, ba đô thị và đối tượng S3; ghi các khoảng thiếu dữ liệu. | Mỗi lượt được kết luận có log và raw đối chiếu; số bản ghi, lỗi và cảnh báo khớp; chưa quan sát thì ghi rõ. | 2,0 | Chờ xác nhận |
| W3-03 | 20/10 | Sinh viên Ngọc Quyên | Rà soát thí nghiệm Projection/Parquet; đối chiếu lược đồ, phạm vi ngày, số dòng, truy vấn và trung vị ba lần đo; giải thích lợi ích cùng giới hạn. | 18 lượt có đầu vào và tổng hợp khớp; phân biệt byte quét, thời gian chạy và chi phí; chỉ đo lại khi thay đầu vào hoặc có lỗi cần kiểm chứng. | 3,0 | Chờ xác nhận |
| W3-04 | 20–21/10 | Sinh viên Ngọc Quyên | Xuất snapshot mới khi có dữ liệu trong tuần; kiểm tra lược đồ, kiểu số, thời gian UTC/Việt Nam, phân vùng và độ phủ đô thị–giờ. | Có raw, bảng chất lượng và phạm vi thời gian; số liệu trong báo cáo/biểu đồ truy về đúng snapshot, giữ nguyên raw lịch sử. | 2,0 | Chờ xác nhận |
| W3-05 | 21–22/10 | Sinh viên Tiến Sơn | Kiểm tra điểm metric phát sinh sau Metric Filters của cả hai môi trường; đối chiếu Dashboard, log và bộ đếm native đang bất thường. | Lưu cấu hình, cửa sổ quan sát và điểm metric thực; không coi thiếu điểm là 0; bất thường chưa giải thích được tiếp tục ghi là giới hạn. | 2,5 | Chờ xác nhận |
| W3-06 | 22/10 | Sinh viên Tiến Sơn | Rà soát điều kiện AQI/PM2.5 và luồng cảnh báo email; đối chiếu số cảnh báo với raw. Nếu có cảnh báo mới, bổ sung bằng chứng SNS và xác nhận người nhận. | Mẫu dưới ngưỡng có 0 cảnh báo là hợp lệ; chỉ xác nhận gửi/nhận email mới khi có minh chứng tương ứng. Giữ email là kênh duy nhất. | 1,5 | Chờ xác nhận |
| W3-07 | 22–23/10 | Sinh viên Ngọc Quyên | Rà soát phép chia theo thời gian và ba phương pháp dự báo; đối chiếu các giờ đích đã qua khi đủ dữ liệu cùng định nghĩa; bổ sung MAE/RMSE/Bias và biểu đồ màu. | Không dùng dữ liệu đích để dự báo ngược; CSV và biểu đồ khớp; phân biệt đánh giá giữ lại, dữ liệu mô hình và dự báo thực sự phát hành trước giờ đích. | 3,5 | Chờ xác nhận |
| W3-08-S | 24–25/10 | Sinh viên Tiến Sơn | Rà soát tài liệu vận hành, minh chứng CI/CD và triển khai; cùng hoàn thiện nội dung kết luận, link commit và nhật ký. | Link truy cập đúng; chỉ ghi gate đã chạy; không đưa khóa phiên hoặc cấu hình bí mật vào hồ sơ; xác nhận giờ làm của mình. | 2,0 | Chờ xác nhận |
| W3-08-Q | 24–25/10 | Sinh viên Ngọc Quyên | Rà soát raw/CSV/biểu đồ, cách diễn giải số liệu và giới hạn kết luận; đối chiếu phân công với sản phẩm và nhật ký. | Mỗi nhận định có dữ liệu hỗ trợ; số liệu và tên sinh viên nhất quán; xác nhận giờ làm của mình. | 1,5 | Chờ xác nhận |

### Tổng thời gian dự kiến

| Sinh viên | Các đầu việc | Giờ dự kiến | Tổng giờ thực tế |
| --- | --- | ---: | --- |
| Sinh viên Tiến Sơn | W3-01, W3-02, W3-05, W3-06, W3-08-S | 10,0 | Chờ xác nhận |
| Sinh viên Ngọc Quyên | W3-03, W3-04, W3-07, W3-08-Q | 10,0 | Chờ xác nhận |
| **Tổng** | | **20,0** | **Chưa chốt** |

Các giờ dự kiến là phân bổ ban đầu, có thể điều chỉnh theo công việc thực hiện. Không xem tổng 20,0 giờ là tổng đã hoàn thành hoặc cộng vào 38,0 giờ của Tuần 1–2.

## 4. Mẫu bổ sung nhật ký thực tế

Mỗi sinh viên ghi một dòng cho mỗi buổi làm; nếu cùng làm một đầu việc thì ghi thời gian riêng của từng người. Chỉ tính thời gian trực tiếp thực hiện/rà soát công việc, không tính toàn bộ khoảng máy chủ chạy tự động hoặc khoảng chờ lịch.

| Ngày thực hiện | Sinh viên | Mã đầu việc | Nội dung đã thực hiện và kết quả | Số giờ thực tế | Link minh chứng | Xác nhận |
| --- | --- | --- | --- | --- | --- | --- |
| Chờ cập nhật | Sinh viên Tiến Sơn | Chờ cập nhật | Chờ cập nhật sau buổi làm | Chờ xác nhận | Chờ bổ sung | Chưa xác nhận |
| Chờ cập nhật | Sinh viên Ngọc Quyên | Chờ cập nhật | Chờ cập nhật sau buổi làm | Chờ xác nhận | Chờ bổ sung | Chưa xác nhận |

## 5. Trạng thái cần tiếp tục theo dõi

- **Sinh viên Ngọc Quyên:** lượt 13:51 sau sửa JSON đã khớp log/raw và có metric mới; tiếp tục theo dõi các lượt trong tuần để đánh giá độ phủ. Lượt đơn lẻ không chứng minh vận hành liên tục.
- **Bộ đếm CloudWatch native:** hai API trả cùng các điểm đã lưu nhưng Errors cao hơn Invocations; chưa xác định nguyên nhân. Không dùng tỷ lệ lỗi của cửa sổ đó làm kết luận vận hành ổn định.
- **Độ phủ Tuần 3:** tại mốc chuẩn bị ngày 18/10 có 0 bản ghi thuộc 19–25/10. Chỉ cập nhật độ phủ sau khi có dữ liệu đúng khoảng ngày.
- **Email:** xác nhận nhận thư ngày 16/10 là bằng chứng của lượt lịch sử đó. Những lượt mới không vượt ngưỡng không chứng minh lại bước nhận email.
- **Dự báo:** chưa có đủ giá trị đích để đánh giá toàn bộ 24 giờ dự báo mới; kết quả giữ lại không thay thế độ chính xác tương lai.
- **Thời gian sinh viên:** kế hoạch đã có phân công và tổng giờ dự kiến; tổng giờ thực tế Tuần 3 chờ xác nhận trước khi chốt báo cáo cuối tuần.

[Báo cáo kỹ thuật](FINAL_REPORT.md) · [Hướng dẫn vận hành](operation.md) · [Hồ sơ Tuần 3](../README.md) · [Nhật ký Tuần 1–2](../../docs/WORKLOG.md)
