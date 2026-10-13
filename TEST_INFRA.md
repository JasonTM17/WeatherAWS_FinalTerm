# TEST_INFRA — E2E Acceptance Testing Infrastructure

> **Target Repository:** `https://github.com/JasonTM17/WeatherAWS_FinalTerm.git` (`d:\AWS_Final_Term`)  
> **Author:** `test_writer_e2e` (Quality Assurance & Test Specialist)  
> **Python Runtime:** Python 3.13.2 / Windows 64-bit  
> **Test Framework:** Standard Library `unittest` (Zero external vendor lock-in)  
> **Test Runner Script:** `tests/test_e2e_acceptance.py`  
> **Date:** 2026-10-13  

---

## 1. Executive Overview & Architecture

The E2E Acceptance Test Suite is an **independent, opaque-box, requirement-driven verification harness** engineered to validate all functional, non-functional, typographic, and architectural requirements (R1 through R4) defined in `ORIGINAL_REQUEST.md` and `PROJECT.md`.

```
                    +----------------------------------------------+
                    |        E2E Acceptance Test Runner            |
                    |       (tests/test_e2e_acceptance.py)         |
                    +----------------------+-----------------------+
                                           |
        +------------------+---------------+----------------+------------------+
        |                  |                                |                  |
        v                  v                                v                  v
+---------------+  +---------------+                +---------------+  +---------------+
|    TIER 1     |  |    TIER 2     |                |    TIER 3     |  |    TIER 4     |
|    Feature    |  |  Boundary &   |                | Cross-Feature |  |  Real-World   |
|   Coverage    |  | Corner Cases  |                |  Consistency  |  |  Acceptance   |
|  (R1.1 - R4.2)|  | (File Formats)|                | (156 rec, DDL)|  | (Git, Secrets)|
+-------+-------+  +-------+-------+                +-------+-------+  +-------+-------+
        |                  |                                |                  |
        v                  v                                v                  v
+---------------+  +---------------+                +---------------+  +---------------+
| tuan_1/tuan_2 |  | Zip / Magic   |                | 11 PNG Figures|  | Root README   |
| Reports W1/W2 |  | %PDF- / %%EOF |                | 28 Unit Tests |  | .gitignore    |
| GitHub Links  |  | UTF-8 BOM JSON|                | Athena Schema |  | Zero Secrets  |
+---------------+  +---------------+                +---------------+  +---------------+
```

---

## 2. Four Verification Tiers

### Tier 1: Feature Coverage (Requirements R1.1 to R4.2)
*Authoritative Source: `ORIGINAL_REQUEST.md` §R1 – §R4*

| Test ID | Method Name | Requirement Target | Authoritative Verification Criteria |
|---|---|---|---|
| **T1.1** | `test_r1_1_tuan_1_directory_structure_and_assets` | **R1.1** | Directory `tuan_1/` exists with `scripts/01_setup_s3.ps1`, `scripts/02_setup_secrets.ps1`, `docs/ARCHITECTURE.md`, diagrams, Week 1 DOCX, PDF, and XLSX. |
| **T1.2** | `test_r1_2_tuan_2_directory_structure_and_assets` | **R1.2** | Directory `tuan_2/` exists with `lambda/`, `athena/`, `scripts/`, `tests/`, `results/`, `analytics/`, and `docs/`. Retains self-contained scripts (`deploy_all.ps1`, `cleanup_all.ps1`). |
| **T1.3** | `test_r1_3_cli_execution_logs_absent` | **R1.3** | Raw CLI log `CLI_EXECUTION_LOGS.md` is purged from all repository directories. |
| **T1.4** | `test_r2_1_week_1_docx_contains_github_url` | **R2.1** | `Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.docx` contains GitHub URL: `https://github.com/JasonTM17/WeatherAWS_FinalTerm.git`. |
| **T1.5** | `test_r2_2_week_1_pdf_contains_github_url` | **R2.2** | `Bao_cao_tuan_1_Dien_toan_dam_may_Nhom_05.pdf` contains GitHub URL: `https://github.com/JasonTM17/WeatherAWS_FinalTerm.git`. |
| **T1.6** | `test_r2_3_week_1_pdf_layout_integrity` | **R2.3** | Week 1 PDF preserves layout: exactly 20 physical pages, 28 native TOC hyperlink annotations (`/Subtype /Link`, `/Dest`). |
| **T1.7** | `test_r3_1_week_2_docx_metadata_and_identities` | **R3.1** | `Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.docx` contains GitHub URL, student names (Nguyễn Tiến Sơn - 24110054, Trần Thị Ngọc Quyên - 24110051), and instructor (ThS. Huỳnh Xuân Phụng). |
| **T1.8** | `test_r3_2_week_2_pdf_exists_and_sections` | **R3.2** | `Bao_cao_tuan_2_Dien_toan_dam_may_Nhom_05.pdf` exists with GitHub URL and 6 chapters (Chương 1 đến Chương 6). |
| **T1.9** | `test_r3_3_week_2_report_technical_substance` | **R3.3** | Week 2 report documents Lambda function, EventBridge 1h scheduler, SNS air quality alerting, Athena DDL, unit test results, and figures. |
| **T1.10** | `test_r4_1_unit_test_suite_28_tests_pass` | **R4.1** | Subprocess executes unit tests (`test_lambda_function`, `test_analytics`, `test_csv_exports`): 28 tests run with 100% pass rate. |
| **T1.11** | `test_r4_2_git_commits_and_remote_tracking` | **R4.2** | Git remote origin matches `https://github.com/JasonTM17/WeatherAWS_FinalTerm.git` and commit history reflects progressive milestones. |

