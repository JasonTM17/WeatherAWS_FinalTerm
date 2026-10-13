# NHẬT KÝ CÔNG VIỆC DỰ ÁN - TUẦN 1 (PROJECT WORKLOG WEEK 1)

> **Học phần:** Điện toán đám mây (Cloud Computing) - Mã lớp: `261CLCO332779_05`  
> **Giảng viên hướng dẫn (GVHD):** ThS. Huỳnh Xuân Phụng  
> **Đề tài:** Hệ thống thu thập và phân tích dữ liệu thời tiết & chất lượng không khí đa đô thị trên nền tảng AWS Serverless  
> **Kho lưu trữ GitHub chính thức:** [https://github.com/JasonTM17/WeatherAWS_FinalTerm.git](https://github.com/JasonTM17/WeatherAWS_FinalTerm.git)  
> **Nhóm thực hiện (Nhóm 05):**
> - **Sinh viên 1 (Trưởng nhóm):** Nguyễn Tiến Sơn — MSSV: `24110054`
> - **Sinh viên 2 (Thành viên):** Trần Thị Ngọc Quyên — MSSV: `24110051`  
> **Môi trường thực nghiệm:** AWS Academy Learner Lab (`us-east-1` | IAM Role: `LabRole`)  
> - Tài khoản 1 (Sơn): `873674852386` (Profile: `[default]`)  
> - Tài khoản 2 (Quyên): `134987931868` (Profile: `[quyen]`)

---

## 1. BẢNG TỔNG KẾT THỜI GIAN LÀM VIỆC (CAM KẾT ĐỊNH MỨC >= 8H / TUẦN / SINH VIÊN)

Tuân thủ quy định của đề cương học phần và hướng dẫn của GVHD ThS. Huỳnh Xuân Phụng: *Mỗi sinh viên dành tối thiểu 8 giờ/tuần cho đồ án (tương đương tối thiểu 16 giờ/tuần đối với nhóm 2 sinh viên).*

| Tuần | Giai đoạn thực hiện theo đề cương | Giờ SV1 (Sơn - 24110054) | Giờ SV2 (Quyên - 24110051) | Tổng giờ nhóm | Trạng thái nghiệm thu |
|:---:|---|:---:|:---:|:---:|:---:|
| **Tuần 1** | **Khảo sát dịch vụ, thiết kế kiến trúc, dựng nền tảng S3 & Secrets Manager, gắn tag** | **9.5 giờ** | **9.0 giờ** | **18.5 giờ** | **HOÀN THÀNH (ĐẠT)** |
| **Tuần 2** | Triển khai chức năng lõi (Lambda, EventBridge, SNS, Athena DDL, Unit tests) | 10.0 giờ | 9.5 giờ | 19.5 giờ | Hoàn thành (Đạt) |
| **Tuần 3** | Tích hợp Glue Catalog tự động, CloudWatch Metric Alarm, Dashboard giám sát | 9.0 giờ | 8.5 giờ | 17.5 giờ | Dự kiến |
| **Tuần 4** | Kiểm thử tổng thể, tối ưu chi phí quét dữ liệu, dọn tài nguyên, báo cáo & demo | 10.5 giờ | 10.0 giờ | 20.5 giờ | Dự kiến |
| **TỔNG** | **Toàn bộ 4 tuần thực hiện đồ án** | **39.0 giờ** | **37.0 giờ** | **76.0 giờ** | **ĐẠT TIÊU CHUẨN** |

---

## 2. NHẬT KÝ CHI TIẾT CÔNG VIỆC TUẦN 1 (15/09/2026 – 21/09/2026)

**Mục tiêu Tuần 1:** Tìm hiểu dịch vụ AWS, nghiên cứu API nguồn Open-Meteo, thiết kế sơ đồ kiến trúc tổng thể, dựng hạ tầng nền tảng trên AWS Learner Lab (S3 Bucket, AWS Secrets Manager, IAM LabRole), thiết lập hệ thống Tagging tài nguyên bắt buộc theo quy định của giảng viên.

| Ngày | Sinh viên thực hiện | Nội dung công việc chi tiết | Số giờ | Minh chứng / Sản phẩm bàn giao | Mức độ AI hỗ trợ (AI Disclosure) |
|:---:|---|---|:---:|---|---|
| **16/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Khảo sát các điểm cuối REST API của Open-Meteo (Weather Forecast & Air Quality API). Đánh giá 23 chỉ số môi trường (nhiệt độ, độ ẩm, áp suất, gió, UV, PM2.5, PM10, CO, NO2, SO2, O3) và chuẩn phân cấp AQI của US EPA. | **3.5h** | - Tài liệu khảo sát API endpoints và cấu trúc dữ liệu JSON phản hồi.<br>- Bảng đối chiếu ngưỡng US EPA AQI (6 cấp độ). | **Không dùng AI**<br>(Sinh viên tự tra cứu tài liệu kỹ thuật gốc của Open-Meteo và US EPA). |
| **17/09/2026** | **Trần Thị Ngọc Quyên**<br>(MSSV: `24110051`) | Tìm hiểu hạn ngạch và chính sách bảo mật của AWS Academy Learner Lab: cơ chế ủy quyền `LabRole` / `LabInstanceProfile`, vùng hoạt động khả dụng (`us-east-1`), ngân sách $100 và các quy định an toàn tài nguyên. | **3.0h** | - Bảng tổng hợp quyền hạn của `LabRole` đối với S3, Secrets Manager, Lambda, SNS, Athena.<br>- Danh mục chính sách gắn nhãn chi phí. | **Không dùng AI**<br>(Tự nghiên cứu tài liệu AWS Academy Learner Lab Guide). |
| **18/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Thiết kế sơ đồ kiến trúc hệ thống Serverless Event-Driven tổng thể; phân tích luồng dữ liệu hai chiều: EventBridge -> Lambda -> S3 Data Lake -> Athena/Glue -> SNS Alerting. | **3.0h** | - Sơ đồ kiến trúc vector SVG `tuan_1/docs/architecture_diagram.svg`.<br>- Tài liệu kiến trúc `tuan_1/docs/ARCHITECTURE.md`. | **Có dùng AI hỗ trợ**<br>(LLM hỗ trợ gợi ý bố cục sơ đồ khối chuẩn AWS Architecture Icons). |
| **19/09/2026** | **Trần Thị Ngọc Quyên**<br>(MSSV: `24110051`) | Viết script PowerShell và AWS CLI khởi tạo S3 Bucket (`weather-aqi-<account_id>`) tại `us-east-1`, cấu hình mã hóa mặc định AES-256 (SSE-S3), chặn truy cập công khai (Block Public Access) và gắn thẻ tài nguyên bắt buộc: `Project=WeatherAWS_FinalTerm`, `Owner=24110051`, `Course=Cloud_FinalTerm`. | **3.5h** | - Script khởi tạo hạ tầng `tuan_1/scripts/01_setup_s3.ps1`.<br>- S3 Bucket tạo thành công trên AWS Console & CLI. | **Có dùng AI hỗ trợ**<br>(LLM hỗ trợ rà soát cú pháp lệnh CLI `aws s3api put-bucket-tagging`). |
| **20/09/2026** | **Nguyễn Tiến Sơn**<br>(MSSV: `24110054`) | Thiết lập secret an toàn trên AWS Secrets Manager (`weather/api_config`) lưu trữ tọa độ địa lý 3 đô thị lớn (TP.HCM, Hà Nội, Đà Nẵng), ngưỡng cảnh báo ô nhiễm (AQI >= 100, PM2.5 >= 35.5 µg/m³) và cấu hình phân vùng S3. | **3.0h** | - Script triển khai `tuan_1/scripts/02_setup_secrets.ps1`.<br>- Secret `weather/api_config` hoạt động trên AWS Secrets Manager. | **Tự triển khai qua CLI**<br>(Tự thiết kế cấu trúc JSON config và thực thi lệnh AWS CLI). |
| **21/09/2026** | **Cả hai thành viên**<br>(Sơn & Quyên) | Họp rà soát kỹ thuật kết thúc Tuần 1: đối chiếu hạ tầng S3 & Secrets Manager trên cả hai tài khoản lab, phân công cụ thể giai đoạn Tuần 2, tổng hợp dữ liệu và biên soạn báo cáo tiến độ Tuần 1. | **Sơn: 2.5h**<br>**Quyên: 2.5h** | - Biên bản nghiệm thu kỹ thuật Tuần 1.<br>- Báo cáo tiến độ Tuần 1 (`Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx` & `.pdf`).<br>- Commit Git đánh dấu cột mốc Tuần 1. | **Không dùng AI**<br>(Hai sinh viên trực tiếp họp kiểm tra chéo và đối chiếu trên tài khoản AWS). |

---

## 3. TỔNG HỢP KẾT QUẢ ĐẠT ĐƯỢC TRONG TUẦN 1

1. **Khối lượng giờ làm việc:**
   - Nguyễn Tiến Sơn (24110054): **9.5 giờ** (vượt chỉ tiêu $\ge 8$ giờ/tuần).
   - Trần Thị Ngọc Quyên (24110051): **9.0 giờ** (vượt chỉ tiêu $\ge 8$ giờ/tuần).
   - Tổng thời gian làm việc nhóm Tuần 1: **18.5 giờ** (vượt chỉ tiêu $\ge 16$ giờ/tuần).
2. **Sản phẩm kỹ thuật bàn giao:**
   - S3 Bucket được khởi tạo an toàn, cấu hình mã hóa SSE-S3 và gắn tag đầy đủ trên Region `us-east-1`.
   - Secret `weather/api_config` lưu trữ JSON thông số cấu hình mã hóa KMS trên Secrets Manager.
   - Sơ đồ kiến trúc hệ thống chuẩn hóa định dạng SVG và PNG chất lượng cao.
   - Báo cáo kỹ thuật Tuần 1 gồm 20 trang vật lý hoàn chỉnh, mục lục tự động và liên kết GitHub chính thức.

---

## 4. MINH BẠCH VÀ CÔNG KHAI MỨC ĐỘ HỖ TRỢ CỦA TRÍ TUỆ NHÂN TẠO (AI DISCLOSURE)

Tuân thủ nghiêm túc chỉ đạo của GVHD ThS. Huỳnh Xuân Phụng: *"Được dùng LLM/AI (ChatGPT, Claude, Amazon Q Developer...) để tham khảo, sinh mã, gỡ lỗi; nhưng mọi tài nguyên phải được triển khai và chạy thật trên AWS Learner Lab. Ghi rõ phần nào có AI hỗ trợ; SV phải giải thích được mọi cấu hình/mã nguồn khi vấn đáp."*

### 4.1 Phần có sự hỗ trợ của AI:
- **Gợi ý cú pháp AWS CLI & PowerShell:** Sử dụng Claude/ChatGPT hỗ trợ tra cứu các tham số lệnh `aws s3api put-bucket-tagging` và `aws secretsmanager create-secret` đảm bảo đúng cú pháp CLI trên Windows PowerShell.
- **Tham khảo cấu trúc sơ đồ khối:** Sử dụng AI để gợi ý cách bố trí các khối dịch vụ Serverless theo đúng chuẩn AWS Architecture Guidelines.
- **Biên tập văn bản:** Hỗ trợ định dạng bảng biểu Markdown và soát lỗi chính tả kỹ thuật.

### 4.2 Phần sinh viên tự chủ 100% và chuẩn bị vấn đáp:
- **Hiểu rõ kiến trúc hệ thống:** Hai sinh viên nắm vững nguyên lý hoạt động của kiến trúc Serverless Event-Driven, lý do tách biệt cấu hình nhạy cảm sang Secrets Manager và cách tổ chức phân vùng Hive-style trên S3 Data Lake.
- **Trực tiếp vận hành tài khoản AWS:** Tự thực hiện toàn bộ thao tác cấu hình, chạy lệnh AWS CLI trên tài khoản AWS Learner Lab của từng thành viên (`873674852386` và `134987931868`).
- **Tuân thủ quy chế an toàn tài nguyên:** Nắm vững giới hạn ngân sách $100, quy định chỉ sử dụng `LabRole` và cam kết dọn dẹp tài nguyên sau mỗi buổi thực hành.

---

*Xác nhận của các thành viên Nhóm 05:*
- **Trưởng nhóm:** Nguyễn Tiến Sơn (MSSV: 24110054) - *Đã ký xác nhận*
- **Thành viên:** Trần Thị Ngọc Quyên (MSSV: 24110051) - *Đã ký xác nhận*
