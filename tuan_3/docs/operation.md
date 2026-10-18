# Vận hành và kiểm chứng Tuần 3

## 1. Kiểm tra kết quả đã lưu

Dùng Python 3.12 trở lên trong môi trường riêng và chạy tại gốc repository:

```bash
python -m pip install -r tuan_3/requirements.txt
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
python tuan_2/scripts/repository_audit.py --check
```

`verify_results.py` kiểm tra đường dẫn/hash/kích thước của 359 tệp trong 11 manifest, tính lại chất lượng raw, đối chiếu 18 kết quả truy vấn, sai số của các mốc dự báo, cấu hình Metric Filters, metric giữa hai API, kết quả thu thập với raw S3 và hồ sơ CD/dọn secrets. Mốc cập nhật 246/285 dòng bổ sung kiểm tra 96 dòng thống kê, 120 dòng tương quan, 24 bộ sai số/576 dòng đánh giá và 12 dòng đối chiếu với dữ liệu mô hình tải về sau, cùng tổng giờ Tuần 3 đã xác nhận. Bản dự báo đã phát hành có 144 giá trị cho 24 giờ đích, ba đô thị và hai chỉ số; tất cả giờ đích đều sau thời điểm phát hành. Mốc cũ có 12 giá trị cho hai giờ đích; mốc mới cutoff 11:00 UTC có 24 giá trị cho bốn giờ đích, vẫn chưa đủ cả 24 giờ. Các kiểm tra này không cần khóa AWS và không chứng minh dịch vụ hiện tại.

[Bản xuất raw mới 246/288 dòng](../results/raw_export_2026_10_18/README.md) bổ sung 96 tệp minh chứng: JSON gốc, CSV, inventory, chất lượng và thời điểm đọc. Verifier đối chiếu từng byte/hash, từng trường JSON–CSV và bảo toàn toàn bộ bản ghi của snapshot trước. Một hồi quy mới kiểm tra lưu byte nguyên vẹn, từ chối đường dẫn vượt thư mục và từ chối ghi đè tệp đã có.

## 2. Chạy một mốc mới trên AWS

Hai profile SDK hiện dùng là `default` cho sinh viên Tiến Sơn và `quyen` cho sinh viên Ngọc Quyên, vùng `us-east-1`. Cấp khóa phiên bằng cơ chế bảo mật của môi trường; không đặt khóa trong tham số, mã nguồn hay tệp được Git theo dõi. Các chương trình không sử dụng AWS CLI.

```bash
python tuan_3/scripts/snapshot.py --output output/week3-new-snapshot --archive-source
python tuan_3/scripts/benchmark.py --snapshot output/week3-new-snapshot --output output/week3-new-benchmark --run-id rnew
python tuan_3/scripts/dashboard.py --output output/week3-new-dashboard --backup output/week3-private-backups
python tuan_3/scripts/forecast.py --output output/week3-new-forecast
python tuan_3/scripts/metric_filters.py --output output/week3-new-filters --backup output/week3-private-filter-backups
python tuan_3/scripts/check_operations.py --output output/week3-new-checks --release-proof tuan_3/results/cd_2026_10_18
```

Thay `rnew` bằng mã lượt hợp lệ, chưa dùng; không ghi đè kết quả cũ. `snapshot.py --archive-source` chỉ đọc AWS và lưu nguyên byte từng JSON dưới `objects/raw/` cùng CSV, inventory/hash và thời điểm thu thập; `benchmark.py` tạo object/bảng riêng và chạy SELECT có phát sinh sử dụng dịch vụ; `dashboard.py` thay toàn bộ nội dung Dashboard riêng `WeatherAirQuality-Week3` sau khi sao lưu; `forecast.py` gọi API Open-Meteo. Đọc các điều kiện trong [kế hoạch](../../docs/WEEK_3_PLAN.md) trước khi thực hiện trên môi trường khác.

Thử nghiệm không thay raw hoặc bảng Glue sản xuất. Để thu hồi tài nguyên thử nghiệm, xác minh đúng bucket/prefix/tên bảng của lượt, rồi chỉ xóa các object dưới prefix thử nghiệm và ba bảng `w3_<run-id>_*` tương ứng. Không chạy thao tác xóa theo tên rút gọn chưa đối chiếu. Dashboard cũ được phục hồi từ bản sao riêng bằng PutDashboard; nếu trước đó không có Dashboard thì có thể xóa đúng Dashboard vừa tạo. Dữ liệu Athena dưới prefix kết quả truy vấn cần được xử lý riêng theo chính sách lưu giữ.

