"""
Generate the master comprehensive study & exam defense Word document (DOCX),
complete with HCMUTE cover page, Table of Contents, 5 in-depth chapters,
rich code blocks, styled tables, 6 embedded real figures/diagrams, and 20 Q&A pairs.
Copies directly to C:\\Users\\Admin\\Downloads.
"""
import os
import shutil
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output"
DOWNLOADS_DIR = Path(os.path.expanduser("~/Downloads"))

DEST_OUTPUT = OUT_DIR / "Bao_cao_hoc_tap_WeatherAWS_SQL_va_CSV.docx"
DEST_DOWNLOADS_1 = DOWNLOADS_DIR / "Bao_cao_hoc_tap_WeatherAWS_SQL_va_CSV.docx"
DEST_DOWNLOADS_2 = DOWNLOADS_DIR / "De_cuong_hoc_tap_va_van_dap_WeatherAWS_HCMUTE.docx"

# Color Palette
COLOR_NAVY = RGBColor(26, 54, 93)       # #1A365D - Heading 1 & Titles
COLOR_BLUE = RGBColor(43, 108, 176)     # #2B6CB0 - Heading 2 & Table Headers
COLOR_DARK_GRAY = RGBColor(45, 55, 72)  # #2D3748 - Heading 3 & Body Dark
COLOR_MUTED = RGBColor(113, 128, 150)   # #718096 - Captions & Subtitles
COLOR_PURPLE = RGBColor(155, 44, 44)    # Warning / Important notes

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E0"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="{color}"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(22)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_BLUE
    return h

def add_heading_3(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(2)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = COLOR_DARK_GRAY
    return h

def add_body_p(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK_GRAY
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_DARK_GRAY
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK_GRAY
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_DARK_GRAY
    return p

def add_callout_box(doc, text, title="LƯU Ý QUAN TRỌNG:"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "FEFCBF") # Yellow warning tint
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="D69E2E"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    r_title = p.add_run(f"📌 {title} ")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(10)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(146, 64, 14)
    
    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = RGBColor(116, 66, 16)
    
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def add_code_snippet(doc, code_str, language="SQL"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F7FAFC")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="2B6CB0"/><w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(9.0)
    run.font.color.rgb = COLOR_DARK_GRAY
    
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def add_table_data(doc, headers, rows):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, "CBD5E0")
    
    # Header
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        set_cell_background(cell, "2B6CB0")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h_text)
        run.font.name = "Arial"
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    # Rows
    for r_idx, row_vals in enumerate(rows):
        bg = "FFFFFF" if r_idx % 2 == 0 else "F7FAFC"
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(val))
            run.font.name = "Arial"
            run.font.size = Pt(9.0)
            run.font.color.rgb = COLOR_DARK_GRAY
            
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(6)

def add_image_figure(doc, img_path, caption, width_in=6.0):
    if not os.path.exists(img_path):
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(img_path), width=Inches(width_in))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Arial"
    r_cap.font.size = Pt(9.0)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

def build_cover_page(doc):
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(0)
    p_top.paragraph_format.space_after = Pt(2)
    r = p_top.add_run("TRƯỜNG ĐẠI HỌC SƯ PHẠM KỸ THUẬT TP. HỒ CHÍ MINH (HCMUTE)\n")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY
    
    r2 = p_top.add_run("KHOA CÔNG NGHỆ THÔNG TIN • BỘ MÔN ĐIỆN TOÁN ĐÁM MÂY\n")
    r2.font.name = "Arial"
    r2.font.size = Pt(11)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_BLUE
    
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(2)
    p_line.paragraph_format.space_after = Pt(36)
    r_line = p_line.add_run("―" * 35)
    r_line.font.color.rgb = RGBColor(203, 213, 224)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(10)
    r_t = p_title.add_run("BÁO CÁO HỌC TẬP VÀ ĐỀ CƯƠNG VẤN ĐÁP ĐỒ ÁN")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(20)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("HỆ THỐNG THU THẬP, XỬ LÝ VÀ PHÂN TÍCH DỮ LIỆU THỜI TIẾT & CHẤT LƯỢNG KHÔNG KHÍ TRÊN NỀN TẢNG SERVERLESS AWS (WEATHERAWS)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_BLUE
    
    # Meta box
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, "E2E8F0")
    
    meta_info = [
        ("Giảng viên hướng dẫn:", "ThS. Huỳnh Xuân Phụng"),
        ("Sinh viên thực hiện 1:", "Nguyễn Tiến Sơn — MSSV: 24110054 (Account: 873674852386)"),
        ("Sinh viên thực hiện 2:", "Trần Thị Ngọc Quyên — MSSV: 24110051 (Account: 134987931868)"),
        ("Học phần / Lớp học:", "Điện toán đám mây • Lớp: 261CLCO332779_05"),
        ("Thời gian thực hiện:", "Tháng 10 năm 2026 (Hoàn tất 4/4 tuần - 78,0 giờ công xác nhận)"),
        ("Kho lưu trữ GitHub:", "https://github.com/JasonTM17/WeatherAWS_FinalTerm.git")
    ]
    
    for idx, (label, val) in enumerate(meta_info):
        c1, c2 = table.cell(idx, 0), table.cell(idx, 1)
        set_cell_background(c1, "F7FAFC")
        set_cell_background(c2, "FFFFFF")
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(label)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_NAVY
        
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(val)
        r2.font.name = "Arial"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_DARK_GRAY
        if "github" in val:
            r2.font.bold = True
            r2.font.color.rgb = COLOR_BLUE
            
    p_bot = doc.add_paragraph()
    p_bot.paragraph_format.space_before = Pt(40)
    p_bot.paragraph_format.space_after = Pt(0)
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bot = p_bot.add_run("TP. HỒ CHÍ MINH — THÁNG 10/2026")
    r_bot.font.name = "Arial"
    r_bot.font.size = Pt(10)
    r_bot.font.bold = True
    r_bot.font.color.rgb = COLOR_MUTED
    
    doc.add_page_break()

