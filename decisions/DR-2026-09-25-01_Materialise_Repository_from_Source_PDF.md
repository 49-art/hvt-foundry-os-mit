# DR-2026-09-25-01 — Decision Record — Materialise the repository from the source PDF

Document ID: DR-2026-09-25-01  
Title: Decision Record — Materialise the repository from the source PDF  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25  
Dependencies: README (source PDF, 109 pages), HVT-0001 Art. V, Appendix A  

---

## Decision

The HVT Foundry record, which until now existed only as a 109-page PDF, is laid out as the repository the README describes. Every document in the PDF is recreated as a Markdown file in the folder the README (or, where more specific, DOC-0009's file map) names. Content is copied, not rewritten.

## Action Taken

1. Recreated 38 documents: README.md; governance/ (HVT-0001, -0002, -0003 v0.4, -0004 v0.1, -0006, HVT-0006-OVL-0001, -0007, BUT-0002…0007 cards and queue, DOC-0008, DOC-0009, SES-0002 dry run and filled theatre, SES-0003 blank, working list); decisions/ (DR-2026-08-04-01…09, DR-2026-09-04-10, -10a, -11, -12, -14); assets/ (DOC-0001, DOC-0004, DOC-0005).
2. Changes were limited to formatting: PDF line breaks rejoined, ligatures (ﬁ, ﬂ) repaired, page-break characters removed, headings and tables rebuilt from the PDF layout, metadata headers put one field per line.
3. The README is kept word for word, including its now out-of-date "Status" section (see Traceability).

## Rationale

The README, kernel and graph all refer to files by path. Without the files, nothing can be checked, tested or reviewed (Art. IV, V). Copying rather than rewriting keeps the Markdown the authoritative record, as HVT-0004 §1 requires.

## Authority

Prepared on the direct instruction of Travis Lee Swift (project owner). It is a Draft: under HVT-0001 Art. IV (AI output must be reviewable and is not authoritative until a qualified human accepts it) and Art. V.3, it carries no institutional weight until reviewed. Nothing in this record approves, stamps or signs anything on behalf of Raj, Stan Lee, Howard, Leonard or any Office.

## Traceability

Discrepancies found while copying — **flagged, not fixed**:

- The README "Status" section is out of date: the Stock and Review Engine Search it calls pending was run and approved in DR-2026-09-04-10.
- The README says the test suite has 17 tests; the suite written in DR-2026-09-25-02 has 23 (it covers the 17 behaviours and adds checks on the graph).
- HVT-0006: header/changelog say v0.5 (2026-09-05); the README table and the overlay say v0.4.
- HVT-0002 says "Ten Offices" but its chain lists 11.
- The Constitution path is written as HVT_Foundry/constitution/… in the text, but the README places governance documents in governance/. governance/ was used.
- DOC-0008, DOC-0009 and the SES files were placed in governance/, following DOC-0009's file map.
- There is no DR-2026-09-04-13 in the record; numbering jumps from -12 to -14.
- HVT-0007 §5.2 maps six vendors onto "SLC-0002–SLC-0006" (five IDs) and seven INT records. See DR-2026-09-25-03.
- DR-2026-08-04-06 says the new types would be formalised in "HVT-0004 v0.3"; DR-2026-08-04-07 describes a single consolidated bump. See DR-2026-09-25-06.
- DR-2026-09-04-11 cites Art. III.3.a for Prototype (already flagged by Howard in the record).
- Documentation assets use the status "Draft", which is the Document vocabulary, not the Asset vocabulary in HVT-0004 §4.

## Explicitly Not Done

- No document text was corrected, even where it contradicts another document.
- The original PDF pages that are only formatting (cover, blank pages) were not reproduced.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft. Repository laid out from the source PDF. |
