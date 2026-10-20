# Kiểm chứng nâng cao thực tế ngày 20/10/2026

Đợt này bổ sung triển khai CloudFormation, vận hành và thực nghiệm Athena bằng các phiên AWS của **sinh viên Tiến Sơn** và **sinh viên Ngọc Quyên**. Dữ liệu ngày 19/10 được giữ nguyên ở thư mục cũ.

## 1. Hai stack ứng dụng mới

| Nội dung | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Stack | `weather-w4-son` | `weather-w4-quyen` |
| CloudFormation | `CREATE_COMPLETE` | `CREATE_COMPLETE` |
| Lambda | `weather-w4-son-collector` | `weather-w4-quyen-collector` |
| Database / Workgroup | `weather_w4_son` / `weather-w4-son` | `weather_w4_quyen` / `weather-w4-quyen` |
| Bản ghi mới / đô thị | 3 / 3 | 3 / 3 |
| Athena quét / engine / tổng | 1.689 byte / 489 ms / 646 ms | 1.689 byte / 682 ms / 1.005 ms |
| Invocations / Errors, chu kỳ 300 giây | 1 / 0 | 1 / 0 |
| SNS Publish kỳ vọng / thực tế | 0 / 0 | 0 / 0 |
| Lịch mới sau kiểm chứng | `DISABLED` | `DISABLED` |

Nguồn: [stack sinh viên Tiến Sơn](stacks/default/) và [stack sinh viên Ngọc Quyên](stacks/quyen/). Mỗi thư mục chứa Events đã chọn trường, hash triển khai, cấu hình đọc lại, NDJSON tải nguyên byte từ S3, CSV đủ 23 trường, SQL và kết quả truy vấn.

SELECT đối chiếu chính xác `record_id`, `city`, `us_aqi`, `pm2_5` trong database/workgroup **của stack mới**, không dùng lại kết quả truy vấn. CSV raw giữ đủ 23 trường; SELECT này kiểm tra bốn cột đã chọn. Runtime có đầy đủ START/END/REPORT và Result của đúng request; hai native metric cùng hàm, cùng chu kỳ.

Các giá trị của lượt này đều dưới ngưỡng `AQI >= 100 OR PM2.5 >= 35.5`; không có Publish là kết quả đúng. Sau lượt thu thập, AWS đọc lại subscription của hai topic mới đều đã xác nhận. Mỗi topic tiếp nhận một thư thử kênh email, và cả hai sinh viên xác nhận đã nhận đúng thư mới: [kết quả Publish](email/) · [xác nhận người nhận](email/recipient_confirmation.json). Thư thử ghi rõ mục đích kiểm chứng, không được tính thành cảnh báo vượt ngưỡng của lượt thu thập. Trạng thái chờ trong snapshot ban đầu được giữ theo thời điểm chụp. Xác nhận cảnh báo dữ liệu ngày 19/10 thuộc topic hiện hữu và nằm riêng trong [hồ sơ ngày 19/10](../verification_2026_10_19/recipient_confirmation.json).

### Tính toàn vẹn và bảo mật

- Cùng source collector chính; source SHA-256: `ade29ff52bfd14accb7c470f82b923704daade8a740ed16584bf523dc04cc219`.
- ZIP SHA-256: `f4ae025b35f04403de43ff5427d8dbd992f4cb7b562b3f3fe13418c0c225179c`.
- Artifact lấy theo Version ID cụ thể, tải lại kiểm tra byte/hash trước CreateStack.
- Trước tạo stack, kiểm tra chín tên tài nguyên xác định trước để tránh dùng nhầm tài nguyên đang có.
- Đọc lại bucket mới: bốn BPA bật, AES256, không public ACL/policy, versioning Enabled, BucketOwnerEnforced và policy từ chối truyền không qua HTTPS.
- Quyền gọi Lambda ràng buộc SourceArn của rule và SourceAccount. Giữ LabRole học phần; không thay IAM.
- Tham số email, Outputs riêng và nhật ký khôi phục không nằm trong bộ công khai.

## 2. Snapshot raw và phép thử Athena mới

| Đầu vào | Sinh viên Tiến Sơn | Sinh viên Ngọc Quyên |
| --- | --- | --- |
| Raw tích lũy | 331 bản ghi | 369 bản ghi |
| JSON gốc trên S3 | 53 tệp | 62 tệp |
| Ngày lọc của truy vấn | 20/10/2026 | 20/10/2026 |
| Bản ghi thuộc ngày lọc | 3 | 3 |
| Số lượt truy vấn | 9 | 9 |

[Snapshot](snapshot/) gồm JSON nguyên byte, inventory SHA-256, CSV và bảng chất lượng. Các lượt lấy lặp vẫn được giữ ở raw; không nhân số mẫu độc lập từ các lượt lặp. Snapshot ghi so sánh package với bản CD ngày 18/10, không phải khẳng định đó là phiên bản mới nhất; hash source hiện tại được kiểm tra riêng trong hồ sơ stack mới.

Ba phương án nhận cùng tập bản ghi của từng sinh viên, cùng nhóm file theo ngày và cùng phép tổng hợp theo đô thị. Tắt result reuse; luân phiên thứ tự ba phương án trong ba vòng.

| Sinh viên | Phương án | Median byte quét | Median engine (ms) | Median tổng (ms) |
| --- | --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | JSON đăng ký phân vùng | 1.558 | 729 | 944 |
| Sinh viên Tiến Sơn | JSON Projection | 1.558 | 485 | 647 |
| Sinh viên Tiến Sơn | Parquet Projection | 302 | 505 | 682 |
| Sinh viên Ngọc Quyên | JSON đăng ký phân vùng | 1.558 | 685 | 910 |
| Sinh viên Ngọc Quyên | JSON Projection | 1.558 | 481 | 640 |
| Sinh viên Ngọc Quyên | Parquet Projection | 302 | 452 | 647 |

[Từng lượt đo, query ID và kết quả](benchmark/) xác nhận kết quả tổng hợp tương đương ở cả 18 truy vấn. Parquet giảm **80,62% byte quét** so với JSON Projection trong bộ đo này. Thời gian tổng của JSON Projection nhỏ hơn Parquet ở cả hai môi trường; kết luận lựa chọn cần xét cả byte quét và độ trễ. Không quy đổi tỷ lệ byte thành tỷ lệ giảm hóa đơn; ngày lọc chỉ có ba bản ghi.

## 3. Tạm dừng và khôi phục thực tế

[Hai bản ghi vận hành](session/) xác nhận `WeatherCollectionSchedule` đi qua **ENABLED → DISABLED → ENABLED**. Account, function, rule, chu kỳ và target giữ nguyên fingerprint; không xóa dữ liệu. Nhật ký phục hồi riêng được ghi bền vững trước thay đổi. Đây là phép thử thật, tách với kiểm thử giả lập và preview.

## 4. Kiểm tra lại

```powershell
python tuan_4/scripts/verify_results.py
python -m unittest discover -s tuan_4/tests -v
```

Manifest bao phủ chính xác thành viên và SHA-256. Kiểm tra offline phát lại quan hệ JSON–CSV, raw–SELECT, phiên bản triển khai, trạng thái vận hành và kết quả backtest; không gọi AWS hoặc chứng minh lại trạng thái dịch vụ hiện tại.

[Báo cáo Tuần 4](../../docs/FINAL_REPORT.md) · [Backtest ba cửa sổ](../backtest_2026_10_20/README.md)
