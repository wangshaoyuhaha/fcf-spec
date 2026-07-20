from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsoleLocalizationConsistencyBoundary:
    presentation_only: bool = True
    preserves_registered_evidence: bool = True
    preserves_deterministic_values: bool = True
    default_simplified_chinese: bool = True
    explicit_english_option: bool = True
    external_network_allowed: bool = False
    credentials_allowed: bool = False
    trading_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all(
            (
                self.presentation_only,
                self.preserves_registered_evidence,
                self.preserves_deterministic_values,
                self.default_simplified_chinese,
                self.explicit_english_option,
            )
        ):
            raise ValueError("localization boundary cannot be weakened")
        if any(
            (
                self.external_network_allowed,
                self.credentials_allowed,
                self.trading_or_execution_allowed,
            )
        ):
            raise ValueError("localization boundary cannot add authority")


FCP_0010_BOUNDARY = ConsoleLocalizationConsistencyBoundary()
