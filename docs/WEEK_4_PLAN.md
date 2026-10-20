# Kế hoạch Tuần 4 — Vận hành, đánh giá và hoàn thiện hồ sơ

**Sinh viên thực hiện:** Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051).

**Học phần:** Điện toán đám mây · Lớp 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.

**Ngày lập:** 19/10/2026 · **Trạng thái:** Đã bổ sung yêu cầu tổng kết theo nhận xét giảng viên; kiểm chứng chuẩn bị được lưu riêng theo ngày thực hiện.

**Lịch đề xuất:** 26/10–01/11/2026, tiếp nối lịch Tuần 3 ngày 19–25/10. Đây là lịch dự kiến để tổ chức công việc; mốc nộp thực hiện theo thông báo của giảng viên.

## 1. Mục tiêu

Tuần 4 tiếp tục khai thác hệ thống đã tích hợp, tập trung vào chất lượng vận hành theo lịch, cảnh báo email và khả năng tái lập kết quả phân tích. Mỗi kết luận trong báo cáo sẽ có dữ liệu đầu vào, thời điểm thực hiện, mã nguồn và minh chứng tương ứng.

- Theo dõi luồng EventBridge → Lambda → S3 cho ba đô thị trong các phiên AWS Learner Lab hoạt động.
- Đối chiếu log, bộ đếm CloudWatch và dữ liệu S3 theo cùng thời điểm; hoàn thiện Dashboard phục vụ theo dõi.
- Kiểm chứng luồng cảnh báo AQI/PM2.5 từ điều kiện ngưỡng đến SNS và hộp thư người nhận.
- Tiếp tục đo NDJSON/Projection/Parquet trên bộ dữ liệu được chốt, đồng thời cập nhật thống kê và biểu đồ màu từ CSV nguồn.
- Đánh giá thêm các kỳ dự báo có thời điểm phát hành, sau đó hoàn thiện báo cáo, nhật ký và nội dung trình bày.

**Phạm vi:** giữ kiến trúc serverless hiện có, ba đô thị và kênh email. Thực hiện trên hai môi trường của sinh viên Tiến Sơn và sinh viên Ngọc Quyên, bằng SDK và workflow đã có trong repository.

## 2. Kết quả Tuần 3 làm đầu vào

| Đầu vào đã có | Mốc và cách sử dụng trong Tuần 4 |
| --- | --- |
| Mã thu thập đã triển khai | [Commit 62f1c08](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/62f1c08e20e7a31447f10d713d4e115d4147c650), có [CI thành công](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39215400909); đối chiếu lại phiên bản trước khi thực hiện công việc mới |
| Raw và nguồn từng bản ghi | [Bản xuất ngày 19/10](../tuan_3/results/daily_update_2026_10_19/README.md): 302/339 bản ghi tích lũy, 95 JSON gốc; số liệu trong ngày chốt lúc 14:22–14:23 UTC+7, thống kê chung 00:00–13:00 |
| Thử nghiệm Athena | [18 lượt đo trên cùng đầu vào](../tuan_3/results/integration_2026_10_18/benchmark/); giữ làm kết quả tham chiếu, lập bộ đo mới cho dữ liệu Tuần 4 |
| Dashboard và phương pháp đối chiếu | [Cấu hình đọc lại từ hai môi trường](../tuan_3/results/monitoring_dashboard_repair_2026_10_18/README.md), [phương pháp vận hành](../tuan_3/docs/operation.md) |
| Cảnh báo email | [Các lượt theo lịch và xác nhận người nhận ngày 16/10](scheduled-run-verification.md); Tuần 4 lập minh chứng riêng cho lượt kiểm tra mới |
| Dự báo đã phát hành | [Kết quả đủ 24/24 giờ đích, 144 giá trị](../tuan_3/results/forecast_followup_2026_10_19/README.md), dùng làm mẫu tổ chức dữ liệu và tính sai số |
| Phân công và nhật ký | [58,0 giờ đã xác nhận của Tuần 1–3](WORKLOG.md); thời gian Tuần 4 được ghi riêng theo công việc thực hiện và xác nhận của sinh viên |

## 3. Phân công

| Sinh viên | Trách nhiệm chính | Trách nhiệm rà soát chéo |
| --- | --- | --- |
| Sinh viên Tiến Sơn | Lambda, EventBridge, S3, Secrets Manager, SNS, CloudWatch và triển khai | Đối chiếu nguồn raw, thời điểm, liên kết minh chứng của phần phân tích |
| Sinh viên Ngọc Quyên | Glue/Athena, chất lượng dữ liệu, xuất CSV, thống kê, biểu đồ và dự báo | Đối chiếu log–S3, ngưỡng cảnh báo và phiên bản mã trong hồ sơ vận hành |
| Hai sinh viên | Tổng hợp báo cáo, kiểm tra repository, hoàn thiện nhật ký và trình bày | Kiểm tra nội dung trước khi công bố; xác nhận riêng số giờ của từng sinh viên |

