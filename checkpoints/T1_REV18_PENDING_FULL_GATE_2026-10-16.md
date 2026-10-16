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


### #30 Lá Chanh — HOLD after original-binary visual inspection
- Candidate: Wikimedia Commons `File:Citrus aurantifolia leaves.jpg`.
- Exact identity/provenance/license: category `Citrus × aurantiifolia`; author Vinayaraj; own work; CC BY-SA 3.0.
- Original binary: 2,484×3,306 JPEG; 1,990,892 bytes; SHA1 `45349373b6dafdcb10e8e405f5acac299ef40345`; SHA256 `e17c761d006000c1c448968a26fc393da1b2b950f614cf7ca7775a7e9db0e12a`.
- Strict ingest run 38880746856 — SUCCESS; artifact 12037476305.
- Direct visual inspection of the original shows leaves still attached to a living shoot.
- Manuscript M5 role is medicinal leaf material, principally fresh leaf; living attached foliage is not promoted as a harvested medicinal-material image under the current gate.
- Verdict: MATERIAL-ROLE GATE FAIL/HOLD — DO NOT INSERT.

### #43 Hoàng Cầm — FULL-GATE PASS
- Manuscript source: `Scutellaria baicalensis Georgi`; medicinal part = root; preparation = dried root, cut/sliced.
- Scientific source: Zhao Q, Chen X-Y, Martin C. (2016), *Scutellaria baicalensis, the golden herb from the garden of Chinese medicinal plants*, Science Bulletin 61:1391–1398, Fig. 1b; DOI 10.1007/s11434-016-1136-5.
- Article license: CC BY 4.0.
- Exact identity/material: Fig. 1b is explicitly captioned as the dried root of `Scutellaria baicalensis` used in traditional Chinese medicine; selected panel visibly shows dried sliced root material.
- Original article PDF: 976,671 bytes; SHA1 `35c4d22e053a7f9fd7d1104de5ea052f3a13f010`; SHA256 `7bdabcf28fc321a8b4e02f046e945df1879919b3c76b1bd6f9f4ff9438d96012`.
- Original embedded Fig. 1 composite: 969×766; 226,707 bytes; SHA1 `e0100def6b1a56c04962efd60c9e1e0ed0917e66`; SHA256 `108ffff43a7de0e9c94ee8007e7e837011773af8e69684382a28a32d95e9767d`.
- Controlled insertion derivative: crop box (670,0,969,330), Fig. 1b only; PNG 299×330; 163,626 bytes; SHA1 `383e2287b7bafee1ec6e03d3dcce26c410ea37ed`; SHA256 `1d0acc5759ff7d4e9557e1700acfb3824ec2722f0954cfa9e81e06d7d510aba7`.
- Transformation: crop only; no content addition/removal inside selected medicinal-material panel; lossless PNG derivative. Original PDF and embedded composite are retained for audit/provenance.
- Reproducible acquisition/crop workflow run: 38848023779 — SUCCESS; artifact `cmct-fullgate-scifig-43-53` / artifact ID 12024122567.
- Required caption attribution: cropped/adapted from Zhao, Chen & Martin, Science Bulletin 2016, Fig. 1b; CC BY 4.0; modification = cropped to dried-root panel only.
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.



