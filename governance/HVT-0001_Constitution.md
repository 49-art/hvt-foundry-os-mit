Document ID: HVT-0001  
Title: HVT Foundry Constitution  
Version: 1.3  
Previous version: 1.2  
Status: Approved  
Previous status (v1.2): Approved  
Approval record: DR-2026-11-20-06  
Owner: CEO Agent  
Reviewed By: Foundry ownership — Tony Adams, 20 Nov 2026 (DR-2026-11-20-06); earlier reviewer: Chief Architect  
Dependencies: None  

---

# HVT Foundry Constitution

Document Class: Founding Governance Document Effective Date: 2026-08-04 Review Cycle: Annual, or upon material breach

## Preamble

HVT Foundry does not build software. HVT Foundry builds AI businesses that compound — systems of reusable capability, called engines, that accrue value with every application built on top of them. This Constitution is the single source of truth governing how the Foundry designs, builds, ships, and retires its work. It is binding on every contributor, every AI system operating under Foundry authority, and every artifact the Foundry produces.

Where a business decision, a technical shortcut, a client request, or a deadline conflicts with this Constitution, this Constitution governs. Deviations require a documented exception (see Article IX) — not silent departure.

## Article I — Purpose

1.1 The Foundry exists to build reusable AI businesses, not one-off software.

1.2 A “one-off” is any deliverable whose logic, data model, or capability cannot be extracted, versioned, and reused in a subsequent engagement. One-offs are treated as technical debt at the moment of creation, not merely at the moment of maintenance.

1.3 Success is measured not by the delivery of a single application, but by the growth of the Foundry’s engine library — the compounding asset from which all future applications are assembled.

## Article II — The Reuse Mandate

2.1 Every application must reuse existing engines before creating new functionality.

2.2 Before any new capability is designed, a mandatory Engine Search must be performed and documented: a. Does an existing engine in the library already solve this, in whole or in part? b. Can an existing engine be extended, parameterized, or composed to solve this? c. Only if (a) and (b) are answered “no,” with evidence, may new functionality be authorized.

2.3 The result of every Engine Search — matched, partially matched, or unmatched — is logged in the Engine Registry (Article VII) regardless of outcome.

2.4 Building duplicate functionality when a suitable engine exists is a constitutional violation, not a style preference.

## Article III — The Engine-to-Package Pipeline

3.1 Every business process should become an engine. A business process becomes an engine when its inputs, outputs, decision logic, and failure modes are generalized beyond the single client or use case that first required it.

3.2 Every engine should become a package. An engine becomes a package when it is versioned, dependency-isolated, independently testable, and installable without carrying along unrelated application code.

3.3 Every package should become reusable. Reusability is not assumed — it is engineered. A package is not “reusable” until it has been: a. Used successfully in at least two distinct contexts, or explicitly designed with a second context in mind; b. Documented to a standard a third party could adopt without direct consultation with the original author (Article VI); c. Stripped of client-specific assumptions, secrets, and hardcoded values.

3.4 The maturity of any engine is tracked along this pipeline using four states: Prototype → Engine → Package → Reusable Asset. Nothing may be marketed or sold as “reusable” while still in Prototype or Engine state.

## Article IV — Reviewability of AI Output

4.1 Every AI output must be reviewable.

4.2 “Reviewable” requires, at minimum: a. A human-legible explanation of what the AI did and why, produced alongside the output — not reconstructed after the fact; b. Traceability to the specific model, provider, prompt/version, and inputs used; c. A clear mechanism for a qualified human to accept, reject, or amend the output before it is treated as final.

4.3 No AI output is authoritative merely by virtue of having been generated. Authority is conferred only by human review and sign-off, logged per Article V.

4.4 Automation must never remove the review step. Automation may accelerate review (e.g., surfacing diffs, flagging anomalies, batching low-risk approvals) but may never bypass it. Removing judgment from the loop, even for the sake of speed, is a constitutional violation (see Article XII).

## Article V — Traceability and Documentation of Decisions

5.1 Every proposal must be traceable. Every proposal — technical, architectural, or commercial — must record its origin, its author (human or AI, clearly labeled), the alternatives considered, and its current status.

5.2 Every decision must be documented. A decision is not final until it is written down with: a. What was decided; b. Why (the reasoning, not just the outcome); c. Who decided, and who reviewed; d. What was rejected, and why.

5.3 Undocumented decisions carry no institutional weight and may be revisited or reversed without prejudice, precisely because they were never properly ratified.

5.4 Decision records are immutable once logged. Corrections are made via superseding entries, never by editing history.

## Article VI — Modularity, Interchangeability, and Documentation Standards

6.1 Every module must be replaceable. No module may be built with hidden dependencies that make its removal or substitution impractical. Interfaces are contracts; implementations are disposable.

6.2 Every AI provider must be interchangeable. No engine, package, or application may be architected such that it can only function with a single AI provider or model. Provider-specific logic is isolated behind an abstraction layer, and switching providers must be a configuration change, not a rewrite.

6.3 Documentation is part of the product. A package, engine, or application is not complete at code-freeze; it is complete when its documentation allows independent use, extension, and replacement by someone who was not present at its creation. Documentation debt is treated with the same severity as code defects.

