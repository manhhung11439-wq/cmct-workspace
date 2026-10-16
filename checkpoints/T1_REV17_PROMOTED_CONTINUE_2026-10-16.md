# CMCT — TẬP 1 REV17 PROMOTED / CONTINUE CHECKPOINT

Date: 2026-10-16

## Promoted source-of-truth
- DOCX: `Tap_1_PRINT_MASTER_REV17_M5_CONSOLIDATED_TOCSYNC_2026-10-16.docx`
- PDF: `Tap_1_PRINT_MASTER_REV17_M5_CONSOLIDATED_TOCSYNC_2026-10-16.pdf`
- DOCX SHA-256: `61c2ad6f52c632be70b384a76150fdeb7ba5625ccbc930b3d73289a536ce0275`
- PDF SHA-256: `b032b098402f9a543caa5f70f37a5c5099c84be93e7fa4ad872b73f7f6f68036`
- Rendered pages: 585

## REV17 controller state
- DOCX ZIP integrity: PASS
- Tracked insertions/deletions: 0 / 0
- Comments: none
- Broken internal relationships: none
- TOC entries: 125
- Heading/page-map: 125/125
- TOC/page mismatch: 0
- Raster pages: 585/585
- Missing/zero-byte raster pages: 0
- PDF text blocks outside page: 0
- Outer-edge dark flags: 0
- Structural controller: PASS

## Changed-page high-resolution regression QA
Reviewed the pages carrying the new consolidated REV17 M5 batch:
`14, 20, 46, 64, 72, 78, 93, 106, 131, 142, 147, 219, 237, 250, 254, 324, 384`.

Result: PASS.
- no clipping/overlap observed;
- no missing/broken image observed;
- M5 captions remain attached to intended figures;
- tables remain readable and do not collide with inserted figures;
- headers/footers/page numbers remain intact on reviewed pages.

REV17 is therefore promoted as the source-of-truth for all subsequent Tập 1 mutation.

## M5 actual manuscript coverage
REV17 contains 23/125 actual M5 drawings:
`#1, #2, #3, #7, #11, #13, #14, #16, #17, #20, #26, #28, #29, #41, #42, #46, #49, #50, #66, #78, #81, #98, #99`.

Remaining M5 slots without actual drawing: 102/125.

Do not infer the two archive-unrecovered historical CORRECTION-READY IDs in #1–25.

## M4 state
- M4 = 124/125.
- Only #78 Ngân Sài Hồ remains unresolved for the exact-variety natural-photo requirement.
- Accepted taxon: `Mesostemma dichotomum var. lanceolatum (Bunge) Arabi, Rabeler & Zarre`
  (syn. `Stellaria dichotoma var. lanceolata Bunge`).
- Exact-variety herbarium/illustration and species-level natural photographs remain prohibited substitutes.

## Current systematic acquisition — #51–58
Manuscript-locked M5 targets:
- #51 Long Đởm Thảo: root + rhizome; root harvested in autumn, washed, dried.
- #52 Bồ Công Anh: whole plant with root; fresh/dried role must be explicit.
- #53 Bản Lam Căn: root harvested in autumn, washed, dried, cut into segments.
- #54 Xạ Can: rhizome; fine roots removed, washed, dried, sliced.
- #55 Xích Thược: unpeeled root; dried and sliced; must not substitute Bai Shao processing.
- #56 Địa Cốt Bì: root bark; washed, dried.
- #57 Thanh Hao: aerial herb; dried/controlled medicinal-herb form.
- #58 Xuyên Tâm Liên: aerial herb; dried/controlled medicinal-herb form.

Latest targeted Commons search run: `38839389552` = SUCCESS.

### Verdicts from the latest run
- #51: HOLD — search results dominated by PDFs/books; no exact reusable processed root/rhizome photograph locked.
- #52: candidate `Taraxaci herba cum radix 132292.jpg` rejected for this manuscript row because the file directly identifies dried `Taraxacum officinale`, while row #52 is `Taraxacum mongolicum`; no species substitution.
- #53: HOLD — high-scoring results are primarily living/botanical `Isatis tinctoria`; no exact dried-root medicinal-material photograph locked.
- #54: HOLD — no exact processed `Iris domestica` rhizome photograph locked.
- #55: HOLD — no exact unpeeled `Paeonia lactiflora` / Radix Paeoniae Rubra processed-root photograph locked.
- #56: HOLD — no exact `Lycium chinense` dried root-bark photograph locked.
- #57: HOLD — no exact processed/dried `Artemisia annua` aerial-herb photograph locked.
- #58: HOLD — no exact processed/dried `Andrographis paniculata` aerial-herb photograph locked.

No surrogate insertion is permitted.

## Next exact execution
1. Continue M5 acquisition from the promoted REV17 source.
2. Prioritize exact crude-drug files with explicit processed/harvested material role and file-level provenance.
3. For every candidate require:
   identity/material → medicinal part → preparation/form → provenance → author → reusable file-level license → authentic original bytes/hash.
4. Each real PASS batch only:
   REV17 mutation → render → derive page-map → TOC sync → re-render → structural/raster QA → high-resolution changed-page regression.
5. Continue exact-natural M4 #78 in parallel.
6. Literal all-page 100%-zoom review remains deferred until M4/M5 image completion stabilizes.
7. Tập 1 Final Controller = NOT PASS until image completion + final visual gate are complete.
