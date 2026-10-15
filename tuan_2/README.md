# Tuần 2 Hai bộ báo cáo dữ liệu của nhóm

Sinh viên thực hiện: Nguyễn Tiến Sơn (24110054) và Trần Thị Ngọc Quyên (24110051). Lớp 261CLCO332779_05, học phần Điện toán đám mây. GVHD ThS. Huỳnh Xuân Phụng.

- [Báo cáo Word](docs/Bao_cao_Tuan_2_24110054_24110051.docx) · [PDF](docs/Bao_cao_Tuan_2_24110054_24110051.pdf)
- [Excel phân tích](docs/Du_lieu_phan_tich_Tuan_2_24110054_24110051.xlsx)
- [CSV Athena mới](results/week2_live/) · [CSV phân tích](results/week2_analysis/)
- [Biểu đồ](results/week2_charts/) · [Dữ liệu raw và metadata](results/week2_evidence/)
- [Nhật ký](docs/WORKLOG.md)
- [Hướng dẫn đọc mã nguồn](../docs/source-guide.md)

Bộ dữ liệu đã lưu của sinh viên Tiến Sơn có 204 bản ghi, trong đó 27 lượt ghi thuộc Tuần 2. Bộ của sinh viên Ngọc Quyên có 231 bản ghi, trong đó 57 lượt ghi thuộc Tuần 2. Khi [tổng hợp theo đô thị và giờ UTC](results/week2_analysis/hourly_city.csv), mỗi sinh viên có 27 nhóm, gồm 21 nhóm cùng giờ để đối chiếu. Bộ của sinh viên Ngọc Quyên có 24 nhóm ghi hai lượt và ba nhóm ghi ba lượt; các chỉ số môi trường trong cùng nhóm bằng nhau. Các lượt ghi gốc được giữ đầy đủ trong CSV và phụ lục. Mẫu Tuần 2 của mỗi sinh viên bao phủ hai ngày, gồm chín giờ có dữ liệu.

Mục 3.12 trong báo cáo đối chiếu AQI và PM2.5 với đúng bộ 156 bản ghi của báo cáo Tuần 1 đã lưu. Phép lọc hai tuần từ lần xuất mới được trình bày riêng, vì cỡ mẫu Tuần 1 khi lọc lại là 42/41 mỗi đô thị. Excel có sheet So_sanh_tuan và hai CSV riêng cho hai phạm vi này.

Phương pháp và cách tái lập được trình bày trong [tổng quan dự án](../README.md) và [tài liệu dữ liệu](../docs/data-analysis.md). Xem [sơ đồ mã nguồn](../docs/repository-layout.md), [thứ tự dùng SQL](athena/README.md) và [danh mục dữ liệu](results/README.md) để tra cứu từng thành phần.