### #44 Hoàng Liên — FULL-GATE PASS
- Manuscript source: `Coptis chinensis Franch.`; medicinal part = rhizome; preparation = dried rhizome.
- Scientific source: Xiang K-L, Wu S-D, Yu S-X, Liu Y, Jabbour F, Erst AS, et al. (2016), *The First Comprehensive Phylogeny of Coptis (Ranunculaceae) and Its Implications for Character Evolution and Classification*, PLOS ONE 11(4): e0153127; DOI 10.1371/journal.pone.0153127.
- Article license: CC BY 4.0.
- Exact identity/material: Fig. 1 is captioned `Coptis chinensis`; panel B is explicitly `dried rhizome (Rhizoma Coptidis)`. Article text states C. chinensis rhizomes are used/exported as Rhizoma Coptidis.
- Original Fig. 1 PNG: 1996×1651; 2,717,045 bytes; SHA1 `717446b96d1b0d8b54858541a39902f9bf900773`; SHA256 `6086639a98d4d7f1c2fa172d3bb2c6299764831095100a94aa2be970de333797`.
- Controlled insertion derivative: crop box `(1235,0,1996,870)`, panel B only; PNG 761×870; 363,357 bytes; SHA1 `69aa49964ce134d325aa40489e6453d6a9a05671`; SHA256 `81dcfb87c9153c0e04b226831a1738fafaa122c542d1d0e709d5ae6181deef2c`.
- Transformation: crop only; excludes living-plant panel A and carpels panel C; no content alteration inside panel B.
- Reproducible acquisition/crop workflow run 38855923179 — SUCCESS; artifact `cmct-m5-044-coptis`, artifact ID 12027271724.
- Controlled caption: `Ảnh 5 – Hoàng Liên (Coptis chinensis): thân rễ khô (Rhizoma Coptidis). Nguồn: Xiang et al., PLOS ONE 2016, Fig. 1B; CC BY 4.0; ảnh đã crop chỉ panel B.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from exact promoted 583-page REV17 base.

### #51 Long Đởm Thảo — FULL-GATE PASS
- Manuscript source: `Gentiana scabra Bunge`; medicinal part = root and rhizome; preparation = harvested root/rhizome, washed and dried.
- Scientific source: Kou B, Jiang Y, Chen Y, Yang J, Sun J, Yan Y, Weng L, Xiao C. *A Study of Gentianae Radix et Rhizoma Class Differences Based on Chemical Composition and Core Efficacy*. Molecules. 2023;28(20):7132. DOI 10.3390/molecules28207132.
- Article license: CC BY 4.0.
- Exact identity/material chain: the study defines Gentianae Radix et Rhizoma (GRR) as the dried root and rhizome of `Gentiana scabra Bunge`; Figure 1 compares first-class (GF) and second-class (GS) GRR.
- Selected material: Figure 1A / GF trait map, visually verified as intact dried root/rhizome material with scale; panel B/GS is excluded.
- Original article PDF: 6,509,534 bytes; SHA1 `848f7224acef53f2607783a0efb156e4f9fcaac3`; SHA256 `ebef84cc9214452a237c9c60a80463b356c18d31678e95c0d8f019f008292172`.
- Original embedded Figure 1 JPEG: 4343×1624; 373,732 bytes; SHA1 `f5d3d6e2d7c014f836634e6bb074a0105556dbda`; SHA256 `f71a6c0488c5e789f59b413acfd2c8e77c721b800541e703053df7669d91bd3f`.
- Controlled insertion derivative: Figure 1A only; crop box `(0,0,2070,1624)`; PNG 2070×1624; 951,426 bytes; SHA1 `b55d4b0920b5edc27d32f49e70f3d14c9dc390c2`; SHA256 `0a6c7aca0d9ea641c186370f03f42722d8c1a64194a3ae834c7ad10d7e96813d`.
- Transformation: crop only from original embedded Figure 1 JPEG; retains GF material and scale, excludes GS panel; no content alteration inside selected panel.
- Reproducible acquisition/crop workflow run 38851930020 — SUCCESS; artifact `cmct-m5-051-gentiana`, artifact ID 12025247336.
- Controlled caption: `Ảnh 5 – Long Đởm Thảo (Gentiana scabra): dược liệu rễ và thân rễ khô, mẫu hạng GF. Nguồn: Kou et al., Molecules 2023, Fig. 1A; CC BY 4.0; ảnh đã crop chỉ panel A.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.

