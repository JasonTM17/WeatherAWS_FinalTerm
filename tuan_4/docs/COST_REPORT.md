# Chi phí AWS theo kỳ thực hành

**Sinh viên:** Nguyễn Tiến Sơn — 24110054; Trần Thị Ngọc Quyên — 24110051.
**Ngày xuất:** 19/10/2026. **Kỳ số liệu:** 12–19/10; ngày kết thúc không bao gồm trong API là 20/10.

## 1. Nguồn và phạm vi

Số liệu được đọc từ Cost Explorer với metric `UnblendedCost`, chu kỳ `DAILY`, nhóm theo `SERVICE` và `RECORD_TYPE`. [CSV gốc sinh viên Tiến Sơn](../results/verification_2026_10_19/environment/default/cost_by_service.csv) và [sinh viên Ngọc Quyên](../results/verification_2026_10_19/environment/quyen/cost_by_service.csv) giữ giá trị chính xác và cờ Estimated của từng nhóm.

| Sinh viên | Nhóm ngày/dịch vụ/record type | Tổng làm tròn đến cent, USD |
| --- | --- | --- |
| Sinh viên Tiến Sơn | 70 | 0,00 |
| Sinh viên Ngọc Quyên | 47 | 0,14 |

Đây là chi phí tài khoản trong kỳ theo dịch vụ, không phải hóa đơn riêng của dự án hoặc chi phí thực tế của một tháng. Bảng hiển thị làm tròn cent; giá trị gốc rất nhỏ được giữ nguyên trong CSV. Khoản dự kiến của báo cáo trước được trình bày riêng với số AWS trả về.

## 2. Tái lập

[cost_analysis.py](../scripts/cost_analysis.py) đọc các CSV đã xác minh hash và kiểm tra tổng bằng Decimal, không gán đơn giá, Free Tier hoặc số lượt sử dụng giả định.

```powershell
python tuan_4/scripts/cost_analysis.py --check
python tuan_4/scripts/cost_analysis.py --output output/week4-cost-moi
```

Đầu ra: [117 nhóm số liệu gốc có tên sinh viên](../results/cost/learner_lab_cost_breakdown.csv), [bảng tổng và phạm vi](../results/cost/cost_summary.json). Thư mục đầu ra mới phải chưa tồn tại. `--check` đối chiếu bản đã lưu và không gọi AWS.

## 3. Quản lý chi phí

- Theo dõi cùng kỳ, cờ Estimated và loại ghi nhận trước khi so sánh.
- Dùng điều kiện phân vùng và đọc thống kê bytes/time của mỗi SELECT; kết quả benchmark Tuần 3 giữ đúng bộ dữ liệu đã chốt.
- Xuất minh chứng và tạm dừng lịch vào cuối phiên bằng [checklist](SESSION_CHECKLIST.md).
- S3, Secret và log còn lưu tiếp tục cần quản lý lưu trữ; tắt lịch không chứng minh mọi dịch vụ hết phí.

[Tài liệu API Cost Explorer](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetCostAndUsage.html) · [Báo cáo chính](FINAL_REPORT.md)
