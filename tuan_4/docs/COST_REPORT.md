# Báo cáo chi phí AWS

**Nguyễn Tiến Sơn (24110054) · Trần Thị Ngọc Quyên (24110051).**
**Cập nhật ngày 20/10/2026.**

## 1. Phương pháp tổng hợp

Chi phí cập nhật ngày **20/10/2026**, theo số liệu sinh viên xác nhận:

| Sinh viên | Chi phí (USD) |
| --- | ---: |
| Sinh viên Tiến Sơn | **0,25** |
| Sinh viên Ngọc Quyên | **0,22** |
| **Tổng cộng** | **0,47** |

Nguồn: [số liệu chi phí đã xác nhận](../results/cost/confirmed_cost_summary.json). Các bản xuất Cost Explorer gốc được giữ riêng để đối chiếu; bảng cập nhật không lấy số nhóm bản ghi của kỳ cũ làm căn cứ cho số tiền mới.

Số tiền được trình bày đến cent, đơn vị USD. Đây là mức chi phí cập nhật do sinh viên xác nhận; chưa có kỳ bắt đầu/kết thúc riêng trong lần xác nhận này.

## 2. Nguồn dữ liệu và đối chiếu

[confirmed_cost_summary.json](../results/cost/confirmed_cost_summary.json) là nguồn cho số tiền hiển thị trên README, báo cáo, nội dung nộp và hướng dẫn demo.

Các bản xuất API trước đó được giữ nguyên trong [bộ Cost Explorer lịch sử](../results/cost/cost_summary.json), [CSV lịch sử](../results/cost/learner_lab_cost_breakdown.csv) và [đợt truy vấn ngày 20/10](../results/cost_refresh_2026_10_20/README.md). Số nhóm bản ghi, kỳ truy vấn và tổng API ở các bản lưu này chỉ mô tả lần tải tương ứng.

Bộ thu thập Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV nguồn giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated; phép cộng API dùng Decimal. Không sửa số gốc hoặc chi tiết dịch vụ để khớp mức xác nhận mới.

Phạm vi chi phí là theo tài khoản; chưa phân bổ riêng cho tài nguyên đồ án hoặc từng stack.

## 3. Tối ưu có căn cứ

- Đo byte quét và độ trễ Athena bằng [18 truy vấn mới](../results/advanced_live_2026_10_20/benchmark/). Byte giảm không được quy đổi trực tiếp thành tỷ lệ giảm hóa đơn.
- Giữ lịch của hai stack mới DISABLED để tránh thu thập trùng; quản lý lịch chuẩn theo [checklist phiên](SESSION_CHECKLIST.md).
- Lưu CSV và manifest để phân tích offline, tránh gọi lại dịch vụ khi không cần dữ liệu cập nhật.
- Kiểm kê tài nguyên có Retain và versioning trước khi kết thúc sử dụng. Tạm dừng EventBridge không xóa Secret, log hoặc S3 và không loại bỏ mọi chi phí lưu trữ.

## 4. Kiểm tra lại

Đối chiếu số tiền trên các trang với [nguồn chi phí đã xác nhận](../results/cost/confirmed_cost_summary.json). Tổng hai tài khoản: **0,25 + 0,22 = 0,47 USD**.

Lệnh sau kiểm tra khả năng tái tạo bộ dữ liệu API lịch sử, được giữ riêng với số tiền hiển thị hiện tại:

```powershell
python tuan_4/scripts/cost_analysis.py --check
```

[Báo cáo Tuần 4](FINAL_REPORT.md) · [Nguồn chi phí hiện tại](../results/cost/confirmed_cost_summary.json) · [Minh chứng ngày 20/10](../results/advanced_live_2026_10_20/README.md).
