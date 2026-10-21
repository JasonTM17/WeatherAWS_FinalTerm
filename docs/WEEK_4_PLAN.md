# Kế hoạch Tuần 4 — Kết quả thực hiện và bàn giao

**Nguyễn Tiến Sơn (24110054) · Trần Thị Ngọc Quyên (24110051).**
Điện toán đám mây · GVHD: ThS. Huỳnh Xuân Phụng.
**Lập ngày 19/10; kết quả AWS ngày 19–20/10; cập nhật hồ sơ bàn giao ngày 21/10/2026.**

## 1. Mục tiêu và điều chỉnh đã thống nhất

Kiểm chứng luồng thu thập–lưu trữ–truy vấn–cảnh báo, đối chiếu CloudWatch, đo Athena, đánh giá dự báo, đóng gói CloudFormation và hoàn thiện hồ sơ. Phạm vi giữ ba đô thị, email và hai môi trường Learner Lab.

Lịch 26/10–01/11 ban đầu là lịch dự kiến. Các kết quả thực hiện sớm được ghi đúng ngày 19–20/10; không ghi ngày tương lai như đã hoàn thành. Ngày 20/10, phương án dự báo được thống nhất chuyển từ chờ ba kỳ phát hành cách nhau 24 giờ sang **backtest ba cửa sổ lịch sử**, có thể đánh giá ngay. Đây là điều chỉnh phương pháp: ba cửa sổ hồi cứu không được gọi là ba bản dự báo đã phát hành thực tế.

## 2. Phân công

| Sinh viên | Trách nhiệm |
| --- | --- |
| Sinh viên Tiến Sơn | Lambda, S3, Secrets Manager, SNS, EventBridge, CloudWatch, hạ tầng và triển khai |
| Sinh viên Ngọc Quyên | Glue/Athena, xuất raw/CSV, chất lượng dữ liệu, phân tích, dự báo và chi phí |
| Hai sinh viên | Tích hợp, đối chiếu chéo, nhật ký, báo cáo và trình bày |

## 3. Đối chiếu đầu việc với kết quả

| Mã | Tiêu chí | Kết quả và nguồn |
| --- | --- | --- |
| W4-01 | Chốt phiên bản/config | Stack mới có source/ZIP/template hash, đọc lại config và quyền gọi đúng rule/account: [hồ sơ ngày 20/10](../tuan_4/results/advanced_live_2026_10_20/README.md) |
| W4-02 | Raw có nguồn và inventory | 700 bản ghi, 115 JSON gốc; CSV, chất lượng, SHA-256 và bảng đô thị–giờ: [snapshot](../tuan_4/results/advanced_live_2026_10_20/snapshot/) |
| W4-03 | Log–metric–S3 theo đúng lượt | Mỗi stack mới có đầy đủ lifecycle, ba bản ghi, một Invocation và 0 Errors trong chu kỳ chứa lượt kiểm chứng: [runtime](../tuan_4/results/advanced_live_2026_10_20/stacks/) |
| W4-04 | Ngưỡng, Publish và người nhận | Ngày 19/10 có cảnh báo dữ liệu vượt ngưỡng, người nhận xác nhận; ngày 20/10 dưới ngưỡng nên 0 cảnh báo, topic mới có thư thử kênh đã nhận: [email](../tuan_4/results/advanced_live_2026_10_20/email/) |
| W4-05 | 18 lượt đo cùng đầu vào | Ba phương án × ba lần × hai môi trường; không reuse, parity và median bytes/engine/total: [benchmark](../tuan_4/results/advanced_live_2026_10_20/benchmark/) |
| W4-06 | Ba backtest theo thời gian | Mỗi cửa sổ 24 giờ train trước gốc, 24 giờ đích, MA24 cố định; 432 dự đoán và 18 dòng sai số: [backtest](../tuan_4/results/backtest_2026_10_20/README.md) |
| W4-07 | Kiểm thử, artifact và CI | Guard kiểm tra môi trường, tên tài nguyên, version, holdout và recovery; [workflow](../.github/workflows/verify-repository.yml), [bộ xác minh](../tuan_4/scripts/verify_results.py) |
| W4-08 | Hồ sơ và trình bày | [Báo cáo](../tuan_4/docs/FINAL_REPORT.md), [nội dung nộp](../tuan_4/docs/SUBMISSION.md), worklog, message commit nguyên bản và [video demo](https://drive.google.com/drive/folders/1G50ZYK7QFGoftLx3hYglw4SRTwr3TvAR?usp=sharing) |
| W4-09 | Chi phí có kỳ/Estimated | 117 nhóm kỳ 12–19/10; giữ số gốc, scope tài khoản: [chi phí](../tuan_4/docs/COST_REPORT.md) |
| W4-10 | Pause/restore bảo toàn trạng thái | Hai lịch chuẩn ENABLED → DISABLED → ENABLED, target không đổi, không xóa dữ liệu: [thao tác thực tế](../tuan_4/results/advanced_live_2026_10_20/session/) |
| W4-11 | Một template triển khai thật | 17 tài nguyên, hai stack CREATE_COMPLETE và E2E đúng function/database/workgroup mới: [hạ tầng](../tuan_4/docs/INFRASTRUCTURE.md) |
| W4-12 | Kiểm tra bảo mật theo phạm vi | BPA, AES256, versioning, ownership và HTTPS mới đọc lại; giữ LabRole: [bảo mật](../tuan_4/docs/SECURITY_AUDIT.md) |

## 4. Kiểm tra nghiệm thu

```powershell
python -m unittest discover -s tuan_2/tests -v
python -m unittest discover -s tuan_2/analytics -p 'test_*.py' -v
python -m unittest discover -s tuan_3/tests -v
python -m unittest discover -s tuan_4/tests -v
python tuan_3/scripts/verify_results.py
python tuan_4/scripts/verify_results.py
python tuan_4/scripts/cost_analysis.py --check
python tuan_4/scripts/reconcile_ops.py --check
python tuan_4/scripts/security_report.py --check
cfn-lint tuan_4/infrastructure/weather-stack.json --regions us-east-1
python tuan_2/scripts/repository_audit.py --check
git diff --check
```

Manifest bảo vệ thành viên và byte dữ liệu; bộ xác minh phát lại JSON–CSV–SELECT và backtest từ phản hồi đã lưu. CI theo commit không thay việc đọc lại dịch vụ thật hoặc xác nhận hộp thư. Hồ sơ ngày 20/10 lưu riêng bằng chứng AWS và xác nhận người nhận.

## 5. Vận hành và bàn giao

Lịch chuẩn được khôi phục sau phép thử; lịch hai stack mới giữ DISABLED. Cuối buổi xuất dữ liệu và đọc lại rule/target trước thay đổi. State phục hồi, Outputs riêng, credentials và tham số email không công bố. [Checklist cuối Lab](../tuan_4/docs/SESSION_CHECKLIST.md) mô tả phạm vi thao tác.

**Tổng theo tuần đã xác nhận:** Tuần 4 có 20 giờ thực tế (10 giờ mỗi sinh viên), toàn đồ án 78 giờ. [Worklog](WORKLOG.md) giữ nguồn xác nhận. Số giờ không được suy ra từ thời gian chương trình chạy.

[Báo cáo tổng kết](FINAL_PROJECT_REPORT.md) · [Nội dung nộp](../tuan_4/docs/SUBMISSION.md) · [Danh mục minh chứng](EVIDENCE_INDEX.md).