### #53 Bản Lam Căn — FULL-GATE PASS
- Manuscript source: `Isatis tinctoria L.`; medicinal part = root; final preparation = dried and cut into segments/slices.
- Controlled identity mapping: the scientific source names the medicinal source as `Isatis indigotica Fort.` / Bei-Ban-Lan-Gen (BBLG); manuscript already preserves `Isatis indigotica` as the medicinal-source synonym context for `Isatis tinctoria`.
- Scientific source: Li Y, Yu Q-X, Yau L-F, Huang G-K, Lu J-G, Liu X-X, Jiang Z-H, Wang J-R. *Chinese Medicine* 2023;18:65. DOI 10.1186/s13020-023-00777-x. Fig. 3d.
- Article methods identify the BBLG samples as roots of `Isatis indigotica`; Fig. 3d is explicitly labeled `Isatidis Radix (BBLG)`.
- Preparation/form chain: pharmacopoeial/Frontiers medicinal-material context defines Isatidis Radix as dried root; the exact Fig. 3d photograph visibly shows the root material already cut into slices/segments, matching manuscript `phơi khô, cắt đoạn`.
- Article license: CC BY 4.0; the article states its images are included in the CC BY license unless a separate credit line says otherwise; Fig. 3 has no contrary third-party credit.
- Original article PDF: 5,631,510 bytes; SHA1 `eaa1cbf3d721df47b62b6c511b1e5bbac55b2aa0`; SHA256 `b61cf353d6c3b2ea2574945dde0cdf5ce8c0efd5ee1aa9a221226282e612363d`.
- Original embedded Fig. 3 composite: 1866×1875; 1,530,426 bytes; SHA1 `bdb6ccaca356c037736702a141931c0ec67cddab`; SHA256 `dc4805e93b988b207f7ccae0dc8bdc734ebf8b5eb5eb2845948cfe810a2654ca`.
- Controlled derivative: crop box (75,1480,470,1840), Fig. 3d drug photograph only; PNG 395×360; 189,166 bytes; SHA1 `b3a8004aa4ef8017a3e8d109e2f29be48d379e5a`; SHA256 `ecc3804720db62672da697767a7705f696c4f65c66ada2a5e66f60fb1edf34ca`.
- Transformation: crop only; excludes chromatogram and unrelated panels; no content addition/removal inside the selected drug photograph; lossless PNG derivative.
- Reproducible workflow: run 38848567614 — SUCCESS; artifact `cmct-fullgate-m5-053-bmc`, artifact ID 12023922845.
- Controlled insertion caption: `Ảnh 5 – Bản Lam Căn (Isatidis Radix): rễ khô đã cắt lát/đoạn. Nguồn: Li et al., Chinese Medicine 2023, Fig. 3d; CC BY 4.0; ảnh đã crop chỉ phần dược liệu.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 source.



### #54 Xạ Can — FULL-GATE PASS
- Manuscript source: `Iris domestica (L.) Goldblatt & Mabb.`; medicinal synonym context = `Belamcanda chinensis`; medicinal part = rhizome; preparation = cleaned/dried rhizome.
- Public specimen-atlas source: `中國藥物標本圖影` (Chinese drug specimen atlas), National Library of China scan, Wikimedia Commons file `File:NLC416-08jh015896-38387 中國藥物標本圖影.pdf`.
- File metadata: Public domain; credit = National Library of China; editor = 中國醫藥研究社編輯.
- Exact medicinal identity: atlas page 126 contains the vertical drug label `射干` (Shegan/Xạ Can) beside photographed crude-drug rhizome pieces; living-plant panel is excluded from the controlled derivative.
- Original PDF: 20,699,714 bytes; SHA1 `1aef378d7c63ab41a2ddd116b492da98e63cae75`; SHA256 `88f39462dedfcfa9475764f7693132abc5de5b6c041cd1038c9f73ea0e4ea61e`.
- Controlled derivative: rendered original scan at Matrix(2.2,2.2) + crop only; page 126; crop box `(600,520,1080,1100)`; PNG 480×580; 248,057 bytes; SHA1 `cc6dc52c7010aa15b129e65ee6b76180d05d39f9`; SHA256 `c45c59759f4940aa368e6833fdd6eeb258c99b55f687d273364f0396577a2e15`.
- Reproducible acquisition run 38852891928 — SUCCESS; artifact `cmct-m5-054-shegan`, artifact ID 12025729073.
- Controlled caption: `Ảnh 5 – Xạ Can (Shegan): thân rễ dược liệu khô. Nguồn: 中國藥物標本圖影, National Library of China scan, p.126; Public Domain; ảnh đã crop chỉ phần dược liệu và nhãn 射干.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.

