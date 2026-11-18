# E9 top-7 scoring: holes settled if the owner answers only 7 questions

A = first 7 numbered "Questions for the owner". B = KB `ask:` decisions (max 7); assumed = `assumed:` batch.
Must-ask M = H1,H2,H4,H5,H8,H15. Partial coverage counted when the question's answer settles the hole's main point (noted).
Not counted: downgrade asked without tools-out (H14), late-fee collection method, eligibility timing, extra notification emails, block-lift mechanics (not key holes).

- A1: H1,H2,H3,H4,H5,H6,H7,H9,H12,H13,H16,H22 (12); must 4 (H1,H2,H4,H5)
- A2: H1,H2,H3,H4,H5,H6,H9,H10,H11,H12,H13,H22 (12); must 4
- A3: H1,H2,H3,H4,H5,H6,H7,H9,H10,H12,H13,H16,H22 (13); must 4
- A4: H1,H2,H3,H4,H5,H7,H11,H12,H13 (9); must 4
- A5: H1,H2,H3,H4,H5,H6,H7,H9,H11,H12,H13,H14 (12); must 4
- A6: H1,H2,H3,H4,H5,H6,H7,H12 (8); must 4
- A7: H1,H2,H3,H4,H6,H9,H12,H13 (8); must 3 (H5 not: asks deposit vs charge, not who decides/amount)
- A8: H1,H2,H3,H4,H5,H6,H7,H12,H22 (9); must 4
- B1: ask H3,H5,H6,H9,H12,H13,H16,H19 (8); must 1 (H5); assumed H24 (1). No amount (H1/H2/H4) is a decision; eligibility-timing settles no hole.
- B2: ask H3,H5,H6,H7,H8,H9,H10,H12,H13 (9); must 2 (H5,H8); assumed H11,H18,H22,H24 (4). where_checked settles no hole.
- B3: ask H5,H6,H8,H9,H11,H12,H13,H16 (8); must 2 (H5,H8); assumed H7 (1). late-fee-collection settles no hole; H6 partial (no window length).
- B4: ask H1,H2,H3,H4,H5,H6,H7,H8,H9,H12,H13,H15,H16,H22 (14); must 6; assumed H18,H24 (2). Amount decisions carry placeholder numbers.
- B5: ask H3,H4,H5,H6,H9,H11,H12,H13,H14,H16 (10); must 2 (H4,H5); assumed H7,H22,H24 (3). H14 via "tools already out can still be returned" on lapse.
- B6: ask H4,H5,H7,H8,H9,H10,H11,H12,H13,H15,H16 (11); must 4 (H4,H5,H8,H15); assumed H6,H24 (2). H15 partial (who marks, not expiry).
- B7: ask H5,H6,H7,H8,H9,H12,H13,H16,H22 (9); must 2 (H5,H8); assumed (prose list) H6,H11,H15,H18,H24 (5). member-messages settles no hole; H6 partial.
- B8: ask H4,H5,H6,H7,H8,H9,H12,H13,H22 (9); must 3 (H4,H5,H8); assumed H3,H11,H15,H23,H24 (5). notifications settles no hole.

| run | settled-by-7 | must-ask | assumed-batch (B) |
|---|---|---|---|
| A1 | 12 | 4/6 | - |
| A2 | 12 | 4/6 | - |
| A3 | 13 | 4/6 | - |
| A4 | 9 | 4/6 | - |
| A5 | 12 | 4/6 | - |
| A6 | 8 | 4/6 | - |
| A7 | 8 | 3/6 | - |
| A8 | 9 | 4/6 | - |
| B1 | 8 | 1/6 | 1 |
| B2 | 9 | 2/6 | 4 |
| B3 | 8 | 2/6 | 1 |
| B4 | 14 | 6/6 | 2 |
| B5 | 10 | 2/6 | 3 |
| B6 | 11 | 4/6 | 2 |
| B7 | 9 | 2/6 | 5 |
| B8 | 9 | 3/6 | 5 |
| **A mean** | **10.4** | **3.9** | - |
| **B mean** | **9.8** | **2.75** | **2.9** |
