# Gemini Atlas — Component Documentation Template

## Purpose

This template exists to produce **implementation-level** documentation for
each of Gemini's 10–15 components (services and batch loaders/jobs), not
summaries. A reader — human or AI — should be able to read one of these docs
and understand the actual control flow, state checks, and decision logic
well enough to reason about a bug or extend the component, without opening
the code.

Two things live in this file:
1. The template structure every component doc should follow.
2. A worked example (Gemini Watchtower) showing the expected depth.

Use section 3 as the prompt you feed to an AI when you point it at the repo
for a given component.

---

## 1. Template Structure

Every component doc should have these sections. Skip a section only if it
genuinely does not apply (e.g. a stateless service has no "batch size").

### 1.1 Component Overview
- One paragraph: what this component exists to do, in the context of Gemini
  as a collateral management system.
- Component type: **service** (long-running, request/event driven) or
  **loader/batch job** (scheduled, processes a batch and exits).
- Is it independent of other Gemini components, or does it depend on /
  feed into others? State the boundary explicitly.

### 1.2 Trigger / Invocation
- What starts this component running: a schedule (Autosys job), a message
  queue event, an API call, a Kubernetes CronJob, etc.
- Frequency and batch size, if applicable (e.g. "polls every N minutes,
  processes up to 100 trades per run").

### 1.3 Input Contract
- Exact shape of what the component consumes: table(s), topic(s), API
  payload. Field-level detail where it matters to the logic (not a full
  schema dump — only fields the processing logic branches on).

### 1.4 Processing Pipeline (step-by-step)
This is the core section. Write it as an ordered sequence of checks and
transformations, not prose description. For each step, state:
- What is checked or computed
- What table/service is consulted
- What happens on each branch (pass / fail / missing data)

Think of this as pseudocode in English — precise enough that someone could
re-derive the actual code structure from it.

### 1.5 State & Data Checks
- Any existence checks against reference data (e.g. "is this instrument
  known to Gemini?").
- Any temporal checks (e.g. "is the price present for T-1 and T-2?").
- What "missing" means concretely for each check, and what the component
  does the instant it detects a miss.

### 1.6 Event Generation Rules
- What conditions cause an event/alert to be created.
- **Deduplication logic**: what key/window prevents the same underlying
  issue from generating duplicate events (this is often the subtlest part
  of these components — document it explicitly, including what does NOT
  count as a duplicate).
- Event severity/classification if applicable.

### 1.7 Downstream Effects / Outputs
- What tables get written, what events/messages get emitted, what other
  components consume that output.

### 1.8 Failure Modes & Edge Cases
- What happens if the component itself fails mid-batch (partial batch
  processed? retried? idempotent?).
- Known edge cases in the business logic (e.g. same instrument booked by
  two accounts in the same batch — is the second one deduped in-memory or
  only against persisted events?).

### 1.9 Dependencies
- Upstream data sources, downstream consumers, shared infra (Conjur/
  CyberArk secrets, DB, Kafka/MQ, Autosys, K8s).

### 1.10 Configuration
- Batch size, thresholds, schedule — anything ops would tune without a
  code change.

### 1.11 Example Scenario Walkthrough
- One concrete trace through the pipeline with made-up but realistic
  values, showing at least one "happy path" and one "miss detected"
  branch.

---

## 2. Worked Example: Gemini Watchtower

### 2.1 Component Overview
Gemini Watchtower monitors newly received trades for data completeness
before they can be safely used in collateral calculations. It is a
standalone application, independent of other Gemini components — it does
not share runtime state with any other service, though it reads from and
writes to shared Gemini data stores.

**Type:** Loader / batch job.

### 2.2 Trigger / Invocation
Runs on a schedule, pulling newly received trades in batches of up to 100
at a time.

### 2.3 Input Contract
- A batch of trades (≤100), each with an instrument ID and an owning
  account.

### 2.4 Processing Pipeline
For each trade in the batch, in order:
1. **Instrument existence check** — look up the trade's instrument ID
   against Gemini's instrument reference database.
   - If present → continue to step 2.
   - If absent → raise a missing-instrument condition (see 2.6).
2. **Price presence check (T-1)** — for the instrument, check whether a
   price exists for T-1.
   - If missing → raise a missing-price condition.
3. **Price presence check (T-2)** — same check for T-2.
   - If missing → raise a missing-price condition.

Because collateral valuation depends on the instrument being known and
priced, both checks gate whether the trade can be treated as complete.

### 2.5 State & Data Checks
- Instrument existence: boolean lookup against the instrument master.
- Price existence: boolean lookup per instrument per date, checked
  independently for T-1 and T-2.

### 2.6 Event Generation Rules
- A **missing-instrument event** is created when an instrument ID on a
  trade isn't found in Gemini's database.
- A **missing-price event** is created when a required price (T-1 or T-2)
  isn't found for an instrument that does exist.
- **Deduplication:** events are keyed at the instrument level, not the
  trade or account level. If Account A books a trade on instrument X and
  a missing-price event is already open for instrument X, Account B
  booking a trade on the same instrument X does **not** create a second
  event — the existing open event already covers the underlying data gap.
  The dedup check is against the event table (persisted), not just
  in-batch — so this holds across batches and across days, not only
  within a single 100-trade run.

### 2.7 Downstream Effects / Outputs
- Writes missing-instrument / missing-price events to the event table,
  which presumably feeds an ops/monitoring view or downstream remediation
  workflow. *(Confirm exact downstream consumer when filling this in from
  the repo.)*

### 2.8 Failure Modes & Edge Cases
- Same instrument, multiple accounts, same batch → only one event
  (per 2.6).
- *(To confirm from code: what happens if the batch job itself dies
  mid-batch — are already-checked trades re-checked on the next run, and
  is that idempotent given the dedup-by-instrument rule?)*

### 2.9 Dependencies
- Instrument reference database, price database, event table.

### 2.10 Configuration
- Batch size: 100 trades per run.

### 2.11 Example Scenario Walkthrough
- Trade 1: Account A, Instrument XYZ. XYZ exists, but no price for T-1.
  → missing-price event created for XYZ.
- Trade 2 (same batch or a later batch): Account B, Instrument XYZ.
  XYZ exists, no price for T-1. → event for XYZ already open → no
  duplicate event created.
- Trade 3: Account C, Instrument ABC. ABC not found in instrument
  database. → missing-instrument event created for ABC.

---

## 3. AI Prompt — Use This to Generate a Component Doc from the Repo

Copy this block, replace `{COMPONENT_NAME}` and point the AI at the
component's repo/namespace:

```
You are documenting a component of Gemini, Nomura's collateral management
system, called {COMPONENT_NAME}. Scan the repository and produce a
markdown document following the structure below. Do not summarize at a
high level — trace the actual control flow, branches, and data checks in
the code. For every conditional or validation in the code, state what is
checked, against what data source, and what happens on each branch
(including the failure/missing-data branch). Pay special attention to any
deduplication, idempotency, or state-comparison logic — these are often
the most important and least obvious parts of the system, and must be
described precisely, including what key/scope the dedup or idempotency
check operates at (e.g. per-instrument vs per-trade vs per-account).

Sections to produce:
1. Component Overview (what it does, service vs loader/job, its
   boundaries relative to other components)
2. Trigger / Invocation (what starts it, schedule, batch size)
3. Input Contract (what it consumes, only fields that affect logic)
4. Processing Pipeline (ordered, step-by-step, pseudocode-precision)
5. State & Data Checks (existence/temporal checks against reference data)
6. Event Generation Rules (conditions + deduplication logic, explicit)
7. Downstream Effects / Outputs (what gets written/emitted, who consumes it)
8. Failure Modes & Edge Cases (partial-batch failure, idempotency, known
   tricky scenarios)
9. Dependencies (upstream/downstream/shared infra)
10. Configuration (tunables: batch size, thresholds, schedule)
11. Example Scenario Walkthrough (concrete trace, happy path + at least
    one failure/miss branch)

If something in the pipeline is ambiguous from the code alone (e.g. exact
downstream consumer of an event, or exact retry behavior on partial
failure), flag it explicitly as "to confirm" rather than guessing.
```

---

## 4. Notes for the Atlas Set

- Keep one markdown file per component, same filename convention as the
  component's repo/namespace so retrieval later is unambiguous.
- Section headers should stay consistent across all component docs (use
  the exact section names above) — this matters if these files are later
  chunked and embedded for retrieval, since consistent structure makes
  chunk boundaries predictable.
- When two components interact (e.g. Watchtower's events feeding another
  component), cross-reference by component name rather than duplicating
  the other component's internal logic.
