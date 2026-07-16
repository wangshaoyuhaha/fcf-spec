from types import MappingProxyType


def build_p0_p3_console_sections(
    backtest_result,
    ai_evaluation,
    experiment,
    gate_decision,
):
    return MappingProxyType(
        {
            "deterministic_backtest": (
                MappingProxyType(
                    {
                        "failure_codes": backtest_result.failure_codes,
                        "result_id": backtest_result.result_id,
                        "status": backtest_result.status.value,
                    }
                ),
            ),
            "ai_historical_evaluation": (
                MappingProxyType(
                    {
                        "advisory_only": True,
                        "incremental_value": str(ai_evaluation.incremental_value),
                        "model_invocation_performed": False,
                        "status": ai_evaluation.status,
                    }
                ),
            ),
            "challenger_experiment": (
                MappingProxyType(
                    {
                        "experiment_id": experiment.experiment_id,
                        "experiment_label": experiment.experiment_label,
                        "status": experiment.status,
                    }
                ),
            ),
            "controlled_evolution_gate": (
                MappingProxyType(
                    {
                        "automatic_activation_allowed": False,
                        "audit_sha256": gate_decision.audit_sha256,
                        "operator_review_required": True,
                        "status": gate_decision.status,
                    }
                ),
            ),
        }
    )
