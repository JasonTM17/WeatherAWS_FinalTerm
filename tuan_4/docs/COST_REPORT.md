# Báo cáo Chi phí Vận hành AWS Cost Explorer (Tuần 4)

**Học phần:** Điện toán đám mây · **Lớp:** 261CLCO332779_05 · **GVHD:** ThS. Huỳnh Xuân Phụng.  
**Sinh viên thực hiện:** Nguyễn Tiến Sơn (MSSV: 24110054) và Trần Thị Ngọc Quyên (MSSV: 24110051).  
**Mốc thực hiện:** Tuần 4 (26/10/2026 – 01/11/2026) · **Nền tảng:** AWS Academy Learner Lab (`us-east-1`).

---

## 1. Bối cảnh và Mô hình Ngân sách AWS Learner Lab

Trong môi trường học tập **AWS Academy Learner Lab**, mỗi sinh viên được cấp một hạn mức tín dụng cố định (thông thường **$100.00 USD**) cho toàn bộ thời gian học kỳ. Nếu một kiến trúc đám mây không được thiết kế tối ưu về mặt kinh tế (FinOps) hoặc bị rò rỉ tài nguyên (như chạy EC2 liên tục, Athena quét toàn bộ bảng không phân vùng, hoặc Secrets Manager lưu trữ nhiều biến không cần thiết), hạn mức tài khoản có thể bị cạn kiệt, dẫn đến việc bị khóa môi trường Lab.

Mục tiêu của báo cáo này:
1. Đánh giá chi tiết chi phí hoạt động thực tế của từng dịch vụ serverless trong hệ thống thu thập dữ liệu thời tiết & chất lượng không khí.
2. Mô phỏng các kịch bản chi phí dài hạn (1 tháng, 3 tháng, 6 tháng, 1 năm và mở rộng 100 đô thị).
3. Đề xuất các giải pháp kiến trúc tối ưu hóa chi phí, bảo toàn tối đa tín dụng AWS Learner Lab.

---

## 2. Bảng phân tích Chi phí Từng Dịch vụ

Số liệu được tính toán dựa trên mức đơn giá công bố của AWS tại vùng `us-east-1` và đối chiếu qua AWS Cost Explorer (chi tiết tại [`tuan_4/results/cost/learner_lab_cost_breakdown.csv`](../results/cost/learner_lab_cost_breakdown.csv)):

| Dịch vụ AWS | Loại hình sử dụng | Định lượng hàng tháng | Đơn giá AWS (`us-east-1`) | Mức miễn phí (Free Tier) | Chi phí gộp (USD) | Miễn phí (USD) | Chi phí ròng (USD) | Tỷ trọng |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **AWS Secrets Manager** | Lưu trữ Secret & API Calls | 1 Secret; 720 lệnh `GetSecretValue` | $0.40 / secret / tháng; $0.05 / 10k calls | 30 ngày dùng thử secret mới | $0.4036 | $0.0000 | **$0.4036** | **99.97%** |
| **Amazon Athena** | Byte dữ liệu quét qua truy vấn | 0.000015 TB (~15 MB quét) | $5.00 / TB dữ liệu quét | Không có Free Tier cố định | $0.000075 | $0.0000 | **$0.0001** | **0.03%** |
| **AWS Lambda** | Số lượt gọi & Bộ nhớ thực thi | 720 invocations; 108 GB-s (256MB) | $0.20 / 1M requests; $0.0000166667 / GB-s | 1,000,000 req & 3.2M GB-s / tháng | $0.000003 | -$0.000003 | **$0.0000** | 0.00% |
| **Amazon S3** | Lưu trữ Standard & Lệnh PUT/GET | 0.15 MB dung lượng; 720 PUTs; 300 GETs | $0.023 / GB; $0.005 / 1k PUT; $0.0004 / 1k GET | 5 GB storage, 20k GET, 2k PUT | $0.0037 | -$0.0037 | **$0.0000** | 0.00% |
| **Amazon CloudWatch** | Ingestion log, Metric Filter, Dashboard, Alarm | 5 MB logs; 2 filters; 1 alarm; 1 dashboard | $0.50 / GB log; $0.10 / alarm; $3.00 / dashboard | 5 GB log, 10 metrics, 10 alarms, 3 dashboards | $0.0025 | -$0.0025 | **$0.0000** | 0.00% |
| **Amazon SNS** | Thông báo đẩy & Gửi Email cảnh báo | ~15 email cảnh báo ô nhiễm | $2.00 / 100k email | 1,000 email thông báo / tháng | $0.0003 | -$0.0003 | **$0.0000** | 0.00% |
| **TỔNG CỘNG** | — | — | — | — | **$0.4102** | **-$0.0065** | **$0.4037** | **100.0%** |

### Nhận xét quan trọng:
- **Secrets Manager chiếm 99.97% tổng chi phí:** Phí duy trì secret cố định ($0.40/tháng) là khoản chi phí duy nhất phát sinh tiền mặt ngoài AWS Free Tier.
- **Tầng Serverless Compute & Storage gần như $0.00:** Nhờ kiến trúc không máy chủ (Serverless), toàn bộ Lambda, S3, CloudWatch và SNS đều nằm gọn 100% trong hạn mức AWS Always-Free Tier.
- **Athena tối ưu vượt bậc:** Nhờ áp dụng **Partition Projection** và nén **Parquet Snappy**, mỗi câu truy vấn chỉ quét từ vài trăm byte đến vài chục kilobyte thay vì quét toàn bộ dữ liệu, đưa tổng chi phí Athena trong cả tháng xuống dưới $0.0001 USD.

