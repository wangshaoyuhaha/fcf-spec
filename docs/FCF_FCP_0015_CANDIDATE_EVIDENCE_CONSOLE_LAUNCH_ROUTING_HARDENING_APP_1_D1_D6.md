# FCF FCP 0015 Candidate Evidence Console Launch Routing Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Registered Review Routes

The FCP-0013 and FCP-0014 launchers build loopback URLs for their exact
registered read-only review routes. Neither launcher targets the console root.

## D2 Explicit Presentation Language

The selected `zh-CN` or `en` language is included exactly once as the `lang`
query parameter. Unregistered language values fail closed.

## D3 One Operator URL

Each launcher uses one URL value for terminal presentation and automatic
browser opening. This prevents the displayed destination from diverging from
the opened destination.

## D4 Regression Coverage

Focused tests cover both routes, both registered languages, and rejection of an
unregistered language.

## D5 Safety Boundary

The change is presentation routing only. It adds no network client, provider
selection, credential input, data activation, write method, gap closure,
product authorization, or execution path.

## D6 Validation And Closeout

Validation order is the isolated FCP-0015 suite, related FCP-0013 and FCP-0014
suites, full pytest, `scripts/run_all_checks.py`, generated-output restoration,
exact changed-file verification, and `git diff --check`.

Validated result:

- FCP-0015 isolated suite: 8 passed
- FCP-0013 through FCP-0015 related suite: 62 passed
- FCP governance guard subset: 44 passed
- full pytest: 5712 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
