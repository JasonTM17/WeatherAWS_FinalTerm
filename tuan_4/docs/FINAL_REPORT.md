# Báo cáo Tuần 4 — Kiểm chứng và hoàn thiện hệ thống AWS

**Nguyễn Tiến Sơn — MSSV 24110054; Trần Thị Ngọc Quyên — MSSV 24110051.**
**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.
**Ngày cập nhật:** 20/10/2026. Số liệu giữ riêng theo từng đợt kiểm chứng.

## 1. Mục tiêu và kết quả tổng hợp

Tuần 4 hoàn thiện luồng thu thập, lưu trữ, truy vấn và cảnh báo của ba đô thị; kiểm chứng hạ tầng dưới dạng mã, giám sát, quản lý phiên và các phép đánh giá phân tích. Hai môi trường AWS Learner Lab sử dụng cùng source collector, với tài nguyên và mã bản ghi độc lập.

| Hạng mục | Kết quả có minh chứng |
| --- | --- |
| Kiểm chứng hệ thống hiện hữu ngày 19/10 | Mỗi môi trường có ba bản ghi, log/request/S3/Athena tương ứng, một Invocation và 0 Errors trong chu kỳ kiểm chứng; mỗi lượt có một SNS Publish và email đã được người nhận xác nhận |
| Triển khai CloudFormation ngày 20/10 | Hai stack riêng đạt CREATE_COMPLETE, gói nguồn đúng hash; Lambda mới thu đủ ba đô thị, SELECT chạy trong database/workgroup mới |
| Bảo vệ lưu trữ của stack mới | Bốn BPA bật, AES256, versioning Enabled, BucketOwnerEnforced, policy HTTPS-only; không public ACL/policy |
| SNS trên topic mới | Hai subscription đã xác nhận; mỗi topic chấp nhận một thư thử kênh và cả hai người nhận xác nhận đã nhận |
| Quản lý phiên thực tế | Lịch chuẩn trên cả hai môi trường qua ENABLED → DISABLED → ENABLED, target và môi trường không đổi |
| Dữ liệu chốt ngày 20/10 | 331/369 bản ghi và 53/62 JSON gốc của sinh viên Tiến Sơn/sinh viên Ngọc Quyên |
| Athena Tuần 4 | 18 truy vấn mới: ba phương án × ba lần × hai môi trường; cùng đầu vào, tắt dùng lại kết quả, kết quả tổng hợp tương đương |
| Backtest lịch sử | Ba cửa sổ 24 giờ, 432 dự đoán và 18 dòng MAE/RMSE/Bias; mỗi cửa sổ chỉ dùng 24 giờ trước gốc |
| Giờ công | Tuần 4: 10 giờ mỗi sinh viên; tổng theo tuần đã xác nhận toàn đồ án: 78 giờ |

Minh chứng mới tập trung tại [bộ kiểm chứng AWS ngày 20/10](../results/advanced_live_2026_10_20/README.md) và [bộ backtest](../results/backtest_2026_10_20/README.md). Các bộ dữ liệu Tuần 1–3 và ngày 19/10 được giữ theo mốc ban đầu.

## 2. Kiến trúc và lựa chọn kỹ thuật

![Kiến trúc hệ thống](../../docs/architecture.png)

EventBridge kích hoạt Lambda mỗi giờ. Lambda đọc tọa độ và ngưỡng trong Secrets Manager, lấy dữ liệu Weather/Air Quality từ Open-Meteo, chuẩn hóa và ghi NDJSON lên S3. Khi US AQI ≥ 100 hoặc PM2.5 ≥ 35,5 µg/m³, collector gửi thông điệp qua SNS. Glue lưu lược đồ, Athena đọc dữ liệu theo phân vùng ngày; CloudWatch giữ log, metric và dashboard.