---

## 3. Kịch bản Dự báo Chi phí (Cost Scenarios)

Dựa trên dữ liệu từ [`tuan_4/results/cost/projected_cost_scenarios.csv`](../results/cost/projected_cost_scenarios.csv):

```
+---------------------------------------------------------------------------------------+
| Kịch bản Vận hành                  | Thời gian | Tổng chi phí (USD) | % Ngân sách Lab |
+------------------------------------+-----------+--------------------+-----------------+
| 1. Baseline Hiện hành (3 đô thị)   | 1 Tháng   | $0.4037            | 0.81%           |
| 2. Học kỳ Sinh viên (3 đô thị)     | 3 Tháng   | $1.2111            | 2.42%           |
| 3. Hoạt động Bán niên (3 đô thị)   | 6 Tháng   | $2.4223            | 4.84%           |
| 4. Hoạt động Trọn năm (3 đô thị)   | 12 Tháng  | $4.8447            | 9.69%           |
| 5. Mở rộng Toàn quốc (100 đô thị)  | 1 Tháng   | $0.4802            | 0.96%           |
+---------------------------------------------------------------------------------------+
```

### Đánh giá tính khả thi:
Với tổng chi phí chưa đến **$1.22 USD cho cả học kỳ 3 tháng**, hệ thống tiêu tốn chưa tới **2.5%** hạn mức được cấp ($50.00 - $100.00), đảm bảo tài khoản hoàn toàn an toàn và không bao giờ gặp nguy cơ thiếu hụt ngân sách.

---

## 4. Các Chiến lược Tối ưu hóa Chi phí (FinOps Recommendations)

Trích xuất từ ma trận khuyến nghị [`tuan_4/results/cost/cost_optimization_recommendations.csv`](../results/cost/cost_optimization_recommendations.csv):

### REC-01: Chuyển đổi Cấu hình sang AWS Systems Manager (SSM) Parameter Store
- **Hiện trạng:** Dùng AWS Secrets Manager tốn $0.40/tháng cho 1 secret lưu tọa độ và ngưỡng AQI.
- **Giải pháp:** Chuyển sang AWS Systems Manager Parameter Store loại Standard Parameters (loại mã hóa KMS SecureString).
- **Hiệu quả:** SSM Standard Parameters được AWS cung cấp **miễn phí 100%** không giới hạn số lượng và số lệnh gọi API.
- **Mức tiết kiệm:** **Tiết kiệm $0.40/tháng (giảm 99.1% tổng hóa đơn)**.

### REC-02: Duy trì Athena Partition Projection & Snappy Parquet
- **Hiện trạng:** Truy vấn NDJSON quét toàn bộ tệp hoặc phụ thuộc `MSCK REPAIR TABLE` tốn thời gian và byte quét.
- **Giải pháp:** Cố định cơ chế Partition Projection tính toán đường dẫn S3 trong bộ nhớ và chuyển đổi định dạng sang Parquet Snappy.
- **Hiệu quả:** Giảm **80.59% đến 96.50%** lượng byte quét mỗi truy vấn (thực nghiệm đã chứng minh ở Tuần 3 từ 11.2 KB xuống còn 393 byte).

### REC-03: Caching Cấu hình trong Bộ nhớ Global Scope của Lambda
- **Hiện trạng:** Mỗi phiên chạy Lambda gọi Boto3 `get_secret_value` một lần (720 lần/tháng).
- **Giải pháp:** Khai báo biến cache ở phạm vi ngoài hàm `lambda_handler`. Khi môi trường thực thi (execution environment) còn ấm (warm container), Lambda tái sử dụng cấu hình mà không gọi lại API Secrets Manager.
- **Hiệu quả:** Giảm 90% số lượng API calls đến Secrets Manager.

### REC-04: Tự động Tạm dừng EventBridge Rule ngoài Giờ Thực hành
- **Hiện trạng:** Nếu sinh viên quên tắt Rule, Lambda tiếp tục kích hoạt 24/7 trong kỳ nghỉ hoặc sau khi hoàn thành môn học.
- **Giải pháp:** Sử dụng bộ công cụ [`tuan_4/scripts/cleanup_resources.ps1`](../scripts/cleanup_resources.ps1) và [`session_control.py`](../scripts/session_control.py) để vô hiệu hóa (`DISABLED`) Rule EventBridge ngay khi kết thúc buổi thực hành.
- **Hiệu quả:** Triệt tiêu hoàn toàn nguy cơ phát sinh chi phí ngoài ý muốn.

---

## 5. Kết luận

Kiến trúc Serverless Event-driven đạt chuẩn tối ưu FinOps xuất sắc. Chi phí vận hành cực kỳ tiết kiệm ($0.40/tháng), có khả năng mở rộng quy mô lên hàng trăm đô thị mà chi phí vẫn duy trì ở mức tối thiểu, chứng minh tính ưu việt của mô hình Serverless trên nền tảng AWS.
