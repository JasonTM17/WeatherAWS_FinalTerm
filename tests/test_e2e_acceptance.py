"""
E2E Acceptance Test Suite for WeatherAWS_FinalTerm Repository
============================================================
Independent, opaque-box, requirement-driven end-to-end acceptance tests
covering user requirements R1 to R4 across four verification tiers:

- Tier 1: Feature Coverage (R1.1 - R4.2)
- Tier 2: Boundary & Corner Cases (non-empty files, format validity, schema integrity)
- Tier 3: Cross-Feature Combinations (image asset parity, 156 records, test counts, DDL consistency)
- Tier 4: Real-World Acceptance Scenarios (root navigation, security cleanliness, module autonomy)

Authoritative sources:
- README.md (current project structure and submission links)
- docs/source-guide.md and docs/data-analysis.md (source and data contracts)
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Optional high-level libraries (gracefully handled if unavailable)
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

# -----------------------------------------------------------------------------
# Constant Specifications & Authoritative Baselines
# -----------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]

GITHUB_REPO_URL = "https://github.com/JasonTM17/WeatherAWS_FinalTerm.git"
STUDENT_1_NAME = "Nguyễn Tiến Sơn"
STUDENT_1_ID = "24110054"
STUDENT_2_NAME = "Trần Thị Ngọc Quyên"
STUDENT_2_ID = "24110051"
INSTRUCTOR_NAME = "Huỳnh Xuân Phụng"

EXPECTED_PHYSICAL_PAGES_W1 = 20
EXPECTED_TOC_ENTRIES_W1 = 28
EXPECTED_RAW_RECORD_COUNT = 156
EXPECTED_UNIT_TEST_COUNT = 48

EXPECTED_REPORT_FIGURES = [
    "docs/architecture.png",
    "tuan_2/results/charts/01_aqi_city_comparison.png",
    "tuan_2/results/charts/02_peak_pollution_hours.png",
    "tuan_2/results/charts/03_aqi_category_distribution.png",
    "tuan_2/results/charts/04_weather_pm25_correlation.png",
]

# -----------------------------------------------------------------------------
# Extraction & Parsing Helpers
# -----------------------------------------------------------------------------
def locate_file(*relative_candidates: str) -> Optional[Path]:
    """Locate the first existing file from candidate paths relative to REPO_ROOT."""
    for rel in relative_candidates:
        candidate = REPO_ROOT / rel
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def locate_dir(*relative_candidates: str) -> Optional[Path]:
    """Locate the first existing directory from candidate paths relative to REPO_ROOT."""
    for rel in relative_candidates:
        candidate = REPO_ROOT / rel
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def extract_docx_text(docx_path: Path) -> str:
    """Extract plain text from a DOCX file using python-docx or standard library zipfile/XML."""
    if not docx_path.exists():
        return ""

    if docx is not None:
        try:
            doc = docx.Document(str(docx_path))
            parts = [p.text for p in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        parts.append(cell.text)
            return " ".join(parts)
        except Exception:
            pass

    # Pure standard library fallback
    parts = []
    try:
        with zipfile.ZipFile(docx_path) as z:
            for name in z.namelist():
                if name.startswith("word/") and name.endswith(".xml"):
                    xml_data = z.read(name)
                    tree = ET.fromstring(xml_data)
                    for elem in tree.iter():
                        if elem.tag.endswith("}t") and elem.text:
                            parts.append(elem.text)
    except Exception:
        return ""
    return " ".join(parts)


def extract_pdf_info(pdf_path: Path) -> Tuple[int, str, List]:
    """Extract page count, text, and page 4 hyperlinks from a PDF file."""
    if not pdf_path.exists():
        return 0, "", []

    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(str(pdf_path))
            pages = reader.pages
            page_count = len(pages)
            full_text = " ".join((p.extract_text() or "") for p in pages)
            links = []
            if page_count > 3:
                annots = pages[3].get("/Annots", [])
                for annot in annots:
                    obj = annot.get_object() if hasattr(annot, "get_object") else annot
                    if obj.get("/Subtype") == "/Link":
                        links.append(obj)
            return page_count, full_text, links
        except Exception:
            pass

    # Subprocess fallback via Python 3.14 if pypdf is installed there
    try:
        py_code = (
            "import json, pypdf; "
            f"r = pypdf.PdfReader(r'{pdf_path}'); "
            "pages = r.pages; "
            "txt = ' '.join((p.extract_text() or '') for p in pages); "
            "links = len(pages[3].get('/Annots', [])) if len(pages) > 3 else 0; "
            "print(json.dumps({'count': len(pages), 'text': txt, 'links_count': links}))"
        )
        proc = subprocess.run(
            ["py", "-3.14", "-c", py_code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout.strip())
            return data["count"], data["text"], [1] * data["links_count"]
    except Exception:
        pass

    # Basic binary check fallback
    try:
        content = pdf_path.read_bytes()
        page_markers = len(re.findall(rb"/Type\s*/Page\b", content))
        text_estimate = content.decode("latin1", errors="ignore")
        return page_markers, text_estimate, []
    except Exception:
        return 0, "", []


# =============================================================================
# Tier 1: Feature Coverage (User Requirements R1 to R4)
# =============================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """Verifies all direct feature requirements R1 to R4 from ORIGINAL_REQUEST.md."""

    def test_r1_1_tuan_1_directory_structure_and_assets(self):
        """R1.1: Verify tuan_1/ directory exists with foundation scripts, architecture docs, and Week 1 reports."""
        tuan_1 = REPO_ROOT / "tuan_1"
        self.assertTrue(
            tuan_1.exists() and tuan_1.is_dir(),
            "Directory 'tuan_1' does not exist at repository root (pending Milestone 1: Repo Reorganization)",
        )

        expected_files = [
            tuan_1 / "scripts" / "01_setup_s3.ps1",
            tuan_1 / "scripts" / "02_setup_secrets.ps1",
            tuan_1 / "docs" / "ARCHITECTURE.md",
            REPO_ROOT / "docs" / "architecture.svg",
            REPO_ROOT / "docs" / "architecture.png",
            tuan_1 / "docs" / "Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx",
            tuan_1 / "docs" / "Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf",
            tuan_1 / "docs" / "Bao_cao_tuan_1_Du_lieu_Athena_Nhom_05.xlsx",
            tuan_1 / "docs" / "WORKLOG_NHOM_05_CAN_XAC_NHAN.md",
            tuan_1 / "README.md",
        ]
        for path in expected_files:
            self.assertTrue(
                path.exists(),
                f"Missing required Week 1 asset: '{path.relative_to(REPO_ROOT)}'",
            )

    def test_r1_2_tuan_2_directory_structure_and_assets(self):
        """R1.2: Verify tuan_2/ directory exists with Lambda, Athena, scripts, tests, results, analytics, and docs."""
        tuan_2 = REPO_ROOT / "tuan_2"
        self.assertTrue(
            tuan_2.exists() and tuan_2.is_dir(),
            "Directory 'tuan_2' does not exist at repository root (pending Milestone 1: Repo Reorganization)",
        )

        # Core directories
        for sub in ["lambda", "athena", "scripts", "tests", "results", "analytics", "docs"]:
            subdir = tuan_2 / sub
            self.assertTrue(
                subdir.exists() and subdir.is_dir(),
                f"Missing required Week 2 subdirectory: 'tuan_2/{sub}'",
            )

        # Essential entry files
        self.assertTrue((tuan_2 / "lambda" / "lambda_function.py").exists(), "Missing tuan_2/lambda/lambda_function.py")
        self.assertTrue((tuan_2 / "README.md").exists(), "Missing tuan_2/README.md")
        self.assertTrue((tuan_2 / "scripts" / "deploy_all.ps1").exists(), "Missing tuan_2/scripts/deploy_all.ps1")
        self.assertTrue((tuan_2 / "scripts" / "test_pipeline.ps1").exists(), "Missing tuan_2/scripts/test_pipeline.ps1")
        self.assertTrue((tuan_2 / "scripts" / "cleanup_all.ps1").exists(), "Missing tuan_2/scripts/cleanup_all.ps1")

        # Self-contained copies of foundational scripts
        self.assertTrue((tuan_2 / "scripts" / "01_setup_s3.ps1").exists(), "Missing tuan_2/scripts/01_setup_s3.ps1")
        self.assertTrue((tuan_2 / "scripts" / "02_setup_secrets.ps1").exists(), "Missing tuan_2/scripts/02_setup_secrets.ps1")

    def test_r1_3_cli_execution_logs_absent(self):
        """R1.3: Verify CLI_EXECUTION_LOGS.md does NOT exist anywhere in repository."""
        forbidden_matches = list(REPO_ROOT.glob("**/CLI_EXECUTION_LOGS.md"))
        # Exclude agent metadata directories (.agents)
        repo_matches = [
            p for p in forbidden_matches
            if ".agents" not in p.parts
        ]
        self.assertEqual(
            len(repo_matches),
            0,
            f"Found forbidden raw CLI execution log file(s): {[str(p.relative_to(REPO_ROOT)) for p in repo_matches]} "
            f"(pending Milestone 1: CLI Log Cleanup)",
        )

    def test_r2_1_week_1_docx_contains_github_url(self):
        """R2.1: Verify Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx contains GitHub URL."""
        w1_docx = locate_file(
            "tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx",
            "docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx",
        )
        self.assertIsNotNone(
            w1_docx,
            "Week 1 DOCX report file not found in 'tuan_1/docs/' or 'docs/'",
        )

        text = extract_docx_text(w1_docx)
        self.assertIn(
            GITHUB_REPO_URL,
            text,
            f"GitHub URL '{GITHUB_REPO_URL}' not found in Week 1 DOCX: {w1_docx.relative_to(REPO_ROOT)} "
            f"(pending Milestone 3: Week 1 Report Update)",
        )

    def test_r2_2_week_1_pdf_contains_github_url(self):
        """R2.2: Verify Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf contains GitHub URL."""
        w1_pdf = locate_file(
            "tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf",
            "docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf",
        )
        self.assertIsNotNone(
            w1_pdf,
            "Week 1 PDF report file not found in 'tuan_1/docs/' or 'docs/'",
        )

        _, text, _ = extract_pdf_info(w1_pdf)
        self.assertIn(
            GITHUB_REPO_URL,
            text,
            f"GitHub URL '{GITHUB_REPO_URL}' not found in Week 1 PDF: {w1_pdf.relative_to(REPO_ROOT)} "
            f"(pending Milestone 3: Week 1 Report Update)",
        )

    def test_r2_3_week_1_pdf_layout_integrity(self):
        """R2.3: Verify Week 1 PDF layout integrity (20 pages, TOC hyperlinks intact)."""
        w1_pdf = locate_file(
            "tuan_1/docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf",
            "docs/Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf",
        )
        self.assertIsNotNone(w1_pdf, "Week 1 PDF report file not found")

        page_count, _, links = extract_pdf_info(w1_pdf)
        self.assertEqual(
            page_count,
            EXPECTED_PHYSICAL_PAGES_W1,
            f"Week 1 PDF page count is {page_count}, expected exactly {EXPECTED_PHYSICAL_PAGES_W1} pages",
        )
        self.assertGreaterEqual(
            len(links),
            EXPECTED_TOC_ENTRIES_W1,
            f"Week 1 PDF TOC has {len(links)} links, expected at least {EXPECTED_TOC_ENTRIES_W1}",
        )

    def test_r3_1_week_2_docx_metadata_and_identities(self):
        """R3.1: Verify Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx exists and contains GitHub URL, students, lecturer."""
        w2_docx = locate_file(
            "tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx",
            "docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx",
        )
        self.assertIsNotNone(
            w2_docx,
            "Week 2 DOCX report file not found (pending Milestone 4: Week 2 Report Creation)",
        )

        text = extract_docx_text(w2_docx)
        self.assertIn(
            GITHUB_REPO_URL,
            text,
            f"GitHub repository URL '{GITHUB_REPO_URL}' not found in Week 2 DOCX",
        )
        self.assertIn(
            STUDENT_1_NAME,
            text,
            f"Student 1 '{STUDENT_1_NAME}' not found in Week 2 DOCX cover/metadata",
        )
        self.assertIn(
            STUDENT_1_ID,
            text,
            f"Student 1 ID '{STUDENT_1_ID}' not found in Week 2 DOCX cover/metadata",
        )
        self.assertIn(
            STUDENT_2_NAME,
            text,
            f"Student 2 '{STUDENT_2_NAME}' not found in Week 2 DOCX cover/metadata",
        )
        self.assertIn(
            STUDENT_2_ID,
            text,
            f"Student 2 ID '{STUDENT_2_ID}' not found in Week 2 DOCX cover/metadata",
        )
        self.assertIn(
            INSTRUCTOR_NAME,
            text,
            f"Instructor '{INSTRUCTOR_NAME}' not found in Week 2 DOCX cover/metadata",
        )

    def test_r3_2_week_2_pdf_exists_and_sections(self):
        """R3.2: Verify Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf exists and contains GitHub URL and required chapters."""
        w2_pdf = locate_file(
            "tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf",
            "docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf",
        )
        self.assertIsNotNone(
            w2_pdf,
            "Week 2 PDF report file not found (pending Milestone 4: Week 2 Report PDF Conversion)",
        )

        page_count, text, _ = extract_pdf_info(w2_pdf)
        self.assertGreaterEqual(page_count, 15, "Week 2 PDF has fewer pages than expected comprehensive report")
        self.assertIn(GITHUB_REPO_URL, text, f"GitHub URL '{GITHUB_REPO_URL}' not found in Week 2 PDF")

        required_chapters = ["Chương 1", "Chương 2", "Chương 3", "Chương 4", "Chương 5", "Chương 6"]
        for ch in required_chapters:
            self.assertIn(ch, text, f"Required chapter '{ch}' not found in Week 2 PDF")

    def test_r3_3_week_2_report_technical_substance(self):
        """Verify Week 2 report contains service design and environmental analysis."""
        w2_docx = locate_file(
            "tuan_2/docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx",
            "docs/Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx",
        )
        self.assertIsNotNone(w2_docx, "Week 2 DOCX report not found")

        text = extract_docx_text(w2_docx)
        keywords = [
            "Lambda",
            "EventBridge",
            "SNS",
            "Athena",
            "Open-Meteo",
            "PM2.5",
        ]
        for kw in keywords:
            self.assertIn(
                kw.casefold(),
                text.casefold(),
                f"Technical core concept '{kw}' not mentioned in Week 2 report",
            )

    def test_r4_1_unit_test_suite_48_tests_pass(self):
        """R4.1: Verify unit test suite runs exactly 48 tests and passes 100%."""
        test_dir = locate_dir("tuan_2/tests", "tests")
        self.assertIsNotNone(test_dir, "Tests directory not found in 'tuan_2/tests' or 'tests'")

        # Explicitly run unit test modules to prevent recursion with this acceptance runner
        cmd = [
            sys.executable, "-m", "unittest",
            "test_lambda_function",
            "test_analytics",
            "test_csv_exports",
            "test_sdk",
        ]

        # Isolate environment from ambient AWS token failures during testing
        test_env = os.environ.copy()
        test_env["AWS_ACCESS_KEY_ID"] = "OFFLINE_TESTING"
        test_env["AWS_SECRET_ACCESS_KEY"] = "OFFLINE_TESTING"
        test_env["AWS_SESSION_TOKEN"] = "OFFLINE_TESTING"

        proc = subprocess.run(
            cmd,
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            env=test_env,
            timeout=45,
        )

        output = proc.stdout + "\n" + proc.stderr
        match = re.search(r"Ran (\d+) tests", output)
        self.assertIsNotNone(
            match,
            f"Failed to find test execution count in unittest output:\n{output}",
        )
        ran_count = int(match.group(1))
        self.assertEqual(
            ran_count,
            EXPECTED_UNIT_TEST_COUNT,
            f"Expected {EXPECTED_UNIT_TEST_COUNT} unit tests, but executed {ran_count}",
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"Unit test suite had failures or errors (return code {proc.returncode}):\n{output} "
            f"(pending Milestone 2: Test Determinism)",
        )

    def test_r4_2_git_commits_and_remote_tracking(self):
        """R4.2: Verify Git commits exist and remote origin tracks repository."""
        proc_url = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_url.returncode, 0, "Failed to retrieve git remote.origin.url")
        remote_url = proc_url.stdout.strip()
        self.assertEqual(
            remote_url,
            GITHUB_REPO_URL,
            f"Remote origin URL is '{remote_url}', expected '{GITHUB_REPO_URL}'",
        )

        proc_log = subprocess.run(
            ["git", "log", "-n", "10", "--oneline"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_log.returncode, 0, "Failed to inspect git log")
        log_output = proc_log.stdout.strip()
        self.assertTrue(len(log_output) > 0, "Git commit history is empty")


# =============================================================================
# Tier 2: Boundary & Corner Cases (Format Validity, Magic Headers, Schemas)
# =============================================================================
class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Verifies edge cases, file integrity, magic bytes, and data schemas."""

    def test_critical_files_non_empty(self):
        """Checks all critical project files are non-zero size."""
        critical_globs = [
            "**/*.py",
            "**/*.ps1",
            "**/*.sql",
            "**/*.docx",
            "**/*.pdf",
        ]
        for pattern in critical_globs:
            for path in REPO_ROOT.glob(pattern):
                if any(x in path.parts for x in [".agents", ".pytest_cache", "_report_work", "node_modules"]):
                    continue
                if path.name == "__init__.py":
                    continue
                size = path.stat().st_size
                self.assertGreater(
                    size,
                    0,
                    f"File '{path.relative_to(REPO_ROOT)}' is unexpectedly empty (0 bytes)",
                )

    def test_pdf_format_and_eof_markers(self):
        """Validates that all PDF reports begin with '%PDF-' header and end with '%%EOF'."""
        pdf_files = list(REPO_ROOT.glob("**/*.pdf"))
        valid_pdfs = [
            p for p in pdf_files
            if not any(x in p.parts for x in [".agents", "_report_work", "node_modules"])
        ]
        self.assertGreater(len(valid_pdfs), 0, "No PDF reports found in repository")

        for pdf_path in valid_pdfs:
            with open(pdf_path, "rb") as f:
                header = f.read(5)
                self.assertEqual(
                    header,
                    b"%PDF-",
                    f"PDF '{pdf_path.relative_to(REPO_ROOT)}' lacks '%PDF-' magic bytes",
                )
                f.seek(-1024, os.SEEK_END)
                tail = f.read()
                self.assertIn(
                    b"%%EOF",
                    tail,
                    f"PDF '{pdf_path.relative_to(REPO_ROOT)}' missing %%EOF end-of-file marker",
                )

    def test_docx_valid_zip_archive(self):
        """Validates DOCX reports are valid uncorrupted ZIP archives containing Word XML."""
        docx_files = list(REPO_ROOT.glob("**/*.docx"))
        valid_docxs = [
            p for p in docx_files
            if not p.name.startswith('~$')
            and not any(x in p.parts for x in [".agents", "_report_work", "node_modules"])
        ]
        self.assertGreater(len(valid_docxs), 0, "No DOCX reports found in repository")

        for docx_path in valid_docxs:
            self.assertTrue(
                zipfile.is_zipfile(docx_path),
                f"DOCX '{docx_path.relative_to(REPO_ROOT)}' is not a valid ZIP file",
            )
            with zipfile.ZipFile(docx_path) as z:
                corrupt_member = z.testzip()
                self.assertIsNone(
                    corrupt_member,
                    f"DOCX '{docx_path.relative_to(REPO_ROOT)}' has corrupt member '{corrupt_member}'",
                )
                names = z.namelist()
                self.assertIn(
                    "word/document.xml",
                    names,
                    f"DOCX '{docx_path.relative_to(REPO_ROOT)}' missing 'word/document.xml'",
                )

    def test_json_and_csv_data_syntactically_valid(self):
        """Validates JSON and CSV data files are well-formed and schema-compliant."""
        # JSON files
        json_files = list(REPO_ROOT.glob("**/results/**/*.json"))
        for jpath in json_files:
            if ".agents" in jpath.parts:
                continue
            with open(jpath, "r", encoding="utf-8-sig") as f:
                try:
                    data = json.load(f)
                    self.assertTrue(data is not None, f"JSON {jpath} is None")
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in '{jpath.relative_to(REPO_ROOT)}': {e}")

        # CSV files
        csv_files = list(REPO_ROOT.glob("**/results/**/*.csv"))
        for cpath in csv_files:
            if ".agents" in cpath.parts:
                continue
            with open(cpath, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                rows = list(reader)
                self.assertGreater(
                    len(rows),
                    1,
                    f"CSV '{cpath.relative_to(REPO_ROOT)}' has fewer than 2 rows (header + data)",
                )


# =============================================================================
# Tier 3: Cross-Feature Combinations & Consistency
# =============================================================================
class TestTier3CrossFeatureConsistency(unittest.TestCase):
    """Verifies consistency between reports, schemas, figures, and raw records."""

    def test_report_image_assets_consistency_real_data_figures(self):
        """Verify the architecture and four CSV-backed report figures are valid PNGs."""
        for fig_name in EXPECTED_REPORT_FIGURES:
            fig_path = REPO_ROOT / fig_name
            self.assertTrue(
                fig_path.exists(),
                f"Required canonical figure '{fig_name}' not found",
            )
            # Verify PNG magic bytes
            with open(fig_path, "rb") as f:
                header = f.read(8)
                self.assertEqual(
                    header,
                    b"\x89PNG\r\n\x1a\n",
                    f"Figure '{fig_name}' does not have valid PNG magic header",
                )

    def test_raw_records_data_consistency_156_rows(self):
        """Verifies raw_weather_aqi_records.csv contains exactly 156 rows across 3 cities."""
        raw_csv = locate_file(
            "tuan_2/results/athena_queries/raw_weather_aqi_records.csv",
            "results/athena_queries/raw_weather_aqi_records.csv",
            "tuan_2/results/data_exports/raw_weather_aqi_records.csv",
            "results/data_exports/raw_weather_aqi_records.csv",
        )
        self.assertIsNotNone(raw_csv, "raw_weather_aqi_records.csv not found")

        with open(raw_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(
            len(rows),
            EXPECTED_RAW_RECORD_COUNT,
            f"Expected {EXPECTED_RAW_RECORD_COUNT} raw records, found {len(rows)}",
        )

        cities = {r.get("city") for r in rows}
        self.assertEqual(
            cities,
            {"HoChiMinh", "HaNoi", "DaNang"},
            f"Expected 3 target cities, found {cities}",
        )

        # 52 records per city
        for city in ["HoChiMinh", "HaNoi", "DaNang"]:
            count = sum(1 for r in rows if r.get("city") == city)
            self.assertEqual(
                count,
                52,
                f"City '{city}' has {count} records, expected exactly 52",
            )

    def test_unit_test_count_parity_48_tests(self):
        """Verifies unit test suite defines exactly 48 test methods across 4 test modules."""
        test_dir = locate_dir("tuan_2/tests", "tests")
        self.assertIsNotNone(test_dir, "Tests directory not found")

        modules = ["test_lambda_function.py", "test_analytics.py", "test_csv_exports.py", "test_sdk.py"]
        total_methods = 0
        for mod in modules:
            mod_path = test_dir / mod
            self.assertTrue(mod_path.exists(), f"Unit test module '{mod}' missing")
            content = mod_path.read_text(encoding="utf-8")
            methods = re.findall(r"def\s+(test_[a-zA-Z0-9_]+)\s*\(", content)
            total_methods += len(methods)

        self.assertEqual(
            total_methods,
            EXPECTED_UNIT_TEST_COUNT,
            f"Found {total_methods} test methods in unit tests, expected {EXPECTED_UNIT_TEST_COUNT}",
        )

    def test_athena_ddl_and_code_schema_consistency(self):
        """Verifies Athena DDL files define expected tables matching Lambda S3 schema."""
        athena_dir = locate_dir("tuan_2/athena", "athena")
        self.assertIsNotNone(athena_dir, "Athena directory not found")

        ddl_table = locate_file(
            "tuan_2/athena/create_table.sql",
            "athena/create_table.sql",
            "tuan_2/athena/create_table_vietnam_weather_aqi.sql",
            "athena/create_table_vietnam_weather_aqi.sql",
        )
        self.assertIsNotNone(ddl_table, "Athena table DDL SQL file not found")
        content = ddl_table.read_text(encoding="utf-8")
        self.assertIn("weather_aqi_db", content, "Database name 'weather_aqi_db' missing in DDL")
        self.assertIn("us_aqi", content, "Column 'us_aqi' missing in DDL")
        self.assertIn("pm2_5", content, "Column 'pm2_5' missing in DDL")


# =============================================================================
# Tier 4: Real-World Acceptance Scenarios (Project Readiness & Hygiene)
# =============================================================================
class TestTier4ProjectReadiness(unittest.TestCase):
    """Verifies root navigation entry points, security hygiene, and autonomy."""

    def test_root_entrypoints_and_navigation(self):
        """Verifies root README.md, .gitignore, and requirements.txt are configured."""
        root_readme = REPO_ROOT / "README.md"
        self.assertTrue(root_readme.exists(), "Root README.md is missing")
        content = root_readme.read_text(encoding="utf-8")
        self.assertIn(GITHUB_REPO_URL, content, "Root README.md missing GitHub repository URL")
        self.assertIn("tuan_1", content.lower(), "Root README.md missing navigation to tuan_1")
        self.assertIn("tuan_2", content.lower(), "Root README.md missing navigation to tuan_2")

        root_gitignore = REPO_ROOT / ".gitignore"
        self.assertTrue(root_gitignore.exists(), "Root .gitignore is missing")

        root_reqs = REPO_ROOT / "requirements.txt"
        self.assertTrue(root_reqs.exists(), "Root requirements.txt is missing")

    def test_security_cleanliness_no_plaintext_credentials(self):
        """Verifies no AWS Secret Access Keys or credentials are committed in plaintext."""
        # Pattern for standard 40-character AWS secret access key
        secret_key_pattern = re.compile(r"""(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*=\s*['"]([A-Za-z0-9/+=]{40})['"]""")

        files_to_check = list(REPO_ROOT.glob("**/*.py")) + list(REPO_ROOT.glob("**/*.ps1"))
        for path in files_to_check:
            if ".agents" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            matches = secret_key_pattern.findall(text)
            # Ignore test dummy strings like 'OFFLINE_TESTING' or 'MOCK'
            real_matches = [m for m in matches if "mock" not in m.lower() and "dummy" not in m.lower()]
            self.assertEqual(
                len(real_matches),
                0,
                f"Potential plaintext AWS secret key in '{path.relative_to(REPO_ROOT)}'",
            )

    def test_week_modules_self_contained(self):
        """Verifies both tuan_1 and tuan_2 contain individual READMEs and setup scripts."""
        tuan_1 = REPO_ROOT / "tuan_1"
        tuan_2 = REPO_ROOT / "tuan_2"

        if tuan_1.exists():
            self.assertTrue(
                (tuan_1 / "README.md").exists(),
                "tuan_1/README.md is missing",
            )
        if tuan_2.exists():
            self.assertTrue(
                (tuan_2 / "README.md").exists(),
                "tuan_2/README.md is missing",
            )


# =============================================================================
# Standalone CLI Entry Point with Formatted Status Matrix
# =============================================================================
if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    print("=" * 80)
    print("  WEATHER AWS FINAL TERM — E2E ACCEPTANCE TEST SUITE (TIERS 1 - 4)")
    print(f"  Target Repository: {REPO_ROOT}")
    print(f"  GitHub Reference : {GITHUB_REPO_URL}")
    print("=" * 80)

    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestSuite()

    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryAndCornerCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4ProjectReadiness))

    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(f"  SUMMARY: {result.testsRun} tests executed | "
          f"{len(result.failures)} failures | "
          f"{len(result.errors)} errors | "
          f"{'PASSED 100%' if result.wasSuccessful() else 'IN PROGRESS / PENDING MILESTONES'}")
    print("=" * 80)

    sys.exit(0 if result.wasSuccessful() else 1)
