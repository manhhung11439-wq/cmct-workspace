# CMCT — TẬP 1 REV17 SOURCE GUARD

Date: 2026-10-16

## Authoritative promotion checkpoint
Use the exact source declared by `checkpoints/T1_REV17_PROMOTED_2026-10-16.md`:
- `Tap_1_PRINT_MASTER_REV17_RECONSTRUCTED_CONSOLIDATED_TOCSYNC_2026-10-16.docx`
- SHA-256: `2a6e0ade56225686bca38bd95155425e70c8ab52df9be58cbacab6a69ff5c5cc`
- Promoted render: 583 pages
- Promoted PDF SHA-256: `7ff2383639f962c75361929136c89d8595d8691b588c53fdaafef996127d11b0`
- M5: 23/125
- M4: 124/125

## Library variant — DO NOT MUTATE FROM THIS FILE
The current Library file `Tap_1_PRINT_MASTER_REV17_M5_CONSOLIDATED_TOCSYNC_2026-10-16.docx` has a different structural QA fingerprint:
- 585 pages
- DOCX SHA-256: `61c2ad6f52c632be70b384a76150fdeb7ba5625ccbc930b3d73289a536ce0275`
- PDF SHA-256: `b032b098402f9a543caa5f70f37a5c5099c84be93e7fa4ad872b73f7f6f68036`
- Same M5 row set 23/125, but pagination differs.

This Library variant is not promoted over the explicit reconstructed-source checkpoint.
Do not silently select it as the next mutation base.

## Execution rule
Continue M5/M4 acquisition and FULL-GATE evidence locking independently.
Queue new PASS rows without mutation until the exact promoted REV17 raw DOCX is recoverable/verified.
Once recovered, mutate only from the exact promoted SHA above, then render -> page-map -> TOC sync -> re-render -> regression QA.
