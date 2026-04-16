# A/B Eval Protocol

Shared evaluation protocol for comparing original vs optimized skill versions. Used by Description Triggering (Target 1), Workflow Chain Integrity (Target 3), and Feedback Iteration.

## Core Steps

```
1. Copy the skill to a working version (e.g. `<skill-name>-optimized/`)
2. Apply the change to the copy only
3. Create 5+ realistic test prompts that should trigger this skill
4. Dispatch two `evaluator` agents (`agents/evaluator.md`) in parallel:
   - Evaluator A: label "original", loaded with the ORIGINAL skill → run all test prompts
   - Evaluator B: label "optimized", loaded with the OPTIMIZED skill → run all test prompts
5. Compare: which version performed better on the comparison dimensions?
6. Present results to user with side-by-side comparison
7. User decides → adopt optimized version (replace original) or discard
```

## Fallback (subagent dispatch unavailable)

Ask the user which fallback to use:
- **Sequential inline:** Read `agents/evaluator.md` and follow its execution protocol inline. Run both evaluations in sequence within this conversation. Randomize which version runs first (flip a coin) to reduce ordering bias — note the execution order in results so the user can judge accordingly
- **Skip A/B:** Apply the change directly with a simple verification pass instead of comparative evaluation

## Comparison Dimensions

Each eval context defines its own comparison focus:

| Context | Dimensions | Skip Condition |
|---------|-----------|----------------|
| Description Triggering | Trigger rate, false negatives, false positives | Change is purely additive (adding trigger conditions without modifying existing phrases) |
| Chain Integrity | Transition quality ratings, broken handoffs | N/A — always run after workflow modifications |
| Feedback Iteration | Output quality, behavioral correctness | Feedback is about structural issues (missing section, wrong heading, broken reference) |

## Chain Eval Differences

Chain evaluation follows the same dispatch and fallback pattern, with these modifications:

1. Define a realistic end-to-end scenario (e.g. "design and scaffold a new bundle-plugin")
2. Dispatch `evaluator` with label "chain" and the ordered skill list
3. Review transition quality ratings — focus on "broken" handoffs
4. Address broken handoffs by improving `## Inputs` / `## Outputs` declarations

Chain eval is sequential by nature (traces a pipeline), so ordering bias is not a concern.

## Feedback Eval Differences

- **Test scenario:** Use the specific scenario from the user's feedback (the input that produced wrong results), not synthetic test prompts
- **What to compare:** Output quality and behavioral correctness, not triggering accuracy
- **When to skip:** If the feedback is about structural issues (missing section, wrong heading level, broken reference) rather than behavioral differences, a simple verification pass is sufficient
