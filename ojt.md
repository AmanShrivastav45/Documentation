Here's the Jira/MR checklist problem reframed as an ideation ask instead of a build:
Problem Statement / Use Case Title: Ideas for Streamlining the Pre-Approval Checklist Process for Jira Tickets and MRs
Background / Context: Before any merge request is approved, reviewers manually verify a 15-20 item mandatory checklist against the linked Jira ticket and the MR — covering things like correct Jira type, affected components, labels, story points, sprint/fix version linkage, test evidence, SonarQube coverage, and branch hygiene.
Current Challenge: This is entirely manual today. Reviewers cross-check Jira fields and MR details separately, items are sometimes missed under time pressure, and there's no single view that surfaces what's incomplete before review begins.
Expected Outcome / Goal: Given the checklist and a few real (sanitized) Jira ticket + MR examples, propose ideas for how this process could be made faster, less error-prone, or less manual — not a working tool, just a short list of approaches with brief reasoning on how each would help and what it would take to build. Ideas can range from lightweight automation to process changes.
Any relevant notes, assumptions, or dependencies:
No API access or environment setup needed — the checklist and sample tickets/MRs are the only inputs required
Not all 15-20 items are equally automatable; part of the value is identifying which ones are (e.g., SonarQube coverage, branch hygiene) versus which are more judgment-based (e.g., issue justification quality)
Deliverable: a short write-up or slide, not code
Want this and the release-management ideation one bundled into a single doc, or kept as separate problem statement pages like the review board template shows?


Here's the release manager ideation problem in the same format:
Problem Statement / Use Case Title: Ideas for Reducing Release Manager Time and Manual Overhead
Background / Context: During release weeks, the release manager carries out a long sequence of manual duties on top of their regular work — drafting release/change tickets and run book (~1 hr), coordinating merges and UAT deployment, completing mandatory release attestations (~2 hrs), collecting UAT sign-offs and attaching them to Jira tickets, manually verifying functional/regression test presence across all tickets in the sprint test cycle, finalizing the run book and regression confluence (~15-20 min), getting run book review and giving walkthroughs, resolving engineering portal items (~1 hr), chasing 6-7+ people for change approvals, preparing for the CAB presentation, manually checking each Jira's component was merged to master with a passing pipeline before cutting the release tag, running smoke tests on non-prod, pulling deployment images, and preparing rollback plans. Combined, this totals roughly 6-7 hours across the release cycle.
Current Challenge: Almost every step above is manual and involves either repetitive checking (verifying test presence per ticket, verifying merge/pipeline status per component) or repetitive chasing (approvals, sign-offs, reviews). There's no single automated view of what's done, pending, or blocking, so the release manager has to individually track and follow up on each item.
Expected Outcome / Goal: Given this full workflow, propose ideas for where and how this could be streamlined — not a working tool, just a short list of concrete ideas with reasoning on what each would save and roughly what it would take to build. Ideas can include automation, consolidated dashboards, notification/chasing bots, or process changes.
Any relevant notes, assumptions, or dependencies:
No environment access needed — the workflow description and rough time breakdown above are the primary input
Some steps are naturally more automatable (verifying merge/pipeline status, verifying test cycle presence) than others (chasing human approvals, CAB presentation)
Deliverable: a short write-up or slide, not code
Team already has some ideas in mind for this area — useful to compare against, but interns shouldn't be primed with them beforehand
Want both problem statements combined into one doc for the review board, or kept separate?


Problem Statement / Use Case Title: Skill to Auto-Generate Release/Change Ticket and Run Book Templates from Past Releases
Background / Context: Drafting the release ticket, release unit, change ticket, and the Confluence run book all involve filling many mandatory fields and sections that look similar release over release. The release manager currently drafts these largely from scratch each sprint, referencing past tickets and run books manually for structure and wording.
Current Challenge: This repetitive drafting work takes real time (part of the ~1 hour spent on initial ticket/run book drafting, plus run book finalization later in the cycle) and depends on the release manager remembering or hunting down how similar fields and run book steps were filled in previous releases.
Expected Outcome / Goal: Propose a skill that, given access to previous release tickets, change tickets, and Confluence run books, generates a draft template for the upcoming release — pre-filling fields and run book sections that follow a consistent pattern release-to-release, and clearly flagging what needs release-specific input (e.g., specific components being released, new steps, environment-specific details). Deliverable is the skill's design: what past data it draws from, what it generates, what it leaves for the release manager to fill in, and how it would be invoked.
Any relevant notes, assumptions, or dependencies:
Access to a sample of past release/change tickets and Confluence run books needed as reference material
Not all fields or run book steps are template-able — part of the exercise is distinguishing boilerplate content from release-specific content
Not implementation-required, but interns can prototype a partial version if time allows, given this is more scoped than the broader agent ideas
Deliverable: a short write-up of the skill design, optionally with a partial working example