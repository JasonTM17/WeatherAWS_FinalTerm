# Revision requested by the user

## Outcome and authority
Remove Week 2 sections 7.3 and 7.4 shown in the screenshot. Use native dash lists in both reports. Review and narrowly repair source defects, remove duplicate chart assets, refresh final Downloads bundle and the authorized GitHub publication. No new AWS deployment or data query.

## Ordered steps and exits
1. Audit current source and report bounds. Exit: exact removals and reproducible defects selected.
2. Repair historical weather joining by timestamp and all-fetch-failure success reporting; correct SDK pagination header handling. Remove unreferenced duplicated chart images and the copy-only detailed-image entry point. Exit: regressions fail old behavior and pass the repairs; canonical chart references valid.
3. Edit the retained document builder: remove 7.3–7.4; native dash numbering for body lists; describe repaired source behavior accurately. Export native TOC/PDF and refresh Markdown. Exit: no removed headings/solid-dot bullets, clickable TOC/GitHub, all quantitative values/images unchanged.
4. Terminal verification and publication. Exit: local unit/acceptance gate, syntax/parser/credential/diff checks, all rendered pages checked; package hash/integrity verified; remote readback matches commit and one final Downloads folder remains.

## Verification budget
- Before implementation: four focused regressions (timestamp reorder, all fetch failure, partial failure, header-only first page) on old code.
- After source batch: affected regressions once, then one terminal acceptance suite including unit tests. Rerun only failing/changed checks.
- Documents: existing final data/TOC audit with current heading counts plus numbering checks; render with established Word COM/PDFium fallback. Review all final pages and compare unchanged dataset/image hashes.
- Rollback: retain committed baseline beb5817 and ignored work snapshots. No destructive live AWS action.

Root owns all edits. No delegation. Out-of-scope improvements such as new concurrent API collection or changing missing-value schema are deferred.

## Completion
All four steps completed. See final-audit.json, source-gate.json, bundle-audit.json and revision-page-comparison.json. Offline test log confirms 44 cases; publication verified at commit 79a83ee002b2798c5410ba05c3df4bcc1ccd6419. Downloads bundle updated in place.
