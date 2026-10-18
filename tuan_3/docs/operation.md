# Vận hành và kiểm chứng Tuần 3

## 1. Kiểm tra kết quả đã lưu

Dùng Python 3.12 trở lên trong môi trường riêng và chạy tại gốc repository:

```bash
python -m pip install -r tuan_3/requirements.txt
python -m unittest discover -s tuan_3/tests -v
python tuan_3/scripts/verify_results.py
python tuan_2/scripts/repository_audit.py --check
```

`verify_results.py` kiểm tra đường dẫn/hash/kích thước của manifest, tính lại chất lượng raw, đối chiếu 18 kết quả truy vấn và 18 bộ sai số dự báo. Các kiểm tra này không cần khóa AWS. Đây là kiểm tra tệp đã lưu, không phải kiểm tra dịch vụ hiện tại.

## 2. Chạy một mốc mới trên AWS

Hai profile SDK hiện dùng là `default` cho sinh viên Tiến Sơn và `quyen` cho sinh viên Ngọc Quyên, vùng `us-east-1`. Cấp khóa phiên bằng cơ chế bảo mật của môi trường; không đặt khóa trong tham số, mã nguồn hay tệp được Git theo dõi. Các chương trình không sử dụng AWS CLI.

```bash
python tuan_3/scripts/snapshot.py --output output/week3-new-snapshot
python tuan_3/scripts/benchmark.py --snapshot output/week3-new-snapshot --output output/week3-new-benchmark --run-id rnew
python tuan_3/scripts/dashboard.py --output output/week3-new-dashboard --backup output/week3-private-backups
python tuan_3/scripts/forecast.py --output output/week3-new-forecast
```

Thay `rnew` bằng mã lượt hợp lệ, chưa dùng; không ghi đè kết quả cũ. `snapshot.py` đọc AWS; `benchmark.py` tạo object/bảng riêng và chạy SELECT có phát sinh sử dụng dịch vụ; `dashboard.py` thay toàn bộ nội dung Dashboard riêng `WeatherAirQuality-Week3` sau khi sao lưu; `forecast.py` gọi API Open-Meteo. Đọc các điều kiện trong [kế hoạch](../../docs/WEEK_3_PLAN.md) trước khi thực hiện trên môi trường khác.

Thử nghiệm không thay raw hoặc bảng Glue sản xuất. Để thu hồi tài nguyên thử nghiệm, xác minh đúng bucket/prefix/tên bảng của lượt, rồi chỉ xóa các object dưới prefix thử nghiệm và ba bảng `w3_<run-id>_*` tương ứng. Không chạy thao tác xóa theo tên rút gọn chưa đối chiếu. Dashboard cũ được phục hồi từ bản sao riêng bằng PutDashboard; nếu trước đó không có Dashboard thì có thể xóa đúng Dashboard vừa tạo. Dữ liệu Athena dưới prefix kết quả truy vấn cần được xử lý riêng theo chính sách lưu giữ.

## 3. Artifact và CD

```bash
python tuan_3/scripts/release.py --output output/lambda-build-new
```

Lệnh mặc định chỉ đóng gói, không gọi AWS. `manifest.json` ghi SHA-256 module và ZIP. ZIP chỉ chứa `lambda_function.py`, không chứa khóa phiên, dữ liệu hay thư viện phân tích.

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

- Kiểm tra cục bộ: 18 hồi quy Tuần 3 đạt; đối chiếu 92 tệp manifest, 18 kết quả Athena và 18 bộ sai số đạt.
- Snapshot AWS, thử nghiệm Athena và Dashboard: đã có dữ liệu thật tại [mốc 18/10](../results/integration_2026_10_18/).
- CI/CD trên GitHub: xem [các lượt chạy](https://github.com/JasonTM17/WeatherAWS_FinalTerm/actions). Trạng thái triển khai của lần kiểm chứng sẽ được ghi kèm run ID và bằng chứng sau khi workflow kết thúc; không suy ra thành công chỉ từ việc có tệp workflow.

[Báo cáo](FINAL_REPORT.md) · [Trang Tuần 3](../README.md)