### #55 Xích Thược — FULL-GATE PASS
- Manuscript source: `Paeonia lactiflora Pall.`; medicinal part = root; preparation = leave bark intact, dry directly, slice; explicitly distinct from Bạch Thược boiling/peeling processing.
- Scientific source: Tan Y-Q, Chen H-W, Li J, Wu Q-J. *Efficacy, Chemical Constituents, and Pharmacological Actions of Radix Paeoniae Rubra and Radix Paeoniae Alba*. Frontiers in Pharmacology 2020;11:1054. DOI 10.3389/fphar.2020.01054.
- Article license: CC BY 4.0.
- Identity/source control: article states Radix Paeoniae Rubra (RPR) is the dried root of `Paeonia lactiflora Pall.`; Figure 1A is explicitly `Characteristics of RPR`.
- Exact preparation/form: article states RPR is dried directly; surface tan/rough with integument retained; medicinal slices differ from RPA. This matches manuscript `rễ nguyên vỏ, phơi khô, thái phiến`.
- Original article PDF: 1,396,253 bytes; SHA1 `e515f57ce90c4f5ba020e8543aa140c266365237`; SHA256 `c7bd7cc5f34469e22981e2e7210e077e6ecd93f705f96923f7ad2c2e225b8e83`.
- Exact embedded Figure 1A image stream (not a screenshot/thumbnail): JPEG 965×724; 150,291 bytes; SHA1 `6707bc34743ece4c9df203c725e88742a99a6c6e`; SHA256 `bfb2d74d1bdb94af1160c6146b5fb7ca22039c10c2dc693e595b972e4ce127e9`.
- Visual controller: PDF page 2 confirms xref27 is panel A/RPR; xref28 is panel B/RPA and is excluded.
- Reproducible acquisition run: 38849091170 — SUCCESS; artifact `cmct-m5-055-rpr`, artifact ID 12023998382.
- Controlled insertion caption: `Ảnh 5 – Xích Thược (Radix Paeoniae Rubra): rễ Paeonia lactiflora phơi khô trực tiếp, còn vỏ và thái phiến. Nguồn: Tan et al., Frontiers in Pharmacology 2020, Fig. 1A; CC BY 4.0.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 source (or a separately controller-approved controlled reconstruction if that raw source remains unavailable).


### #57 Thanh Hao — FULL-GATE PASS
- Manuscript source: `Artemisia annua L.`; medicinal part = aerial herb; preparation target = harvested aerial parts dried under controlled low-heat/shade conditions.
- Scientific source: Gavarić N, Aćimović M, Kladar N, Hitl M, Drljača Lero J, Milić N, Radovanović K. *Unlocking the Bioactivity of Sweet Wormwood (Artemisia annua L., Asteraceae) Ethanolic Extract: Phenolics, Antioxidants, and Cytotoxic Effects*. Pharmaceutics. 2025;17(7):890. DOI 10.3390/pharmaceutics17070890.
- Article license: CC BY 4.0.
- Exact identity/material chain: Methods state aerial parts of `Artemisia annua L.` were collected at full flowering; botanical identity was confirmed and voucher No. 2-1513 deposited.
- Exact preparation chain: after collection the plant material was air-dried in the shade to constant weight and stored dry; Figure 1b is explicitly captioned as the herbal drug prepared for extraction, consisting of fragmented inflorescence, leaves and stems.
- Original article PDF: 2,157,394 bytes; SHA1 `a5e9eeaf01d83a6a6d47cd42cda0586a6c4b3674`; SHA256 `b0628a2bb601c20a1e5d367a4d67ff2dc0da88322795af11c310f4af11b180aa`.
- Original embedded Fig. 1 composite: JPEG 748×413; 76,612 bytes; SHA1 `66cf8c4813ac4321abb632767d0be07e911fd0d2`; SHA256 `3d1ff7c1daec57a83709d66935f03031414c0d4170e992af8463c2073e7976e3`.
- Controlled insertion derivative: Fig. 1b only, crop box `(236,0,748,413)`; PNG 512×413; 426,668 bytes; SHA1 `78360c7ed885be9887830180d42825f0fee3dfc0`; SHA256 `f8adc8e512fb23f1c0266f2b7c1ecb508c5acc7fc81cf17bda3b8bbb4caf0673`.
- Transformation: crop only; removes panel 1a living leaves and retains only panel 1b herbal-drug material; lossless PNG derivative.
- Reproducible acquisition/crop workflow: run 38850944643 — SUCCESS; artifact `cmct-m5-057-artemisia`, artifact ID 12025435751.
- Controlled caption: `Ảnh 5 – Thanh Hao (Artemisia annua): phần trên mặt đất thu ở giai đoạn ra hoa, phơi âm can đến khối lượng không đổi; hình dược liệu gồm cụm hoa, lá và thân đã phân mảnh. Nguồn: Gavarić et al., Pharmaceutics 2025, Fig. 1b; CC BY 4.0; ảnh đã crop chỉ phần dược liệu.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.


