# Nhật ký kỹ thuật mốc tích hợp 18/10/2026

Tài liệu ghi đầu việc và sản phẩm đã lưu. Phân công tiếp nối [bảng thành phần](../../docs/components.md). Chưa có xác nhận giờ làm Tuần 3 của từng sinh viên; không suy số giờ từ commit, thời gian chạy chương trình hoặc thời gian của tác vụ tự động.

| Mã | Phụ trách theo kế hoạch | Sản phẩm tại mốc tích hợp |
| --- | --- | --- |
| W3-01 | Sinh viên Tiến Sơn | Snapshot trạng thái/hash của hai Lambda; chương trình đóng gói và cập nhật có kiểm tra tài khoản/RevisionId/khôi phục |
| W3-02 | Sinh viên Tiến Sơn | Snapshot lịch chuẩn và target; dẫn lại hai lượt theo lịch đã có xác nhận email ngày 16/10; độ phủ vận hành dài ngày còn theo dõi |
| W3-03 | Sinh viên Ngọc Quyên | Sáu bảng thử nghiệm trong hai môi trường, 18 truy vấn, CSV số đo và biểu đồ Parquet/Projection |
| W3-04 | Sinh viên Ngọc Quyên | Raw 237/273 dòng, CSV kiểm tra chất lượng và thống kê đô thị–giờ |
| W3-05 | Sinh viên Tiến Sơn | Hai Dashboard riêng; cấu hình JSON, 381 dòng metric và 10 ảnh AWS |
| W3-06 | Sinh viên Tiến Sơn | Giữ kênh email; đối chiếu minh chứng nhận thư của hai sinh viên đã xác nhận, không mở SMS/Webhook |
| W3-07 | Sinh viên Ngọc Quyên | 519 dòng lịch sử mô hình, 18 bộ sai số, 432 dòng đánh giá và 144 dòng dự báo chưa đánh giá tương lai |
| W3-08 | Cả hai sinh viên | CI kiểm tra hồ sơ/dữ liệu và tạo artifact; workflow CD thủ công có xác nhận môi trường; README và báo cáo mốc tích hợp |

Các dòng trên ghi phạm vi phụ trách, không chứng minh ai tự viết từng dòng mã. Kết quả kiểm tra và triển khai thật được ghi trong [hướng dẫn vận hành](operation.md); dữ liệu và phép đo nằm trong [manifest](../results/integration_2026_10_18/manifest.json).

Mốc bổ sung ngày 18/10 lưu thêm [431 dòng metric và Dashboard có kiểm tra bộ đếm](../results/monitoring_2026_10_18/), cùng [hai lượt CD và biên bản xóa secrets tạm](../results/cd_2026_10_18/). Hai cửa sổ metric có thời gian chồng lên nhau, không cộng số dòng thành số quan sát độc lập. Tổng Errors vượt Invocations vẫn là điểm chưa giải thích được; hồ sơ không tính tỷ lệ lỗi cho cửa sổ đó. Bộ kiểm tra Tuần 3 hiện có 19 trường hợp hồi quy.

Đợt đối chiếu tiếp theo bổ sung [Metric Filters và hồ sơ log–S3](../results/operations_2026_10_18/), sửa định dạng JSON cấu hình của sinh viên Ngọc Quyên và thay baseline snapshot bằng hồ sơ CD công khai. Lượt 13:15 của sinh viên Tiến Sơn có ba bản ghi đúng theo log và đã tạo một điểm metric log mới; sinh viên Ngọc Quyên còn chờ lượt sau tạo filter/sửa cấu hình. Bộ hồi quy sau bổ sung có 29 trường hợp. Không phát sinh số giờ worklog được tự suy đoán từ các thao tác này.

Đối chiếu thời gian dự báo phát hiện sáu dòng của bản đầu có giờ đích trước lúc lấy nguồn. Bản sửa ghi thời điểm phát hành, bắc cầu các giờ chưa quan sát bằng dự báo đệ quy và chỉ xuất 24 giờ đích sau phát hành; [mốc mới](../results/forecast_issued_2026_10_18/) có 144 dòng được kiểm tra lại. Ba hồi quy thời gian mới nâng tổng số trường hợp lên 32; chưa ghi độ chính xác tương lai khi chưa có dữ liệu đích.

**Cần bổ sung khi kết thúc tuần:** ngày làm, công việc thực tế, số giờ được từng sinh viên xác nhận và các lượt chạy trong lịch 19–25/10/2026. Nhật ký [Tuần 1–2](../../docs/WORKLOG.md) giữ tổng 38,0 giờ đã xác nhận.
