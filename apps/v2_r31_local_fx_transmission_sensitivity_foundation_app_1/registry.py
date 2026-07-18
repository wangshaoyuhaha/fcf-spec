from dataclasses import dataclass, replace
from .contracts import FXTransmissionSensitivityRecord, RegisteredFXTransmissionSeries
@dataclass(frozen=True)
class LocalFXTransmissionSensitivityRegistry:
    series: tuple[RegisteredFXTransmissionSeries,...]=(); records: tuple[FXTransmissionSensitivityRecord,...]=(); capacity:int=10000
    def __post_init__(self)->None:
        series,records=tuple(self.series),tuple(self.records)
        if isinstance(self.capacity,bool) or not 1<=self.capacity<=100000 or len(series)+len(records)>self.capacity: raise ValueError("FX registry capacity is invalid")
        if len({x.series_id for x in series})!=len(series) or len({x.series_hash for x in series})!=len(series): raise ValueError("duplicate FX series is prohibited")
        if len({x.record_id for x in records})!=len(records) or len({x.record_hash for x in records})!=len(records): raise ValueError("duplicate FX record is prohibited")
        hashes={x.series_hash for x in series}
        if any(x.series.series_hash not in hashes for x in records): raise ValueError("sensitivity series must be registered")
        object.__setattr__(self,"series",series);object.__setattr__(self,"records",records)
    def append_series(self,item:RegisteredFXTransmissionSeries)->"LocalFXTransmissionSensitivityRegistry":
        if not isinstance(item,RegisteredFXTransmissionSeries): raise ValueError("registry accepts RegisteredFXTransmissionSeries only")
        return replace(self,series=(*self.series,item))
    def append_record(self,item:FXTransmissionSensitivityRecord)->"LocalFXTransmissionSensitivityRegistry":
        if not isinstance(item,FXTransmissionSensitivityRecord): raise ValueError("registry accepts FXTransmissionSensitivityRecord only")
        return replace(self,records=(*self.records,item))
