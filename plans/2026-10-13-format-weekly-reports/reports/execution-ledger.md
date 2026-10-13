# Execution ledger
Active plan: plans/2026-10-13-format-weekly-reports/plan.md

Current phase: phase 03 full report audit, step 4.
Next step: update same Downloads submission, commit/push reviewed reports/docs and verify remote identity.
Exit criterion: 12 copied files and 93-member source ZIP match canonical; remote HEAD/readback matches published scope.

Ruling: user chose editing both reports and project source, removing AWS CLI code. Preserve functions through boto3 instead of deleting functionality. No live cloud mutation authorized by this formatting/source task.

Baseline: root README and week READMEs read; no nested AGENTS/config; git clean. Local/global Codex AgentKit office registry missing; bundled Documents/PDF loaded. Reports at tuan_1/docs and tuan_2/docs; PowerShell scripts contain direct aws invocations.

Phase 03 user ruling: confirmed Week 2 Son 10.0 h and Quyen 9.5 h, total 19.5 h. Nominated docs/WORKLOG.md is absent; create it as a portable linked index and update canonical Week 2 worklog/report tables. Supplied CSV, Excel and chart paths refer to the saved Week 1 snapshot, retained for Week 2 analysis; no new cloud-run claim. Week 1 hours remain unknown.

Phase 03 report/data gate PASS: 20/25 pages, 28/37 native TOC/PDF destinations, every quantitative table including both 24-row hourly tables, sequential captions and all raw-derived aggregates verified. Four figure hashes equal across both DOCX, Excel and canonical PNGs. Confirmed hours appear consistently in both Week 2 tables and worklog. 53 local document links valid. Eight focused report acceptance cases PASS; unchanged unit suite not rerun. Text credential/direct invocation scan PASS and diff check clean.

Phase 03 visual QA: 22 pages were pixel-identical to previously reviewed baseline 79a83ee and all 23 changed pages inspected at normal page size. First pagination repair moved source/config section headings with their tables and prevented a five-query metric table from orphaning its last row. Post-repair 36 pages equal to the fully reviewed pre-repair render; all nine changed pages inspected. The metric-table check fails for the prior split layout and passes for the final whole table on physical page 20. No overflow or footer collision observed; original margins preserved. Open-Meteo official terms and Air Quality docs verified rate limits, optional provider key and CAMS data provenance. Week 1 stale demo-key/current-source wording corrected; saved snapshots and chart hashes unchanged.

Completed audit: actual data source is tuan_2/results/athena_queries; 156 unique raw records, 52 per city; five recorded queries. Week 2 draft metrics and hours conflicted with source and user confirmation. No new AWS data is claimed.

Source implementation: boto3 project management and Athena exporter; PowerShell entry points forward to Python. Explicit offline snapshot mode, no simulated execution metadata. Query failure/timeout/pagination and deletion guards covered by 12 SDK regressions. Earlier 40-test local gate passed; chart generator changed after that run, so affected terminal regression is pending.

Documents: body left aligned, Times New Roman, native linked TOC, consistent heading/table/caption format; code boxes changed into readable specifications; four actual CSV charts synchronized. Original documents preserved in ignored work directory. Word COM used after bundled renderer could not find LibreOffice. Visual inspection identified cover style, split AQI row, old hours and stale diagram, repaired narrowly.

Authorized plan delta: user explicitly requested GitHub About and docs. Add phase 5 publication of reviewed scope. No AWS mutation. Remote main matches local base; caller has ADMIN permission; main is not protected. About is initially empty.

GitHub doc ruling: remove six old illustrative dashboards and contact sheet from public docs; retain architecture and four CSV-backed charts. Acceptance image expectation changes to those five figures, reflecting the current report contents; data/count/security oracles stay intact.

Terminal evidence: 40 local unit cases passed inside acceptance gate; 22 acceptance checks verified after one report-text repair. 13 PowerShell scripts parsed; 16 Python files syntax checked; credential/direct executable invocation scan and git diff check PASS. Live AWS NOT_RUN.

Document audit PASS: 20/24 PDF pages, 28/39 linked TOC rows; all PDF destinations checked against heading pages and DOCX bookmarks. Both cover and introduction GitHub URLs now real hyperlinks, visually inspected after export. All quantitative report tables, raw schema, workbook rows and four shared image hashes match the saved CSVs. Final audit JSON retains exact image hashes.

Word export repair: a COM Find loop stalled during hyperlink creation. Only the hidden Word process created by that export was terminated; a bounded OOXML hyperlink edit replaced the loop. Export/render and hyperlink audit then PASS; user's pre-existing Word instance preserved.

Submission: 12 files at Downloads/Bao_cao_Tuan_1_2_Nhom_05_Ban_nop, including two DOCX/two PDF, unchanged Excel, six CSV and 104-file source ZIP. ZIP contents and every copied file matched source bytes/hashes. Previous Downloads submission copied into ignored work backup, verified, then removed from Downloads.

Publication: commit beb5817079939be06121c9d02f8c1088a973c7d3 pushed to origin/main; remote ref identical. README blob 55f1557371e626a4597a83e283e3b433566cc359 and docs README blob 187f113f3a6421ff072454ee0a738a6913f774e3 match local. About description, docs homepage and twelve topics read back. No configured check-runs observed; no CI or new live deployment claim. Durable plan/audit files remain local and untracked; public changes are committed.

Phase 02 evidence: removed Week 2 7.3/7.4 and their TOC entries; native dash lists in both reports. Four old-code regressions reproduced wrong weather ordering, false all-failed success, missing partial status and dropped page-2 row equal to header. Narrow repairs pass. 44 unit cases pass with AWS credentials/profile removed and metadata disabled; 22 acceptance checks verified after excluding an Office lock file from DOCX ZIP validation (21 in full suite, repaired case rerun PASS). PowerShell 13, Python syntax 15, credential/direct-invocation scan and diff check PASS.

Source cleanup: removed 11 duplicated PNG/SVG assets and one copy-only image script; removed unused pandas/PyMuPDF/pytest dependencies and an unused test import, declared numpy directly. Test Lambda import uses temporary dummy credentials and restores the caller environment. Existing API collection deadline and missing-value policy changes are deferred; no live AWS verification or mutation.

Visual QA: 20/23 final pages, 28/37 linked TOC entries and GitHub hyperlinks. 33 pages are pixel-identical to the previous fully reviewed baseline; all 10 changed pages inspected at normal scale. Latest one-paragraph dependency wording change reviewed again on Week 2 page 6. Quantitative tables, schema, workbook data and four PNG hashes remain identical to saved CSV evidence. Package now has 92 source files; 12 final Downloads files match verified staging hashes, same single submission folder and previous version backed up internally.

User-requested source recheck: archived 92 files match the current workspace; repository HEAD and remote main equal 79a83ee002b2798c5410ba05c3df4bcc1ccd6419. Production/source text audit found zero AWS CLI references or aws executable invocations. Python AST process calls reviewed (six, all tests/PDF inspection/Git metadata); no shell=True. PowerShell AST for 13 scripts shows named Join-Path commands and dynamic invocation only of $Python. Four Python entry-point help checks PASS. Extracted ZIP ran all 44 tests PASS with AWS executable absent from PATH, AWS credentials/profile removed and metadata disabled. Archive SHA256 89a9a1c0a25bdc4215c465bbb4b6f727806356e5d3ac840808645c484a1abd86. No public changes needed; detailed evidence in source-recheck.json. Live AWS NOT_RUN.
