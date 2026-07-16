# FCF Current State - MULTI-MARKET-ADAPTERS Stage 6 Final

## Status

COMPLETED_VALIDATED_READY_FOR_MAIN_MERGE

## Branch

sidecar-multi-market-adapters-stage-6

## Approval commit

`996414deaa7ff186622569f702d144d4bda554a1`

## Delivery commit

Pending current delivery commit.

## Completed scope

- shared immutable market-adapter boundary and versioned profile contracts
- China A-share adapter
- United States equity adapter
- Hong Kong equity adapter
- gold and commodity adapter
- digital-asset adapter
- futures adapter
- ordered registry, immutable review packets, and Stage 6 acceptance

## Sidecar validation

- independent pytest: 18 passed
- targeted pytest: 131 passed, 2 skipped
- full pytest: 4464 passed, 5 skipped
- `scripts/run_all_checks.py`: PASSED
- generated outputs: RESTORED
- `git diff --check`: PASSED

## Next dependency

Portfolio Construction and Portfolio Stress Test remain not started and
require separate approval.

No live data retrieval, model invocation, Prompt execution, credential,
account, wallet, broker, exchange connection, balance, position, order,
execution, tag, release, or deployment is authorized.
