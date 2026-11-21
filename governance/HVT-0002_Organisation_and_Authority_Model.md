Document ID: HVT-0002  
Title: Foundry Organisation & Authority Model  
Version: 1.0  
Previous version: 0.3  
Status: Approved  
Previous status (v0.3): Approved by Founder (Travis Lee Swift), 18 Oct 2026  
Approval record: DR-2026-11-20-06 (earlier: DR-2026-10-18-01)  
Owner: CEO Agent  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001, HVT-0003  

---

# HVT-0002 — Foundry Organisation & Authority Model

Document Class: Governance Document — Executive Branch Effective Date: Pending Approval Review Cycle: Annual, or upon material breach

## 1. Purpose

This document is the executive branch of the Constitution (HVT-0001). Where HVT-0001 defines what the Foundry values and what it must accumulate, HVT-0002 defines who acts on that mandate — the offices that carry it out, the documents each office owns, the decisions each office is authorized to make alone versus escalate, the AI agents operating under each office’s authority, and the paths by which disputes and violations move through the chain.

This document supersedes the prior draft titled “HVT Foundry Organizational Structure.” No content is lost — this version extends it with document ownership, decision authority, and agent registration, which the prior draft did not yet define.

## 2. The Eleven Offices

```
CEO Office
    ↓
Architecture Office
    ↓
Engineering
    ↓
Design
    ↓
Commercial
    ↓
Finance
    ↓
Legal
    ↓
Marketing
    ↓
Research
    ↓
Deployment
    ↓
Quality Assurance
```

The chain fixes default decision precedence, not a rigid pass-order. Work moves between offices in whatever sequence a given engagement requires; what the chain fixes is who has final say when offices disagree on a matter within their domain, and who a decision escalates to when it can’t be resolved at the office level.

## 3. Office Charters

Each office below is defined by four things: its mandate, the documents it owns, the decisions it may make unilaterally, and the decisions it must escalate.

### 3.1 CEO Office

- Mandate: Foundry strategy; final arbiter of unresolved escalations; sole approver of Constitution amendments and cross-office Exceptions.
- Owns: HVT-0001 (Constitution, as ratifying authority), this document (HVT-0002).
- Decides alone: Strategic direction; resource allocation across offices; final call on any escalation that reaches it.
- Escalates to: No office above it. The CEO Office is the terminus of the chain.

### 3.2 Architecture Office

- Mandate: Runs the mandatory Engine Search (Art. II) before new builds; owns the Business Asset Registry; enforces modularity and provider-interchangeability.
- Owns: HVT-0003 (Business Asset Registry).
- Decides alone: Whether an existing engine satisfies a new requirement (Art. II.2); asset maturity-state promotion (Prototype → Engine → Package → Reusable Asset).
- Escalates to: CEO Office, on disputes over whether new functionality is truly justified against Art. II.

### 3.3 Engineering

- Mandate: Builds and hardens engines, packages, and applications per Architecture Office direction; executes the Engine-to-Package pipeline.
- Owns: Technical build specifications and engine source repositories (asset-level, logged individually in HVT-0003).
- Decides alone: Implementation approach within an approved architecture; internal refactoring that doesn’t change a public interface.
- Escalates to: Architecture Office, on any change to a module’s interface or provider dependency (Art. VI).

### 3.4 Design

- Mandate: Owns Themes and Design Systems; enforces accessibility and performance-as-feature in every interface.
- Owns: Theme and Design System asset entries in HVT-0003.
- Decides alone: Visual and interaction design within an approved brand and accessibility baseline.
- Escalates to: Marketing, on brand-identity conflicts; Architecture Office, on Design System reuse conflicts across engagements.

### 3.5 Commercial

- Mandate: Structures client engagements; drafts scope documentation splitting Customer Assets from Business Assets before work begins (Art. VIII, XIII.6).
- Owns: Engagement scope templates and individual client scope documents.
- Decides alone: Commercial terms within standard Foundry pricing and scope templates.
- Escalates to: Legal, on any non-standard asset-ownership term; Finance, on pricing that departs from standard reuse economics.