---

### Tier 2: Boundary & Corner Cases (Integrity & Format Validity)
*Authoritative Source: Defensive Engineering & File Format RFCs*

| Test ID | Method Name | Scope | Verification Logic |
|---|---|---|---|
| **T2.1** | `test_critical_files_non_empty` | Repository-wide | Asserts that all scripts (`.ps1`, `.py`), DDLs (`.sql`), and reports (`.docx`, `.pdf`) have byte length > 0 (excluding gitignored internal tools). |
| **T2.2** | `test_pdf_format_and_eof_markers` | Document Standards | Checks that all PDF deliverables begin with magic bytes `%PDF-` and terminate with `%%EOF` marker. |
| **T2.3** | `test_docx_valid_zip_archive` | OpenXML Standards | Verifies DOCX deliverables are uncorrupted ZIP archives (`zipfile.testzip() is None`) containing `word/document.xml`. |
| **T2.4** | `test_json_and_csv_data_syntactically_valid` | Data Lake Standards | Validates JSON schemas (with UTF-8 / UTF-8-BOM support) and CSV headers across `results/` partitions. |

---

### Tier 3: Cross-Feature Combinations & Consistency
*Authoritative Source: Report Claims vs. Source Assets Consistency*

| Test ID | Method Name | Scope | Verification Logic |
|---|---|---|---|
| **T3.1** | `test_report_image_assets_consistency_11_figures` | Visual Assets | Verifies that all 11 figures referenced in reports (`01_` to `10_` plus `architecture_report.png`) exist on disk and possess valid PNG magic headers (`\x89PNG\r\n\x1a\n`). |
| **T3.2** | `test_raw_records_data_consistency_156_rows` | Data Consistency | Verifies `raw_weather_aqi_records.csv` contains exactly 156 data rows, covering exactly 3 target cities: `HoChiMinh` (52), `HaNoi` (52), `DaNang` (52). |
| **T3.3** | `test_unit_test_count_parity_28_tests` | QA Parity | Scans unit test files and asserts exact definition parity of 28 test methods across `test_lambda_function.py` (12), `test_analytics.py` (4), and `test_csv_exports.py` (12). |
| **T3.4** | `test_athena_ddl_and_code_schema_consistency` | Schema Parity | Cross-references Athena DDL SQL tables/views with Lambda S3 partitioning schema and query columns (`us_aqi`, `pm2_5`). |

---

### Tier 4: Real-World Acceptance Scenarios (Hygiene & Autonomy)
*Authoritative Source: Repository Delivery Standards*

| Test ID | Method Name | Scope | Verification Logic |
|---|---|---|---|
| **T4.1** | `test_root_entrypoints_and_navigation` | Repository Root | Verifies root `README.md` contains GitHub link and dual-week navigation; confirms `.gitignore` and `requirements.txt` are present. |
| **T4.2** | `test_security_cleanliness_no_plaintext_credentials` | Security Compliance | Scans all scripts and source code with regex to ensure no plaintext 40-character AWS Secret Access Keys are committed. |
| **T4.3** | `test_week_modules_self_contained` | Autonomy | Asserts that `tuan_1/README.md` and `tuan_2/README.md` exist and provide self-contained execution instructions. |

---

## 3. How to Execute the Acceptance Test Suite

### Method A: Standard Python Unittest Runner (Recommended)
```powershell
py -3.13 -m unittest tests/test_e2e_acceptance.py
```

### Method B: Standalone Interactive Runner (With Header & Summary Matrix)
```powershell
py -3.13 tests/test_e2e_acceptance.py
```

### Method C: Running Individual Tiers
```powershell
# Run Tier 1 only
py -3.13 -m unittest tests.test_e2e_acceptance.TestTier1FeatureCoverage

# Run Tier 2 only
py -3.13 -m unittest tests.test_e2e_acceptance.TestTier2BoundaryAndCornerCases

# Run Tier 3 only
py -3.13 -m unittest tests.test_e2e_acceptance.TestTier3CrossFeatureConsistency

# Run Tier 4 only
py -3.13 -m unittest tests.test_e2e_acceptance.TestTier4ProjectReadiness
```

---

## 4. Milestone Traceability Matrix

| Milestone | Target Scope | Corresponding Acceptance Tests |
|---|---|---|
| **M1** | Repo Reorganization & Log Cleanup | `test_r1_1_tuan_1_directory_structure_and_assets`, `test_r1_2_tuan_2_directory_structure_and_assets`, `test_r1_3_cli_execution_logs_absent`, `test_root_entrypoints_and_navigation`, `test_week_modules_self_contained` |
| **M2** | Test Determinism & Path Resolution | `test_r4_1_unit_test_suite_28_tests_pass` |
| **M3** | Week 1 Report Update & Verification | `test_r2_1_week_1_docx_contains_github_url`, `test_r2_2_week_1_pdf_contains_github_url`, `test_r2_3_week_1_pdf_layout_integrity` |
| **M4** | Week 2 Report Creation & Conversion | `test_r3_1_week_2_docx_metadata_and_identities`, `test_r3_2_week_2_pdf_exists_and_sections`, `test_r3_3_week_2_report_technical_substance` |
| **M5** | Git Standardization & Remote Push | `test_r4_2_git_commits_and_remote_tracking`, Full Suite Pass (22/22) |
