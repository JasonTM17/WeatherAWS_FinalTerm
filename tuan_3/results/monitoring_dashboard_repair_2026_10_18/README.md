# Dashboard sau sửa biểu thức metric math

Đã thay biểu thức tỷ lệ lỗi nhiều lớp IF bằng **một IF với điều kiện kết hợp**, cập nhật Dashboard `WeatherAirQuality-Week3` trong cả hai môi trường và đọc lại khớp cấu hình gửi. Đã sao lưu cấu hình trước cập nhật ở nơi riêng. Không thay mã/cấu hình Lambda, lịch EventBridge, ngưỡng cảnh báo hoặc dữ liệu metric.

```text
IF((inv>0) AND (FILL(err,-1)>=0) AND (err<=inv),100*err/inv)
```

Theo [quy tắc IF của AWS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/using-metric-math.html), nhánh được chọn nhưng thiếu điểm có thể trả 0. Vì vậy, một IF bên ngoài có thể làm điểm đã bị IF bên trong loại bỏ hiện lại thành 0. Điều kiện phẳng loại trực tiếp khoảng thiếu Errors, thiếu Invocations, mẫu số 0 hoặc Errors lớn hơn Invocations. Các biểu thức đánh dấu thiếu cặp cũng được đổi sang một IF.

## Kiểm chứng trên dịch vụ thật

Đã chạy sáu trường hợp bằng **GetMetricData chỉ đọc**, biến đổi chuỗi đầu vào trong truy vấn để kiểm tra biểu thức; không ghi metric/log/sự kiện giả vào AWS. Các chuỗi kiểm tra được lưu riêng, không được gọi là số liệu vận hành native.

| Trường hợp | Biểu thức cuối |
| --- | --- |
| Thiếu Errors | Bỏ điểm thiếu |
| Errors lớn hơn Invocations | Bỏ điểm không hợp lệ |
| Thiếu Invocations | Bỏ điểm thiếu |
| Invocations = 0 | Không tính tỷ lệ |
| Invocations hợp lệ, Errors = 0 | Giữ 0% |
| Invocations gấp đôi Errors | Giữ 50% |

- **Sinh viên Tiến Sơn:** [sáu kết quả API](default/metric_math_checks.json) · [đọc lại cấu hình](default/verification.json) · [Dashboard JSON](default/dashboard.json).
- **Sinh viên Ngọc Quyên:** [sáu kết quả API](quyen/metric_math_checks.json) · [đọc lại cấu hình](quyen/verification.json) · [Dashboard JSON](quyen/dashboard.json).

## Điểm thiếu cặp của sinh viên Tiến Sơn

![AWS: Errors có điểm nhưng thiếu Invocations](default/cloudwatch_07.png)

Ảnh AWS giữ điểm Errors = 3 lúc 09:15 UTC để chẩn đoán. Tỷ lệ ở các khoảng có đủ cặp là 0%; tỷ lệ toàn cửa sổ vẫn không được tính. [CSV ghép từng khoảng](../monitoring_followup_2026_10_18/default/period_reconciliation.csv) ghi rõ vị trí thiếu, không điền Invocations = 0.

[Ảnh native sinh viên Tiến Sơn](default/cloudwatch_01.png) · [Tỷ lệ chỉ trên các khoảng đủ cặp](default/cloudwatch_03.png) · [Ảnh native sinh viên Ngọc Quyên](quyen/cloudwatch_01.png) · [Tỷ lệ sinh viên Ngọc Quyên](quyen/cloudwatch_03.png) · [Chẩn đoán thiếu cặp sinh viên Ngọc Quyên](quyen/cloudwatch_07.png).

CloudWatch có thể nối các điểm trên đồ thị đường; đoạn nối không bổ sung số đo tại các khoảng trống. Đọc cùng bảng CSV và đồ thị chẩn đoán để phân biệt điểm thiếu với 0 đã được đo.

[Manifest](manifest.json) · [Bộ dữ liệu native/log gốc của phép đối chiếu](../monitoring_followup_2026_10_18/README.md) · [Vận hành](../../docs/operation.md#9-đối-chiếu-bộ-đếm-và-giờ-dự-báo-bổ-sung).
