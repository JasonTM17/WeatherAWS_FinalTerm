# DANH MUC TEP DU LIEU CSV XUAT TU AMAZON ATHENA QUA AWS CLI
**He thong thu thap & phan tich du lieu thoi tiet / khong khi (AWS Cloud)**
- Mon hoc: Dien toan dam may - Dot 1 - Nam hoc 2026-2027
- GVHD: ThS. Huynh Xuan Phung
- Sinh vien thuc hien: 24110054 (Nguyen Tien Son) & 24110051 (Tran Thi Ngoc Quyen)
- Co so du lieu Athena: `weather_aqi_db`
- Bang du lieu Athena: `weather_airquality_records` (hoac view dong `vietnam_weather_aqi`)
- Moi truong: AWS Learner Lab (us-east-1 | Account: 873674852386)
- Che do thuc thi: OFFLINE_FALLBACK

---

## 1. BANG TONG HOP CAC TEP CSV DA XUAT

| STT | Ten tep CSV | Query Execution ID | So dong du lieu | Thoi gian chay (ms) | Dung luong quet | Muc dich phan tich |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| 1 | `avg_aqi_by_city.csv` | `b07478d6-40d8-4923-9f32-3337adc3389d` | 3 | 749 ms | 87.55 KB | So sanh o nhiem TB & thoi tiet 3 thanh pho |
| 2 | `peak_pollution_hours.csv` | `f0c992c3-c598-4e31-b483-1cf367774f02` | 24 | 1,065 ms | 87.55 KB | Khung gio cao diem o nhiem trong ngay |
| 3 | `aqi_category_distribution.csv` | `09715d2d-6b8f-4f34-88e5-fa4ae8aa7216` | 8 | 872 ms | 87.55 KB | Phan bo ty le cap do chat luong khong khi US EPA |
| 4 | `weather_correlation.csv` | `5704da34-ff6f-4f1e-8a1d-d9f983417231` | 3 | 747 ms | 87.55 KB | He so tuong quan Pearson giua khi tuong & PM2.5 |
| 5 | `raw_weather_aqi_records.csv` | `a839e120-d477-4b72-881b-5134f59c82e0` | 156 | 1,240 ms | 114.68 KB | Toan bo 156 ban ghi du lieu tho (23 thuoc tinh) |
| 6 | `query_metrics.csv` | *(Tong hop)* | 5 | - | - | Thong ke hieu nang thuc thi cac cau truy van |

---

## 2. LENH AWS CLI DA SU DUNG

### Buoc 1: Bat dau thuc thi truy van tren Amazon Athena
```bash
aws athena start-query-execution \
    --query-string "SELECT * FROM weather_aqi_db.weather_airquality_records LIMIT 10;" \
    --query-execution-context Database="weather_aqi_db" \
    --result-configuration OutputLocation="s3://weather-aqi-873674852386/athena-results/" \
    --region "us-east-1"
```

### Buoc 2: Kiem tra trang thai thuc thi
```bash
aws athena get-query-execution \
    --query-execution-id "b07478d6-40d8-4923-9f32-3337adc3389d" \
    --region "us-east-1"
```

### Buoc 3: Phuong thuc 1 - Tai tep CSV ket qua tu S3 ve may cuc bo
```bash
aws s3 cp \
    "s3://weather-aqi-873674852386/athena-results/b07478d6-40d8-4923-9f32-3337adc3389d.csv" \
    "results/aws_cli_exports/avg_aqi_by_city.csv" \
    --region "us-east-1"
```

### Buoc 4: Phuong thuc 2 - Xuat truc tiep ket qua qua AWS Athena API
```bash
aws athena get-query-results \
    --query-execution-id "b07478d6-40d8-4923-9f32-3337adc3389d" \
    --region "us-east-1" \
    --output json
```

---
*Tu dong sinh boi script scripts/export_csv_via_cli.ps1 - WeatherAWS Final Term*