### #58 Xuyên Tâm Liên — FULL-GATE PASS
- Manuscript source: `Andrographis paniculata (Burm.f.) Nees`; medicinal part = aerial herb; preparation = harvested aerial parts dried/cut.
- Scientific source: Tabboon P, Limpongsa E, Rongthong T, Pongjanyakul T, Jaipakdee N. *Intestinal Permeation Characteristics via Non-Everted Gut Sac of Diterpene Lactones from Pure Andrographolide and Three Different Andrographis Extracts: An Investigation into Liqui-Mass with Different Solvents*. Pharmaceutics. 2026;18(1):90. DOI 10.3390/pharmaceutics18010090.
- Article license: CC BY 4.0.
- Exact identity: `A. paniculata` specimens authenticated by a botanist; voucher collections HB 200/66–HB 202/66 retained at Khon Kaen University.
- Exact material/form: Figure 2a is explicitly captioned `Dried aerial parts of A. paniculata`; this matches manuscript Herba Andrographitis aerial-part dried-drug target.
- Original article PDF: 6,886,997 bytes; SHA1 `9f67320ae1f7822a523952a37745e94bd0d71dbf`; SHA256 `bde0c1265ac1d4c9c8d8ad0d35b3b5b9791a92f72e8155dec71b08d9c632e370`.
- PDF page 4 uses Figure 2 split into multiple thin image strips; original PDF bytes and all embedded strips are retained for provenance.
- Controlled derivative: original PDF rendered reproducibly at Matrix(2.2,2.2), then cropped to Figure 2a only; crop box `(360,500,755,790)`; PNG 395×290; 109,459 bytes; SHA1 `56a17eeba13d5427e02403d8ee9407a8d9ac2baa`; SHA256 `9263d62e95300f331b87744e88d173830127ad32d8fd2cd4b25e4467fdaa77f1`.
- Transformation: page render + crop only; panel 2b powdered leaves and panel 2c TLC are excluded; no content alteration inside panel 2a.
- Reproducible workflow run 38851531020 — SUCCESS; artifact `cmct-m5-058-andrographis`, artifact ID 12026030448.
- Controlled caption: `Ảnh 5 – Xuyên Tâm Liên (Andrographis paniculata): phần trên mặt đất đã làm khô. Nguồn: Tabboon et al., Pharmaceutics 2026, Fig. 2a; CC BY 4.0; ảnh đã crop chỉ phần dược liệu.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.

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




### #71 Bạch Tiên Bì — HOLD after supplementary inspection
- Scientific source: Park S et al., *Dictamnus dasycarpus Turcz. Root Bark Improves Skin Barrier Function and Symptoms of Atopic Dermatitis in Mice*, Int J Mol Sci. 2024;25(23):13178; DOI 10.3390/ijms252313178; CC BY 4.0.
- Exact material context: methods use dried root bark of `Dictamnus dasycarpus`; voucher MS2021-1029.
- Original article PDF: 2,886,689 bytes; SHA1 `9e817c0a088f3f46c5c17c019f0f33e61780b557`; SHA256 `8a555da8cfea2605622e9b9dfa1fdff3f4ed3207bce2ebdada54fbdc9acab55a`.
- Supplement ZIP: 366,783 bytes; SHA1 `23af9baaeb36c83be163cf2f095c78351efed3ca`; SHA256 `2b4cd3a5d595d51a1d2a3f896b1af21ff2586ef623e22d133c6acc6e106a7d33`.
- Reproducible scout run 38878985444 — SUCCESS; artifact `cmct-m5-071-dictamnus`, artifact ID 12036527436.
- Direct inspection of Supplementary data S2 confirms Figure S2 is **chromatograms for dictamnine and root-bark extract**, not a photograph of the crude root-bark medicinal material.
- Verdict: scientific evidence supports identity/material context only; M5 IMAGE GATE FAIL → HOLD / DO NOT INSERT.


### #73 Tử Hoa Địa Đinh — HOLD due underlying PPBC license
- Candidate scientific source: *A Comprehensive Review of the Phytochemistry and Therapeutic Efficacy of Viola yedoensis Makino*, Molecules 2025;30(9):1922; DOI 10.3390/molecules30091922.
- Figure 2 caption explicitly identifies panel D as `dry medicinal parts` of `Viola yedoensis`; material/part/form match is scientifically strong.
- Direct PDF inspection confirms Figure 2D is the dry medicinal-material panel.
- However the figure credits Plant Photo Bank of China (PPBC), and the embedded image carries PPBC copyright/watermark.
- PPBC copyright policy states non-teaching reuse requires written authorization; teaching use is BY-NC-ND, must retain logo/watermark, and images may not be cropped/modified or used for commercial publication.
- Therefore the article's general CC BY 4.0 status is not sufficient to establish a clean file-level publication/reuse license for this third-party PPBC image.
- Verdict: LICENSE GATE FAIL/HOLD — DO NOT INSERT; do not crop or reuse the PPBC panel without separate permission.

### #70 Khổ Sâm — FULL-GATE PASS
- Manuscript source: `Sophora flavescens Aiton`; medicinal part = root; preparation target = dried/sliced root.
- Scientific source: *Determination of Antioxidant, Cytotoxicity, and Acetylcholinesterase Inhibitory Activities of Alkaloids Isolated from Sophora flavescens Ait. Grown in Dak Nong, Vietnam*. Pharmaceuticals. 2022;15(11):1384. DOI 10.3390/ph15111384.
- Article license: CC BY 4.0.
- Exact identity/material chain: study identifies the Vietnamese material as `Sophora flavescens`; DNA sequencing matched reference sequence AB127037.1 at 99%, 1025/1025 nucleotide similarity; Figure 1 caption explicitly labels panel D as `dried root`.
- Original article PDF: 14,263,464 bytes; SHA1 `ce4848deb56e8e73778907c54834de86e22fef7f`; SHA256 `b472973580f5e181d6bfaac761cbea41b5db58d1f7620dd228785e6ba0e1e8e7`.
- Original embedded Figure 1 composite selected for audit: PNG 3183×663; 4,235,252 bytes; SHA1 `c3f736177310c7e6b694a4205acfcd32dd6e436d`; SHA256 `f04f1c1d0486d06ed7eb0372539bdbd429e782f3593ab9d20f77cc80e5bc6c1e`.
- Controlled insertion derivative: Figure 1D only; crop box `(1629,0,2390,663)`; PNG 761×663; 457,928 bytes; SHA1 `81fc9c3a1ccec99b97e765c6fab3251917d6064b`; SHA256 `9450f5a8906cba23f7e8c0c9ee7551f8c1e82d09962f51071e900d026cc5e5f9`.
- Transformation: crop only; retains the panel explicitly captioned `dried root`; excludes living plant, fresh-root and cross-section panels; no content alteration inside panel D.
- Reproducible acquisition/crop workflow run 38878773779 — SUCCESS; artifact `cmct-m5-070-sophora`, artifact ID 12036452266.
- Controlled caption: `Ảnh 5 – Khổ Sâm (Sophora flavescens): rễ đã làm khô. Nguồn: Pharmaceuticals 2022, Fig. 1D; CC BY 4.0; ảnh đã crop chỉ panel D.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; insert only from the exact promoted 583-page REV17 base.