- **Lambda và thư viện chuẩn:** phù hợp công việc ngắn theo lịch; cùng module được đóng gói xác định để đối chiếu Git với mã triển khai.
- **S3 NDJSON:** giữ từng bản ghi có record_id, thời điểm dữ liệu và thời điểm thu thập. Một lượt có thể lưu ba đô thị trong một object; số object và số bản ghi được thống kê riêng.
- **Partition Projection:** ánh xạ year/month/day sang tiền tố S3; điều kiện phân vùng thu hẹp vị trí đọc, không tự bảo đảm giảm thời gian hoặc chi phí thanh toán.
- **Parquet Snappy:** định dạng cột phục vụ truy vấn chọn trường; lợi ích được đo bằng cùng dữ liệu và phép tổng hợp.
- **SNS email:** tách kiểm tra ngưỡng, Publish được chấp nhận và xác nhận người nhận. Đăng ký email của topic mới cần xác nhận riêng.
- **CloudWatch:** ghép theo đúng function, request, khoảng thời gian và chu kỳ. Tỷ lệ lỗi chỉ tính từ cặp Errors/Invocations hợp lệ.

Mã chính: [collector](../../tuan_2/lambda/lambda_function.py), [benchmark](../../tuan_3/scripts/benchmark.py), [backtest](../scripts/backtest_three_windows.py), [triển khai stack](../scripts/deploy_stack.py), [kiểm chứng stack](../scripts/verify_stack.py), [quản lý phiên](../scripts/session_control.py).

## 3. Triển khai thực tế một template CloudFormation

[weather-stack.json](../infrastructure/weather-stack.json) khai báo **17 tài nguyên ứng dụng**, gồm bucket và policy, Secret, SNS và subscription, Lambda/log, EventBridge/permission, Glue/database/table, workgroup, hai metric filter, alarm/topic policy và dashboard. Giữ LabRole do học phần cấp; template không tạo hoặc thay IAM role.

### 3.1. Phiên bản và khả năng truy vết

| Đối tượng | SHA-256 |
| --- | --- |
| Source collector | `ade29ff52bfd14accb7c470f82b923704daade8a740ed16584bf523dc04cc219` |
| ZIP triển khai | `f4ae025b35f04403de43ff5427d8dbd992f4cb7b562b3f3fe13418c0c225179c` |
| Template | `ae0ce4073330492137e3d8354543ef0bf71001a81897df2461d872b81bef781e` |

Artifact nằm trong bucket riêng tư có versioning, key theo hash và Version ID cụ thể. Công cụ tải lại đúng version để so byte trước CreateStack, sau đó tải gói Lambda để kiểm tra hash và nội dung module. Trước tạo stack, chín tên tài nguyên được kiểm tra nhằm tránh sử dụng nhầm tài nguyên hiện hữu.

### 3.2. Kết quả hai môi trường

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Stack | weather-w4-son | weather-w4-quyen |
| CloudFormation | CREATE_COMPLETE | CREATE_COMPLETE |
| Function | weather-w4-son-collector | weather-w4-quyen-collector |
| Database | weather_w4_son | weather_w4_quyen |
| Workgroup | weather-w4-son | weather-w4-quyen |
| Lịch của stack mới | DISABLED | DISABLED |
| Source và artifact đối chiếu | Khớp | Khớp |

Hồ sơ [Events và Outputs đã chọn trường của sinh viên Tiến Sơn](../results/advanced_live_2026_10_20/stacks/default/) và [sinh viên Ngọc Quyên](../results/advanced_live_2026_10_20/stacks/quyen/) chứng minh bước tạo và chạy stack, bổ sung sau [kiểm tra template ngày 19/10](../results/template_validation_2026_10_19/README.md). Lịch mới vẫn tắt để tránh hai bộ collector chạy tự động song song. Quy trình tái lập có trong [INFRASTRUCTURE.md](INFRASTRUCTURE.md).

## 4. Raw, Lambda, S3 và Athena

### 4.1. Lượt thực thi trên stack mới ngày 20/10

| Chỉ số | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | ---: | ---: |
| Bản ghi mới / đô thị | 3 / 3 | 3 / 3 |
| SELECT theo record_id | 3 dòng khớp | 3 dòng khớp |
| Byte Athena quét | 1.689 | 1.689 |
| Engine / tổng thời gian (ms) | 489 / 646 | 682 / 1.005 |
| Kết quả truy vấn dùng lại | Không | Không |
| SNS kỳ vọng / thực tế | 0 / 0 | 0 / 0 |