## 4. Đầu việc, sản phẩm và tiêu chí hoàn thành

Các mã W4-01–W4-08 dưới đây là **đầu việc dự kiến**. Đường dẫn đầu ra Tuần 4 là quy ước sẽ sử dụng khi thực hiện; kết quả Tuần 1–3 được giữ nguyên theo mốc.

| Mã | Nội dung và người phụ trách | Sản phẩm dự kiến | Tiêu chí hoàn thành |
| --- | --- | --- | --- |
| W4-01 | **Chốt phiên bản và cấu hình** — sinh viên Tiến Sơn | Bảng commit/hash Lambda, rule/target, cấu hình ngưỡng đã loại giá trị bí mật, gói khôi phục lưu riêng | Hai môi trường có thời điểm đọc và phiên bản xác định; đối chiếu mã triển khai với source; lịch chuẩn có đúng target và quyền gọi hàm |
| W4-02 | **Thu thập và xuất raw theo ngày** — sinh viên Tiến Sơn; sinh viên Ngọc Quyên kiểm tra | JSON gốc, CSV đủ trường, danh mục object/hash, bảng đô thị–giờ và nguồn từng bản ghi | Đối chiếu số dòng JSON–CSV; đủ ba đô thị trong mỗi lượt báo complete; mọi giờ dự kiến trong phiên Lab có trạng thái đối chiếu; tách lượt theo lịch, gọi trực tiếp và backfill |
| W4-03 | **Đối chiếu CloudWatch và Dashboard** — sinh viên Tiến Sơn | CSV native metric/log metric, bảng ghép theo thời gian, cấu hình Dashboard và ảnh do AWS trả về | Cùng hàm, dimension, cửa sổ UTC và chu kỳ 300 giây; đối chiếu request với log và object S3; mỗi giá trị tỷ lệ truy được về cặp Errors/Invocations hợp lệ |
| W4-04 | **Kiểm chứng cảnh báo email** — sinh viên Tiến Sơn; sinh viên Ngọc Quyên rà soát | Bảng dữ liệu–ngưỡng–kết quả, phản hồi SNS đã loại thông tin riêng tư, xác nhận người nhận | Mỗi môi trường có trường hợp dưới ngưỡng và trường hợp vượt ngưỡng được kiểm tra có kiểm soát; ghi riêng điều kiện cảnh báo, Publish, giao thông báo và xác nhận email của lượt mới |
| W4-05 | **Đo truy vấn và thống kê** — sinh viên Ngọc Quyên | Bộ SQL/CSV, query ID, ba lần đo mỗi cấu hình mỗi môi trường, thống kê và biểu đồ màu | Cùng bản chốt đầu vào cho NDJSON, NDJSON Projection và Parquet Projection; tắt dùng lại kết quả; tổng hợp median bytes, engine time và total time; hình khớp CSV |
| W4-06 | **Đánh giá các kỳ dự báo kế tiếp** — sinh viên Ngọc Quyên | Dự báo có issued_at, phản hồi nguồn, bảng đối chiếu và MAE/RMSE/Bias theo đô thị/chỉ số | Mục tiêu ba kỳ phát hành cách nhau 24 giờ, mỗi kỳ 24 giờ đích cho ba đô thị và hai chỉ số; cố định phương pháp trước khi xem giá trị đích; lưu nguyên bản phát hành |
| W4-07 | **Kiểm tra mã và quy trình phát hành** — sinh viên Tiến Sơn; hai sinh viên rà soát | Kết quả hồi quy, artifact xác định, CI theo commit; hồ sơ phát hành nếu có thay đổi source | Các kiểm tra liên quan đạt; source/artifact có hash; nếu triển khai, đọc lại mã và cấu hình của từng môi trường, có bản sao khôi phục riêng |
| W4-08 | **Tổng hợp hồ sơ và trình bày** — hai sinh viên | README Tuần 4, báo cáo, worklog, chỉ mục dữ liệu/commit và nội dung trình bày | Tất cả liên kết công khai mở đúng tệp; số liệu trong báo cáo khớp CSV; ghi trạng thái từng đầu việc theo minh chứng và giờ công theo xác nhận thực tế |
| W4-09 | **Báo cáo chi phí** — sinh viên Ngọc Quyên | CSV Cost Explorer theo ngày, service, record type, USD và Estimated | Giữ nguyên giá trị gốc; phân biệt chi phí tài khoản và mức dự kiến; nhóm chưa được AWS trả về không coi là chi phí 0 |
| W4-10 | **Kết thúc phiên Lab** — sinh viên Tiến Sơn; hai sinh viên đối chiếu | Checklist xuất minh chứng, preview/pause/restore và state file riêng | Đọc lại đúng rule/target; giữ dữ liệu; không tự thu hồi toàn dự án khi kết thúc một buổi |
| W4-11 | **Đóng gói hạ tầng** — sinh viên Tiến Sơn | Một template CloudFormation, ZIP đúng source, hash và hướng dẫn triển khai Console | Template được kiểm tra schema; stack mới có tên riêng, lịch ban đầu tắt và dữ liệu Retain; kết quả tạo stack được ghi riêng khi thực hiện |
| W4-12 | **Rà soát bảo mật** — sinh viên Tiến Sơn; sinh viên Ngọc Quyên kiểm tra | BPA, mã hóa, ACL/policy status, rule binding và scope LabRole | Bốn BPA bật, không public ACL/policy; không sửa role học phần dùng chung; mẫu policy runtime giới hạn theo tài nguyên |