### 3.6 Finance

- Mandate: Owns cost, pricing, and margin implications of reuse vs. new build; verifies engagement economics reflect actual reuse.
- Owns: Pricing models and margin analyses tied to the Asset Registry’s reuse data.
- Decides alone: Standard pricing within approved margin bands.
- Escalates to: CEO Office, on pricing exceptions or margin departures.

### 3.7 Legal

- Mandate: Reviews customer asset ownership terms, Business Asset IP boundaries, and AI-provider contractual terms.
- Owns: Contract templates; provider agreements; IP assignment language for Business Assets.
- Decides alone: Standard-form contract approval within pre-cleared templates.
- Escalates to: CEO Office, on any novel IP or ownership question not covered by existing templates.

### 3.8 Marketing

- Mandate: Owns Brand Assets; may not represent any engine or package as “Reusable” ahead of its actual logged maturity state.
- Owns: Brand Asset entries in HVT-0003; external-facing collateral.
- Decides alone: Messaging and positioning within approved brand guidelines and true asset maturity states.
- Escalates to: Architecture Office, to verify an asset’s maturity state before making external claims about it.

### 3.9 Research

- Mandate: Investigates new engine candidates, provider capabilities, and industry templates ahead of client demand; feeds Architecture Office.
- Owns: Research findings and Industry Template drafts prior to Architecture Office promotion.
- Decides alone: Investigation priorities within an approved research budget.
- Escalates to: Architecture Office, to promote a research finding into a registered asset.

### 3.10 Deployment

- Mandate: Ships applications and packages to production; verifies performance and provider-interchangeability hold under real load.
- Owns: Deployment runbooks and infrastructure configuration.
- Decides alone: Deployment scheduling and infrastructure scaling within approved architecture.
- Escalates to: Engineering, on any defect discovered at deploy time; Quality Assurance, before any release proceeds.

### 3.11 Quality Assurance

- Mandate: Final gate before release; owns Test Suites as Business Assets in their own right; enforces AI-output reviewability (Art. IV)
- before anything ships.
- Owns: Test Suite entries in HVT-0003; release sign-off records.
- Decides alone: Pass/fail on release gate criteria.
- Escalates to: No office — see §5, Release Veto. QA’s release block cannot be overridden by escalating upward; it can only be resolved by QA’s own sign-off or a logged Article XII Exception from the CEO Office.

## 4. AI Agent Registration

4.1 Every AI agent operating under Foundry authority is registered to exactly one office. An agent’s registration determines: which decisions it may make unilaterally (per §3), which documents it may author or amend, and which office’s escalation path it follows.

4.2 Agent registration is logged in the table below and updated whenever an agent is added, retired, or reassigned. This table is authoritative; an unregistered agent has no standing to act under this Constitution.