CSV raw giữ đủ **23 trường theo lược đồ dự án**. SELECT kiểm tra bốn trường record_id, city, us_aqi và pm2_5; truy vấn bắt buộc dùng database/workgroup của stack mới. Object S3 được tải và lưu nguyên byte, sau đó so với CSV. Giá trị dưới ngưỡng trong lượt này giải thích số cảnh báo bằng 0.

- [Raw sinh viên Tiến Sơn](../results/advanced_live_2026_10_20/stacks/default/raw_invocation.csv) · [SQL](../results/advanced_live_2026_10_20/stacks/default/exact_records.sql) · [Athena](../results/advanced_live_2026_10_20/stacks/default/athena_exact.csv).
- [Raw sinh viên Ngọc Quyên](../results/advanced_live_2026_10_20/stacks/quyen/raw_invocation.csv) · [SQL](../results/advanced_live_2026_10_20/stacks/quyen/exact_records.sql) · [Athena](../results/advanced_live_2026_10_20/stacks/quyen/athena_exact.csv).

### 4.2. Snapshot tích lũy dùng cho phân tích

[Bộ raw ngày 20/10](../results/advanced_live_2026_10_20/snapshot/) chứa **700 bản ghi và 115 JSON gốc**: sinh viên Tiến Sơn 331/53, sinh viên Ngọc Quyên 369/62. Mỗi object có số bản ghi, dung lượng và SHA-256. CSV giữ các lượt thu thập lặp; bảng đô thị–giờ được xuất riêng để phân tích đúng đơn vị mẫu.

Dữ liệu thời tiết/AQI đến từ mô hình Open-Meteo/CAMS. Hai môi trường có thể trả giá trị bằng nhau khi cùng tọa độ và thời điểm nguồn; record_id và thời điểm thực thi vẫn độc lập. Tổng raw tích lũy không đồng nghĩa số giờ quan trắc độc lập hoặc độ phủ đầy đủ của cả tuần.

## 5. Log, metric và email

Hai stack mới đều có START/END/REPORT và dòng Result khớp đúng request cùng object S3. Trong chu kỳ 300 giây chứa lượt kiểm chứng, mỗi function có **1 Invocation, 0 Errors**. Đây là kết quả của hai lượt đã chỉ định.

Sau khi người nhận xác nhận subscription, AWS đọc lại cả hai đăng ký ở trạng thái confirmed. Mỗi topic nhận một lệnh Publish thư kiểm chứng kênh email; cả hai sinh viên xác nhận đã nhận đúng thư mới. Thư thử ghi rõ không phải cảnh báo vượt ngưỡng và được lưu riêng với lượt thu thập không có cảnh báo.

- [Runtime và metric sinh viên Tiến Sơn](../results/advanced_live_2026_10_20/stacks/default/runtime_controls.json).
- [Runtime và metric sinh viên Ngọc Quyên](../results/advanced_live_2026_10_20/stacks/quyen/runtime_controls.json).
- [Publish và xác nhận email topic mới](../results/advanced_live_2026_10_20/email/).

Phép kiểm chứng cảnh báo bằng **dữ liệu vượt ngưỡng** ngày 19/10 được giữ nguyên: Hà Nội AQI 101, mỗi môi trường có một Publish và người nhận xác nhận email. [Hồ sơ vận hành](LOG_METRIC_S3_RECONCILIATION.md) tách rõ các lượt này theo ngày và ứng dụng.

## 6. Thực nghiệm Athena Tuần 4

Cùng snapshot của từng sinh viên được chuyển thành JSON và Parquet, nhóm theo ngày với một file mỗi ngày/định dạng. So sánh JSON đăng ký phân vùng, JSON Projection và Parquet Projection. Mỗi cấu hình đo ba lần, luân phiên thứ tự chạy, tắt result reuse; tổng **18 truy vấn** có query ID và Statistics.

