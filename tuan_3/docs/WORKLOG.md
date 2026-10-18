# Nhật ký kỹ thuật và tổng giờ sinh viên công bố — Tuần 3

**Nguyễn Tiến Sơn — 24110054 · Trần Thị Ngọc Quyên — 24110051**

## 1. Phạm vi ghi nhận

Hồ sơ ghi các mốc kỹ thuật chuẩn bị ngày 18/10/2026 và tổng giờ hai sinh viên công bố cho công việc tích hợp Tuần 3. Kỳ Tuần 3 theo lịch là 19–25/10; dữ liệu ngày 18/10 được giữ đúng ngày thực tế, không đổi thành dữ liệu trong tuần sau. Thời điểm log/commit ở mục 2 là thời điểm hệ thống, không phải ngày hoặc ca làm việc của sinh viên.

Tổng thời gian được ghi theo thông tin sinh viên công bố, không suy từ AWS/commit và không tự chia thành giờ thực tế cho từng đầu việc. Không ghi ngày làm việc khi chưa có nhật ký ngày tương ứng.

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

## 3. Tổng giờ theo thông tin sinh viên công bố

| Giai đoạn | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên | Tổng | Căn cứ |
| --- | --- | --- | --- | --- |
| Tuần 1 | 9,5 giờ | 9,0 giờ | 18,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 2 | 10,0 giờ | 9,5 giờ | 19,5 giờ | Tổng theo tuần đã xác nhận |
| Tuần 3 — công việc tích hợp | 10,0 giờ | 10,0 giờ | 20,0 giờ | Tổng do sinh viên công bố, không phân bổ ngày |
| **Cộng dồn** | **29,5 giờ** | **28,5 giờ** | **58,0 giờ** | Không suy số giờ từ thời gian hệ thống chạy |

[CSV tổng giờ Tuần 3](../worklog.csv) · [Bản CSV trong hồ sơ](worklog.csv) · [Tổng Tuần 1–2](../../worklog.csv).

Hai dòng CSV Tuần 3 ghi tổng 10,0 giờ mỗi sinh viên, không chứa ngày làm hoặc phân bổ giờ theo nhiệm vụ. Các mốc kỹ thuật là căn cứ về sản phẩm, không tự chứng minh thời lượng lao động.

## 4. Phân công và rà soát cập nhật

- Sinh viên Tiến Sơn: phiên bản triển khai, lịch thu thập, cấu hình, giám sát và cảnh báo email.
- Sinh viên Ngọc Quyên: raw, Glue/Athena, thống kê, đối chiếu dự báo và CSV/biểu đồ.
- Hai sinh viên: đối chiếu kết quả, rà soát báo cáo và các liên kết minh chứng.

Đợt đọc mới sau cập nhật phiên Lab có 246/285 bản ghi; mã Lambda khớp gói đã kiểm chứng. [Hồ sơ mới](../results/refresh_2026_10_18/README.md) bổ sung thống kê tái lập, so sánh MA 3 giờ và đối chiếu được 2/24 giờ đích với dữ liệu mô hình tải về sau. Không ghi 2 giờ này là toàn bộ 24 giờ đã đánh giá.

## 5. Phần cần tiếp tục theo dõi

Raw hiện có 0 bản ghi thuộc kỳ 19–25/10. Các bộ đếm CloudWatch native không nhất quán vẫn là giới hạn chưa xác định nguyên nhân. Xác nhận email ngày 16/10 là bằng chứng của đợt đó; lượt dưới ngưỡng không chứng minh nhận email mới. Số giờ sinh viên công bố được ghi riêng với độ phủ dữ liệu và trạng thái kỹ thuật.

[Báo cáo kỹ thuật](FINAL_REPORT.md) · [Vận hành](operation.md) · [Hồ sơ Tuần 3](../README.md)
