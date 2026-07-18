from dataclasses import FrozenInstanceError,replace
from types import MappingProxyType
import pytest
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent,InstitutionalCalendarSource
from apps.v2_r31_local_fx_transmission_sensitivity_foundation_app_1 import *

def _event()->InstitutionalCalendarEvent:
    source=InstitutionalCalendarSource(source_id="official-fx-source",source_kind="OFFICIAL",registered_artifact_id="fx-artifact",artifact_version="v1",license_id="local-license",permitted_use="local-paper-research",retention_days=3650)
    return InstitutionalCalendarEvent(record_id="fx-event-r0",calendar_id="macro-calendar-v1",event_id="fx-event",event_type="MACRO_RELEASE",market="a-share",horizon="daily",event_at_utc="2026-01-02T00:00:00Z",publication_at_utc="2026-01-02T00:00:00Z",first_legally_available_at_utc="2026-01-02T00:01:00Z",retrieved_at_utc="2026-01-02T00:02:00Z",ingested_at_utc="2026-01-02T00:03:00Z",first_tradable_at_utc="2026-01-02T01:30:00Z",source=source,content_sha256="e"*64)
def _series(**changes:object)->RegisteredFXTransmissionSeries:
    values:dict[str,object]={"series_id":"fx-series-r0","subject_id":"issuer-000001","market":"a-share","horizon":"daily","observed_at_utc":"2026-01-10T00:00:00Z","available_at_utc":"2026-01-10T00:01:00Z","asset_returns":("1","2","3"),"usd_cny_returns":("1","2","3"),"usd_cnh_returns":("2","4","6"),"dxy_returns":("-1","-2","-3"),"rate_changes":("0.5","1","1.5"),"source_event":_event()};values.update(changes);return RegisteredFXTransmissionSeries(**values) # type: ignore[arg-type]
def _registry(series:RegisteredFXTransmissionSeries|None=None)->LocalFXTransmissionSensitivityRegistry:
    series=series or _series();record=FXTransmissionSensitivityRecord(record_id="fx-record-r0",series=series,available_at_utc="2026-01-10T00:02:00Z");return LocalFXTransmissionSensitivityRegistry().append_series(series).append_record(record)
def test_d1_boundary_closed_immutable():
    boundary=V2_R31_LOCAL_FX_TRANSMISSION_SENSITIVITY_BOUNDARY;assert not boundary.foreign_flow_inference_allowed
    with pytest.raises(ValueError,match="prohibited capability"):V2R31LocalFXTransmissionSensitivityBoundary(causal_conclusion_allowed=True)
    with pytest.raises(FrozenInstanceError):boundary.causal_conclusion_allowed=True # type: ignore[misc]
def test_d2_requires_three_samples():
    with pytest.raises(ValueError,match="at least three"):_series(asset_returns=("1","2"),usd_cny_returns=("1","2"),usd_cnh_returns=("1","2"),dxy_returns=("1","2"),rate_changes=("1","2"))
def test_d2_requires_equal_lengths():
    with pytest.raises(ValueError,match="equal length"):_series(rate_changes=("1","2","3","4"))
def test_d2_rejects_nonfinite():
    with pytest.raises(ValueError,match="bounded"):_series(asset_returns=("1","2","NaN"))
def test_d2_missing_series_explicit():
    empty={name:() for name in ("asset_returns","usd_cny_returns","usd_cnh_returns","dxy_returns","rate_changes")};item=_series(series_state="MISSING",missing_fields=("registered-fx-series",),**empty);assert item.series_state=="MISSING"
def test_d3_metrics_deterministic():
    record=_registry().records[0];assert (record.usd_cny_beta_bps,record.usd_cnh_beta_bps,record.dxy_beta_bps,record.rate_beta_bps,record.usd_cny_correlation_bps)==(10000,5000,-10000,20000,10000)
def test_d3_zero_variance_rejected():
    with pytest.raises(ValueError,match="variance"):_registry(_series(usd_cny_returns=("1","1","1")))
def test_d3_no_flow_causal_or_factor_claim():
    record=_registry().records[0]
    with pytest.raises(ValueError,match="foreign flow"):replace(record,foreign_flow_inference=True)
    with pytest.raises(ValueError,match="causation"):replace(record,causal_conclusion=True)
    with pytest.raises(ValueError,match="activate"):replace(record,factor_activated=True)
def test_d3_registry_requires_parent():
    record=_registry().records[0]
    with pytest.raises(ValueError,match="must be registered"):LocalFXTransmissionSensitivityRegistry(records=(record,))
def test_d4_missing_resolver_state():assert resolve_fx_transmission_sensitivity(LocalFXTransmissionSensitivityRegistry(),subject_id="issuer-000001",market="a-share",as_of_utc="2026-01-11T00:00:00Z").state=="MISSING_SERIES"
def test_d5_future_metrics_hidden():assert resolve_fx_transmission_sensitivity(_registry(),subject_id="issuer-000001",market="a-share",as_of_utc="2026-01-10T00:01:30Z").state=="MISSING_METRICS"
def test_d5_stale_series_blocked():
    empty={name:() for name in ("asset_returns","usd_cny_returns","usd_cnh_returns","dxy_returns","rate_changes")};series=_series(series_state="STALE",missing_fields=("fresh-fx-series",),**empty);registry=LocalFXTransmissionSensitivityRegistry().append_series(series);assert resolve_fx_transmission_sensitivity(registry,subject_id="issuer-000001",market="a-share",as_of_utc="2026-01-11T00:00:00Z").state=="STALE"
def test_d6_presentation_acceptance_read_only():
    registry=_registry();snapshot=resolve_fx_transmission_sensitivity(registry,subject_id="issuer-000001",market="a-share",as_of_utc="2026-01-11T00:00:00Z");model=build_read_model(registry);acceptance=build_operator_acceptance(snapshot);assert snapshot.state=="RESOLVED" and isinstance(model.payload,MappingProxyType) and acceptance.status=="WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):model.payload["causal_conclusion"]=True # type: ignore[index]
