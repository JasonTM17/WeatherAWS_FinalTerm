# Vận hành và kiểm chứng Tuần 3

## 1. Kiểm tra kết quả đã lưu

Dùng Python 3.12 trở lên trong môi trường riêng và chạy tại gốc repository:

```bash
python -m pip install -r tuan_3/requirements.txt
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
python tuan_2/scripts/repository_audit.py --check
```

`verify_results.py` kiểm tra đường dẫn/hash/kích thước của 193 tệp trong sáu manifest, tính lại chất lượng raw, đối chiếu 18 kết quả truy vấn, sai số của hai mốc dự báo, cấu hình Metric Filters, metric giữa hai API, kết quả thu thập với raw S3 và hồ sơ CD/dọn secrets. Mốc sau sửa cấu hình được kiểm tra riêng về thời gian, lịch, raw ba đô thị, điều kiện cảnh báo và metric log mới. Phần dự báo mới kiểm tra đủ 144 giờ đích đều sau thời điểm phát hành và khớp phép tính lại. Các kiểm tra này không cần khóa AWS. Đây là kiểm tra tệp đã lưu, không phải kiểm tra dịch vụ hiện tại.

## 2. Chạy một mốc mới trên AWS

Hai profile SDK hiện dùng là `default` cho sinh viên Tiến Sơn và `quyen` cho sinh viên Ngọc Quyên, vùng `us-east-1`. Cấp khóa phiên bằng cơ chế bảo mật của môi trường; không đặt khóa trong tham số, mã nguồn hay tệp được Git theo dõi. Các chương trình không sử dụng AWS CLI.

```bash
python tuan_3/scripts/snapshot.py --output output/week3-new-snapshot
python tuan_3/scripts/benchmark.py --snapshot output/week3-new-snapshot --output output/week3-new-benchmark --run-id rnew
python tuan_3/scripts/dashboard.py --output output/week3-new-dashboard --backup output/week3-private-backups
python tuan_3/scripts/forecast.py --output output/week3-new-forecast
python tuan_3/scripts/metric_filters.py --output output/week3-new-filters --backup output/week3-private-filter-backups
python tuan_3/scripts/check_operations.py --output output/week3-new-checks --release-proof tuan_3/results/cd_2026_10_18
```

Thay `rnew` bằng mã lượt hợp lệ, chưa dùng; không ghi đè kết quả cũ. `snapshot.py` đọc AWS; `benchmark.py` tạo object/bảng riêng và chạy SELECT có phát sinh sử dụng dịch vụ; `dashboard.py` thay toàn bộ nội dung Dashboard riêng `WeatherAirQuality-Week3` sau khi sao lưu; `forecast.py` gọi API Open-Meteo. Đọc các điều kiện trong [kế hoạch](../../docs/WEEK_3_PLAN.md) trước khi thực hiện trên môi trường khác.

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

Khôi phục có thể không thực hiện được ngay nếu Lambda vẫn đang cập nhật hoặc khóa phiên hết hạn; `release.json` phải ghi trạng thái thất bại thay vì báo thành công. Gói khôi phục trong runner là tệp riêng tạm thời, không được upload vào artifact công khai. Người vận hành cần giữ thêm bản sao riêng lâu dài nếu yêu cầu khôi phục sau khi runner kết thúc.

Workflow không gọi trực tiếp Lambda để tạo thêm bản ghi hoặc email. Triển khai thành công chỉ chứng minh gói/cấu hình đúng tại thời điểm kiểm tra; kiểm chứng luồng theo lịch và xác nhận người nhận là bước riêng.

## 4. Kết quả thực hiện

- Kiểm tra hồi quy gồm 32 trường hợp sau phần bổ sung thời điểm phát hành; đối chiếu 193 tệp manifest và các phép tính lại đã đạt. Kết quả toàn bộ bộ thử được ghi riêng theo lượt CI.
- Snapshot AWS, thử nghiệm Athena và Dashboard: đã có dữ liệu thật tại [mốc 18/10](../results/integration_2026_10_18/).
- [CI của bản tích hợp `0b26858`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101602570): thành công, gồm kiểm tra hồ sơ/chức năng/phân tích/Tuần 3 và tạo artifact.
- [CI của bản sửa ZIP `c28da19`](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101839037): thành công. Artifact tải từ Linux khớp từng byte với gói dựng trên Windows, trước khi cấp lại secrets cho đợt kiểm chứng.

