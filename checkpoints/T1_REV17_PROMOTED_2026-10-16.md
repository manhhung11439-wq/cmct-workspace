# CMCT — TẬP 1 REV17 CONTROLLED PROMOTION CHECKPOINT

Date: 2026-10-16

## Authoritative source
- Promoted controlled source-of-truth: `Tap_1_PRINT_MASTER_REV17_RECONSTRUCTED_CONSOLIDATED_TOCSYNC_2026-10-16.docx`.
- DOCX SHA-256: `2a6e0ade56225686bca38bd95155425e70c8ab52df9be58cbacab6a69ff5c5cc`.
- Lineage: raw promoted REV16 DOCX was not recoverable on the active Files/Library surface at mutation time. REV17 was therefore reconstructed from recoverable REV15 + exact verified REV16 delta (#16 Cúc Hoa, #99 Trà Xanh) + all currently locked FULL-GATE rows. This is a controlled reconstruction; no byte-identical claim is made against the unavailable raw REV16.
- Prior `Tap_1_PRINT_MASTER_REV17_M5_028_PRETOC_2026-10-15.docx` is superseded.

## M5 manuscript coverage
Actual M5 drawings = **23/125**:
#1, #2, #3, #7, #11, #13, #14, #16, #17, #20, #26, #28, #29, #41, #42, #46, #49, #50, #66, #78, #81, #98, #99.

Remaining M5 slots without actual drawing = **102/125**.

The two archive-unrecovered historical CORRECTION-READY IDs in #1–25 remain unrecovered and were **NOT inferred**.

New/reconstructed insertions in this controlled mutation:
- REV16-delta reconstruction: #16, #99.
- New FULL-GATE rows: #1, #2, #7, #11, #13, #14, #17, #20, #26, #28, #29, #42, #46, #49, #50, #66, #81.
- Existing REV15 M5 retained: #3, #41, #78, #98.

## FULL-GATE rule
Every newly inserted M5 row was locked for:
identity/material → medicinal part → preparation/form → provenance → author → file-level license → authentic original bytes/hash.

Original evidence bytes are preserved separately. Clean JPEG insertion derivatives were created only to remove malformed EXIF/container metadata that caused DOCX parsing failure; derivative hashes were recorded separately.

## M4
M4 manuscript coverage = **124/125**.
Only #78 Ngân Sài Hồ remains unresolved at exact-variety natural-photo level.
Accepted taxon: `Mesostemma dichotomum var. lanceolatum` (syn. `Stellaria dichotoma var. lanceolata`).
Species-level natural images, herbarium specimens, and illustrations remain prohibited substitutes.

## Render / TOC / regression controller
- Rendered PDF pages: **583**.
- PNG pages: **583/583**.
- Raster dimensions: **1414×2000** for all pages.
- Zero-byte raster pages: **0**.
- Monograph heading page-map: **125/125**.
- TOC entries: **125/125**.
- TOC/page-map mismatch: **0**.
- Group 2 actual page: **163**; TOC synchronized.
- DOCX ZIP integrity: **PASS**.
- Comments: **0**.
- Tracked insertions/deletions: **0 / 0**.
- Broken image relationships: **0**.
- PDF text blocks outside page: **0**.
- Changed-page visual QA: **19/19 insertion pages PASS**.
- TOC visual QA pages 6–9: **PASS**.
- Rendered PDF SHA-256: `7ff2383639f962c75361929136c89d8595d8691b588c53fdaafef996127d11b0`.

Literal final all-page 100%-zoom review remains **DEFERRED by project rule** until M4/M5 stabilizes.

## Controller state
- REV17 controlled mutation batch = **PASS / PROMOTED**.
- M5 = **23/125**.
- M4 = **124/125**.
- TẬP 1 FINAL CONTROLLER = **NOT PASS**.
- Publication-image completion = **NOT READY**.

## Next exact action
1. Continue M5 FULL-GATE acquisition for the remaining 102 slots from this REV17 source.
2. Preserve all HOLD/reject decisions; do not promote species-only or living-organism imagery to processed M5 unless manuscript explicitly permits the fresh harvested form and the file role matches.
3. Continue M4 #78 exact-variety natural-photo acquisition in parallel.
4. Every new real PASS batch: mutate from this REV17 → full render → actual page-map → TOC sync → re-render → structural/raster/changed-page regression QA.
5. Only after M4/M5 stabilizes: literal all-page 100%-zoom review → rerun Final Controller.