### #95 Sơn Đậu Căn — FULL-GATE PASS
- Manuscript source: `Sophora tonkinensis Gagnep.`; medicinal part = root and rhizome; preparation = wash, slice and dry.
- Medicinal-name control: Kew MPNS maps `山豆根 / Shandougen / Sophorae Tonkinensis Radix et Rhizoma` to accepted `Sophora tonkinensis Gagnep.`; Pharmacopoeia of China and Taiwan Herbal Pharmacopoeia specify dried root and rhizome.
- Selected file: Wikimedia Commons `File:HK 金鐘 Admiralty 德立街 Drake Street 海富中心商場 Admiralty Centre mall shop 新生堂 June 2020 SS2 11.jpg`.
- Exact material-role visual verification: original photograph shows a separate bowl explicitly labeled `山豆根（有毒）`, containing sliced dried root/rhizome pieces. Neighboring bowls are different drugs and are excluded from the controlled insertion crop.
- Author: Leirus Yat Shung.
- Provenance: own work → Wikimedia Commons; photographed in a Chinese herbal-medicine shop.
- License: CC BY-SA 4.0.
- Original dimensions: 4128 × 3096; original bytes: 3,036,900.
- Commons SHA1: `a163e3b054d8837d351436b57e9814ca608c67da`.
- SHA256: `75057c5c7dac348d8dd6dfb5e726025625f13c7be3eebb6b3a9b6bd7a2a45fc5`.
- Original-binary/provenance ingest run 38865185693: SUCCESS; artifact 12029864867.
- Controlled insertion derivative prepared locally: crop isolates the `山豆根（有毒）` bowl/label; crop/padding only, no medicinal-material content alteration. Attribution must state that the image was cropped/adapted.
- Controlled caption: `Ảnh 5 – Dược liệu Sơn Đậu Căn (Sophora tonkinensis): rễ/thân rễ khô thái phiến; ảnh cắt từ khay dược liệu có nhãn “山豆根（有毒）”. Nguồn: Wikimedia Commons; tác giả Leirus Yat Shung; CC BY-SA 4.0; ảnh đã crop để cô lập đúng dược liệu.`
- Status: FULL-GATE PASS.
- Mutation rule: queue for REV18; DO NOT mutate from the 585-page Library variant; insert only after the exact promoted 583-page REV17 raw DOCX (SHA-256 `2a6e0ade56225686bca38bd95155425e70c8ab52df9be58cbacab6a69ff5c5cc`) is recovered/verified.