### Bổ sung theo nhận xét duyệt Tuần 3

- Cạnh mỗi link commit trong nội dung nộp ghi **đúng message gốc của Git**; phần giải thích tiếng Việt có thể đặt sau nhưng không thay message.
- Video demo tối đa **10 phút**, trình bày luồng xử lý, kết quả thực tế và quản lý tài nguyên; bổ sung liên kết sau khi quay và kiểm tra quyền xem.
- [Hồ sơ Tuần 4](../tuan_4/README.md) tập hợp source kiểm chứng, một template ứng dụng và quy trình [kết thúc phiên Lab](../tuan_4/docs/SESSION_CHECKLIST.md).
- Các lần chuẩn bị/kiểm chứng ngày 19/10 được ghi đúng ngày thực hiện; không thay thế các kỳ thu thập và dự báo dự kiến trong lịch tuần bên dưới.

### 4.1. Trình tự và phụ thuộc

1. **W4-01 trước W4-02–W4-04:** xác định chính xác phiên bản và cấu hình đang được theo dõi.
2. **W4-02 trước W4-05:** chốt dữ liệu, kiểm tra chất lượng rồi mới tạo bảng và đo truy vấn.
3. **W4-06 khởi động ngay đầu tuần:** phát hành kỳ thứ nhất ngày 26/10, kỳ thứ hai ngày 27/10, kỳ thứ ba ngày 28/10; thu giá trị đối chiếu sau khi các giờ đích hoàn tất.
4. **W4-07 áp dụng cho từng thay đổi source:** CI trước triển khai; theo dõi lượt sau triển khai với đúng phiên bản mới.
5. **W4-08 tổng hợp sau các điểm kiểm tra:** mỗi mục báo cáo dẫn về sản phẩm và commit thực hiện tương ứng.

### 4.2. Nội dung đối chiếu vận hành

- Lập danh sách giờ dự kiến trong từng phiên Lab, lấy từ lịch và thời gian phiên hoạt động. Ghi thời điểm sự kiện, request ID đã xử lý thông tin riêng tư, trạng thái Lambda, object S3, số đô thị và số cảnh báo.
- Phân biệt thời gian của dữ liệu mô hình với thời điểm Lambda thu thập; ngày báo cáo dùng UTC+7, phân vùng S3 giữ UTC.
- Giữ riêng dữ liệu gốc và bảng theo đô thị–giờ. Thống kê so sánh sử dụng cùng tập giờ hoàn tất và cùng trọng số cho mỗi giờ.
- Native metric và Metric Filters có bảng riêng. Tỷ lệ lỗi sử dụng cặp Errors/Invocations cùng chu kỳ, với Invocations > 0 và Errors ≤ Invocations; khoảng vắng metric giữ trạng thái thiếu dữ liệu trong bảng kỹ thuật.
- Với cảnh báo, đối chiếu đúng quy tắc `AQI >= threshold_aqi OR PM2.5 >= threshold_pm25`. Giữ cấu hình ngưỡng hiện hành; kiểm tra dữ liệu mẫu cục bộ trước bước kiểm chứng dịch vụ. Lượt backfill lưu ở chế độ lịch sử và gửi 0 cảnh báo lịch sử.
- Tài liệu công khai dùng minh chứng đã loại địa chỉ email, mã tài khoản, khóa phiên và giá trị Secret. Xác nhận người nhận gắn với đúng lượt thông báo.