| Môi trường | Lượt CD đã thành công | Đọc lại trực tiếp từ AWS |
| --- | --- | --- |
| Sinh viên Tiến Sơn | [39101930450](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101930450) | Gói khớp artifact CI, module khớp source, Active/Successful, cấu hình giữ nguyên |
| Sinh viên Ngọc Quyên | [39101934718](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions/runs/39101934718) | Gói khớp artifact CI, module khớp source, Active/Successful, cấu hình giữ nguyên |

Hai lượt triển khai dùng commit `c28da19568a7bbe4b5be60d844574ad2853bf356`; SHA-256 gói cùng là `a8cfeb7d3f569a34573d1986299d82eefbc043bb749e3fe373403716604a1ea5`. Module thu thập giữ hash `d9d0ad2584feef121234d634bf26bdc43097bb9b8798123cfd767023397ed3cf`. [JSON từng môi trường và đối chiếu artifact](../results/cd_2026_10_18/) ghi thời điểm đọc lại.

Ở đợt đầu, hai job GitHub đã thành công nhưng phép kiểm tra bổ sung phát hiện metadata ZIP và dữ liệu nén khác giữa Windows/Linux. Module bên trong vẫn giống nhau. Đợt sau dùng metadata cố định và ZIP không nén, đã vượt qua đối chiếu byte toàn gói. [Hồ sơ lần đầu](../results/cd_2026_10_18/initial-attempt.json) được giữ để truy vết việc sửa.

Mỗi đợt cấp tạm bốn secrets cho mỗi môi trường. [Biên bản dọn đợt đầu](../results/cd_2026_10_18/initial-secret-cleanup.json) và [đợt kiểm chứng lại](../results/cd_2026_10_18/secret-cleanup.json) đều xác nhận đã xóa đủ tám secrets; danh sách secrets của cả hai Environment còn rỗng. Việc xóa khỏi GitHub không có nghĩa phiên AWS gốc đã bị thu hồi; lần triển khai sau cần cấp khóa phiên theo quyền được cho phép.

## 5. Giới hạn của metric vận hành

Đợt [cập nhật Dashboard](../results/monitoring_2026_10_18/) vẫn nhận tổng Errors lớn hơn Invocations: 69/1 trong môi trường sinh viên Tiến Sơn và 71/1 trong môi trường sinh viên Ngọc Quyên. Hai tổng này không tạo được tỷ lệ lỗi hợp lệ; JSON ghi `INCONSISTENT_COUNTS` và tỷ lệ `null`. Chưa kết luận nguyên nhân từ các bộ đếm này.

Dashboard dùng `IF(inv>0,IF(FILL(err,-1)>=0,IF(err<=inv,100*err/inv)))` cho từng chu kỳ: bỏ điểm thiếu Errors, không có lượt gọi hoặc Errors vượt Invocations. CSV chỉ giữ điểm dịch vụ trả về. Một vài điểm hợp lệ trên biểu đồ không chứng minh toàn cửa sổ có metric đầy đủ. Triển khai mã thành công cũng chưa chứng minh lịch chạy liên tục hay email mới đã tới người nhận.

[Đối chiếu bổ sung](../results/operations_2026_10_18/) dùng hai API metric trên cùng cửa sổ: kết quả từng điểm khớp nhau, nên chưa có bằng chứng quy nguyên nhân cho phần xuất CSV. Mốc này bổ sung Metric Filters, sửa định dạng Secret cấu hình của sinh viên Ngọc Quyên và kiểm tra các lượt thu với raw S3. Các giá trị Secret không được đưa vào hồ sơ; phiên bản trước sửa được giữ để khôi phục.

## 6. Lượt theo lịch sau sửa cấu hình

[Hồ sơ 13:51 của sinh viên Ngọc Quyên](../results/post_repair_2026_10_18/README.md) có ba bản ghi khớp log/S3, đủ ba đô thị, không có đô thị lỗi; AQI/PM2.5 dưới ngưỡng nên không phát cảnh báo mới. Một điểm `ResultLogLines` đã được CloudWatch ghi nhận sau tạo filter/sửa cấu hình; không có sự kiện khớp thông báo đọc Secret thất bại trong cửa sổ log đã kiểm tra. Chương trình quan sát không gọi Lambda và không thay đổi lịch. Đây là minh chứng thu thập và metric mới, không phải bằng chứng nhận email mới hoặc vận hành liên tục.

[Báo cáo](FINAL_REPORT.md) · [Trang Tuần 3](../README.md)
