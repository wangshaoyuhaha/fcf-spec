import hashlib,json
from dataclasses import dataclass
from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier,instant,utc
from .contracts import FXTransmissionSensitivityRecord,RegisteredFXTransmissionSeries
from .registry import LocalFXTransmissionSensitivityRegistry
@dataclass(frozen=True)
class FXTransmissionSensitivitySnapshot:
    subject_id:str;market:str;evaluated_at_utc:str;state:str;series:RegisteredFXTransmissionSeries|None;record:FXTransmissionSensitivityRecord|None;reason_codes:tuple[str,...];operator_review_required:bool;snapshot_hash:str
    def __post_init__(self)->None:
        if self.state not in {"MISSING_SERIES","MISSING","STALE","CONFLICT","MISSING_METRICS","RESOLVED"} or self.operator_review_required is not True: raise ValueError("invalid FX sensitivity snapshot")
def resolve_fx_transmission_sensitivity(registry:LocalFXTransmissionSensitivityRegistry,*,subject_id:str,market:str,as_of_utc:str)->FXTransmissionSensitivitySnapshot:
    subject,market_id,evaluated=identifier(subject_id,"subject_id"),identifier(market,"market"),utc(as_of_utc,"as_of_utc");as_of=instant(evaluated)
    values=tuple(sorted((x for x in registry.series if x.subject_id==subject and x.market==market_id and instant(x.available_at_utc)<=as_of),key=lambda x:(x.observed_at_utc,x.series_id)));series=values[-1] if values else None
    record=next((x for x in reversed(registry.records) if series is not None and x.series.series_hash==series.series_hash and instant(x.available_at_utc)<=as_of),None)
    if series is None: state,reasons="MISSING_SERIES",["NO_REGISTERED_FX_SERIES_AT_AS_OF"]
    elif series.series_state=="MISSING": state,reasons="MISSING",["REGISTERED_FX_SERIES_IS_MISSING"]
    elif series.series_state=="STALE": state,reasons="STALE",["REGISTERED_FX_SERIES_IS_STALE"]
    elif series.series_state=="CONFLICT": state,reasons="CONFLICT",["REGISTERED_FX_SERIES_IS_CONFLICTED"]
    elif record is None: state,reasons="MISSING_METRICS",["NO_REGISTERED_FX_METRICS_AT_AS_OF"]
    else: state,reasons="RESOLVED",["REGISTERED_FX_SENSITIVITY_RESOLVED","NO_FOREIGN_FLOW_INFERENCE","NO_CAUSAL_CONCLUSION"]
    payload={"evaluated":evaluated,"market":market_id,"reasons":reasons,"record":None if record is None else record.record_hash,"series":None if series is None else series.series_hash,"state":state,"subject":subject};digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()
    return FXTransmissionSensitivitySnapshot(subject,market_id,evaluated,state,series,record,tuple(reasons),True,digest)