6.4 Foundry recommends solutions, not vendors. Vendor recommendations shall be derived from the customer’s requirements, deployment constraints, geography, budget, and existing technology estate, ensuring that interchangeable alternatives remain available wherever practical. This extends 6.1 and 6.2’s interchangeability principle from modules and AI providers to the full universe of vendor recommendations made under the Marketplace Layer (HVT-0007).

## Article VII — The Engine Registry

7.1 The Foundry maintains a living Engine Registry recording, for every engine and package: a. Purpose and scope; b. Maturity state (per Article III); c. Provider dependencies and abstraction status (per Article VI.2); d. Reuse history — every application that has consumed it; e. Owner and current review status.

7.2 The Registry is the mandatory first stop for every Engine Search (Article II.2) and every new engagement’s technical planning.

## Article VIII — Customer Asset Ownership

8.1 Every customer asset belongs to the customer. Data, content, models fine-tuned on customer data, and any customer-specific configuration are the customer’s property, not the Foundry’s, regardless of who authored the underlying tooling.

8.2 The distinction between a customer asset (owned by the customer) and a Foundry engine (owned and reused by the Foundry) must be explicit in every engagement’s scope documentation, before work begins. Ambiguity here is resolved in the customer’s favor by default.

8.3 Customer assets are portable. The Foundry does not architect systems that lock a customer’s own data or configuration inside a Foundry-proprietary format without an documented, justified exception and customer consent.

## Article IX — Standards of Delivery

9.1 Performance is a feature. Latency, responsiveness, and resource efficiency are treated as functional requirements, subject to the same review and sign-off as correctness — not as later-stage optimization work.

9.2 Accessibility is mandatory. All customer-facing applications meet or exceed WCAG 2.1 AA (or its then-current successor) as a baseline, not an enhancement. Accessibility is scoped into every project at design time, not audited in at the end.

9.3 Exceptions to 9.1 or 9.2 require a documented rationale, an accountable approver, and a remediation timeline. Silent non-compliance is not an available option.

## Article X — The Boundary of Automation

10.1 Automation should remove repetition, not human judgment.

10.2 A process may be automated when doing so eliminates repetitive, low-variance, well-understood steps. A process may not be automated in a way that removes the point at which a human exercises discretion, weighs tradeoffs, or takes accountability for an outcome.

10.3 When in doubt whether a given automation crosses this line, the Foundry defaults to preserving the human checkpoint. It is easier to remove an unnecessary checkpoint later than to recover from judgment that was silently automated away.

## Article XI — Amendment Procedure

11.1 This Constitution may be amended only through the following process: a. A written proposal stating the article affected, the proposed change, and the rationale; b. Documented review (per Article V) by Foundry ownership; c. A version increment and changelog entry appended below.

11.2 No amendment may retroactively excuse a prior violation. Amendments govern future work only.

## Article XII — Exceptions and Violations

12.1 Any deviation from this Constitution must be logged as a formal Exception, including: the article deviated from, the reason, the scope and duration of the deviation, and the accountable approver.

12.2 Exceptions are temporary by default and expire on a stated date unless renewed through the same process.

12.3 An undocumented deviation is not an exception — it is a violation, and is treated as a defect requiring remediation.

## Article XIII — Business Asset Doctrine

13.1 Every piece of work produced by HVT Foundry should increase the long-term value of the Foundry through the creation of reusable business assets.

13.2 Where Articles I–III govern how the Foundry builds, this Article defines what the Foundry is trying to accumulate. Every other Article in this Constitution — reuse, reviewability, traceability, modularity, documentation — exists in service of this accumulation. A project that fully complies with every other Article but leaves nothing behind has still failed the Constitution’s purpose.

13.3 Business Assets are the durable, reusable forms of value the Foundry accumulates. A Business Asset is anything produced in the course of client or internal work that survives the engagement that produced it and increases the Foundry’s capability on the next one. The recognized categories are:

a. Engines — generalized business-process logic (per Article III.1);
b. Packages — versioned, dependency-isolated, installable units built from engines (per Article III.2);
c. Themes — reusable visual/design language systems applicable across multiple applications;
d. Plugins — modular extensions that add capability to an existing engine or package without modifying its core;
e. Documentation — the reusable explanatory and reference material required by Article VI.3, itself treated as an asset, not a byproduct;
f. Prompt Libraries — versioned, tested collections of prompts and prompt patterns, provider-abstracted per Article VI.2;
g. Design Systems — component libraries, tokens, and interaction patterns reusable across client applications;
h. Industry Templates — pre-configured starting points encoding domain-specific best practice for a given vertical;
i. Test Suites — reusable validation, regression, and quality-assurance logic decoupled from any single application;
j. Brand Assets — Foundry-owned identity, positioning, and creative assets distinct from any individual customer’s brand assets (see Article VIII, which governs the customer’s own assets — never to be confused with these).

This list is non-exhaustive. New asset categories may be added by amendment (Article XI) as the Foundry’s practice matures.