## Current execution state
- Promoted manuscript M5 remains 23/125 until a controlled mutation is performed.
- New FULL-GATE queue after promotion = 15 rows (#43, #44, #47, #48, #51, #53, #54, #55, #57, #58, #70, #95, #109, #111, #121).
- If/when #43, #44, #47, #48, #51, #53, #54, #55, #57, #58, #70, #95, #109, #111 and #121 are mutated from the exact promoted REV17 base, expected M5 count becomes 38/125, subject to render/TOC/regression PASS.
- Remaining unfilled M5 slots before mutation = 102/125; after successful #43 + #44 + #47 + #48 + #51 + #53 + #54 + #55 + #57 + #58 + #70 + #95 + #109 + #111 + #121 mutation = 87/125.
- M4 #78 remains unresolved at exact-variety reusable natural-photo level.
- Two historical CORRECTION-READY IDs in #1–25 remain unrecovered and MUST NOT be inferred.

## Targeted-search verdicts since REV17 promotion
- #51–58 broad Commons search: no direct Commons FULL-GATE; subsequent exact scientific-figure acquisition promoted #51, #53, #55, #57 and #58 to FULL-GATE.
- #67–75: no new FULL-GATE.
- #76–85: no new FULL-GATE.
- #86–97: no new FULL-GATE.
- #101–110: no new FULL-GATE.
- #111–125 broad Commons pass: #121 promoted to FULL-GATE after exact detached-fruit verification; other rows remain HOLD unless individually re-verified.


### #51–58 broad targeted Commons rerun — NO DIRECT COMMONS FULL-GATE (later scientific-source passes recorded above)
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

### #91–100 targeted Commons rerun — #95 PROMOTED, others HOLD
- Run 38864713394: SUCCESS.
- #91, #92, #93, #94, #96, #97 and #100: no exact crude-drug/harvested photograph satisfying all gates.
- #95 Sơn Đậu Căn: candidate category/label `山豆根` was followed through authentic original-byte acquisition and direct visual review; exact drug bowl + sliced dried material verified; promoted to FULL-GATE PASS above.
- No surrogate insertion performed.

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



### #90 Rau Ngót — HOLD (new 2026 Commons candidate)
- Candidate: Wikimedia Commons `File:Sauropus androgynus (Vitamin leaf).jpg`.
- Exact identity: `Sauropus androgynus`.
- Author: Shreesha Sharma.
- Provenance: own work → Wikimedia Commons; Wiki Loves Medicinal Plants 2026.
- License: CC BY-SA 4.0.
- Original size: 4240×2832; original binary/hash gate PASS.
- Commons SHA1: `f61d7732004b108a5073f66dac9f2d5d2d6f2b05`.
- Binary/provenance ingest run 38855231207: SUCCESS; artifact 12026887594.
- Direct visual material-state verification: leaves remain attached to living branches/plant; this is not harvested leaf material.
- Manuscript M5 requires medicinal leaf material in a harvested fresh/dried role.
- Verdict: MATERIAL-ROLE FAIL → HOLD / DO NOT INSERT.



### #52 / #56 CC-BY scientific-figure scout — NO IMAGE PASS
- Reproducible scout run 38855492170: SUCCESS.
- #52 Bồ Công Anh: Huang, Li & Chen, Antioxidants 2026 (PMC13295379) explicitly authenticates dried whole `Taraxacum mongolicum` material (root/stem/leaf/flower), but all 13 article figures are extraction schemes, compound structures, assays, signaling/docking figures; no photograph of the authenticated dried medicinal material is present. Evidence strengthens identity/preparation only; M5 image remains HOLD.
- #56 Địa Cốt Bì: Yang et al., Antioxidants 2024 (PMC11590933), CC BY 4.0, studies root bark of `Lycium chinense`, but all 10 figures are cell/animal assay, dental/histology or graph figures; no photograph of the exact root-bark medicinal material is present. Evidence strengthens exact-species material context only; M5 image remains HOLD.
- Existing public-domain atlas image labeled `地骨皮` is not promoted because the pharmacopoeial drug scope can include both `Lycium chinense` and `L. barbarum`; manuscript is locked specifically to `L. chinense`.
- Verdict: no new FULL-GATE row from this scout; no mutation.

