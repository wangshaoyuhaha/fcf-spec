from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import RegisteredCausalTransmissionGraph


@dataclass(frozen=True)
class LocalCausalTransmissionGraphRegistry:
    graphs: tuple[RegisteredCausalTransmissionGraph, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("causal transmission graph capacity is invalid")
        graphs = tuple(self.graphs)
        if len(graphs) > self.capacity:
            raise ValueError("causal transmission graph capacity exceeded")
        identities = {(item.graph_id, item.graph_version) for item in graphs}
        if len(identities) != len(graphs):
            raise ValueError("duplicate causal transmission graph identity is prohibited")
        if len({item.graph_hash for item in graphs}) != len(graphs):
            raise ValueError("duplicate causal transmission graph hash is prohibited")
        object.__setattr__(self, "graphs", graphs)

    def append(
        self, graph: RegisteredCausalTransmissionGraph
    ) -> LocalCausalTransmissionGraphRegistry:
        if not isinstance(graph, RegisteredCausalTransmissionGraph):
            raise ValueError("registry accepts RegisteredCausalTransmissionGraph only")
        if len(self.graphs) >= self.capacity:
            raise ValueError("causal transmission graph capacity exceeded")
        return replace(self, graphs=(*self.graphs, graph))
