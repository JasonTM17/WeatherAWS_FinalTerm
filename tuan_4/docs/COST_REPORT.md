# Báo cáo chi phí AWS Cost Explorer

**Nguyễn Tiến Sơn (24110054) · Trần Thị Ngọc Quyên (24110051).**
**Kỳ số liệu:** từ 12/10 đến hết 19/10/2026; truy vấn Start inclusive 12/10, End exclusive 20/10. Nguồn được lưu trong đợt kiểm chứng ngày 19/10 theo phạm vi trả về của API; ngày chi phí và thời điểm tải là hai trường riêng.

## 1. Phương pháp tổng hợp

Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated. Phép cộng dùng Decimal; bản hiển thị làm tròn đến cent.

| Sinh viên | Nhóm ngày/dịch vụ/loại ghi nhận | Tổng UnblendedCost gốc (USD) | Hiển thị đến cent (USD) |
| --- | ---: | ---: | ---: |
| Sinh viên Tiến Sơn | 70 | -0,000000339 | 0,00 |
| Sinh viên Ngọc Quyên | 47 | 0,1364702401 | 0,14 |

Nguồn: [cost_summary.json](../results/cost/cost_summary.json), [117 dòng chi tiết](../results/cost/learner_lab_cost_breakdown.csv), [snapshot môi trường](../results/verification_2026_10_19/environment/). Kỳ chính xác trong cost_summary.json/cost.json là căn cứ của bảng; số liệu Estimated có thể được AWS cập nhật sau.

## 2. Diễn giải

CSV có cả Usage và Credit. Tổng của sinh viên Tiến Sơn có trị tuyệt đối nhỏ hơn một cent nên hiển thị 0,00; giá trị gốc và các dòng âm được giữ nguyên. Không đổi âm thành số dương hoặc thay tổng API bằng mức dự kiến. Không suy ra một khoản Credit cụ thể chỉ từ dấu của tổng; xem từng nhóm để đối chiếu.

Đây là chi phí **tài khoản** theo kỳ và nhóm dịch vụ, chưa phân bổ riêng theo tài nguyên đồ án. Không dùng bảng này để kết luận mọi dịch vụ thuộc Free Tier, chi phí tháng bằng 0 hoặc ngân sách được bảo toàn tuyệt đối. Các mức 0,05/0,03 USD của Tuần 2 là dự kiến đã được xác nhận riêng trong báo cáo tuần đó.

Hai stack mới tạo ngày 20/10 nằm sau kỳ chi phí này; chi phí của chúng không được suy diễn từ bảng. Theo dõi kỳ cập nhật tiếp theo và tài nguyên còn lưu giữ, gồm artifact version, Secret, log và S3.

## 3. Tối ưu có căn cứ

- Đo byte quét và độ trễ Athena bằng [18 truy vấn mới](../results/advanced_live_2026_10_20/benchmark/). Byte giảm không được quy đổi trực tiếp thành tỷ lệ giảm hóa đơn.
- Giữ lịch của hai stack mới DISABLED để tránh thu thập trùng; quản lý lịch chuẩn theo [checklist phiên](SESSION_CHECKLIST.md).
- Lưu CSV và manifest để phân tích offline, tránh gọi lại dịch vụ khi không cần dữ liệu cập nhật.
- Kiểm kê tài nguyên có Retain và versioning trước khi kết thúc sử dụng. Tạm dừng EventBridge không xóa Secret, log hoặc S3 và không loại bỏ mọi chi phí lưu trữ.

## 4. Kiểm tra lại

```powershell
python tuan_4/scripts/cost_analysis.py --check
```

Công cụ tính lại tổng từ nguồn đã lưu và kiểm tra byte bảng dẫn xuất, không gọi Cost Explorer. Không giữ dữ liệu hoặc câu lệnh có thông tin xác thực trong repository.

[Báo cáo Tuần 4](FINAL_REPORT.md) · [Dữ liệu chi phí](../results/cost/) · [Minh chứng ngày 20/10](../results/advanced_live_2026_10_20/README.md).