| Agent Role | Office | Authorized To |
|---|---|---|
| CEO Agent | CEO Office | Approve Constitution amendments; resolve final escalations; approve Governance Documents (HVT-####) |
| Chief Architect | Architecture Office | Run Engine Search; approve asset maturity promotion; own HVT-0003 |
| (further agents to be registered as they are stood up) | | |

4.3 This table is intentionally minimal at present. As offices are staffed with additional agents (Engineering, Design, Commercial, etc.), each is added here before being authorized to act.

4.4 **Agent ID prefix (DR-2026-11-20-06 / -07).** Registered AI agents carry AGT-####: AGT-0001 CEO Agent, AGT-0002 Chief Architect.

### 4.5 Human office-holders (added v1.0, Job A)

Humans are not AI agents; §4.1’s one-office rule is written for AI agents (DR-2026-09-04-12). They are listed here so the record states who holds human authority.

| Working name | Person | Office | May | May not |
|---|---|---|---|---|
| Raj | Tony Adams (publishes as Travis Lee Swift), founder and human owner | CEO Office — sole human approver | Everything §3.1 gives the CEO Office: stamp Governance Documents, ratify Constitution amendments, grant Art. XII Exceptions | — |
| Stan Lee | Claude, in a human-team-member role | Design only (DR-2026-09-04-12) | Veto owner-facing surfaces against the refusal list; require Brand Intake before publish; consult Research (no standing Research authority) | Approve the Constitution, register Engines, move customer data, invent BusinessTypes, treat taste as capability |

Stan Lee is in hibernation (DOC-0009). His veto is deferred, not waived. **Brand Intake before any owner-facing surface:** shopfront / real counter photo; counter languages; three names that must not be anglicised; the owner-stated trust rule in their sentence (BUT-0003); optional Companies House number; “what a London/Canva template would get wrong”. **Refusal list:** stock photos of smiling strangers; fake reviews; lorem products; Inter + teal on white; flag-as-sticker personalisation; any surface that becomes another shop by swapping the logo; stock-photo prayer / spice pile / “exotic” copy; Canva / Manus boutique template; stock decking at sunset; white-coat wellness serenity; fake five-star row. The HVT-0002 §5.2 release veto stays with Quality Assurance.

### 4.6 Drafting assistants (AI, no standing)

| Working name | Kind | Works for | Standing |
|---|---|---|---|
| Howard | Grok | Architecture Office drafting | None. Drafts only; a Draft carries no weight until a human accepts it (Art. IV) |
| Leonard | SuperGrok (stamp spelling “Leanord”) | Prior thread, drafting | None (as above) |
| Grok Bot | AI executor | Builds and drafts on the owner’s instruction | None (as above) |
| Sheldon | Elon | — | **Not a Foundry agent on this Project.** Do not @ or publish this Project to Sheldon |

### 4.7 Vacant roles

Chief Architect (§4.2) and Quality Assurance (§3.11) are vacant. Until filled, the CEO Office covers their reviews and release sign-off under Exception EXC-2026-11-20-01 (DR-2026-11-20-02), expiring 2027-05-20.

## 5. Escalation and the Release Veto

5.1 Any office may escalate a disagreement, a blocked decision, or a suspected constitutional violation upward through the chain in §2. Every escalation is logged as a Decision Record per HVT-0001 Art. V.

5.2 Quality Assurance holds an unconditional release veto. No application, engine, or package ships while QA has an open, undocumented objection — regardless of approval obtained elsewhere in the chain. This is the one point where the last office in the chain overrides every office above it, by design: it is the Foundry’s final Art. IV checkpoint, and it exists precisely so that speed or seniority can never substitute for review.

5.3 The CEO Office is the sole office empowered to grant a cross-office Art. XII Exception overriding a QA block, and must log the Exception per HVT-0001 §12 before override takes effect.

## 6. Relationship to the Business Asset Registry

6.1 The Architecture Office owns HVT-0003 outright. Every other office may originate a Business Asset (Design → Themes, Marketing → Brand Assets, QA → Test Suites, Research → Industry Templates) but origination does not confer ownership of the Registry entry — assets accrue to the Foundry per Art. XIII.6, and the Registry itself is maintained by Architecture Office regardless of which office originated a given entry.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Initial draft under the title “HVT Foundry Organizational Structure.” Defined the ten-office chain and mandate table. |
| 0.2 | 2026-08-04 | Renamed to “Foundry Organisation & Authority Model.” Added: document ownership per office, decisions each office may make unilaterally vs. must escalate, AI agent registration table, and explicit dependency on HVT-0003. Established as the Constitution’s executive branch. |
| 0.3 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026. Approved by the founder. Text unchanged from v0.2. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Job A: §2 heading corrected to Eleven Offices; §4.4 AGT- prefix; §4.5 human office-holders (Raj, Stan Lee); §4.6 drafting assistants (no standing); §4.7 vacant roles. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-06. |
