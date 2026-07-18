from dataclasses import dataclass
from .resolver import FXTransmissionSensitivitySnapshot
@dataclass(frozen=True)
class V2R31OperatorAcceptance:
    snapshot_hash:str;snapshot_state:str;status:str="WAITING_FOR_OPERATOR_REVIEW";operator_review_required:bool=True;automatic_approval:bool=False;foreign_flow_inference:bool=False;causal_conclusion:bool=False;factor_activated:bool=False;action_created:bool=False
def build_operator_acceptance(snapshot:FXTransmissionSensitivitySnapshot)->V2R31OperatorAcceptance:return V2R31OperatorAcceptance(snapshot.snapshot_hash,snapshot.state)
