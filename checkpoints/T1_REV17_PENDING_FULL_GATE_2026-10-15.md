# CMCT — TẬP 1 PENDING REV17 FULL-GATE CHECKPOINT

Date: 2026-10-15

## Source control
- Promoted source-of-truth remains: `Tap_1_PRINT_MASTER_REV16_M5_016_099_TOCSYNC_2026-10-15.docx`.
- REV16 M5 actual drawings: 6/125 (#3, #16, #41, #78, #98, #99).
- M4 remains 124/125; only #78 Ngân Sài Hồ is unresolved at exact-variety natural-photo level.
- Existing `Tap_1_PRINT_MASTER_REV17_M5_028_PRETOC_2026-10-15.docx` contains #28 only and is NOT promoted.
- Do not infer the two archive-unrecovered historical CORRECTION-READY IDs in #1–25.

## Newly locked / acquired M5 candidates for one consolidated REV17 batch

### #2 Tía Tô — FULL-GATE PASS
- File: Wikimedia Commons `File:Perilla leaves.jpg`.
- Structured data depicts `Perilla frutescens`; file description identifies detached kkaennip/perilla leaves.
- Manuscript M5 target: leaf; fresh or dried form permitted. This image is controlled as the fresh harvested/detached-leaf form.
- Source: Flickr → Wikimedia Commons; Flickr review confirmed.
- Author: Sous Chef.
- License: CC BY 2.0.
- Commons SHA1: 57f55f6f6db99853238253aba56559b0d9118839.
- Original-binary ingest run 38727978197: SUCCESS; artifact 11969590327.
- Status: FULL-GATE PASS; NOT a recovery claim for either archive-unrecovered historical CORRECTION-READY ID.


### #1 Cát Căn — candidate FULL-GATE, identity mapping controlled
- File: Wikimedia Commons `File:Wild Pueraria slices.jpg`.
- File captions: “Wild Pueraria slices” / “野生葛根片”.
- Official medicinal mapping used for identity reconciliation: 野葛 / Pueraria lobata → Puerariae Lobatae Radix; dried root, freshly cut into thick slices/pieces, then dried.
- Manuscript accepts Pueraria lobata as a source for #1 and requires root slices dried.
- Author: Fumikas Sagisavas.
- Source: own work.
- License: CC0 1.0.
- Commons checksum: c85f8ea31da21f9ed600e160b1b3cf979d818eb0.
- Original-binary ingest run 38725302371: SUCCESS.
- Status: PASS candidate after controlled botanical-source mapping; NOT a recovery claim for historical CR IDs.

### #11 Bạch Chỉ — FULL-GATE PASS
- File: Wikimedia Commons `File:Dried angelica dahurica slices.jpg`.
- Direct file identity: dried Angelica dahurica slices; structured data depicts Angelica dahurica.
- Manuscript: Radix Angelicae Dahuricae; root; harvested then dried.
- Author: Fumikas Sagisavas.
- Source: own work.
- License: CC0 1.0.
- Original-binary ingest run 38724907798: SUCCESS.
- Artifact: 11967706427.
- Status: FULL-GATE PASS.

### #13 Thương Nhĩ Tử — FULL-GATE PASS for dried raw-fruit form
- File: Wikimedia Commons `File:Xanthium strumarium MHNT.BOT.2004.0.213.jpg`.
- Direct identity: Xanthium strumarium; four brown dried burrs; fruits and seeds.
- Manuscript: Fructus Xanthii; fruit with hooked spines; mature fruit; preparation form must be explicit.
- Caption/control for insertion must state dried/raw fruit form and must NOT imply roasted/processed form.
- Photographer: Roger Culos.
- Source: own work / MHNT.
- License: CC BY-SA 3.0.
- Original-binary ingest run 38725552208: SUCCESS.
- Artifact: 11968041696.
- Status: FULL-GATE PASS for dried raw-fruit form.

### #28 Thông Bạch — FULL-GATE PASS
- File: Wikimedia Commons `File:Starr 070730-7902 Allium fistulosum.jpg`.
- Exact species: Allium fistulosum; harvested/bundled material in store; white basal portion and roots visible.
- Manuscript target: fresh white bulb/stalk base with roots.
- Authors: Forest & Kim Starr.
- License: CC BY.
- Original-binary ingest: PASS with exact Commons SHA1.
- Already inserted in REV17-PRETOC, but REV17 not promoted.
- Status: FULL-GATE PASS.

### #50 Lô Căn — FULL-GATE PASS
- File: Wikimedia Commons `File:Dried reed root segments.jpg`.
- Direct file description: “Dried reed root segments” / “芦根 / 干芦苇根段”.
- Category: Phragmites australis products.
- Manuscript: Phragmites australis; Rhizoma Phragmitis; rhizome fresh/dried; dried form cut into segments.
- Author: Fumikas Sagisavas.
- Source: own work.
- License: CC0 1.0.
- Commons SHA1: c136472eba93453c30f15414de830ceb05cac92b.
- Original-binary ingest run 38724747453: SUCCESS.
- Artifact: 11967805356.
- Status: FULL-GATE PASS.

## Systematic processed-material searches
- #26–50: completed.
- #51–75: run 38724494988 completed SUCCESS.
- #76–100: run 38724583436 completed SUCCESS.
- #101–125: run 38724643985 completed SUCCESS.
Most hits in these ranges were live plants, catalogue scans, herbarium/illustrations, or PDFs and are NOT promoted to M5.

Specific rejects / HOLD:
- #70 Sophora flavescens Wellcome hit is a historical woodcut illustration, not a processed crude-drug photograph → reject for M5.
- #91 dried lotus-leaf candidate lacks direct file-level species identity → HOLD.
- #25 douchi image does not distinguish medicinal Dàn Dòu Chǐ from food douchi → HOLD.
- #19 iNaturalist sequence has exact taxon/CC BY/attribution but shows moulting sequence rather than isolated empty exuviae → HOLD.
- #100 Kalanchoe candidate shows leaf still attached to plant → HOLD.
- #23 available Vitex trifolia fruit photos show fruit on living plant, not dried medicinal fruit → HOLD.
- #48 available “Dried gardenia seeds” is wrong part relative to manuscript’s mature dried whole fruit → reject.

## M4 #78 parallel state
Exact-variety search remains unresolved. Exact-name results are preserved/herbarium specimens, not natural field photographs. Species-level natural images and exact-variety herbarium sheets remain prohibited substitutes.

## Next exact mutation sequence
When DOCX/runtime access is available:
1. Rebuild REV17 from REV16 with the consolidated PASS batch (#1 if final identity mapping remains accepted, #2, #11, #13, #28, #50), rather than stacking uncertain PRETOC branches.
2. Preserve all existing REV16 M5 upgrades.
3. Render full artifact.
4. Derive actual page-map; do not reuse the prior #28-only +1 TOC shift.
5. Regenerate/sync all affected TOC page numbers.
6. Re-render.
7. Run DOCX structural QA, 100% raster presence checks, TOC/heading page-map regression, and high-resolution changed-page visual QA.
8. Promote REV17 only if all checks PASS.
9. Continue systematic acquisition of remaining M5 slots and M4 #78 in parallel.
10. Defer literal all-page 100%-zoom final visual gate until M4/M5 stabilizes.
