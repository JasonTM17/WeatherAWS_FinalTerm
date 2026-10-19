# Tuần 4 — Kiểm chứng hệ thống và chuẩn bị bảo vệ

**Nguyễn Tiến Sơn — 24110054; Trần Thị Ngọc Quyên — 24110051.**
**Mốc kiểm chứng:** 19/10/2026. Hồ sơ thực hiện các yêu cầu tổng kết sau khi Tuần 3 được duyệt.

| Nội dung | Tài liệu và minh chứng |
| --- | --- |
| Báo cáo chính | [Kết quả, phương pháp, phân công và kết luận](docs/FINAL_REPORT.md) |
| Vận hành | [Hai request có kiểm soát](docs/LOG_METRIC_S3_RECONCILIATION.md) · [Raw/log/metric/Athena trực tiếp](results/verification_2026_10_19/README.md) |
| Chi phí | [Cost Explorer đúng kỳ](docs/COST_REPORT.md) · [CSV theo dịch vụ](results/cost/learner_lab_cost_breakdown.csv) |
| Hạ tầng | [Một template CloudFormation — 17 tài nguyên](infrastructure/weather-stack.json) · [Cách triển khai](docs/INFRASTRUCTURE.md) |
| Bảo mật | [Cấu hình quan sát và phạm vi quyền](docs/SECURITY_AUDIT.md) · [Policy runtime tham khảo](infrastructure/collector-policy.example.json) |
| Kết thúc phiên Lab | [Xuất minh chứng, preview/pause/restore](docs/SESSION_CHECKLIST.md) |
| Video | [Lời thoại đi cùng từng bước bấm, khoảng 9 phút](docs/VIDEO_DEMO_SCRIPT.md) · [Hướng dẫn chi tiết](docs/DEMO_GUIDE.md) |
| Nhật ký | [20 giờ Tuần 4, tổng 78 giờ đã xác nhận](docs/WORKLOG.md) · [CSV](worklog.csv) |
| Kế hoạch | [Đầu việc và tiêu chí theo dõi](../docs/WEEK_4_PLAN.md) |

## Kết quả kiểm chứng

- Mỗi môi trường có một lượt realtime thu đủ ba đô thị, ba bản ghi; JSON S3, CSV và SELECT theo record_id khớp nhau.
- Chu kỳ chứa lượt kiểm chứng có một Invocation, không có Error; mỗi lượt có một Publish được SNS chấp nhận. Cả hai người nhận đã xác nhận email mới.
- Chi phí được giữ theo đúng kỳ và Estimated. Cấu hình S3 hiện hữu và thiết kế stack mới được ghi riêng.
- Source collector tiếp tục là [lambda_function.py](../tuan_2/lambda/lambda_function.py). Template dùng artifact thật, không có hàm minh họa trả complete.

## Tái lập trên máy

```powershell
python -m pip install -r tuan_3/requirements.txt cfn-lint==1.57.2
python -m unittest discover -s tuan_4/tests -v
python tuan_4/scripts/verify_results.py
python tuan_4/scripts/cost_analysis.py --check
python tuan_4/scripts/reconcile_ops.py --check
python tuan_4/scripts/security_report.py --check
python tuan_4/scripts/prepare_stack.py --output output/week4-stack-moi
cfn-lint --template tuan_4/infrastructure/weather-stack.json --regions us-east-1
```

Các lệnh trên kiểm tra snapshot hoặc dựng artifact; không gọi Lambda, thay ngưỡng hoặc tắt lịch. Muốn đọc trạng thái AWS mới, dùng [verify_environment.py](scripts/verify_environment.py) với phiên Lab hợp lệ và thư mục đầu ra mới. Muốn tạo đúng một lượt realtime, dùng [run_demo_check.py](scripts/run_demo_check.py) và tùy chọn `--invoke`; mặc định chỉ xem trước.

Mã nguồn, báo cáo và bằng chứng phân biệt kiểm thử cục bộ, API kiểm tra template và triển khai stack. Bản template trong snapshot ngày 19/10 là phiên bản 17 tài nguyên đã kiểm chứng lúc chụp; source chính hiện tại bổ sung hai metric filter và có hồ sơ kiểm tra riêng khi phát hành.

[Trang chính](../README.md) · [Tuần 3](../tuan_3/README.md)
