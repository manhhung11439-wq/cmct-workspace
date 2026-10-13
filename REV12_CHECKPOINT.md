# Tập 1 REV12 — Execution checkpoint

## Controlled revision model
- REV11 = immutable audit/source copy.
- REV12_WORK = editable controlled-revision copy.
- Never rename an unchanged copy and call it REV12.
- Final REV12 only after real byte changes + QA PASS.

## Known correction targets
Apply/verify at minimum:
- #20 Sả: traditional steam practice only; burn-risk warning; no proven cold-treatment claim.
- #24 Phù Bình: fix `lifecycle lợi niệu tiêu thũng` -> `lợi niệu tiêu thũng`; frame “thấu chẩn” as historical/YHCT.
- #26/#29/#30/#31: normalize steam safety.
- #29 Rau Mùi: remove modern measles-treatment implication and “safe for children” absolute; measles requires appropriate medical care.
- #30 Lá Chanh: accepted name `Citrus × aurantiifolia (Christm.) Swingle`; synchronize TOC/heading/identity; traditional steam wording only.
- #39 Bạch Hoa Xà Thiệt Thảo: `Scleromitrion diffusum (Willd.) R.J.Wang; syn. Hedyotis diffusa Willd.`; cancer wording limited to preclinical evidence.
- #52 Bồ Công Anh: remove/qualify “thánh dược” and absolute safety wording.
- #62 Lá Mơ Lông: do not present dysentery/diarrhea treatment as safe established therapy.
- #63 Chè Dây: symptom-support wording; H. pylori requires standard eradication regimen.
- #64 Dạ Cẩm: traditional/supportive framing; no absolute safety.
- #67 Sài Đất: `Sphagneticola calendulacea (L.) Pruski; syn. Wedelia chinensis (Osbeck) Merr.`; remove absolute pediatric safety/treatment claims.
- #81 Rau Má: distinguish food use from medicinal/extract exposure; qualify rare reported liver injury.
- #87 Cây Mật Gấu: `Gymnanthemum amygdalinum (Delile) Sch.Bip.; syn. Vernonia amygdalina Delile`; verify/fix any real truncated text such as `kéo d` only if present.
- #93 Đơn Buốt: lower metabolic/BP claims to actual evidence level; snakebite not a self-treatment indication.
- #95 Sơn Đậu Căn: `Có độc —tỳ vị` -> `Có độc — tỳ vị`.
- #102 Vọng Cách: liver/BP claims traditional or preclinical, not established treatment.
- #103 Sương Sâm: no absolute safety; separate food vs medicinal use.
- #104 Sương Sáo: BP/glucose/lipid effects labeled preclinical/animal where appropriate.
- #105 Rau Càng Cua: gout/urate claims preclinical; not a gout treatment.
- #106 Rau Đắng Đất: remove `Trfav.`; qualify liver claims.
- #107 Dâm Bụt: `Hibiscus × rosa-sinensis L.`; remove “effective, safe” absolute wording.
- #117 Thài Lài: preserve snakebite emergency warning; remove absolute safety; qualify antiviral/glucose/fever evidence.

## Global scans
Contextual scan (no blind global replace):
`thánh dược`, `đặc trị`, `chuyên trị`, `chủ lực trị`, `rất an toàn`, `an toàn cho trẻ em`, `an toàn`, `trị ung thư`, `diệt H. pylori`, `trị sốt rét`, `rắn cắn`, `gout nhẹ`, `hạ đường`, `hạ áp`, `vàng da nhẹ`, `bệnh gan`.

Known mechanical defects required to be zero:
`Trfav.`, `lifecycle lợi niệu`, `kéo d` (only if truly present in the DOCX), `Có độc —tỳ vị`.

## Taxonomy synchronization
At minimum synchronize TOC + Heading 2 + identity table + relevant references/captions for:
- #30 `Citrus × aurantiifolia (Christm.) Swingle`
- #39 `Scleromitrion diffusum (Willd.) R.J.Wang; syn. Hedyotis diffusa Willd.`
- #67 `Sphagneticola calendulacea (L.) Pruski; syn. Wedelia chinensis (Osbeck) Merr.`
- #87 `Gymnanthemum amygdalinum (Delile) Sch.Bip.; syn. Vernonia amygdalina Delile`
- #107 `Hibiscus × rosa-sinensis L.`

## QA gates
- 125 monographs / Heading 2 = 125.
- TOC entries = 125; TOC mismatch = 0 using actual rendered page map.
- comments = 0; tracked changes = 0.
- DOCX ZIP integrity PASS; no broken relationships.
- Render complete PDF and visually inspect all changed pages plus spot checks.
- Accessibility/prepress checks.
- SHA256 + changelog + correction register + open-image register + page map.
- Only then create `Tap_1_PRINT_MASTER_FINAL_REV12.docx` and PDF.
- Keep `IMAGE COMPLETION = OPEN` if M4/M5 documentary images are not fully resolved.
