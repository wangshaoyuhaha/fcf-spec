from types import MappingProxyType


def build_p4_console_sections(
    case_retrieval,
    challenger_candidate,
    shadow_validation,
    schedule_proposal,
    training_evaluation,
):
    return MappingProxyType(
        {
            "case_memory_retrieval": (
                MappingProxyType(
                    {
                        "case_count": len(case_retrieval.records),
                        "network_access_used": False,
                        "point_in_time_enforced": True,
                        "query_id": case_retrieval.query_id,
                        "read_only": True,
                    }
                ),
            ),
            "challenger_proposal": (
                MappingProxyType(
                    {
                        "automatic_activation_allowed": False,
                        "candidate_id": challenger_candidate.candidate_id,
                        "candidate_only": True,
                        "operator_review_required": True,
                    }
                ),
            ),
            "realtime_shadow_validation": (
                MappingProxyType(
                    {
                        "network_access_used": False,
                        "observation_count": shadow_validation.observation_count,
                        "real_execution_used": False,
                        "status": shadow_validation.status,
                    }
                ),
            ),
            "experiment_schedule_proposal": (
                MappingProxyType(
                    {
                        "job_execution_allowed": False,
                        "schedule_id": schedule_proposal.schedule_id,
                        "status": schedule_proposal.status,
                    }
                ),
            ),
            "specialist_training_governance": (
                MappingProxyType(
                    {
                        "advisory_only": True,
                        "automatic_activation_allowed": False,
                        "status": training_evaluation.status,
                        "training_execution_allowed": False,
                    }
                ),
            ),
        }
    )
