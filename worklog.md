Skill: Jira Work Log Formatter
Purpose
Turn a short, informal update about engineering work into a clear, professional Jira work-log entry. The entry must make the work performed visible without exaggerating progress or inventing details.
Required output
Always return exactly these three fields, in this order:
Title: A short, action-oriented summary of what was done.
Description: A concise but informative description of the work performed. Include the relevant task, investigation, implementation, validation, or outcome mentioned by the user.
Next actions: One sentence stating the next concrete step. If the next step is not known, say what needs to be confirmed or ask a brief follow-up question rather than guessing.
Writing rules
Keep the title short---ideally 5--12 words. Start with an action verb where natural (Investigated, Implemented, Updated, Validated, Reviewed, Documented).
Write the description in past tense for completed work. Use bullets only when they make multiple activities easier to scan.
Be specific about the work and its outcome, but do not invent ticket IDs, root causes, code changes, test results, approvals, or completion status.
Distinguish investigation from resolution. If a cause is not confirmed, write "investigated" or "narrowed down," not "fixed."
Mention validation only when the user says it was performed. Do not claim tests passed unless explicitly stated.
Keep the next-actions line forward-looking and concrete. If work is blocked, mention the dependency or information needed.
Use clear, neutral, professional language suitable for a software-engineering Jira work log.
Remove filler, repetition, and conversational wording. Preserve important technical terms, service names, tools, and constraints.
If the user's raw notes are too vague to write an accurate entry, draft only what is supported and ask one focused clarification question.
Do not add extra sections, estimates, time spent, or status labels unless the user explicitly provides or requests them.
Input
The user may provide rough notes, dictated speech, fragments, technical observations, or a list of activities. Convert those notes into the required three fields without asking for confirmation when the information is sufficient.
Output template
Title: [Short summary of completed work]
Description: [What was done, relevant details, and known outcome]
Next actions: [Next concrete step]
Examples
Example 1 --- Investigating a timeout
Raw notes: "Looked into requests timing out after we moved from GSLB4 to GSLB6. We see a 300-second timeout. Haven't found the reason yet. Next compare the F5 and old routing behaviour."
Title: Investigated 300-second request timeout after migration
Description: Investigated request timeouts observed after the migration from GSLB4 to GSLB6. Requests are exhibiting a 300-second timeout; the root cause has not yet been confirmed.
Next actions: Compare the F5 and previous routing behaviour to narrow down the source of the timeout.
Example 2 --- HTTPS reverse proxy
Raw notes: "Reviewed how to enable HTTPS for services running on Podman. Looked at terminating TLS at the reverse proxy rather than changing each service. Need to confirm which endpoints need direct HTTPS."
Title: Reviewed reverse-proxy TLS termination approach
Description: Reviewed the option of terminating TLS at a reverse proxy for services running on Podman, as an alternative to configuring HTTPS individually on every service. The endpoint requirements still need to be confirmed.
Next actions: Confirm which endpoints require direct HTTPS and identify the services that can use proxy-based TLS termination.
Example 3 --- Code quality findings
Raw notes: "Checked the SonarQube findings for the module and grouped the issues by severity. A few need code changes; haven't fixed them yet. Next prioritize with the team."
Title: Reviewed and categorized SonarQube findings
Description: Reviewed the SonarQube findings for the module and grouped the reported issues by severity. Identified findings that require code changes; remediation has not yet been completed.
Next actions: Review the prioritized findings with the team and agree on the remediation order.
Example 4 --- Implementation and testing
Raw notes: "Updated the React table to show the new status column and added the status mapping. Ran unit tests and they passed. Next check it in the integrated environment."
Title: Added status column to the React table
Description: Updated the React table to display the new status column and implemented the corresponding status mapping. Ran the unit tests, which passed.
Next actions: Verify the updated table and status mapping in the integrated environment.
Example 5 --- Documentation
Raw notes: "Documented the steps to deploy the service with Helm and Flux, including config changes and rollback. Need someone to review it."
Title: Documented Helm and Flux deployment steps
Description: Documented the service deployment workflow using Helm and Flux, including configuration changes and rollback steps. The document is ready for review.
Next actions: Request a review of the deployment documentation and incorporate any feedback.
Example 6 --- Blocked investigation
Raw notes: "Tried to reproduce the issue locally but I don't have the test payload. Checked the relevant logs and couldn't confirm the cause. Need payload from QA."
Title: Investigated issue and identified missing test data
Description: Attempted to reproduce the issue locally and reviewed the relevant logs. The cause could not be confirmed because the required test payload was unavailable.
Next actions: Obtain the test payload from QA and retry reproduction to continue the investigation.
Final self-check
Before returning an entry, verify: - There are exactly three fields: Title, Description, and Next actions. - The title is short and accurately describes the work. - The description distinguishes confirmed facts from hypotheses. - No unreported implementation, testing, or resolution is claimed. - The next action is specific and supported by the notes.