### 4.3. Nội dung đánh giá phân tích

- Mỗi bộ đo Athena ghi số dòng nguồn, mốc chốt, lược đồ, vị trí đầu vào và query ID. Đo ba lần mỗi cấu hình/môi trường, tổng hợp cả từng lượt và trung vị.
- Báo cáo byte quét và thời gian bằng đơn vị cụ thể. Phần chi phí giữ riêng số Cost Explorer, cờ Estimated và mức dự kiến do sinh viên xác nhận.
- Dự báo dùng nguồn mô hình Open-Meteo/CAMS. Cố định các phương pháp cơ sở và cửa sổ trước kỳ đánh giá; giữ riêng phân tích khám phá bổ sung.
- Mỗi kỳ dự báo có 144 giá trị đích dự kiến (24 giờ × 3 đô thị × 2 chỉ số). Mục tiêu ba kỳ tạo 432 giá trị đối chiếu cho mỗi phương pháp được phát hành đủ ba kỳ; bảng kết quả ghi số giá trị thực sự đối chiếu được.
- Tính MAE/RMSE/Bias cho từng kỳ trước khi tổng hợp; ghi rõ Bias = trung bình(dự báo − giá trị mô hình tải về sau). Giữ mốc tải và phản hồi nguồn để tái lập phép tính.

## 5. Lịch thực hiện đề xuất

| Ngày dự kiến, UTC+7 | Công việc | Điểm kiểm tra cuối ngày |
| --- | --- | --- |
| 26/10 | W4-01; bắt đầu W4-02/W4-03; phát hành dự báo kỳ 1 | Chốt baseline hai môi trường, danh sách giờ theo dõi, bản dự báo kỳ 1 và dữ liệu đầu vào |
| 27/10 | Tiếp tục thu thập, đối chiếu metric; kiểm chứng email W4-04; phát hành kỳ 2 | Bảng lượt theo lịch, kết quả hai trường hợp cảnh báo và hồ sơ dự báo kỳ 2 |
| 28/10 | Xuất raw tiếp theo, rà soát chất lượng; phát hành kỳ 3; chốt đầu vào Athena | CSV/JSON/hash khớp; cố định bộ đo và truy vấn; đủ ba bản phát hành để theo dõi |
| 29/10 | W4-05; thu giá trị đích đã hoàn tất của ba kỳ | Bảng từng lượt đo Athena, kết quả truy vấn theo đô thị và dữ liệu đối chiếu dự báo |
| 30/10 | W4-06; tổng hợp thống kê và biểu đồ | Bảng sai số theo kỳ, CSV nguồn và biểu đồ màu có đơn vị, chú giải, thời gian |
| 31/10 | W4-07; rà soát chéo toàn bộ hồ sơ | Kiểm tra mã/dữ liệu đạt, CI theo commit; đọc lại AWS nếu có phát hành mới |
| 01/11 | W4-08; hoàn thiện nội dung nộp và demo | README, báo cáo, worklog, liên kết commit và nội dung trình bày thống nhất |

Các lượt thu thập theo lịch được theo dõi trong suốt các phiên Lab hoạt động của tuần, kèm thời điểm bắt đầu/kết thúc phiên trong hồ sơ kỹ thuật.

## 6. Tổ chức sản phẩm dự kiến

| Đường dẫn dự kiến | Nội dung |
| --- | --- |
| `tuan_4/README.md` | Tóm tắt kết quả, điều hướng dữ liệu, biểu đồ và commit |
| `tuan_4/docs/FINAL_REPORT.md` | Mục tiêu, triển khai, số liệu, giải thích cấu hình, kết luận và công việc tiếp theo |
| `tuan_4/docs/WORKLOG.md` | Nhật ký công việc và số giờ do từng sinh viên xác nhận |
| `tuan_4/results/<moc-thoi-gian>/raw/` | JSON/CSV nguồn, danh mục object và manifest SHA-256 |
| `tuan_4/results/<moc-thoi-gian>/monitoring/` | Log, metric, Dashboard và bảng đối chiếu lượt chạy |
| `tuan_4/results/<moc-thoi-gian>/alerts/` | Minh chứng kiểm tra ngưỡng, SNS và xác nhận email đã loại thông tin riêng tư |
| `tuan_4/results/<moc-thoi-gian>/benchmark/` | Truy vấn, query ID, từng lượt đo và bảng tổng hợp |
| `tuan_4/results/<moc-thoi-gian>/forecast/` | Bản phát hành, nguồn tải về sau, bảng so sánh, sai số và hình |

