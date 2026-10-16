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

### #109 Lá Bàng — FULL-GATE PASS
Selected file:
- Wikimedia Commons: `File:444Talisay leaves camote slices 01.jpg`
- Exact identity: file description names `Terminalia catappa L.`; Commons category = `Terminalia catappa leaves`.
- Exact medicinal part: leaf.
- Exact represented form: detached fresh leaf, visibly separated from the source tree and held in hand.
- Manuscript permits fresh leaf (“rửa sạch, dùng ngay”) or gently dried leaf; this row is controlled as fresh detached leaf.
- Author: Judgefloro.
- Provenance: own work → Wikimedia Commons.
- License: CC0.
- Original dimensions: 4608 × 3456.
- Original bytes: 6,528,493.
- Commons SHA-1: `a58e812ec4a54684557c087662555e446580f467`.
- SHA-256: `b9f1a570100b5a2d8d51efa1e5828f967afb13c3426c0bd3e36c0abf60cf409a`.
- Binary/provenance ingest run: 38836956723 — SUCCESS.
- Visual material-state check: PASS.
- Status: FULL-GATE PASS.
- Mutation rule: insert only into the next revision derived from the exact promoted REV17 base.

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
- New FULL-GATE queue after promotion = 3 rows (#109, #111, #121).
- If/when #109, #111 and #121 are mutated from the exact promoted REV17 base, expected M5 count becomes 26/125, subject to render/TOC/regression PASS.
- Remaining unfilled M5 slots before mutation = 102/125; after successful #109 + #111 + #121 mutation = 99/125.
- M4 #78 remains unresolved at exact-variety reusable natural-photo level.
- Two historical CORRECTION-READY IDs in #1–25 remain unrecovered and MUST NOT be inferred.

## Targeted-search verdicts since REV17 promotion
- #51–58: no new FULL-GATE.
- #67–75: no new FULL-GATE.
- #76–85: no new FULL-GATE.
- #86–97: no new FULL-GATE.
- #101–110: no new FULL-GATE.
- #111–125 broad Commons pass: #121 promoted to FULL-GATE after exact detached-fruit verification; other rows remain HOLD unless individually re-verified.


### #51–58 targeted rerun — NO NEW FULL-GATE
- Run 38839389552: SUCCESS after manuscript-exact role re-lock.
- #51 Long Đởm Thảo: search returned materia-medica PDFs/illustrations, not an exact reusable photograph of dried root + rhizome.
- #52 Bồ Công Anh: top crude-drug file remains `Taraxaci herba cum radix 132292.jpg`, but file-level species is `Taraxacum officinale`, not manuscript-locked `T. mongolicum` → reject for insertion.
- #53 Bản Lam Căn: exact `Isatis tinctoria` photos found are botanical/live or specimen images, not dried root cut into segments.
- #54 Xạ Can: no exact reusable dried rhizome photograph recovered.
- #55 Xích Thược: no exact reusable unpeeled dried-root/sliced `Paeonia lactiflora` photograph recovered.
- #56 Địa Cốt Bì: no exact reusable dried root-bark photograph recovered.
- #57 Thanh Hao: no exact reusable shade-dried aerial-herb photograph recovered.
- #58 Xuyên Tâm Liên: no exact reusable dried/cut aerial-herb photograph recovered.
- Verdict: 0 new PASS; no manuscript mutation triggered.


### Direct original-binary visual holds — preserved
- #90 Rau Ngót: Commons file `'Maddaji' or Leaf Asparagus,Sauropus androgynus.jpg` has exact file-level identity, author AditiB08, CC BY-SA 4.0 and original-byte/hash PASS, but direct original-image inspection shows the leaves still attached to a living plant. M5 fresh/dried leaf material gate = HOLD.
- #100 Cây Lá Bỏng: both verified original candidates (`Kalanchoe pinnata leaf.jpg`, `Miracle leaf.jpg`) show leaves attached to living plants; detached fresh-leaf material gate = HOLD.
- #103 Sương Sâm: `Lá sương sâm.jpg` has exact `Tiliacora triandra`, Bùi Thụy Đào Nguyên, CC BY-SA 3.0 and original-byte/hash PASS, but direct original-image inspection shows a living vine with attached leaves. M5 harvested-leaf gate = HOLD.
- #110 Lá Xoài: candidate originals have reusable licenses and authentic bytes, but one shows mango foliage/branch being handled outdoors and the ritual image uses mango leaves decoratively; the complete exact `Mangifera indica` + harvested medicinal-leaf chain is not cleanly established at file level. Status = HOLD.

## Next exact action
1. Continue FULL-GATE acquisition for remaining M5 rows while the exact promoted 583-page REV17 raw source is being recovered/verified.
2. Queue PASS rows here; do not mutate the 585-page Library variant.
3. When exact promoted base is available: mutate queued PASS batch -> full render -> actual page-map -> TOC sync -> re-render -> DOCX structural QA -> raster QA -> changed-page high-resolution visual regression.
4. Promote REV18 only if all controller checks PASS.
5. Continue M4 #78 exact-variety natural-photo acquisition in parallel.
6. Defer literal all-page 100%-zoom final gate until M4/M5 stabilize.


## Additional post-REV17 strict verification — HOLD / REJECT

### #15 Tang Diệp — HOLD
- Candidate: Wikimedia Commons `File:Ppongnip-cha.jpg`.
- File-level identity: `Morus alba`; description = “Ppongnip-cha (mulberry leaf tea)”.
- Author: 백만볼투; license CC BY 4.0; original binary/hash verified.
- Original: 740 × 493; 102,229 bytes; SHA1 `50eb44b3649ffffd8ea399b237e61b02dc1295f8`; SHA256 `62b5d6d5a489093c2e58cd3b65d497a268e395e19fed7ebc0a99fc7581680dc6`.
- Ingest run 38843470852: SUCCESS.
- Manuscript target is harvested mature mulberry leaf, dried (or explicitly honey-prepared). The candidate is the finished brewed tea, not medicinal leaf material.
- Verdict: ROLE/PREPARATION FAIL → HOLD / DO NOT INSERT.

### #19 Thiền Thoái — HOLD
- Candidate: Wikimedia Commons `File:Cicada molt.jpg`.
- Exact role/form: empty cicada molt/exuvia; description = “A cicada's molt found on a hilly region”; category = `Cicadidae exuvia`.
- Author: Srichakra Pranav; own work; CC BY-SA 4.0.
- Original: 5136 × 3344; 8,513,895 bytes.
- SHA1 `cf83a7241a3f4cc1eb9cb4659a506584e3ac7cef`; SHA256 `91104364ea98d835933a639a258cd3707dfe8b7095318aaa368c3e4e83e05ada`.
- Ingest run 38843686912: SUCCESS.
- Identity is only controlled to family-level Cicadidae; file metadata does not identify `Cryptotympana atrata` / medicinal synonym `C. pustulata`.
- Verdict: SPECIES IDENTITY FAIL → HOLD / DO NOT INSERT.

### #40 Thảo Quyết Minh — HOLD
Candidate A:
- `File:Cassia Tora (the seeds).JPG`; category `Senna tora`; author Nikitakamka; own work; CC BY-SA 4.0.
- Description = “old branch with seeds”.
- 2592 × 1944; 2,154,961 bytes; SHA1 `38050a5c787c681104ff42a704828a5c8d3a8ca7`; SHA256 `35b6ec0501bfadb21b5e93697f6f0022dfae93ccb79d27d6d29e3e16c5f3eb24`.
- Ingest run 38843348819: SUCCESS.
- Fails material/preparation gate: seeds remain on branch and are not demonstrated as mature dried Semen Cassiae / roasted medicinal seed.

Candidate B:
- `File:Gyeolmyeongja-cha.jpg`; category `Senna tora`; description = “gyeolmyeongja-cha (senna tea)”.
- Author sks2015; CC BY 4.0.
- 560 × 420; 81,031 bytes; SHA1 `9ef83b5f55ebb4f5c4a0e0e90bd4ef44c1a5f994`; SHA256 `84265d779d74cfe02e0ab04ddccf922fc735a62543029512b4dca0fa37e1f2f3`.
- Ingest run 38843409415: SUCCESS.
- Fails material-role gate: finished brewed tea, not the dried/roasted seed drug itself.
- Verdict for both: HOLD / DO NOT INSERT.