`snapshot.py` đối chiếu gói hiện hành với hồ sơ CD được công bố; dùng `--release-proof` để chọn mốc đã kiểm chứng khác, không trỏ ngầm tới bản sao riêng trên máy. Kết quả partial được đếm riêng. `check_operations.py` chỉ đọc AWS, giữ dữ liệu raw của các object được log khai báo và đối chiếu cả số dòng lẫn ngưỡng cảnh báo; không tạo lượt gọi Lambda hay thông báo mới.

`metric_filters.py` tạo hai bộ đếm dòng log trong mỗi môi trường sau khi AWS kiểm tra chính xác các mẫu; từ chối ghi đè filter cùng tên nhưng khác thiết lập. Có thể dùng `--observe-only --output output/week3-new-filter-observation` để chỉ đọc điểm metric. Không chèn log giả để chứng minh chạy thật. Filter mới không hồi tố log cũ và có thể phát sinh phí custom metrics. Nếu cần khôi phục, đối chiếu bản sao riêng: xóa đúng filter vừa tạo nếu trước đó chưa tồn tại, hoặc phục hồi đúng định nghĩa cũ; không xóa các filter khác trong log group.

## 3. Artifact và CD

```bash
python tuan_3/scripts/release.py --output output/lambda-build-new
```

Lệnh mặc định chỉ đóng gói, không gọi AWS. `manifest.json` ghi SHA-256 module và ZIP. ZIP chỉ chứa `lambda_function.py`, dùng metadata hệ thống cố định và không nén để tránh khác biệt giữa các phiên bản zlib trên Windows/Linux; không chứa khóa phiên, dữ liệu hay thư viện phân tích.

Workflow [Verify repository](../../.github/workflows/verify-repository.yml) tạo artifact sau các kiểm tra. Workflow [Week 3 Lambda release](../../.github/workflows/week3-release.yml) chạy thủ công trên `main` cho đúng một mục tiêu `tien-son` hoặc `ngoc-quyen`; ô `confirm` phải giống mục tiêu. Hai GitHub Environment tương ứng là `week3-tien-son` và `week3-ngoc-quyen`.