| Sinh viên | Phương án | Median byte | Engine (ms) | Tổng (ms) |
| --- | --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | JSON đăng ký phân vùng | 1.558 | 729 | 944 |
| Sinh viên Tiến Sơn | JSON Projection | 1.558 | 485 | 647 |
| Sinh viên Tiến Sơn | Parquet Projection | 302 | 505 | 682 |
| Sinh viên Ngọc Quyên | JSON đăng ký phân vùng | 1.558 | 685 | 910 |
| Sinh viên Ngọc Quyên | JSON Projection | 1.558 | 481 | 640 |
| Sinh viên Ngọc Quyên | Parquet Projection | 302 | 452 | 647 |

Kết quả COUNT/AVG theo đô thị tương đương ở cả ba phương án. Ngày lọc 20/10 có ba bản ghi trong mỗi snapshot. Parquet giảm **80,62% byte quét**, trong khi JSON Projection có tổng thời gian trung vị thấp hơn Parquet ở cả hai môi trường. Từ đó, lựa chọn lưu trữ cần cân nhắc cả lượng quét và độ trễ; tỷ lệ byte của bộ đo nhỏ này không phải tỷ lệ giảm hóa đơn.

[Tất cả lượt đo và SQL](../results/advanced_live_2026_10_20/benchmark/) · [Snapshot và danh mục object](../results/advanced_live_2026_10_20/snapshot/). Kết quả Tuần 3 vẫn giữ tại [benchmark ngày 18/10](../../tuan_3/results/integration_2026_10_18/benchmark/).

## 7. Backtest ba cửa sổ lịch sử

Phương án thống nhất ngày 20/10 là backtest lịch sử. Mô hình **MA24 đệ quy** được cố định trước đánh giá; mỗi cửa sổ nhận 24 giờ liền trước gốc và dự đoán 24 bước. Ba cửa sổ đích liên tiếp không chồng lấn, ba đô thị và hai biến tạo **432 dự đoán, 18 dòng sai số**. Bộ lịch sử có 519 dòng đô thị–giờ, kèm ba phản hồi mô hình đã lưu.

![MAE ba cửa sổ lịch sử](../results/backtest_2026_10_20/backtest_mae.png)

MAE AQI tại TP. Hồ Chí Minh khoảng 26,03; 9,39; 6,99 điểm qua ba cửa sổ. MAE PM2.5 tương ứng khoảng 7,00; 4,49; 8,44 µg/m³. Sai số của hai biến biến động khác nhau; bảng giữ riêng cửa sổ và đô thị. RMSE phản ánh ảnh hưởng của sai số lớn; Bias giữ dấu, với quy ước dự đoán trừ giá trị mô hình đối chiếu.

Đây là đánh giá hồi cứu trên chuỗi mô hình được tải cùng đợt. Không coi ba cửa sổ là ba bản phát hành trong quá khứ hoặc số đo trạm. Kỳ dự báo phát hành ngày 18/10, đối chiếu đủ 144 giá trị ngày 19/10, tiếp tục nằm riêng trong [hồ sơ Tuần 3](../../tuan_3/results/forecast_followup_2026_10_19/README.md).

[Phương pháp, hình đường và dữ liệu](../results/backtest_2026_10_20/README.md) · [432 dự đoán](../results/backtest_2026_10_20/predictions.csv) · [18 dòng MAE/RMSE/Bias](../results/backtest_2026_10_20/metrics.csv).

## 8. Bảo mật, chi phí và quản lý tài nguyên

Đọc lại hai bucket stack mới xác nhận BPA 4/4, AES256, versioning Enabled, BucketOwnerEnforced, không public ACL/policy và policy từ chối truyền không qua HTTPS. Permission gọi Lambda ràng buộc ARN rule và SourceAccount. LabRole được giữ nguyên; policy runtime theo tài nguyên là mẫu tham khảo, không được xem là chứng nhận effective permissions của role học phần. [Báo cáo bảo mật](SECURITY_AUDIT.md) nêu từng phép kiểm tra và nguồn.

Cost Explorer kỳ **12–19/10** có 117 nhóm ngày/dịch vụ/loại ghi nhận; Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated. Phép cộng dùng Decimal; bản hiển thị làm tròn đến cent:

