# CMCT — TẬP 1 REV18 PENDING FULL-GATE QUEUE

Date: 2026-10-16

## Authoritative base — guarded
Next mutation must use ONLY the promoted REV17 declared by:
`checkpoints/T1_REV17_PROMOTED_2026-10-16.md`

Required exact base:
- DOCX: `Tap_1_PRINT_MASTER_REV17_RECONSTRUCTED_CONSOLIDATED_TOCSYNC_2026-10-16.docx`
- DOCX SHA-256: `2a6e0ade56225686bca38bd95155425e70c8ab52df9be58cbacab6a69ff5c5cc`
- promoted render: 583 pages
- PDF SHA-256: `7ff2383639f962c75361929136c89d8595d8691b588c53fdaafef996127d11b0`
- M5 = 23/125
- M4 = 124/125

Do NOT mutate from the 585-page Library variant.
See `checkpoints/T1_REV17_SOURCE_GUARD_2026-10-16.md`.

## New post-REV17 FULL-GATE queue

### #111 Mãng Cầu Xiêm — FULL-GATE PASS
Selected file:
- Wikimedia Commons: `File:Soursop leaves.jpg`
- Exact identity: structured data depicts `Annona muricata`
- Exact medicinal part: leaf
- Exact represented form: detached/harvested fresh leaves (“Soursop leaves in a bag”)
- Manuscript permits leaf material in fresh or gently dried form; this row is controlled as fresh detached leaves.
- Author: Zenyrgarden
- Provenance: own work → Wikimedia Commons
- License: CC BY-SA 4.0
- Original dimensions: 2448 × 3264
- Original bytes: 1,417,626
- Commons SHA-1: `59ad698ea6726b28b821a562c9a97ceec0f421d7`
- SHA-256: `c09c42e0345d112a2f617860b0e0c9ac565747d7b704fc74db4bc7d7a9d16392`
- Binary/provenance ingest run: 38837326929 — SUCCESS
- Status: FULL-GATE PASS
- Mutation rule: insert only into the next revision derived from the exact promoted REV17 base.

### #121 Chùm Ruột — FULL-GATE PASS
Selected file:
- Wikimedia Commons: `File:Phyllanthus acidus - whole and cross section.jpg`
- Exact identity: `Phyllanthus acidus`
- Exact medicinal part: fruit
- Exact represented form: detached fresh whole fruit + cross section
- Manuscript permits fruit and the fresh form (“rửa sạch, dùng ngay”); caption must explicitly represent fresh fruit and must not imply root use.
- Author: Salil Kumar Mukherjee
- Provenance: own work / Wikimedia Commons
- License: CC BY-SA 4.0
- Original dimensions: 4416 × 3034
- Original bytes: 1,681,409
- Commons SHA-1: `5903c265374070fec2ef6da37b2f80e975abb1b3`
- SHA-256: `879abca6c050e24dd99f2d232c7d2403b3e7e020c428961f90f0628797ecbbe5`
- Binary/provenance ingest run: 38833574294 — SUCCESS
- Status: FULL-GATE PASS
- Safety/caption control: fruit only; manuscript warns root/root-bark use is toxic/high-risk and must not be represented by this image.

Rejected alternate for #121:
- `File:Phyllanthus acidus2.jpg` is exact detached/market fruit and Public Domain, but its source/author are only machine-assumed from legacy Commons metadata. It passed binary/hash but is not selected because the CC BY-SA 4.0 own-work candidate above has a cleaner provenance chain.

## Current execution state
- Promoted manuscript M5 remains 23/125 until a controlled mutation is performed.
- New FULL-GATE queue after promotion = 2 rows (#111, #121).
- If/when #111 and #121 are mutated from the exact promoted REV17 base, expected M5 count becomes 25/125, subject to render/TOC/regression PASS.
- Remaining unfilled M5 slots before mutation = 102/125; after successful #111 + #121 mutation = 100/125.
- M4 #78 remains unresolved at exact-variety reusable natural-photo level.
- Two historical CORRECTION-READY IDs in #1–25 remain unrecovered and MUST NOT be inferred.

## Targeted-search verdicts since REV17 promotion
- #51–58: no new FULL-GATE.
- #67–75: no new FULL-GATE.
- #76–85: no new FULL-GATE.
- #86–97: no new FULL-GATE.
- #101–110: no new FULL-GATE.
- #111–125 broad Commons pass: #121 promoted to FULL-GATE after exact detached-fruit verification; other rows remain HOLD unless individually re-verified.

## Next exact action
1. Continue FULL-GATE acquisition for remaining M5 rows while the exact promoted 583-page REV17 raw source is being recovered/verified.
2. Queue PASS rows here; do not mutate the 585-page Library variant.
3. When exact promoted base is available: mutate queued PASS batch -> full render -> actual page-map -> TOC sync -> re-render -> DOCX structural QA -> raster QA -> changed-page high-resolution visual regression.
4. Promote REV18 only if all controller checks PASS.
5. Continue M4 #78 exact-variety natural-photo acquisition in parallel.
6. Defer literal all-page 100%-zoom final gate until M4/M5 stabilize.
