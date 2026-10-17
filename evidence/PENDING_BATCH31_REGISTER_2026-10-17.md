# CMCT — Tập 1 — Pending Batch31 FULL-GATE Register

Date: 2026-10-17

## Authoritative base

- Source: `Tap_1_PRINT_MASTER_REV18_M5_FULLGATE_BATCH30_TOCSYNC_2026-10-17.docx`
- Batch30 M5: 70/125
- Remaining before Batch31 mutation: 55
- Batch31 has **not** yet been mutated/rendered. Do not count projected rows as manuscript execution until DOCX mutation + render/page-map/TOC/regression PASS.

## READY — #37 Dây Thìa Canh

Target: `Gymnema sylvestre` — §37.5 uses leaf + vine/stem, washed/cut and dried; dry material may be used for decoction/tea/extract.

Source: Suchitra Boxi, Haleshi C. “Phytochemical Screening and Pharmacognostic studies and Antidiabetic activity of Meshashringi (Gymnema sylvestre (Retz.) R.Br. ex. Sm.) Leaf and Stem Components.” Acta Botanica Plantae. 2026;5(1):4–10. DOI 10.51470/ABP.2026.05.01.04.

- License: CC BY 4.0.
- Source text: collected material was shade-dried and powdered; Results explicitly identify powdered leaf and stem material of `Gymnema sylvestre`; Figure 1A = “Plant powder sample”.
- PDF SHA-1: `5cfdd1ae56e26648b909935546951093a45793d2`
- PDF SHA-256: `1fd99f18d519424fa99e9d68ccc9e2d2bfb75c2215b00407c9df1b35c3ddb7f0`
- Figure 1 original embedded JPEG: 709×943; SHA-1 `c64585245d4a79ac5649a67e324fd356d536c244`; SHA-256 `05be96c42977e6d8173bef8692ce6d04da65bfe5f8bda7d5e0b04d935259855d`
- Controlled crop: panel A only, box `[0,0,230,225]`, 230×225 PNG.
- Crop SHA-1: `28e55d46ba65d168f7584f2c0582d6f19571c76d`
- Crop SHA-256: `ddd916f5d055ca30afc839b740509ea4cf561d92a2946a5ed8b80be25e37d32c`
- Transform: crop only; no retouch/recolor/content alteration.
- Visual controller: PASS — bowl of dried leaf/stem powder, panel label A retained, no adjacent microscopy panel.

Decision: **FULL-GATE PASS / READY FOR BATCH31 MUTATION**.

Proposed conservative caption:
“Ảnh 5 – Dược liệu Dây Thìa Canh (Gymnema sylvestre (Retz.) R.Br. ex Schult.): bột lá và thân đã làm khô. Nguồn: Boxi S., Haleshi C., Acta Botanica Plantae 2026;5(1):4–10, Hình 1A; DOI 10.51470/ABP.2026.05.01.04; CC BY 4.0. Ảnh là crop kiểm soát từ panel A ‘Plant powder sample’, không thay đổi nội dung dược liệu.”

## READY — #118 Kim Vàng

Target: `Barleria lupulina Lindl.`

Manuscript:
- §118.1 explicitly: used part = leaves, young branches; fresh.
- §118.5 permits fresh use.

Source: Chhabra A., Gupta R. “Pharmacognostical Study of Barleria lupulina Lindl. - A Lesser-known Medicinal Herb.” J Ayu Int Med Sci. 2025;10(6):91–97. DOI 10.21760/jaims.10.6.13.

- License: CC BY 4.0.
- Article states fresh whole-plant parts of exact `Barleria lupulina` were procured and authenticated.
- Figure 1 caption: B = adaxial surface of leaf; Figure 1 shows fresh parts of `Barleria lupulina`.
- Selected original embedded Figure 1B bytes; no crop.
- Dimensions: 290×513 JPEG.
- Bytes: 16,096.
- SHA-1: `32a85502c96688bae29217bc749fc5ee0fe9873d`
- SHA-256: `b25b63579ec913e3ca4e4e61f2cee0270ea7f6c3f624f161d1e9b88fb7ce57e9`
- Source PDF SHA-1: `de87837d8be155492f2f2dfb7c9a7ccf28849870`
- Source PDF SHA-256: `e1a7b06360cb7502d5677cde7c9481a3d5cf1b4a4df3b31d81094526b41def13`
- Visual controller: PASS — detached single leaf on neutral background; not living/in-ground imagery.

Decision: **FULL-GATE PASS / READY FOR BATCH31 MUTATION**.

Proposed conservative caption:
“Ảnh 5 – Dược liệu Kim Vàng (Barleria lupulina Lindl.): lá tươi đã thu hái. Nguồn: Chhabra A., Gupta R., J Ayu Int Med Sci. 2025;10(6):91–97, Hình 1B; DOI 10.21760/jaims.10.6.13; CC BY 4.0. Sử dụng ảnh gốc của panel B ‘Adaxial surface of leaf’, không chỉnh sửa nội dung dược liệu.”

## HOLD / REJECT updates from completed workflows

- #113 Lá Cẩm — exact `Dicliptera tinctoria` / synonym chain and reusable license locked, but visual review of `File:Lá cẩm.jpg` shows a living flowering plant with leaves/flowers still attached. **HOLD/REJECT for M5 role**.
- #123 Bán Chi Liên — Frontiers 2024 CC BY source exact `Scutellaria barbata`; Figure 1 is living aerial morphology over growth stages; other figures analytical. **HOLD**.
- #125 Cam Thảo Đất — PMC3733203 pharmacognosy source is CC BY-NC-SA 3.0 and its figures are drawing/morphology/microscopy rather than a reusable commercial-safe dried whole-plant material image. **HOLD**.
- #100 Cây Lá Bỏng — Frontiers 2023 CC BY exact `Kalanchoe pinnata`, but detached-leaf Figure 2 is propagation/plantlet formation after 9–15 days, not a medicinal-material preparation image. **HOLD**.
- #107 Dâm Bụt — detached flower candidate has reusable license and “freshly plucked” role, but metadata does not lock exact `Hibiscus × rosa-sinensis`. Exact-category images reviewed are generally attached/living. **HOLD**.
- #32 and #120 WIKTROP species probe — species pages resolved but `downloaded = 0` media candidates for both. **OPEN**.

## Next exact action

1. Once DOCX runtime is available, materialize Batch30 authoritative source.
2. Mutate #37 and #118 only, after §37.5 and §118.5 tables respectively, before §37.6 / §118.6.
3. Save Batch31 high-resolution source.
4. Build layout-preserving low-res QA surrogate.
5. Render complete QA PDF; regenerate 125-heading page map; update static TOC only from actual rendered reflow.
6. Rerender and require TOC/page-map mismatch = 0.
7. Changed-page regression around both #37 and #118 plus affected TOC pages.
8. Only after PASS, lock Batch31 checkpoint. Projected structural M5 after successful mutation = 72/125; remaining = 53.
9. M4 #78 remains UNRESOLVED / NO SUBSTITUTE.
10. Literal high-resolution 100%-zoom all physical pages remains deferred until M5 stabilizes.