| Sinh viên | Nhóm ngày/dịch vụ/loại ghi nhận | Tổng UnblendedCost gốc (USD) | Hiển thị đến cent (USD) |
| :--- | :---: | :---: | :---: |
| Sinh viên Tiến Sơn | 70 | -0,000000339 | 0,00 |
| Sinh viên Ngọc Quyên | 47 | 0,1364702401 | 0,14 |

Nguồn: [cost_summary.json](../results/cost/cost_summary.json), [117 dòng chi tiết](../results/cost/learner_lab_cost_breakdown.csv), [snapshot môi trường](../results/verification_2026_10_19/environment/). Kỳ chính xác trong cost_summary.json/cost.json là căn cứ của bảng; số liệu Estimated có thể được AWS cập nhật sau. Đây là chi phí tài khoản của kỳ đã chọn; không dùng để ước tính chi phí các stack mới tạo ngày 20/10, và không suy diễn toàn bộ dịch vụ thuộc Free Tier. [Báo cáo chi phí](COST_REPORT.md) giữ cách tổng hợp và đối soát chi tiết.

Ngày 20/10, mỗi lịch chuẩn đã được tạm dừng rồi khôi phục thực tế: **ENABLED → DISABLED → ENABLED**. Fingerprint account/function/rule/target không đổi; không xóa raw. Nhật ký phục hồi được ghi bền vững trước thay đổi và giữ riêng. Hai lịch mới vẫn DISABLED. [Minh chứng quản lý phiên](../results/advanced_live_2026_10_20/session/) · [Checklist cuối Lab](SESSION_CHECKLIST.md).

## 9. Kiểm tra và tái lập

```powershell
python -m unittest discover -s tuan_4/tests -v
python tuan_4/scripts/verify_results.py
python tuan_4/scripts/cost_analysis.py --check
python tuan_4/scripts/reconcile_ops.py --check
python tuan_4/scripts/security_report.py --check
cfn-lint tuan_4/infrastructure/weather-stack.json --regions us-east-1
python tuan_2/scripts/repository_audit.py --check
```

Bộ kiểm tra bao phủ ranh giới môi trường, tên tài nguyên đã tồn tại, artifact bất biến, database/workgroup của stack mới, phục hồi lịch, dữ liệu thiếu/trùng và bất biến dự đoán khi thay đổi holdout. Bộ xác minh offline kiểm tra manifest và phát lại quan hệ raw–CSV–SELECT, cùng 432 dự đoán và 18 dòng sai số. Kiểm tra offline dùng bằng chứng đã lưu; CI kiểm tra đúng phiên bản Git tại [GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/workflows/verify-repository.yml).

## 10. Phân công và kết luận

Sinh viên Tiến Sơn phụ trách Lambda, S3, Secrets Manager, SNS, EventBridge, CloudWatch và hạ tầng. Sinh viên Ngọc Quyên phụ trách Glue/Athena, xuất dữ liệu, phân tích, dự báo và chi phí. Hai sinh viên cùng tích hợp và đối chiếu hồ sơ. **Tổng theo tuần đã xác nhận:** Tuần 4 là 20 giờ, toàn đồ án 78 giờ (sinh viên Tiến Sơn 39,5 giờ; sinh viên Ngọc Quyên 38,5 giờ). [Worklog](WORKLOG.md) · [CSV](../worklog.csv).

Kết quả Tuần 4 nối được source triển khai với tài nguyên CloudFormation, request thực thi, log/metric, dữ liệu S3, kết quả Athena và xác nhận email. Phần phân tích bổ sung phép đo Athena mới và đánh giá lịch sử có tách dữ liệu huấn luyện/đích. Các bộ dữ liệu, hash và phương pháp được giữ cùng mốc để có thể kiểm tra lại. Video trình bày dưới 10 phút được bổ sung bằng liên kết sau khi sinh viên quay và kiểm tra quyền xem.

[Báo cáo tổng kết đồ án](../../docs/FINAL_PROJECT_REPORT.md) · [Nội dung nộp có URL đầy đủ](SUBMISSION.md) · [Danh mục minh chứng](../../docs/EVIDENCE_INDEX.md).
