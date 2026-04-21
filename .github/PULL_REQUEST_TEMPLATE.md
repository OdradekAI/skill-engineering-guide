<!--
BEFORE SUBMITTING: Read every word of this template. PRs that leave
sections blank, contain multiple unrelated changes, or show no evidence
of human involvement will be closed without review.
-->

## What problem are you trying to solve?
<!-- Describe the specific problem you encountered. What broke? What
     failed? What was the user experience that motivated this?

     "Improving" something is not a problem statement. If this was a
     session issue, include: what you were doing, what went wrong, the
     exact failure mode, and ideally a log or transcript. -->

## What does this PR change?
<!-- 1-3 sentences. What, not why — the "why" belongs above. -->

## Is this change appropriate for the core toolkit?
<!-- Bundles Forge core contains skills, agents, scripts, hooks, and
     infrastructure that benefit all bundle-plugin authors. Ask yourself:

     - Would this be useful to someone building a completely different
       kind of bundle-plugin than yours?
     - Is this specific to your project, team, or a single platform?
     - Does this integrate or promote a third-party service?

     If your change is specific to your own plugin or domain, it belongs
     in your own repo — not here. -->

## What alternatives did you consider?
<!-- What other approaches did you try or evaluate before landing on this
     one? Why were they worse? If you didn't consider alternatives, say so
     — but know that's a red flag. -->

## Does this PR contain multiple unrelated changes?
<!-- If yes: stop. Split it into separate PRs. Bundled PRs will be closed.
     If you believe the changes are related, explain the dependency. -->

## Existing PRs
- [ ] I have reviewed all open AND closed PRs for duplicates or prior art
- Related PRs: <!-- #number, #number, or "none found" -->

<!-- If a related closed PR exists, explain what's different about your
     approach and why it should succeed where the other didn't. -->

## Environment tested

| Platform (e.g. Claude Code, Cursor) | Python version | OS |
|--------------------------------------|----------------|----|
|                                      |                |    |

## Validation

- [ ] `bundles-forge audit-skill .` passes
- [ ] `bundles-forge audit-security .` passes
- [ ] `bundles-forge audit-docs .` passes
- [ ] `bundles-forge audit-workflow .` passes
- [ ] `bundles-forge bump-version --check .` — no version drift
- [ ] `bundles-forge checklists --check .` — no checklist drift
- [ ] `python tests/run_all.py` — all 6 test suites pass

## Rigor

- [ ] If this is a skills change: I used `bundles-forge:auditing` and
      completed adversarial pressure testing (paste results below)
- [ ] This change was tested adversarially, not just on the happy path
- [ ] I did not modify behavior-shaping content (SKILL.md instructions,
      agent definitions, hook prompts) without eval evidence showing
      the change is an improvement

<!-- If you changed wording in skills or agents that shape AI behavior,
     show your eval methodology and results. These are not prose — they
     are code. -->

## Human review
- [ ] A human has reviewed the COMPLETE proposed diff before submission

<!--
STOP. If the checkbox above is not checked, do not submit this PR.

PRs will be closed without review if they:
- Show no evidence of human involvement
- Contain multiple unrelated changes
- Promote or integrate third-party services or tools
- Submit project-specific or personal configuration as core changes
- Leave required sections blank or use placeholder text
- Modify behavior-shaping content without eval evidence
-->