Mỗi Environment cần bốn secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_ACCOUNT_ID`. Chỉ người được phép mới cấp các giá trị cho đúng môi trường. Các khóa phiên tạm của lần kiểm chứng phải được xóa sau khi chạy; các lần tiếp theo cần khóa phiên còn hiệu lực. Workflow không tạo IAM role hoặc tăng quyền.

### Điều kiện bảo vệ triển khai

1. Kiểm tra nguồn và các hồi quy trước khi gọi AWS.
2. STS phải khớp tài khoản kỳ vọng, Lambda phải có runtime/handler/state phù hợp.
3. Tải ZIP hiện tại, kiểm tra hash rồi sao lưu riêng trước cập nhật.
4. Cập nhật mã bằng RevisionId cũ; không cập nhật biến môi trường, ngưỡng hay lịch.
5. Chờ cập nhật rồi so hash gói, trạng thái Active/Successful và dấu vân tay cấu hình.
6. Nếu kiểm chứng lỗi, chỉ khôi phục khi RevisionId vẫn là phiên bản thuộc lượt này. Nếu đã có người khác cập nhật, dừng để người vận hành đối chiếu.

Khôi phục có thể không thực hiện được ngay nếu Lambda vẫn đang cập nhật hoặc khóa phiên hết hạn; `release.json` ghi trạng thái thất bại thay vì báo thành công. Nếu lời gọi cập nhật không nhận được phản hồi xác nhận, chương trình ghi `NOT_ATTEMPTED_UPDATE_NOT_ACKNOWLEDGED`: chưa thể biết AWS đã nhận cập nhật hay chưa, nên không tự ghi đè mã. Nếu bước xác minh lỗi và không đọc được RevisionId hiện tại, chương trình ghi `BLOCKED_UNAVAILABLE_CURRENT_REVISION` và không thử khôi phục khi chưa xác định được quyền sở hữu phiên bản. Hai nhánh lỗi này dùng thông báo chuẩn hóa, không chép nội dung lỗi provider vào hồ sơ.

Gói khôi phục trong runner là tệp riêng tạm thời, không được upload vào artifact công khai. Người vận hành cần giữ thêm bản sao riêng lâu dài nếu yêu cầu khôi phục sau khi runner kết thúc.

Workflow không gọi trực tiếp Lambda để tạo thêm bản ghi hoặc email. Triển khai thành công chỉ chứng minh gói/cấu hình đúng tại thời điểm kiểm tra; kiểm chứng luồng theo lịch và xác nhận người nhận là bước riêng.

## 4. Kết quả thực hiện

- Bộ hồi quy hiện có 48 trường hợp, gồm năm trường hợp về hạng đồng hạng, thống kê, MA 3 giờ và loại giờ chưa hoàn tất khi đối chiếu mô hình tải về sau. Bảy kiểm tra tập trung vào đóng gói/cập nhật/khôi phục trước đó đã đạt; hai trường hợp lỗi triển khai đã tái hiện trước sửa. Đây là kiểm tra giả lập, chưa phải phép gây lỗi trên AWS thật. Đối chiếu 359 tệp manifest và các phép tính lại được thực hiện riêng; kết quả toàn bộ bộ thử được ghi theo lượt CI.
- Snapshot AWS, thử nghiệm Athena và Dashboard: đã có dữ liệu thật tại [mốc 18/10](../results/integration_2026_10_18/).
- [CI của bản tích hợp `0b26858`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101602570): thành công, gồm kiểm tra hồ sơ/chức năng/phân tích/Tuần 3 và tạo artifact.
- [CI của bản sửa ZIP `c28da19`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101839037): thành công. Artifact tải từ Linux khớp từng byte với gói dựng trên Windows, trước khi cấp lại secrets cho đợt kiểm chứng.
- [CI của bộ dữ liệu cập nhật `9480d14`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39116618730): thành công, gồm 39 kiểm tra Tuần 3, đối chiếu 219 tệp minh chứng và tạo artifact. Đây là kiểm tra snapshot đã lưu; không phải một lượt triển khai hoặc thu thập AWS mới.

### Đối chiếu độc lập các bảng số cập nhật

Đợt rà soát dùng cách tính riêng bằng thư viện chuẩn Python để đối chiếu 96 dòng thống kê (độ lệch chuẩn mẫu, phân vị tuyến tính), 120 dòng tương quan (hạng trung bình cho các giá trị bằng nhau), 24 bộ sai số/576 dòng giữ lại và 12 dòng so sánh với phản hồi mô hình tải về sau. Các giá trị khớp CSV. Kết quả 18 lượt Athena và trung vị cũng được đối chiếu với đúng bộ raw đầu vào ban đầu; raw cập nhật không thay đầu vào lịch sử đó.

Các bảng thống kê, tương quan, phân bố AQI, từng lượt Athena và sai số trong báo cáo được so lại với CSV nguồn; biểu đồ màu dùng cùng các tệp. Tổng 38,0 giờ Tuần 1–2 giữ nguyên, 20,0 giờ Tuần 3 ghi là tổng theo tuần đã xác nhận, không tự gán ngày hoặc phân bổ thời lượng theo nhiệm vụ. Việc rà soát không mở rộng 2 giờ đích đã đối chiếu thành kết luận cho cả 24 giờ.

| Môi trường | Lượt CD đã thành công | Đọc lại trực tiếp từ AWS |
| --- | --- | --- |
| Sinh viên Tiến Sơn | [39101930450](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450) | Gói khớp artifact CI, module khớp source, Active/Successful, cấu hình giữ nguyên |
| Sinh viên Ngọc Quyên | [39101934718](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) | Gói khớp artifact CI, module khớp source, Active/Successful, cấu hình giữ nguyên |

Hai lượt triển khai dùng commit `c28da19568a7bbe4b5be60d844574ad2853bf356`; SHA-256 gói cùng là `a8cfeb7d3f569a34573d1986299d82eefbc043bb749e3fe373403716604a1ea5`. Module thu thập giữ hash `d9d0ad2584feef121234d634bf26bdc43097bb9b8798123cfd767023397ed3cf`. [JSON từng môi trường và đối chiếu artifact](../results/cd_2026_10_18/) ghi thời điểm đọc lại.

Ở đợt đầu, hai job GitHub đã thành công nhưng phép kiểm tra bổ sung phát hiện metadata ZIP và dữ liệu nén khác giữa Windows/Linux. Module bên trong vẫn giống nhau. Đợt sau dùng metadata cố định và ZIP không nén, đã vượt qua đối chiếu byte toàn gói. [Hồ sơ lần đầu](../results/cd_2026_10_18/initial-attempt.json) được giữ để truy vết việc sửa.

Mỗi đợt cấp tạm bốn secrets cho mỗi môi trường. [Biên bản dọn đợt đầu](../results/cd_2026_10_18/initial-secret-cleanup.json) và [đợt kiểm chứng lại](../results/cd_2026_10_18/secret-cleanup.json) đều xác nhận đã xóa đủ tám secrets; danh sách secrets của cả hai Environment còn rỗng. Việc xóa khỏi GitHub không có nghĩa phiên AWS gốc đã bị thu hồi; lần triển khai sau cần cấp khóa phiên theo quyền được cho phép.

## 5. Giới hạn của metric vận hành

Đợt [cập nhật Dashboard](../results/monitoring_2026_10_18/) vẫn nhận tổng Errors lớn hơn Invocations: 69/1 trong môi trường sinh viên Tiến Sơn và 71/1 trong môi trường sinh viên Ngọc Quyên. Hai tổng này không tạo được tỷ lệ lỗi hợp lệ; JSON ghi `INCONSISTENT_COUNTS` và tỷ lệ `null`. Chưa kết luận nguyên nhân từ các bộ đếm này.

Biểu thức IF lồng của mốc cũ đã được thay bằng một IF phẳng sau khi phát hiện nhánh chọn điểm thiếu có thể phát sinh 0 theo quy tắc AWS. Bản cuối dùng `IF((inv>0) AND (FILL(err,-1)>=0) AND (err<=inv),100*err/inv)`, kèm đồ thị riêng cho điểm thiếu cặp. [Kết quả sửa, sáu phép thử chỉ đọc mỗi môi trường và readback](../results/monitoring_dashboard_repair_2026_10_18/README.md). Các số native lịch sử không bị sửa.

[Đối chiếu bổ sung](../results/operations_2026_10_18/) dùng hai API metric trên cùng cửa sổ: kết quả từng điểm khớp nhau, nên chưa có bằng chứng quy nguyên nhân cho phần xuất CSV. Mốc này bổ sung Metric Filters, sửa định dạng Secret cấu hình của sinh viên Ngọc Quyên và kiểm tra các lượt thu với raw S3. Các giá trị Secret không được đưa vào hồ sơ; phiên bản trước sửa được giữ để khôi phục.

## 6. Lượt theo lịch sau sửa cấu hình

[Hồ sơ 13:51 của sinh viên Ngọc Quyên](../results/post_repair_2026_10_18/README.md) có ba bản ghi khớp log/S3, đủ ba đô thị, không có đô thị lỗi; AQI/PM2.5 dưới ngưỡng nên không phát cảnh báo mới. Một điểm `ResultLogLines` đã được CloudWatch ghi nhận sau tạo filter/sửa cấu hình; không có sự kiện khớp thông báo đọc Secret thất bại trong cửa sổ log đã kiểm tra. Chương trình quan sát không gọi Lambda và không thay đổi lịch. Đây là minh chứng thu thập và metric mới, không phải bằng chứng nhận email mới hoặc vận hành liên tục.

## 7. Tái lập phân tích cập nhật từ tệp đã lưu

```bash
python tuan_3/scripts/reconcile_analysis.py --snapshot tuan_3/results/refresh_2026_10_18/snapshot --later-source tuan_3/results/refresh_2026_10_18/analysis/later_model --output output/week3-recompute-new
```

Chọn thư mục output mới nếu đã chạy trước đó. Lệnh dùng đúng snapshot và phản hồi mô hình đã lưu, không cần gọi AWS/API. Cờ `--collect-later-model` dùng để tải một mốc mô hình mới khi cần, lưu vào thư mục khác và chỉ đối chiếu giờ đã hoàn tất; không dùng thay số liệu trạm hoặc ghi đè bản dự báo đã phát hành. [Nguồn và kết quả cập nhật](../results/refresh_2026_10_18/README.md).

## 8. Đối chiếu hồ sơ trước khi nộp

Hồ sơ ghi nhận **các sản phẩm công việc tích hợp Tuần 3 đã hoàn thành tại mốc 18/10/2026**. Bảng sau nêu đúng bộ đầu vào và phạm vi kiểm chứng để người đọc đối chiếu giữa báo cáo, CSV và biểu đồ.

| Hạng mục | Kết quả đã lưu và đối chiếu | Minh chứng, phạm vi áp dụng |
| --- | --- | --- |
| Raw đầy đủ | Sinh viên Tiến Sơn 246 dòng; sinh viên Ngọc Quyên 288 dòng; tổng 534 bản ghi, 83 JSON gốc và 23 trường mỗi bản ghi | [CSV/JSON, inventory và thời điểm đọc](../results/raw_export_2026_10_18/README.md). Các trường trong CSV khớp JSON gốc; 531 bản ghi của snapshot trước được bảo toàn |
| Chất lượng raw | Bảy nhóm kiểm tra đã khai báo không phát hiện lỗi trong hai bộ xuất | [Chất lượng sinh viên Tiến Sơn](../results/raw_export_2026_10_18/snapshot/default/quality.csv) · [Sinh viên Ngọc Quyên](../results/raw_export_2026_10_18/snapshot/quyen/quality.csv). Kết quả kiểm tra cấu trúc/thời gian không xác nhận độ chính xác ngoài thực địa |
| Bảng và biểu đồ phân tích | 96 dòng thống kê, 120 dòng tương quan; PNG dùng cùng dữ liệu tính từ snapshot 246/285 dòng | [Nguồn và SHA-256 đầu vào](../results/refresh_2026_10_18/analysis/provenance.json). Bộ raw mới 246/288 được lưu riêng; số dòng của các bảng cũ không bị đổi theo snapshot mới |
| Athena | 18 lượt SELECT, ba cách lưu/khai báo, hai môi trường; kết quả tổng hợp khớp cùng raw 237/273 dòng | [Từng truy vấn, số đo và cấu hình](../results/integration_2026_10_18/benchmark/). Số byte và thời gian thuộc toàn truy vấn; Parquet được ghi bằng PyArrow/Snappy |
| Đánh giá và phát hành dự báo | 576 dòng đánh giá bổ sung của bốn phương pháp; bản phát hành có 144 giá trị cho 24 giờ đích | [Đánh giá giữ lại](../results/refresh_2026_10_18/analysis/ma_comparison_predictions.csv) · [Bản phát hành](../results/forecast_issued_2026_10_18/forecast_24h.csv). Đối chiếu mới với mô hình tải về sau có [24/144 giá trị cho 4/24 giờ đích](../results/forecast_followup_2026_10_18/README.md); dữ liệu CAMS không phải số đo trạm |
| Triển khai | Hai lượt CD thành công; hash gói đọc lại từ AWS khớp artifact và cấu hình được giữ nguyên | [Hồ sơ CD](../results/cd_2026_10_18/). Kết quả thuộc các lượt đã ghi thời điểm, không tự xác nhận trạng thái AWS ở một thời điểm khác |
| Thu thập và email | Các lượt theo lịch có log–S3 đối chiếu; email ngày 16/10 đã có xác nhận của hai người nhận | [Theo lịch và email](../../docs/scheduled-run-verification.md) · [Sau sửa cấu hình](../results/post_repair_2026_10_18/README.md). Lượt mới dưới ngưỡng có 0 cảnh báo, không được gọi là một phép kiểm chứng nhận email mới |
| Giám sát | Đã ghép theo timestamp và sửa IF phẳng; Dashboard hai môi trường đọc lại khớp, sáu phép thử metric math chỉ đọc mỗi môi trường đạt | [Native/log đối chiếu](../results/monitoring_followup_2026_10_18/README.md) · [Dashboard cuối](../results/monitoring_dashboard_repair_2026_10_18/README.md). Điểm Errors = 3 thiếu Invocations của sinh viên Tiến Sơn giữ nguyên; không tính tỷ lệ toàn cửa sổ từ điểm này |
| Giờ công | Tuần 1: 18,5 giờ; Tuần 2: 19,5 giờ; Tuần 3: 20,0 giờ; cộng 58,0 giờ | [Worklog và bảng từng sinh viên](WORKLOG.md#3-tổng-giờ-theo-tuần-đã-xác-nhận) · [CSV Tuần 3](../worklog.csv). Căn cứ: **Tổng theo tuần đã xác nhận** |
| Tính toàn vẹn hồ sơ | Verifier tính lại số liệu và đối chiếu 359 tệp trong 11 manifest; audit kiểm tra danh mục CSV và liên kết nội bộ | [Verifier](../scripts/verify_results.py) · [Audit repository](../../tuan_2/scripts/repository_audit.py). Các kiểm tra này chạy trên tệp đã lưu |

Ba mốc mã trực tiếp cho công việc Tuần 3: [tích hợp công cụ `0b26858`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/0b2685883c92eba1f31e27c735fdc48c94a8a12e), [gói triển khai `c28da19`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/c28da19568a7bbe4b5be60d844574ad2853bf356) và [raw nguyên bản/worklog `7ec1b32`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/commit/7ec1b3269388214111c96466a01a7fc9541e58b1). [CI của bản xuất raw](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39118199735) đã đạt 40 kiểm tra Tuần 3 và phép đối chiếu 315 tệp. Kết quả từng phiên bản tiếp theo được đọc tại [GitHub Actions](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions).


## 9. Đối chiếu bộ đếm và giờ dự báo bổ sung

- [Native metric/log: hai API, hai bộ dimension và chu kỳ 60/300 giây](../results/monitoring_followup_2026_10_18/README.md): cửa sổ 07:40–10:40 UTC. Sinh viên Tiến Sơn có hai khoảng đủ cặp, một điểm Errors = 3 thiếu Invocations; sinh viên Ngọc Quyên có ba khoảng đủ cặp, Errors = 0. Tỷ lệ trên các khoảng đủ cặp khác với tỷ lệ của toàn bộ bộ đếm trong cửa sổ.
- [Dashboard cuối sau sửa biểu thức](../results/monitoring_dashboard_repair_2026_10_18/README.md): giữ điểm thiếu cặp, dùng một IF và có backup/readback. Kết quả GetMetricData tái hiện lỗi của IF lồng và kiểm tra bản sửa trên sáu trường hợp mỗi môi trường. Đây là truy vấn tính toán chỉ đọc; không phải ghi dữ liệu mô phỏng vào metric/log.
- [Bản đối chiếu dự báo mới](../results/forecast_followup_2026_10_18/README.md): cutoff 11:00 UTC, 24 giá trị cho bốn giờ đích 07:00–10:00 UTC. Bản dự báo gốc và các snapshot trước được giữ nguyên. Sai số không được diễn giải thành kết quả cả 24 giờ hoặc số đo trạm.

```bash
python tuan_3/scripts/monitoring_followup.py --output output/monitoring-followup-new
python tuan_3/scripts/forecast_followup.py --output output/forecast-followup-new
```

Lệnh monitoring mặc định chỉ đọc AWS. Muốn cập nhật đúng Dashboard dự án, dùng thêm `--apply-dashboard --backup output/monitoring-private-backup-new`; chương trình kiểm tra dấu nhận diện Dashboard, sao lưu rồi đọc lại cấu hình. Không dùng lại thư mục output/backup đã tồn tại. Hai lệnh không gọi Lambda, không gửi email thử và không thay ngưỡng/lịch thu thập.

`verify_results.py` kiểm tra thêm manifest, CSV ghép từng khoảng, so sánh API/dimension/chu kỳ, lifecycle hash, kết quả metric math và các giá trị đối chiếu với payload CAMS đã lưu. Tám hồi quy mới bao phủ ghép sai thời gian, một khoảng không hợp lệ bị tổng lớn che khuất, missing khác zero, timezone, trùng điểm, loại thông tin riêng trong log và cutoff dự báo. Sáu phép thử biểu thức trên dịch vụ là lớp kiểm chứng riêng với kiểm thử Python.

Tài liệu kỹ thuật: [AWS — định nghĩa Invocations/Errors](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics-types.html), [AWS — metric math và IF](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/using-metric-math.html), [GetMetricStatistics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_GetMetricStatistics.html) và [GetMetricData](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_GetMetricData.html).

[Báo cáo](FINAL_REPORT.md) · [Trang Tuần 3](../README.md)
