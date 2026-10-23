"""
Render docs/CAM_NANG_HOC_TAP_SQL_CSV_VA_BAO_CAO_WORD.md to a beautifully styled DOCX file.
"""
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "CAM_NANG_HOC_TAP_SQL_CSV_VA_BAO_CAO_WORD.md"
OUT_DIR = ROOT / "output"
OUT_PATH = OUT_DIR / "Bao_cao_hoc_tap_WeatherAWS_SQL_va_CSV.docx"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0]
    if level == 1:
        run.font.name = "Arial"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(26, 54, 93) # #1A365D
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(43, 108, 176) # #2B6CB0
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(45, 55, 72) # #2D3748
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_code_block(doc, code_lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F7FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    # Left border highlight
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="2B6CB0"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    text = "\n".join(code_lines)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.0)
    run.font.color.rgb = RGBColor(45, 55, 72)
    
    # spacing after table
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def parse_markdown_table(lines):
    rows = []
    for line in lines:
        line = line.strip()
        if not line or not line.startswith("|") or not line.endswith("|"):
            continue
        # Check if separator line
        parts = [p.strip() for p in line[1:-1].split("|")]
        if all(re.match(r"^:?-+:?$", p) for p in parts):
            continue
        rows.append(parts)
    return rows

def add_rendered_table(doc, table_rows):
    if not table_rows:
        return
    cols_count = len(table_rows[0])
    table = doc.add_table(rows=len(table_rows), cols=cols_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, "CBD5E0")
    
    for r_idx, row in enumerate(table_rows):
        for c_idx, val in enumerate(row):
            if c_idx >= cols_count:
                break
            cell = table.cell(r_idx, c_idx)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            
            clean_val = val.replace("**", "").replace("`", "")
            run = p.add_run(clean_val)
            run.font.name = "Arial"
            
            if r_idx == 0:
                set_cell_background(cell, "2B6CB0")
                run.font.bold = True
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, "F7FAFC")
                run.font.size = Pt(9.0)
                run.font.color.rgb = RGBColor(45, 55, 72)
                if "**" in val:
                    run.font.bold = True
                    
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(6)

def format_inline_runs(paragraph, text):
    # Pattern to match bold, code, and plain text
    # e.g., **bold**, `code`, plain
    tokens = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.font.name = "Arial"
            run.font.bold = True
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(184, 50, 128) # purple-red
        else:
            run = paragraph.add_run(token)
            run.font.name = "Arial"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()
    
    # Page setup: A4, 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    for line in lines:
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                add_code_block(doc, code_lines)
                code_lines = []
                in_code_block = False
            else:
                if in_table:
                    table_rows = parse_markdown_table(table_lines)
                    add_rendered_table(doc, table_rows)
                    table_lines = []
                    in_table = False
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle tables
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_lines.append(stripped)
            continue
        else:
            if in_table:
                table_rows = parse_markdown_table(table_lines)
                add_rendered_table(doc, table_rows)
                table_lines = []
                in_table = False

        if not stripped:
            continue

        # Headings
        if stripped.startswith("# "):
            add_styled_heading(doc, stripped[2:], level=1)
        elif stripped.startswith("## "):
            add_styled_heading(doc, stripped[3:], level=2)
        elif stripped.startswith("### "):
            add_styled_heading(doc, stripped[4:], level=3)
        elif stripped.startswith("---"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run("―" * 50)
            run.font.color.rgb = RGBColor(203, 213, 224)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            format_inline_runs(p, stripped[2:])
        elif re.match(r"^\d+\.\s", stripped):
            match = re.match(r"^(\d+\.)\s+(.*)", stripped)
            prefix, content = match.group(1), match.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run_p = p.add_run(prefix + " ")
            run_p.font.name = "Arial"
            run_p.font.bold = True
            format_inline_runs(p, content)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            format_inline_runs(p, stripped)

    if in_code_block:
        add_code_block(doc, code_lines)
    if in_table:
        table_rows = parse_markdown_table(table_lines)
        add_rendered_table(doc, table_rows)

    doc.save(OUT_PATH)
    print(f"Successfully generated DOCX: {OUT_PATH}")

if __name__ == "__main__":
    main()
