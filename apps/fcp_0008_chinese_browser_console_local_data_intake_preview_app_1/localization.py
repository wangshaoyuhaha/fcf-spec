from __future__ import annotations

import re
from types import MappingProxyType
from typing import Mapping

from .contracts import ConsoleLocale


ZH_CN_TRANSLATIONS: Mapping[str, str] = MappingProxyType(
    {
        "FCF Browser Product Console": "FCF \u91d1\u878d\u8ba4\u77e5\u6846\u67b6\u63a7\u5236\u53f0",
        "Paper-only / Local loopback / Operator review required": (
            "\u7eb8\u4e0a\u7814\u7a76 / \u672c\u673a\u56de\u73af / \u5fc5\u987b\u4eba\u5de5\u590d\u6838"
        ),
        "Overview": "\u603b\u89c8",
        "Data Workspace": "\u6570\u636e\u5de5\u4f5c\u533a",
        "Stock Candidates": "\u80a1\u7968\u5019\u9009",
        "Research Runs": "\u7814\u7a76\u8fd0\u884c",
        "AI Comparison": "AI \u5bf9\u6bd4",
        "Evidence and Risk": "\u8bc1\u636e\u4e0e\u98ce\u9669",
        "Paper and Shadow Validation": "\u7eb8\u4e0a\u4e0e\u5f71\u5b50\u9a8c\u8bc1",
        "Operator Review": "\u64cd\u4f5c\u5458\u590d\u6838",
        "Reports and Archive": "\u62a5\u544a\u4e0e\u5f52\u6863",
        "Governance": "\u6cbb\u7406",
        "Audit History": "\u5ba1\u8ba1\u5386\u53f2",
        "Evidence Audit": "\u8bc1\u636e\u5ba1\u8ba1",
        "Artifact Explorer": "\u5de5\u4ef6\u6d4f\u89c8",
        "Evidence Lineage": "\u8bc1\u636e\u8840\u7f18",
        "Risk and AI": "\u98ce\u9669\u4e0e AI",
        "Validation Lifecycle": "\u9a8c\u8bc1\u751f\u547d\u5468\u671f",
        "Review Lifecycle": "\u590d\u6838\u751f\u547d\u5468\u671f",
        "Archive Lifecycle": "\u5f52\u6863\u751f\u547d\u5468\u671f",
        "Local Data Intake": "\u672c\u5730\u6570\u636e\u63a5\u5165",
        "Local Data Intake Preview": "\u672c\u5730\u6570\u636e\u63a5\u5165\u9884\u68c0",
        "Data classification": "\u6570\u636e\u5206\u7c7b",
        "Verify registered evidence and complete Operator review before any decision.": (
            "\u4efb\u4f55\u51b3\u7b56\u524d\u5fc5\u987b\u6838\u9a8c\u5df2\u767b\u8bb0\u8bc1\u636e\u5e76\u5b8c\u6210\u64cd\u4f5c\u5458\u590d\u6838\u3002"
        ),
        "Correlation ID": "\u5173\u8054 ID",
        "Registered artifacts": "\u5df2\u767b\u8bb0\u5de5\u4ef6",
        "Stock candidates": "\u80a1\u7968\u5019\u9009",
        "Workspace state": "\u5de5\u4f5c\u533a\u72b6\u6001",
        "Available": "\u53ef\u7528",
        "Planned": "\u5df2\u89c4\u5212",
        "Registered artifact types": "\u5df2\u767b\u8bb0\u5de5\u4ef6\u7c7b\u578b",
        "Available workspaces": "\u53ef\u7528\u5de5\u4f5c\u533a",
        "Planned workspaces": "\u5df2\u89c4\u5212\u5de5\u4f5c\u533a",
        "State": "\u72b6\u6001",
        "Artifact ID": "\u5de5\u4ef6 ID",
        "Type": "\u7c7b\u578b",
        "Registered path": "\u767b\u8bb0\u8def\u5f84",
        "Payload": "\u8f7d\u8377",
        "Rank": "\u6392\u540d",
        "Symbol": "\u4ee3\u7801",
        "Name": "\u540d\u79f0",
        "Score": "\u5f97\u5206",
        "Risk flags": "\u98ce\u9669\u6807\u8bb0",
        "Confidence": "\u7f6e\u4fe1\u5ea6",
        "Presentation language": "\u754c\u9762\u8bed\u8a00",
        "Simplified Chinese": "\u7b80\u4f53\u4e2d\u6587",
        "English": "\u82f1\u6587",
        "Registered local CSV previews": "\u5df2\u767b\u8bb0\u672c\u5730 CSV \u9884\u68c0",
        "No registered local CSV preview": "\u6682\u65e0\u5df2\u767b\u8bb0\u672c\u5730 CSV \u9884\u68c0",
        "Rows": "\u884c\u6570",
        "Columns": "\u5b57\u6bb5",
        "BOM markers normalized in memory": "\u5185\u5b58\u4e2d\u89c4\u8303\u5316\u7684 BOM \u6807\u8bb0",
        "Rights state": "\u6743\u5229\u72b6\u6001",
        "Retention state": "\u4fdd\u7559\u6743\u72b6\u6001",
        "Product evidence state": "\u4ea7\u54c1\u8bc1\u636e\u72b6\u6001",
        "Read-only intake guidance": "\u53ea\u8bfb\u63a5\u5165\u6307\u5f15",
        "Register exact byte length and SHA-256 before preview.": (
            "\u9884\u68c0\u524d\u5fc5\u987b\u767b\u8bb0\u7cbe\u786e\u5b57\u8282\u957f\u5ea6\u548c SHA-256\u3002"
        ),
        "Preview never copies, rewrites, uploads, or automatically registers source bytes.": (
            "\u9884\u68c0\u4e0d\u4f1a\u590d\u5236\u3001\u6539\u5199\u3001\u4e0a\u4f20\u6216\u81ea\u52a8\u767b\u8bb0\u6e90\u6570\u636e\u3002"
        ),
        "Commercial, retention, realtime, and provider decisions remain separate Operator gates.": (
            "\u5546\u4e1a\u6388\u6743\u3001\u4fdd\u7559\u6743\u3001\u5b9e\u65f6\u6570\u636e\u548c\u4f9b\u5e94\u5546\u51b3\u7b56\u4ecd\u662f\u72ec\u7acb\u7684\u64cd\u4f5c\u5458\u95e8\u7981\u3002"
        ),
        "This console does not provide trading, order, broker, exchange, account,": (
            "\u672c\u63a7\u5236\u53f0\u4e0d\u63d0\u4f9b\u4ea4\u6613\u3001\u8ba2\u5355\u3001\u5238\u5546\u3001\u4ea4\u6613\u6240\u6216\u8d26\u6237\u6743\u9650\uff0c"
        ),
        "balance, position, wallet, promotion, or automatic approval authority.": (
            "\u4e5f\u4e0d\u63d0\u4f9b\u4f59\u989d\u3001\u6301\u4ed3\u3001\u94b1\u5305\u3001\u63a8\u5e7f\u6216\u81ea\u52a8\u5ba1\u6279\u6743\u9650\u3002"
        ),
    }
)


def localize_html(document: str, locale: ConsoleLocale) -> str:
    if not isinstance(locale, ConsoleLocale):
        raise TypeError("locale must be ConsoleLocale")
    if locale.locale_id == "en":
        return document
    localized = document.replace('lang="en"', 'lang="zh-CN"')
    protected: list[str] = []

    def preserve(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__FCF_LOCALIZATION_PROTECTED_{len(protected) - 1}__"

    localized = re.sub(
        r"<(?:code|td)\b[^>]*>.*?</(?:code|td)>",
        preserve,
        localized,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for source in sorted(ZH_CN_TRANSLATIONS, key=len, reverse=True):
        localized = localized.replace(source, ZH_CN_TRANSLATIONS[source])
    for index, value in enumerate(protected):
        localized = localized.replace(
            f"__FCF_LOCALIZATION_PROTECTED_{index}__",
            value,
        )
    return localized