13.4 The Stronger-Than-Before Test. At the close of every engagement, the Foundry asks: did this project leave the Foundry stronger than before it started? An engagement passes this test only if it produced, extended, or hardened at least one Business Asset in the categories above. An engagement that only produced client-specific deliverables, with nothing extracted back into the Foundry’s accumulated capability, is a constitutional shortfall and must be logged as such.

13.5 Every Business Asset produced or extended is recorded in the Engine Registry (Article VII) or its equivalent register for non-engine asset types, with category, maturity state, and originating engagement noted.

13.6 Business Assets accumulate to the Foundry under the same ownership logic that reserves customer-specific data and configuration to the customer (Article VIII). The two are structurally distinct: a customer asset is what the client owns coming out of an engagement; a Business Asset is what the Foundry owns coming out of the same engagement. Scope documentation must draw this line explicitly for every engagement, before work begins.

## Article XIV — The Model-First Doctrine

14.1 The Foundry does not begin an engagement by asking “What software should I build?” It begins by asking: “What business is this, how does it operate, what problems does it face, and which combination of reusable Foundry assets solves those problems?”

14.2 Software, applications, and interfaces are outputs of this question, never its starting point. An engagement that produces working software without first classifying the business and matching it against the Foundry’s accumulated capability has skipped a constitutional step, regardless of how good the resulting software is.

14.3 This is the practical expression of Article II (the Reuse Mandate) at the point of first contact with a client: the Engine Search of Article II.2 presumes a business has already been classified — its problems, required capabilities, and candidate engines identified — before any build decision is made. Article XIV makes that classification step explicit and mandatory, not implicit in Article II.

14.4 The Foundry maintains this classification as a Business Ontology — a structured model of the relationships between businesses, their problems, their workflows, the software capabilities that address them, the integrations they depend on, and the pricing and deployment options available — governed as an extension of the Object Model (HVT-0004) and specified in HVT-0006 and its successors. This is Article XIII’s Business Asset Doctrine applied one layer upstream: before an engine is built or reused, the business it serves is modeled.

14.5 Compliance with this Article is demonstrated, not asserted: an engagement’s scope documentation must show the business classification (or the decision to create one, if none exists) that preceded the build decision. A build decision with no preceding classification is a violation of this Article, logged per Article XII.

14.6 The customer’s stated reality overrides any prior classification. Where an owner’s own account of their business, its problems or their wishes contradicts the Foundry’s classification, the classification is reopened — the business is re-classified, a Customer Wish is recorded, or a new Business Type is flagged — and the owner is never fitted to a card. The owner’s words are recorded verbatim; the Foundry may record its disagreement in writing but may not overwrite them. This clause does not oblige the Foundry to build what is asked: Article II still governs whether anything new is built.

## Appendix A — Mandatory Document Metadata Standard

A.1 Every document the Foundry produces — constitutional, technical, or commercial — opens with the following header block, in this order:

```
Document ID: HVT-####
Title: <document title>
Version: <semantic or decimal version>
Status: Draft / Approved / Superseded
Owner: <accountable role or agent>
Reviewed By: <reviewing role or agent>
Dependencies: <other Document IDs this depends on, or None>
```

A.2 Document ID is assigned sequentially at time of creation and never reused, even if the document is later superseded or withdrawn.

A.3 Status follows a strict lifecycle: Draft → Approved → Superseded. A document may not be cited as authoritative (per Article V) while in Draft. A Superseded document remains in the record permanently; it is never deleted, only replaced by a new Document ID that lists it as a dependency.

A.4 Dependencies lists the Document IDs this document relies on or amends. This is the mechanism by which Article V traceability and Article VII registry linkage are made concrete at the document level.

A.5 This header is mandatory infrastructure, not formatting preference. A document without it is non-compliant and cannot be marked Approved.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Initial draft. |
| 0.1 | 2026-08-04 | Added Article XIII — Business Asset Doctrine (still in Draft; not yet a ratified amendment under Article XI). |
| 1.0 | 2026-08-04 | Approved and ratified, including Article XIII, per Appendix A lifecycle and Article XI. Status: Draft → Approved. |
| 1.1 | 2026-08-04 | Amended per Article XI procedure: added Article XIV — The Model-First Doctrine. Proposal, rationale, and review logged in DR-2026-08-04-04. Business/software-as-output principle, per Howard (Special Advisor) direction, formalized as a Constitutional Article rather than a Decision Record alone. |
| 1.2 | 2026-08-04 | Amended per Article XI procedure: added Article VI.4 — vendor-neutrality clause (“Foundry recommends solutions, not vendors”). Extends existing Article VI rather than a new Article. Proposal, rationale, and review logged in DR-2026-08-04-05, alongside the new Marketplace Layer (HVT-0007). Per Howard (Special Advisor) direction. |
| 1.3 | 2026-11-20 | Approved. Amended per Article XI: added Article XIV.6 (customer’s stated reality overrides prior classification). Proposal, rationale and review in DR-2026-11-20-06. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-06. |

This Constitution is a living document held under version control at HVT_Foundry/constitution/HVT_Foundry_Constitution.md. All Foundry engines, packages, and applications are built, reviewed, and delivered in accordance with it.