def build_content(doc):
    # TOC Overview
    add_heading_1(doc, "MỤC LỤC TỔNG QUAN BÁO CÁO")
    toc_items = [
        "CHƯƠNG 1: TỔNG QUAN TOÀN DIỆN DỰ ÁN WEATHERAWS",
        "  1.1. Bối cảnh đề tài và bài toán xử lý dữ liệu môi trường",
        "  1.2. Kiến trúc giải pháp AWS Serverless 5 tầng (EventBridge -> Lambda -> S3 -> Athena)",
        "  1.3. Bảng phân nhiệm và vai trò chi tiết của 10 dịch vụ AWS cốt lõi",
        "  1.4. Vòng đời dữ liệu của một bản ghi khí tượng (Data Pipeline Flow)",
        "  1.5. Tổng kết kết quả triển khai toàn diện qua 4 tuần",
        "CHƯƠNG 2: CHUYÊN SÂU VỀ SQL VÀ CƠ CHẾ TRUY VẤN TRÊN AMAZON ATHENA",
        "  2.1. Bản chất kiến trúc Athena: Presto/Trino distributed SQL engine",
        "  2.2. Phân tích DDL External Table, SerDe JSON và thuộc tính phòng vệ",
        "  2.3. Tại sao phải phân tách giữa External Table vật lý và Athena View logic",
        "  2.4. Kỹ thuật Phân vùng (Partitioning) & Partition Pruning tối ưu hóa I/O",
        "  2.5. Kỹ thuật nâng cao: Partition Projection (Tự động hóa không cần Glue Crawler)",
        "  2.6. Tối ưu hóa Columnar: Kỹ thuật CTAS và định dạng Parquet Snappy",
        "  2.7. 10 Bẫy cú pháp và lưu ý sống còn khi viết SQL trong Amazon Athena",
        "  2.8. Phân tích chi tiết 4 câu truy vấn SQL phân tích nghiệp vụ trong đồ án",
        "CHƯƠNG 3: HƯỚNG DẪN CHI TIẾT QUY TRÌNH TRÍCH XUẤT CÁC BẢN CSV",
        "  3.1. Phương pháp 1: Trích xuất CSV tự động qua AWS CLI (3 bước chuẩn)",
        "  3.2. Phương pháp 2: Trích xuất CSV qua Python Boto3 SDK (AthenaExporter)",
        "  3.3. Phân loại và cấu trúc của 384 tệp CSV trong repository đồ án",
        "  3.4. Cơ chế sao lưu và tái lập kết quả Ngoại tuyến (Offline Mode)",
        "CHƯƠNG 4: QUẢN TRỊ VẬN HÀNH, AN NINH BẢO MẬT VÀ TÀI CHÍNH FINOPS",
        "  4.1. Đối chiếu 3 chiều Log – Metric – S3 Data Lake",
        "  4.2. Rà soát an ninh bảo mật 11 tiêu chuẩn (Security Audit)",
        "  4.3. Quản trị tài chính đám mây FinOps với AWS Cost Explorer (117 dòng đối soát)",
        "  4.4. Tự động hóa quản lý vòng đời tài nguyên và bảo toàn credit phiên Lab",
        "CHƯƠNG 5: NGÂN HÀNG 20 CÂU HỎI VẤN ĐÁP PHẢN BIỆN VÀ CÂU TRẢ LỜI MẪU",
        "  Bộ 20 câu hỏi trọng tâm thường gặp nhất của Giảng viên chấm thi và hướng trả lời xuất sắc."
    ]
    for item in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(item)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        if item.startswith("CHƯƠNG"):
            r.font.bold = True
            r.font.color.rgb = COLOR_NAVY
        else:
            r.font.color.rgb = COLOR_DARK_GRAY
            
    doc.add_page_break()

    # ==========================================
    # CHƯƠNG 1
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 1: TỔNG QUAN TOÀN DIỆN DỰ ÁN WEATHERAWS")
    
    add_heading_2(doc, "1.1. Bối cảnh đề tài và bài toán xử lý dữ liệu môi trường")
    add_body_p(doc, "Ô nhiễm không khí và biến đổi khí hậu đang là một trong những thách thức đô thị hàng đầu tại Việt Nam. Hai đô thị đặc biệt là TP. Hồ Chí Minh và Hà Nội cùng với trung tâm kinh tế - du lịch miền Trung là TP. Đà Nẵng thường xuyên ghi nhận các đợt nồng độ bụi mịn PM2.5 vượt ngưỡng cảnh báo của Tổ chức Y tế Thế giới (WHO).")
    add_body_p(doc, "Đề tài WeatherAWS giải quyết bài toán xây dựng đường ống dữ liệu (Data Pipeline) theo kiến trúc không máy chủ (Serverless Architecture) trên nền tảng điện toán đám mây Amazon Web Services (AWS) nhằm: thu thập dữ liệu thời tiết và chất lượng không khí theo chu kỳ 1 giờ/lần từ API nguồn Open-Meteo, chuẩn hóa lưu trữ vào S3 Data Lake, thực hiện phân tích tương tác bằng SQL trên Amazon Athena, đồng thời phát cảnh báo tự động qua email khi chỉ số AQI vượt ngưỡng nguy hại.")

    add_heading_2(doc, "1.2. Kiến trúc giải pháp AWS Serverless 5 tầng")
    add_body_p(doc, "Hệ thống được thiết kế theo mô hình kiến trúc hướng sự kiện (Event-Driven Architecture) gồm 5 tầng phân tách rõ ràng:")
    add_bullet_p(doc, "Amazon EventBridge Rule với biểu thức lịch rate(1 hour) đóng vai trò bộ định thời phát sự kiện định kỳ.", "Tầng 1 - Kích hoạt (Scheduling): ");
    add_bullet_p(doc, "Hàm AWS Lambda (Python 3.12, 256 MB RAM, timeout 60s) đóng vai trò trung tâm xử lý, gọi API, chuẩn hóa 23 trường chỉ số và ghi dữ liệu.", "Tầng 2 - Xử lý (Compute): ");
    add_bullet_p(doc, "Amazon S3 Bucket được bảo vệ bởi Block Public Access (4/4), mã hóa mặc định AES256, tổ chức theo phân vùng Hive raw/year=YYYY/month=MM/day=DD/.", "Tầng 3 - Lưu trữ Hồ dữ liệu (Storage / Data Lake): ");
    add_bullet_p(doc, "AWS Glue Data Catalog lưu lược đồ bảng metadata và Amazon Athena thực thi câu lệnh SQL phân tán (Presto engine), xuất kết quả ra CSV.", "Tầng 4 - Phân tích & Trích xuất (Analytics & Query): ");
    add_bullet_p(doc, "Amazon CloudWatch (Logs, Metric Filters, Dashboard, Alarm) theo dõi vận hành; Amazon SNS phân phối cảnh báo email; CloudFormation IaC quản lý 17 tài nguyên; AWS Cost Explorer phân rã chi phí FinOps.", "Tầng 5 - Giám sát, Cảnh báo & Quản trị (Governance & Ops): ");

    # Embed Architecture Diagram
    arch_img = ROOT / "output/study-handbook-code-2026-10-23/architecture-study.png"
    if arch_img.exists():
        add_image_figure(doc, arch_img, "Hình 1.1: Sơ đồ Kiến trúc Tổng thể 5 tầng Serverless của Dự án WeatherAWS trên nền tảng AWS", width_in=6.2)

    add_heading_2(doc, "1.3. Bảng phân nhiệm và vai trò chi tiết của 10 dịch vụ AWS cốt lõi")
    svc_headers = ["Dịch vụ AWS", "Phân loại", "Vai trò cụ thể trong Dự án WeatherAWS"]
    svc_rows = [
        ["Amazon EventBridge", "Serverless Scheduler", "Kích hoạt Lambda định kỳ mỗi 1 giờ mà không cần máy chủ cron."],
        ["AWS Lambda", "Serverless Compute", "Thu thập dữ liệu Open-Meteo, trích xuất 23 chỉ số, ghi S3 và kích hoạt SNS."],
        ["AWS Secrets Manager", "Security & Config", "Lưu URL API và cấu hình Open-Meteo, cô lập tuyệt đối khỏi mã nguồn Git."],
        ["Amazon S3", "Object Data Lake", "Lưu trữ tệp NDJSON thô, lưu trữ kết quả truy vấn Athena và artifact ZIP."],
        ["Amazon SNS", "Pub/Sub Messaging", "Phân phối thông báo đẩy qua email khi AQI vượt ngưỡng hoặc hệ thống lỗi."],
        ["AWS Glue Catalog", "Metadata Catalog", "Quản lý siêu dữ liệu bảng weather_airquality_records (20 cột dữ liệu + 3 cột phân vùng)."],
        ["Amazon Athena", "Serverless SQL", "Thực thi truy vấn SQL phân tán trên S3, tính toán thống kê và trích xuất CSV."],
        ["Amazon CloudWatch", "Observability", "Lưu log thực thi, đếm Metric Filters, vẽ Dashboard và kích hoạt Alarm."],
        ["AWS CloudFormation", "IaC Automation", "Khai báo toàn bộ 17 tài nguyên trong 1 template JSON, triển khai tự động."],
        ["AWS Cost Explorer", "FinOps Management", "Giám sát chi phí tài khoản theo ngày và dịch vụ qua API GetCostAndUsage."]
    ]
    add_table_data(doc, svc_headers, svc_rows)

    add_heading_2(doc, "1.4. Vòng đời dữ liệu của một bản ghi khí tượng (Data Pipeline Flow)")
    add_body_p(doc, "Mỗi giờ một lần, một bản ghi dữ liệu trải qua 8 bước xử lý khép kín:")
    add_bullet_p(doc, "1. EventBridge Rule bắn tín hiệu sự kiện theo lịch tới Lambda.")
    add_bullet_p(doc, "2. Lambda gọi Secrets Manager lấy cấu hình weather/api_config.")
    add_bullet_p(doc, "3. Lambda gọi 2 HTTP request đồng thời tới Open-Meteo (1 thời tiết + 1 AQI cho mỗi thành phố).")
    add_bullet_p(doc, "4. Lambda chuẩn hóa 23 trường dữ liệu, tạo record_id duy nhất (UUIDv4) và cặp timestamp_utc / timestamp_vn.")
    add_bullet_p(doc, "5. Lambda gộp thành dòng NDJSON và ghi vào đường dẫn S3: raw/year=YYYY/month=MM/day=DD/data_*.json.")
    add_bullet_p(doc, "6. Nếu AQI >= 150 hoặc PM2.5 >= 55.4 µg/m³, Lambda gọi sns:Publish gửi email cảnh báo tức thời.")
    add_bullet_p(doc, "7. Lambda ghi dòng log chuẩn cấu trúc [INFO] Result: city=..., aqi=... vào CloudWatch Logs.")
    add_bullet_p(doc, "8. Athena truy vấn trực tiếp trên S3 để tổng hợp thống kê và xuất bảng CSV phục vụ nghiên cứu.")

    add_heading_2(doc, "1.5. Tổng kết kết quả triển khai toàn diện qua 4 tuần")
    add_body_p(doc, "Hệ thống đã trải qua 4 tuần hoàn thiện tuần tự, đáp ứng 100% yêu cầu đề cương môn học:")
    add_bullet_p(doc, "Khởi tạo nền tảng S3, IAM LabRole, Secrets Manager. Bộ 156 bản ghi mẫu đầu tiên.", "Tuần 1: ");
    add_bullet_p(doc, "Triển khai Lambda, EventBridge 1h/lần, SNS Alerting, Athena DDL/Views, xuất 27 bảng CSV và 4 biểu đồ.", "Tuần 2: ");
    add_bullet_p(doc, "CI/CD GitHub Actions, CloudWatch Dashboard, Benchmark Athena tối ưu I/O, Dự báo chuỗi thời gian Moving Average 24h và kiểm định sai số Holdout (MAE, RMSE).", "Tuần 3: ");
    add_bullet_p(doc, "CloudFormation 17 tài nguyên (CREATE_COMPLETE), đối chiếu 3 chiều Log–Metric–S3, Security Audit 11 controls, FinOps Cost Explorer 117 dòng, script dọn dẹp cuối phiên và kịch bản video demo dưới 10 phút.", "Tuần 4: ");

    doc.add_page_break()

    # ==========================================
    # CHƯƠNG 2
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 2: CHUYÊN SÂU VỀ SQL VÀ CƠ CHẾ TRUY VẤN TRÊN AMAZON ATHENA")
    
    add_heading_2(doc, "2.1. Bản chất kiến trúc Athena: Presto/Trino distributed SQL engine")
    add_body_p(doc, "Điểm cốt lõi cần khẳng định đầu tiên khi vấn đáp: Amazon Athena KHÔNG PHẢI là một hệ cơ sở dữ liệu quan hệ truyền thống (RDBMS) như MySQL hay SQL Server. Athena là một dịch vụ Interactive Query Serverless dựa trên công nghệ Presto/Trino mã nguồn mở.")
    add_body_p(doc, "Cơ chế hoạt động Schema-on-Read: Dữ liệu thực tế nằm nguyên bản dưới dạng file (JSON, CSV, Parquet) trên Amazon S3. Bảng trong Athena chỉ là siêu dữ liệu ánh xạ (Metadata) lưu trong Glue Catalog. Khi câu lệnh SELECT được kích hoạt, Athena tự động cấp phát tài nguyên tính toán phân tán, đọc các file S3, giải mã cú pháp theo SerDe, lọc dữ liệu và trả về kết quả.")

    add_heading_2(doc, "2.2. Phân tích DDL External Table, SerDe JSON và thuộc tính phòng vệ")
    add_body_p(doc, "Dưới đây là câu lệnh DDL cốt lõi khai báo bảng vật lý trong file tuan_2/athena/create_table.sql:")
    
    ddl_sql = """CREATE EXTERNAL TABLE IF NOT EXISTS weather_aqi_db.weather_airquality_records (
    record_id STRING,
    city STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    timestamp_utc STRING,
    timestamp_vn STRING,
    temperature_2m DOUBLE,
    relative_humidity_2m DOUBLE,
    surface_pressure DOUBLE,
    wind_speed_10m DOUBLE,
    pm2_5 DOUBLE,
    pm10 DOUBLE,
    carbon_monoxide DOUBLE,
    nitrogen_dioxide DOUBLE,
    sulphur_dioxide DOUBLE,
    ozone DOUBLE,
    us_aqi INT,
    aqi_category STRING,
    hour INT,
    collected_at STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
    'ignore.malformed.json' = 'true'
)
LOCATION 's3://weather-aqi-ACCOUNT_ID/raw/'
TBLPROPERTIES ('has_encrypted_data'='false');"""
    add_code_snippet(doc, ddl_sql, "SQL")

    add_body_p(doc, "Phân tích kỹ thuật chuyên sâu:", bold_prefix="Giải thích từng từ khóa DDL: ")
    add_bullet_p(doc, "Bắt buộc phải có trong Athena. Báo hiệu dữ liệu nằm ngoài Athena. Nếu DROP TABLE thì chỉ xóa metadata trong Glue, dữ liệu file JSON trên S3 hoàn toàn an toàn.", "Từ khóa EXTERNAL: ");
    add_bullet_p(doc, "Thư viện Serializer/Deserializer mã nguồn mở đọc từng dòng NDJSON và ánh xạ tên trường JSON vào các cột tương ứng.", "ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe': ");
    add_bullet_p(doc, "Cơ chế phòng vệ lỗi: nếu có 1 dòng JSON bị đứt đoạn hoặc hỏng cú pháp, SerDe sẽ bỏ qua dòng đó thay vì quăng lỗi làm sập toàn bộ câu truy vấn.", "ignore.malformed.json = 'true': ");
    add_bullet_p(doc, "Đường dẫn S3 gốc chứa dữ liệu thô. Athena sẽ quét đệ quy các phân vùng bên dưới.", "LOCATION 's3://.../raw/': ");

    add_heading_2(doc, "2.3. Tại sao phải phân tách giữa External Table vật lý và Athena View logic")
    add_body_p(doc, "Trong đồ án, nhóm tạo thêm View vietnam_weather_aqi đọc từ bảng weather_airquality_records:")
    view_sql = """CREATE OR REPLACE VIEW weather_aqi_db.vietnam_weather_aqi AS
SELECT record_id, city, latitude, longitude, timestamp_utc, timestamp_vn,
       temperature_2m, relative_humidity_2m, surface_pressure, wind_speed_10m,
       pm2_5, pm10, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone,
       us_aqi, aqi_category, hour, collected_at, year, month, day
FROM weather_aqi_db.weather_airquality_records;"""
    add_code_snippet(doc, view_sql, "SQL")
    add_callout_box(doc, "Phân tách tầng vật lý và logic (Data Abstraction): Bảng vật lý gắn liền với SerDe và vị trí file S3. Khi người dùng chỉ truy vấn qua View, nếu sau này người quản trị tối ưu hóa đổi định dạng S3 từ JSON sang Parquet hoặc chuyển sang bucket mới, chỉ cần cập nhật View mà toàn bộ các câu truy vấn của người dùng và Dashboard bên trên không hề bị ảnh hưởng!")

    add_heading_2(doc, "2.4. Kỹ thuật Phân vùng (Partitioning) & Partition Pruning tối ưu hóa I/O")
    add_body_p(doc, "Hồ dữ liệu được tổ chức theo quy ước Hive Partitioning: raw/year=YYYY/month=MM/day=DD/.")
    add_body_p(doc, "Cắt tỉa phân vùng (Partition Pruning): Khi câu truy vấn có điều kiện WHERE year = '2026' AND month = '10' AND day = '19', Athena đọc siêu dữ liệu và chỉ liệt kê duy nhất các file trong thư mục ngày 19/10/2026 để đọc, bỏ qua 100% dữ liệu của các ngày khác.")
    add_body_p(doc, "Hiệu quả thực tế đo đạc: Lượng byte quét (Data Scanned) giảm từ 75,28% đến 86,76% so với truy vấn toàn bảng. Vì Athena tính phí 5 USD / 1 TB dữ liệu quét, kỹ thuật này trực tiếp tiết kiệm tiền cho dự án.")

    add_heading_2(doc, "2.5. Kỹ thuật nâng cao: Partition Projection (Tự động hóa không cần Glue Crawler)")
    add_body_p(doc, "Trong phân vùng truyền thống, mỗi khi có dữ liệu ngày mới ghi vào S3, người dùng phải chạy MSCK REPAIR TABLE hoặc bật Glue Crawler tốn thời gian và chi phí.")
    add_body_p(doc, "Partition Projection giải quyết triệt để vấn đề này bằng cách cấu hình trực tiếp trong TBLPROPERTIES:")
    proj_sql = """TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.year.type' = 'integer',
    'projection.year.range' = '2026,2030',
    'projection.month.type' = 'integer',
    'projection.month.range' = '1,12',
    'projection.month.digits' = '2',
    'projection.day.type' = 'integer',
    'projection.day.range' = '1,31',
    'projection.day.digits' = '2',
    'storage.location.template' = 's3://weather-aqi-ACCOUNT_ID/raw/year=${year}/month=${month}/day=${day}/'
);"""
    add_code_snippet(doc, proj_sql, "SQL")
    add_body_p(doc, "Nguyên lý hoạt động: Athena tự nội suy danh sách đường dẫn phân vùng dựa trên quy tắc dải số học (Range). Dữ liệu vừa được Lambda ghi vào S3 là Athena có thể truy vấn được ngay tức thì (Zero-latency data availability) mà không cần Crawler.")

    add_heading_2(doc, "2.6. Tối ưu hóa Columnar: Kỹ thuật CTAS và định dạng Parquet Snappy")
    add_body_p(doc, "Trong Tuần 3 và 4, nhóm thực hiện câu lệnh CTAS (Create Table As Select) để chuyển đổi từ NDJSON sang Parquet Snappy:")
    ctas_sql = """CREATE TABLE weather_aqi_db.vietnam_weather_parquet
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    external_location = 's3://weather-aqi-ACCOUNT_ID/optimized/parquet/'
) AS 
SELECT * FROM weather_aqi_db.weather_airquality_records;"""
    add_code_snippet(doc, ctas_sql, "SQL")

    bench_headers = ["Phương án lưu trữ & truy vấn", "Data Scanned (Byte quét)", "Execution Time (Độ trễ)", "Tiết kiệm chi phí"]
    bench_rows = [
        ["1. Raw NDJSON (Quét toàn bảng)", "~ 152 KB", "1.150 ms", "Mức cơ sở (Baseline)"],
        ["2. Partition Projection (NDJSON)", "~ 24 KB", "680 ms", "Giảm 84,2% chi phí quét"],
        ["3. CTAS Parquet Snappy (Tối ưu nhất)", "~ 4.2 KB", "420 ms", "Giảm 97,2% chi phí quét"]
    ]
    add_table_data(doc, bench_headers, bench_rows)

    add_heading_2(doc, "2.7. 10 Bẫy cú pháp và lưu ý sống còn khi viết SQL trong Amazon Athena")
    add_bullet_p(doc, "Nháy đơn 'Ho Chi Minh' dùng cho chuỗi; nháy kép \"column_name\" dùng cho tên cột. Dùng nháy kép cho chuỗi sẽ gây lỗi Column not found.", "1. Phân biệt dấu nháy: ");
    add_bullet_p(doc, "Dùng dấu chấm SELECT air_quality.pm2_5, weather.temperature FROM ....", "2. Truy vấn Struct lồng nhau: ");
    add_bullet_p(doc, "Dùng TRY_CAST(pm2_5 AS DOUBLE) để trả về NULL khi dữ liệu bẩn thay vì làm sập query như CAST.", "3. Ép kiểu an toàn: ");
    add_bullet_p(doc, "Dùng from_iso8601_timestamp(collected_at) AT TIME ZONE 'Asia/Ho_Chi_Minh' để quy đổi sang giờ Việt Nam.", "4. Múi giờ UTC sang UTC+7: ");
    add_bullet_p(doc, "COUNT(*) / 100 sẽ ra 0 do phép chia nguyên. Bắt buộc viết COUNT(*) * 100.0 / total.", "5. Phép chia số thực: ");
    add_bullet_p(doc, "Hàm corr(temperature_2m, pm2_5) tính hệ số tương quan Pearson chuẩn trong khoảng [-1.0, 1.0].", "6. Tương quan Pearson: ");
    add_bullet_p(doc, "approx_percentile(pm2_5, 0.5) tính trung vị trên dữ liệu lớn mà không cần sắp xếp tốn RAM.", "7. Phân vị xấp xỉ: ");
    add_bullet_p(doc, "ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) tính tỷ lệ phần trăm theo từng nhóm thành phố.", "8. Window Function: ");
    add_bullet_p(doc, "ROW_NUMBER() OVER (PARTITION BY city ORDER BY timestamp_utc DESC) để lọc đúng 1 bản ghi mới nhất.", "9. Lọc bản ghi mới nhất: ");
    add_bullet_p(doc, "Mỗi query Athena luôn bị tính phí tối thiểu 10 MB dữ liệu quét, dù query chỉ đọc 5 KB.", "10. Chi phí tối thiểu 10 MB: ");

    add_heading_2(doc, "2.8. Phân tích chi tiết 4 câu truy vấn SQL phân tích nghiệp vụ trong đồ án")
    
    add_heading_3(doc, "Query 1: So sánh chất lượng không khí và khí tượng theo từng thành phố")
    add_body_p(doc, "Tệp nguồn: tuan_2/athena/query_avg_aqi_by_city.sql")
    q1_sql = """SELECT city,
       COUNT(*) AS total_records,
       ROUND(AVG(us_aqi), 2) AS avg_aqi,
       MIN(us_aqi) AS min_aqi,
       MAX(us_aqi) AS max_aqi,
       ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
       ROUND(AVG(pm10), 2) AS avg_pm10,
       ROUND(AVG(temperature_2m), 2) AS avg_temp,
       ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity
FROM weather_aqi_db.weather_airquality_records
GROUP BY city
ORDER BY avg_aqi DESC;"""
    add_code_snippet(doc, q1_sql, "SQL")
    fig1 = ROOT / "tuan_2/results/charts/01_aqi_city_comparison.png"
    add_image_figure(doc, fig1, "Hình 2.1: Biểu đồ so sánh AQI trung bình, min và max giữa 3 đô thị xuất từ Query 1", width_in=5.8)

    add_heading_3(doc, "Query 2: Phân tích khung giờ cao điểm ô nhiễm trong ngày")
    add_body_p(doc, "Tệp nguồn: tuan_2/athena/query_peak_pollution_hours.sql")
    q2_sql = """SELECT hour,
       ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
       ROUND(AVG(pm10), 2) AS avg_pm10,
       ROUND(AVG(us_aqi), 2) AS avg_aqi,
       COUNT(*) AS sample_count
FROM weather_aqi_db.weather_airquality_records
GROUP BY hour
ORDER BY hour ASC;"""
    add_code_snippet(doc, q2_sql, "SQL")
    fig2 = ROOT / "tuan_2/results/charts/02_peak_pollution_hours.png"
    add_image_figure(doc, fig2, "Hình 2.2: Biểu đồ biến động nồng độ bụi PM2.5, PM10 và AQI theo 24 khung giờ UTC xuất từ Query 2", width_in=5.8)

    add_heading_3(doc, "Query 3: Phân bố cấp độ chất lượng không khí theo tiêu chuẩn US EPA")
    add_body_p(doc, "Tệp nguồn: tuan_2/athena/query_aqi_category_distribution.sql")
    q3_sql = """SELECT city,
       aqi_category,
       COUNT(*) AS occurrence_count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS percentage
FROM weather_aqi_db.weather_airquality_records
GROUP BY city, aqi_category
ORDER BY city, occurrence_count DESC;"""
    add_code_snippet(doc, q3_sql, "SQL")
    fig3 = ROOT / "tuan_2/results/charts/03_aqi_category_distribution.png"
    add_image_figure(doc, fig3, "Hình 2.3: Biểu đồ tỷ lệ phân bố các cấp độ ô nhiễm không khí tại 3 thành phố xuất từ Query 3", width_in=5.8)

    add_heading_3(doc, "Query 4: Phân tích tương quan Pearson giữa Thời tiết và Bụi mịn PM2.5")
    add_body_p(doc, "Tệp nguồn: tuan_2/athena/query_temperature_humidity_correlation.sql")
    q4_sql = """SELECT city,
       ROUND(corr(temperature_2m, pm2_5), 4) AS corr_temp_pm25,
       ROUND(corr(relative_humidity_2m, pm2_5), 4) AS corr_humidity_pm25,
       ROUND(corr(wind_speed_10m, pm2_5), 4) AS corr_wind_pm25
FROM weather_aqi_db.weather_airquality_records
GROUP BY city;"""
    add_code_snippet(doc, q4_sql, "SQL")
    fig4 = ROOT / "tuan_2/results/charts/04_weather_pm25_correlation.png"
    add_image_figure(doc, fig4, "Hình 2.4: Biểu đồ tương quan giữa nhiệt độ, độ ẩm, tốc độ gió và nồng độ PM2.5 xuất từ Query 4", width_in=5.8)

    doc.add_page_break()

    # ==========================================
    # CHƯƠNG 3
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 3: HƯỚNG DẪN CHI TIẾT QUY TRÌNH TRÍCH XUẤT CÁC BẢN CSV")
    
    add_heading_2(doc, "3.1. Phương pháp 1: Trích xuất CSV tự động qua AWS CLI (3 bước chuẩn)")
    add_body_p(doc, "Đây là quy trình thao tác trên PowerShell / Terminal bằng lệnh AWS CLI nguyên bản:")
    
    cli_code = """# BƯỚC 1: Khởi tạo câu truy vấn Athena bất đồng bộ
$QueryString = "SELECT city, ROUND(AVG(us_aqi),2) AS avg_aqi FROM weather_aqi_db.weather_airquality_records GROUP BY city;"
$S3Output = "s3://weather-aqi-873674852386/athena-query-results/"

$StartRes = aws athena start-query-execution `
    --query-string "$QueryString" `
    --query-execution-context Database="weather_aqi_db" `
    --result-configuration OutputLocation="$S3Output" `
    --region us-east-1 `
    --output json | ConvertFrom-Json

$QueryId = $StartRes.QueryExecutionId
Write-Host "Query ID vừa tạo: $QueryId"

# BƯỚC 2: Thăm dò (Polling) trạng thái đến khi SUCCEEDED
do {
    Start-Sleep -Seconds 2
    $Exec = aws athena get-query-execution --query-execution-id $QueryId --region us-east-1 --output json | ConvertFrom-Json
    $State = $Exec.QueryExecution.Status.State
    Write-Host "Trạng thái truy vấn: $State..."
} while ($State -in @("QUEUED", "RUNNING"))

if ($State -ne "SUCCEEDED") { throw "Query failed with state $State" }

# BƯỚC 3: Tải trực tiếp file CSV kết quả từ S3 về máy cục bộ
$S3CsvUri = "$S3Output$QueryId.csv"
aws s3 cp $S3CsvUri "./avg_aqi_by_city.csv" --region us-east-1
Write-Host "Xuất file CSV thành công!" """
    add_code_snippet(doc, cli_code, "PowerShell")

    add_heading_2(doc, "3.2. Phương pháp 2: Trích xuất CSV qua Python Boto3 SDK (AthenaExporter)")
    add_body_p(doc, "Trong mã nguồn tuan_2/scripts/athena_export.py, nhóm xây dựng class AthenaExporter tự động hóa quy trình:")
    boto3_code = """class AthenaExporter:
    def __init__(self, athena, s3, database, output_location):
        self.athena, self.s3 = athena, s3
        self.database, self.output_location = database, output_location

    def execute(self, sql):
        # 1. Start query execution
        qid = self.athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': self.output_location}
        )['QueryExecutionId']

        # 2. Polling loop
        while True:
            exec_info = self.athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']
            state = exec_info['Status']['State']
            if state == 'SUCCEEDED':
                return qid, exec_info
            if state in ('FAILED', 'CANCELLED'):
                raise RuntimeError(f'Athena query {qid} failed: {state}')
            time.sleep(1)

    def download_csv(self, exec_info, dest_file):
        # 3. Direct S3 GetObject
        uri = urlparse(exec_info['ResultConfiguration']['OutputLocation'])
        res = self.s3.get_object(Bucket=uri.netloc, Key=uri.path.lstrip('/'))
        content = res['Body'].read()
        dest_file.write_bytes(content)"""
    add_code_snippet(doc, boto3_code, "Python")

    add_heading_2(doc, "3.3. Phân loại và cấu trúc của 384 tệp CSV trong repository đồ án")
    csv_cat_headers = ["Nhóm tập tin CSV", "Số lượng", "Đường dẫn tiêu biểu", "Ý nghĩa và mục đích sử dụng"]
    csv_cat_rows = [
        ["1. Dữ liệu thô (Raw CSV)", "12 tệp", "results/data_exports/raw_weather_aqi_records.csv", "Toàn bộ bản ghi khí tượng được làm phẳng từ S3 NDJSON."],
        ["2. Bảng phân tích Athena", "35 tệp", "results/athena_queries/*.csv", "Kết quả trích xuất từ 5 câu truy vấn phân tích Athena."],
        ["3. Bảng thống kê mở rộng", "54 tệp", "tuan_2/results/week2_analysis/*.csv", "27 bảng phân tích chuyên sâu của từng sinh viên Tuần 2."],
        ["4. Bảng FinOps Cost Explorer", "4 tệp", "tuan_4/results/cost/learner_lab_cost_breakdown.csv", "117 dòng chi tiết đối soát chi phí từ API GetCostAndUsage."],
        ["5. Bảng Chuỗi thời gian Dự báo", "18 tệp", "tuan_4/results/backtest_2026_10_20/predictions.csv", "432 điểm dự đoán chuỗi thời gian và 18 dòng sai số MAE/RMSE."],
        ["6. Snapshot đối soát môi trường", "261 tệp", "tuan_4/results/verification_2026_10_19/...", "Bằng chứng snapshot trạng thái dịch vụ và kiểm toán."]
    ]
    add_table_data(doc, csv_cat_headers, csv_cat_rows)

    add_heading_2(doc, "3.4. Cơ chế sao lưu và tái lập kết quả Ngoại tuyến (Offline Mode)")
    add_body_p(doc, "Trong môi trường học phần, phiên AWS Learner Lab thường hết hạn sau 4 tiếng. Để đảm bảo tính bền vững khi Giảng viên chấm thi offline, nhóm tích hợp cờ --offline trong các script:")
    add_bullet_p(doc, "Sao chép bộ 156 bản ghi thô từ snapshot lưu trữ mà không cần kết nối S3.", "python tuan_2/scripts/export_raw_records.py --offline: ");
    add_bullet_p(doc, "Tính toán đối soát lại 117 dòng chi phí từ nguồn JSON/CSV đã lưu mà không gọi Cost Explorer.", "python tuan_4/scripts/cost_analysis.py --check: ");
    add_bullet_p(doc, "Kiểm tra toàn bộ 1.400 liên kết Markdown và 384 CSV đảm bảo không có link gãy.", "python tuan_2/scripts/repository_audit.py --check: ");

    doc.add_page_break()

    # ==========================================
    # CHƯƠNG 4
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 4: QUẢN TRỊ VẬN HÀNH, AN NINH BẢO MẬT VÀ TÀI CHÍNH FINOPS")
    
    add_heading_2(doc, "4.1. Đối chiếu 3 chiều Log – Metric – S3 Data Lake")
    add_body_p(doc, "Trong Tuần 4, nhóm thực hiện kiểm thử E2E có kiểm soát trên cả 2 tài khoản, đối chiếu đồng thời 3 nguồn bằng chứng độc lập:")
    recon_headers = ["Trục đối chiếu", "Bằng chứng SV Tiến Sơn (default)", "Bằng chứng SV Ngọc Quyên (quyen)", "Đánh giá"]
    recon_rows = [
        ["1. CloudWatch Logs", "Request 415b1e..., đủ START/END/REPORT và [INFO] Result", "Request 6ae57d..., đủ START/END/REPORT và [INFO] Result", "Khớp 100% vòng đời"],
        ["2. CloudWatch Metrics", "1.0 Invocation, 0.0 Errors trong chu kỳ 300s (Lỗi: 0,0%)", "1.0 Invocation, 0.0 Errors trong chu kỳ 300s (Lỗi: 0,0%)", "Khớp 1-1 với lượt gọi"],
        ["3. Lưu trữ Amazon S3", "1 tệp NDJSON, 3 dòng bản ghi, khớp byte JSON tải lại", "1 tệp NDJSON, 3 dòng bản ghi, khớp byte JSON tải lại", "Toàn vẹn dữ liệu"],
        ["4. Amazon SNS Alert", "1 Publish được chấp nhận; email đã xác nhận tại hộp thư", "1 Publish được chấp nhận; email đã xác nhận tại hộp thư", "Khớp điều kiện cảnh báo"]
    ]
    add_table_data(doc, recon_headers, recon_rows)

    add_heading_2(doc, "4.2. Rà soát an ninh bảo mật 11 tiêu chuẩn (Security Audit)")
    add_body_p(doc, "Nhóm rà soát an ninh hệ thống theo 11 tiêu chuẩn nghiêm ngặt:")
    add_bullet_p(doc, "Bật đầy đủ 4/4 thiết lập Block Public Access, ngăn chặn rò rỉ dữ liệu.", "1. S3 Block Public Access: ");
    add_bullet_p(doc, "Mã hóa mặc định AES256 (SSE-S3) cho toàn bộ bucket.", "2. S3 Encryption at Rest: ");
    add_bullet_p(doc, "Chính sách S3 Bucket Policy từ chối mọi yêu cầu có aws:SecureTransport = false.", "3. Enforce HTTPS in Transit: ");
    add_bullet_p(doc, "Bật BucketOwnerEnforced, vô hiệu hóa ACL để quản trị tập trung.", "4. S3 Object Ownership: ");
    add_bullet_p(doc, "S3 Versioning Enabled giúp bảo vệ lịch sử và khôi phục khi bị ghi đè.", "5. S3 Versioning: ");
    add_bullet_p(doc, "Lưu trữ URL và API key trong Secrets Manager, không hardcode vào Git.", "6. Secrets Hygiene: ");
    add_bullet_p(doc, "Lambda Permission chỉ chấp nhận lời gọi từ đúng ARN của EventBridge Rule và đúng SourceAccount.", "7. Lambda Least Privilege Trigger: ");
    add_bullet_p(doc, "Chính sách SNS Topic Policy chỉ chấp nhận sự kiện bắn từ CloudWatch Alarm cụ thể.", "8. SNS Topic Policy: ");
    add_bullet_p(doc, "CloudWatch Log Group giới hạn retention, che giấu các chuỗi token nhạy cảm.", "9. Log Sanitization: ");
    add_bullet_p(doc, "Template CloudFormation tuân thủ cfn-lint 1.57.2 và ValidateTemplate API.", "10. IaC Security Linting: ");
    add_bullet_p(doc, "Sử dụng IAM LabRole có sẵn của AWS Academy, không tự ý tạo role vượt quyền.", "11. IAM Role Boundary: ");

    add_heading_2(doc, "4.3. Quản trị tài chính đám mây FinOps với AWS Cost Explorer")
    add_body_p(doc, "Phương pháp tổng hợp: Boto3 gọi GetCostAndUsage, Granularity DAILY, Metric UnblendedCost, GroupBy SERVICE và RECORD_TYPE. CSV giữ ngày UTC, dịch vụ, loại ghi nhận, số gốc USD và Estimated. Phép cộng dùng Decimal; bản hiển thị làm tròn đến cent.")
    
    cost_headers = ["Sinh viên thực hiện", "Số nhóm ngày/dịch vụ/ghi nhận", "Tổng UnblendedCost gốc (USD)", "Hiển thị đến cent (USD)"]
    cost_rows = [
        ["Sinh viên Tiến Sơn (24110054)", "70", "-0,000000339", "0,00"],
        ["Sinh viên Ngọc Quyên (24110051)", "47", "0,1364702401", "0,14"]
    ]
    add_table_data(doc, cost_headers, cost_rows)
    add_body_p(doc, "Nguồn: cost_summary.json, 117 dòng chi tiết learner_lab_cost_breakdown.csv. Tổng chi phí của Tiến Sơn mang dấu âm rất nhỏ do điều chỉnh credit/hoàn tiền tự động của AWS, được bảo lưu nguyên gốc để đảm bảo tính trung thực học thuật.")

    add_heading_2(doc, "4.4. Tự động hóa quản lý vòng đời tài nguyên và bảo toàn credit phiên Lab")
    add_body_p(doc, "Để giải quyết vấn đề hao hụt credit khi kết thúc buổi thực hành, nhóm xây dựng công cụ session_control.py cùng 2 script PowerShell:")
    add_bullet_p(doc, "Lưu trạng thái an toàn vào file JSON và chuyển EventBridge Rule sang DISABLED. Lambda ngừng chạy ngầm.", "cleanup_resources.ps1: ");
    add_bullet_p(doc, "Đọc file trạng thái, kiểm tra fingerprint môi trường và khôi phục Rule sang ENABLED.", "start_resources.ps1: ");

    doc.add_page_break()

    # ==========================================
    # CHƯƠNG 5
    # ==========================================
    add_heading_1(doc, "CHƯƠNG 5: NGÂN HÀNG 20 CÂU HỎI VẤN ĐÁP PHẢN BIỆN VÀ CÂU TRẢ LỜI MẪU")
    add_body_p(doc, "Dưới đây là 20 câu hỏi trọng tâm thường gặp nhất của Giảng viên chấm thi và định hướng trả lời xuất sắc:")

    qa_list = [
        ("Câu 1: Tại sao nhóm không lưu dữ liệu vào RDS MySQL mà lại dùng S3 Data Lake?",
         "Dữ liệu thời tiết là chuỗi thời gian phát sinh liên tục. S3 Data Lake lưu trữ không giới hạn với chi phí cực thấp (~0.023 USD/GB/tháng so với hàng chục USD/tháng cho RDS instance chạy 24/7), dữ liệu thô bất biến và cho phép nhiều công cụ phân tích (Athena, Glue, EMR) cùng truy cập đồng thời."),
        
        ("Câu 2: Khác biệt cốt lõi giữa External Table trong Athena và Table trong SQL Server là gì?",
         "Athena áp dụng Schema-on-Read, chỉ lưu metadata trên Glue Catalog còn dữ liệu nằm trên S3. Lệnh DROP TABLE trong Athena chỉ xóa metadata trong Glue, toàn bộ file dữ liệu gốc trên S3 vẫn còn nguyên vẹn 100%."),
         
        ("Câu 3: Cơ chế Partition Pruning hoạt động như thế nào và tại sao lại giảm chi phí?",
         "Cắt tỉa phân vùng ở tầng đường dẫn S3 (prefix) trước khi đọc dữ liệu. Khi có điều kiện WHERE year=... AND month=... AND day=..., Athena chỉ quét đúng thư mục của ngày đó, cắt giảm từ 75% đến 86% byte quét I/O, qua đó giảm trực tiếp chi phí truy vấn tương ứng."),
         
        ("Câu 4: Partition Projection giải quyết hạn chế gì của Glue Crawler và MSCK REPAIR TABLE?",
         "Phân vùng truyền thống bắt buộc phải đăng ký phân vùng trước. Partition Projection tự nội suy cấu trúc phân vùng theo quy tắc số học, giúp dữ liệu mới vừa ghi vào S3 là truy vấn được ngay tức thì (Zero-latency) mà không cần Crawler."),
         
        ("Câu 5: Tại sao định dạng Parquet Snappy lại nhanh và tốn ít byte quét hơn file JSON?",
         "Parquet là định dạng cột (chỉ đọc đúng các cột có trong SELECT), nén khối bằng Snappy giảm 60-80% dung lượng, và có sẵn thống kê Min/Max tại Footer giúp bỏ qua các khối không thỏa mãn điều kiện WHERE."),
         
        ("Câu 6: Làm thế nào để nhóm xuất được kết quả truy vấn Athena ra file CSV?",
         "Qua AWS CLI bằng lệnh start-query-execution, polling kiểm tra get-query-execution, và tải file từ S3 bằng aws s3 cp. Qua Python SDK bằng boto3 client tương tự trong script athena_export.py."),
         
        ("Câu 7: Tại sao cần tạo Athena View vietnam_weather_aqi mà không để truy vấn thẳng bảng gốc?",
         "Đây là nguyên tắc phân tách tầng dữ liệu vật lý và tầng logic (Data Abstraction). Khi người dùng chỉ truy vấn qua View, nếu sau này nhóm tối ưu đổi định dạng S3 sang Parquet hoặc chuyển bucket, chỉ cần cập nhật View mà mã nguồn của người dùng không bị gãy."),
         
        ("Câu 8: Nhóm xử lý lệch múi giờ UTC và UTC+7 như thế nào trong SQL?",
         "Lambda lưu song song cả timestamp_utc và timestamp_vn. Trong SQL Athena, dùng hàm from_iso8601_timestamp(collected_at) AT TIME ZONE 'Asia/Ho_Chi_Minh' để chuyển đổi chính xác sang giờ Việt Nam."),
         
        ("Câu 9: Hàm corr() trong SQL Athena tính gì và kết quả thực nghiệm ra sao?",
         "Tính hệ số tương quan tuyến tính Pearson. Thực nghiệm cho thấy tốc độ gió có tương quan âm với nồng độ PM2.5 (gió mạnh giúp phân tán bụi), còn độ ẩm buổi sáng có tương quan dương với PM2.5 (giữ bụi lơ lửng)."),
         
        ("Câu 10: Ý nghĩa của cấu hình ignore.malformed.json = 'true' trong SerDe là gì?",
         "Cơ chế phòng vệ lỗi: nếu một dòng JSON trên S3 bị đứt đoạn do sự cố mạng, SerDe sẽ bỏ qua dòng hỏng đó hoặc trả về NULL thay vì quăng lỗi làm sập toàn bộ câu truy vấn của người dùng."),
         
        ("Câu 11: Đối chiếu 3 chiều Log – Metric – S3 trong Tuần 4 được thực hiện như thế nào?",
         "Kiểm chứng sự toàn vẹn 1-1 của một lượt chạy: Log có đủ START/END/REPORT và dòng [INFO] Result; Metric ghi nhận đúng 1.0 Invocation và 0.0 Errors; S3 xuất hiện tệp JSON mới và Athena đọc ra đúng record_id."),
         
        ("Câu 12: Tại sao chi phí thực tế của sinh viên Tiến Sơn lại là số âm hoặc 0,00 USD?",
         "API GetCostAndUsage trả về tổng chi phí gốc là -0.000000339 USD, làm tròn thành 0.00 USD. Dấu âm rất nhỏ này do điều chỉnh hoàn tiền (Credit adjustment) tự động từ hệ thống thanh toán của AWS, được bảo lưu nguyên gốc để đảm bảo tính trung thực học thuật."),
         
        ("Câu 13: Template CloudFormation của nhóm quản lý bao nhiêu tài nguyên?",
         "Template weather-stack.json quản lý trọn vẹn 17 tài nguyên AWS Serverless: S3 Bucket, Bucket Policy, Secrets Manager Secret, Lambda Function, Lambda Permission, Log Group, EventBridge Rule, Glue Database, Athena Table, Athena Workgroup, SNS Topic, Email Subscription, SNS Policy, 2 Metric Filters, 1 Alarm và 1 Dashboard."),
         
        ("Câu 14: Nhóm đã thực hiện các biện pháp bảo mật nào (Security Audit)?",
         "11 tiêu chí: Block Public Access 100%, bắt buộc HTTPS bằng Bucket Policy, mã hóa AES256, S3 Versioning, Secrets Manager không hardcode key, Lambda trigger ràng buộc ARN EventBridge, SNS topic policy kiểm tra SourceArn."),
         
        ("Câu 15: Sau khi kết thúc buổi thực hành, nhóm làm cách nào để không bị trừ hết tiền?",
         "Chạy cleanup_resources.ps1 để lưu trạng thái và chuyển EventBridge Rule sang DISABLED. Đầu phiên sau chạy start_resources.ps1 để khôi phục ENABLED. Nhờ vậy Lambda không chạy ngầm khi không ngồi máy."),
         
        ("Câu 16: Nếu API Open-Meteo bị sập hoặc trả về mã lỗi 500, Lambda xử lý như thế nào?",
         "Lambda bắt ngoại lệ HTTP error, ghi dòng log [ERROR] vào CloudWatch Logs. Metric Filter ErrorLogLines bắt được tín hiệu tăng bộ đếm, kích hoạt CloudWatch Alarm và gửi email thông báo sự cố qua SNS."),
         
        ("Câu 17: Phép chia tỷ lệ phần trăm trong Athena có bẫy gì cần lưu ý?",
         "Presto thực hiện phép chia số nguyên (Integer Division). Nếu viết COUNT(*) / total thì kết quả là 0. Bắt buộc phải nhân số thực: COUNT(*) * 100.0 / total."),
         
        ("Câu 18: Sự khác biệt giữa hàm CAST và TRY_CAST trong SQL Athena?",
         "CAST sẽ quăng lỗi và dừng toàn bộ query nếu gặp chuỗi không thể chuyển đổi thành số. TRY_CAST sẽ trả về giá trị NULL an toàn, giúp câu query vẫn tiếp tục thực thi thành công."),
         
        ("Câu 19: Mô hình dự báo chuỗi thời gian trong Tuần 3 hoạt động như thế nào?",
         "Sử dụng kỹ thuật Moving Average trượt 3 chu kỳ và Seasonal Baseline 24h. Đánh giá sai số trên tập kiểm thử Holdout 24h bằng các chỉ số MAE, RMSE và Mean Bias Error."),
         
        ("Câu 20: Chế độ Ngoại tuyến (Offline Mode) trong các script phục vụ mục đích gì?",
         "Khi chấm thi không có mạng hoặc phiên AWS hết hạn, cờ --offline giúp script đọc trực tiếp từ bộ snapshot bằng chứng có chữ ký SHA-256 để tái lập 100% kết quả phân tích mà không cần gọi AWS.")
    ]

    for q, a in qa_list:
        add_body_p(doc, q, bold_prefix="❓ ", space_after=2)
        add_body_p(doc, a, bold_prefix="💡 Trả lời: ", space_after=8)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    doc = Document()
    
    # 0.8-inch margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)
        
    build_cover_page(doc)
    build_content(doc)
    
    # Save to output/
    doc.save(DEST_OUTPUT)
    print(f"Saved: {DEST_OUTPUT}")
    
    # Copy to Downloads/
    shutil.copyfile(DEST_OUTPUT, DEST_DOWNLOADS_1)
    print(f"Copied to: {DEST_DOWNLOADS_1}")
    
    shutil.copyfile(DEST_OUTPUT, DEST_DOWNLOADS_2)
    print(f"Copied to: {DEST_DOWNLOADS_2}")

if __name__ == "__main__":
    main()
