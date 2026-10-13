---
status: in-progress
---
# Hoàn thiện báo cáo Tuần 1 Tuần 2 và source

## Outcome Contract
Hai báo cáo Word/PDF giữ mẫu bìa, tên sinh viên và bố cục học thuật, có mục lục cập nhật được, bảng/hình rõ và không nhắc AWS CLI hoặc chứa lệnh AWS. Bộ source thao tác AWS bằng Python SDK, giữ các chức năng triển khai, truy vấn, xuất dữ liệu, xác minh và thu hồi tài nguyên. Bộ nộp chứa hai tuần và source dùng được.

## Authority and scope
User xác nhận chỉnh cả báo cáo và source, bỏ code AWS CLI; sau đó yêu cầu điền GitHub About và tài liệu GitHub. Cho phép cập nhật About và xuất bản README/tài liệu/source/báo cáo liên quan sau kiểm tra. Không triển khai/xóa tài nguyên AWS. Giữ số liệu theo nguồn hiện có; không tự tạo số giờ, kết quả live, chi phí hay dữ liệu. Phân công đã xác nhận: Sơn S3/Secrets/Lambda/SNS; Quyên Glue/Athena/biểu đồ/kiểm tra; cùng kiến trúc/tích hợp/báo cáo.

## Evidence and assumptions
Project hiện tách tuan_1 và tuan_2; git sạch lúc bắt đầu. Word Tuần 2 có nhiều lệnh AWS và định dạng nhỏ; source PowerShell gọi chương trình aws. Registry .codex/skills và global ak-document-skills không có, dùng kỹ năng Documents/PDF hiện cài.

## Ordered steps
1. Đọc nguồn, đo các lệch dữ liệu/bố cục, giữ snapshot hồi phục trong thư mục work bị ignore. Exit: xác định được nguồn số liệu và phạm vi sửa.
2. Thay thao tác AWS bằng boto3, giữ wrapper PowerShell; bỏ fallback giả thực thi, sửa tài liệu source và kiểm thử liên quan. Exit: không gọi aws executable, kiểm thử SDK lỗi/timeout/pagination và source tests pass.
3. Sửa hai Word theo mẫu, thay lệnh bằng mô tả/cấu hình, đối chiếu bảng/hình và bỏ tuyên bố không có bằng chứng. Exit: hai DOCX có heading/TOC/caption/format nhất quán và dữ liệu khớp nguồn.
4. Cập nhật TOC và xuất PDF; render xem từng trang, sửa lỗi quan sát; đóng gói bộ nộp và source. Exit: toàn bộ trang đạt visual QA, liên kết TOC đúng, no AWS CLI/code, package integrity pass.
5. Cập nhật GitHub About và docs. Exit: README/docs có liên kết hợp lệ, diff/secret check đạt, remote commit và About được đọc lại xác nhận.

## Verification checkpoints
- Baseline: kiểm tra bảng Word so với CSV và schema/raw summary consistency; không chạy mạng.
- SDK: unittest discover -s tuan_2/tests -v; syntax/PowerShell parser; stub negative query failure/timeout and pagination; không live AWS.
- Documents: python-docx/OOXML no CLI and table checks, Word COM cập nhật TOC/export; packaged render attempt, nếu không có bundled LibreOffice dùng Word COM PDF + pypdfium2.
- Terminal: inspect every rendered page, PDF TOC links and headings, package ZIP/list/hash; git diff --check.
- Rerun chỉ checkpoint bị thay đổi hoặc lỗi. Broadening chỉ khi phát hiện lỗi cụ thể.

## Risk and recovery
Giữ bản gốc DOCX/PDF và scripts trong docs/_report_work của tuần trước khi sửa. SDK chưa chạy live nên không tuyên bố đã triển khai phiên bản mới. Không đóng các Word/Excel của người dùng. Thu hồi tài nguyên chỉ là chức năng source có xác nhận account.

## Documentation and release impact
Cập nhật README và mô tả source theo Python SDK; xuất bản thay đổi đã kiểm tra lên remote hiện có, không rewrite lịch sử Git. Bộ nộp final ở Downloads, không có work scripts/caches/credentials.

## Blockers
Không có blocker hiện tại. Số giờ/ngày làm việc và tuyên bố chi phí/live không được lấy bản nháp làm bằng chứng; giữ nội dung có căn cứ hoặc trình bày điều kiện/giới hạn thích hợp.

## Completion evidence
- Hai báo cáo: Tuần 1 20 trang/28 liên kết TOC; Tuần 2 24 trang/39 liên kết TOC. Từng trang đã được xem, lỗi quan sát được sửa; liên kết GitHub thật trong Word và PDF.
- `reports/final-audit.json`: 156 bản ghi/23 trường; mọi bảng phân tích được đối chiếu với CSV, bốn ảnh khớp Word hai tuần/Excel/source, 42 liên kết tài liệu local tồn tại.
- Source: 40 ca cục bộ đạt; 22 acceptance checks đạt sau sửa mục thiếu Open-Meteo (21 đạt ở suite và ca bị lỗi đạt khi chạy lại). 13 PowerShell parse đạt; 16 Python syntax đạt; `git diff --check` và credential scan đạt. Không chạy AWS live.
- Bộ nộp 12 tệp, source ZIP 104 tệp; kiểm tra byte/hash và integrity đạt. Chỉ còn một bộ nộp Tuần 1–2 trong Downloads, bản cũ được giữ trong work backup.
- GitHub About có description/homepage/12 topics; commit `beb5817079939be06121c9d02f8c1088a973c7d3` được push lên main, remote SHA và blob README/docs đọc lại khớp local. GitHub check-runs hiện bằng 0; không tuyên bố CI đã chạy.

## User-authorized revision
User yêu cầu bỏ nội dung ảnh gồm mục 7.3/7.4 của Tuần 2, thay dấu chấm đầu dòng bằng dấu gạch trong cả hai báo cáo và rà source để sửa lỗi/dọn phần dư. Xử lý theo `phase-02-revision.md`; không chạy dịch vụ AWS. Các nguồn dữ liệu và bốn biểu đồ giữ nguyên.

Revision complete: 20/23 pages; 28/37 linked TOC entries; native dash lists; removed requested sections. 44 offline unit cases PASS and affected acceptance gate PASS. Duplicate assets/dependencies removed, 92-file source ZIP and all 12 final Downloads hashes verified. Commit 79a83ee002b2798c5410ba05c3df4bcc1ccd6419 pushed and remote SHA read back equal. No live AWS claim.

## Full report audit requested by user
Audit both reports and their Downloads copies under phase-03-report-audit.md. Correct source-version wording in Week 1, add missing Week 2 hourly numeric table, clarify that Week 2 analysis reuses the saved Week 1 snapshot. Preserve removed sections, dash lists, fonts, chart/data identities and no AWS CLI. Teacher rubric is contextual evidence, not authority to reinsert content the user removed or invent hours/API keys/live results.