Tái sử dụng các module thu thập, SDK, phân tích và triển khai hiện có; đặt phần điều phối Tuần 4 riêng khi cần. Mỗi thư mục kết quả được tạo sau khi có đầu ra thực tế, có README giải thích nguồn và lệnh tái lập.

## 7. Kiểm tra và nghiệm thu

### 7.1. Kiểm tra repository trước khi phát hành

Chạy từ thư mục gốc, trong môi trường đã cài [phụ thuộc hiện có](../tuan_3/requirements.txt):

```bash
python tuan_2/scripts/repository_audit.py --check
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p 'test_*.py' -v
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
python tuan_3/scripts/release.py --output output/lambda-artifact
git diff --check
```

Đây là các kiểm tra hiện có. Khi bổ sung đầu ra Tuần 4, cần nối kiểm tra manifest, JSON–CSV, giờ dữ liệu, bảng sai số và liên kết của đầu ra mới vào bộ xác minh/CI tương ứng trước khi nghiệm thu W4-08.

### 7.2. Hồ sơ nghiệm thu cuối tuần

- [ ] W4-01: bảng phiên bản/config hai môi trường có timestamp và mã commit.
- [ ] W4-02: raw, nguồn bản ghi, số dòng, chất lượng, danh mục object và hash khớp nhau.
- [ ] W4-03: log–metric–S3 truy được theo lượt; cấu hình Dashboard đọc lại khớp; tỷ lệ có mẫu số rõ ràng.
- [ ] W4-04: kiểm tra dưới/vượt ngưỡng có kết quả; cả hai môi trường có hồ sơ email mới và xác nhận người nhận.
- [ ] W4-05: 18 lượt đo Athena theo thiết kế, cùng đầu vào cho mỗi môi trường; hình và bảng khớp CSV.
- [ ] W4-06: ba kỳ dự báo có thời điểm phát hành, bảng giá trị đích và sai số theo đúng phạm vi đã thu được.
- [ ] W4-07: CI đạt trên đúng commit; nếu triển khai, hash AWS và cấu hình khớp bản đã kiểm tra.
- [ ] W4-08: nội dung nộp có liên kết repo, hồ sơ tuần, raw, biểu đồ, worklog và ít nhất 2–3 commit trực tiếp phù hợp công việc.

## 8. Vận hành và khôi phục

Thực hiện trong phiên AWS Learner Lab còn hiệu lực. Chốt cấu hình trước mỗi thay đổi, giữ gói Lambda cũ riêng, cập nhật mã với RevisionId và đọc lại hash/cấu hình. Nếu cần khôi phục, kiểm tra phiên bản hiện tại trước khi dùng gói sao lưu để bảo toàn thay đổi đồng thời.

Đối với dữ liệu, luôn xuất vào mốc mới và đối chiếu bản trước; lỗi xuất giữ nguyên tệp đã lưu. Thử nghiệm Athena dùng bảng/prefix riêng, giữ bộ đầu vào cố định. Mọi thay đổi ngưỡng/lịch dùng đúng phạm vi lượt kiểm tra và được đọc lại sau thao tác. Khóa phiên chỉ lưu ở cơ chế quản lý bí mật đã có, tệp sao lưu riêng nằm ngoài repository công khai.

## 9. Nhật ký và cách tổng hợp báo cáo

Tổng giờ Tuần 1–3 đã xác nhận là **58,0 giờ**. Tuần 4 đã xác nhận thêm **20,0 giờ thực tế** (10,0 giờ mỗi sinh viên), tổng cộng **78,0 giờ**. Nhật ký ghi sản phẩm, liên kết commit/minh chứng và trạng thái từng phép kiểm chứng. Khi công việc được thực hiện, cập nhật trạng thái từng mã W4 và kết quả kiểm tra tương ứng.

Kết cấu báo cáo dự kiến: **mục tiêu → phiên bản/cấu hình → raw và chất lượng → vận hành và email → Athena/thống kê → dự báo → kiểm chứng → phân công và kết luận**. Mỗi hình có CSV nguồn; mỗi số đo có cửa sổ thời gian; mỗi kết quả triển khai có commit và hash đọc lại.

[Báo cáo nộp LMS](../BAO_CAO.md) · [Hồ sơ Tuần 3](../tuan_3/README.md) · [Kết quả kế hoạch Tuần 3](WEEK_3_PLAN.md) · [Chỉ mục mã nguồn và commit](components.md)
