from typing import Any, Dict, Optional

API_NAME = "paper_execution_response_templates"
API_VERSION = "0.1.0"

SAFETY_NOTICE = (
    "安全边界：当前结果仅为 paper / sandbox execution。系统没有连接真实交易所，"
    "没有保存真实 API key，没有读取钱包私钥，没有真实下单，没有真实资金变化，"
    "也没有真实仓位变化。"
)

FORBIDDEN_INTENTS = {
    "place_real_order",
    "connect_exchange",
    "save_api_key",
    "read_wallet_private_key",
    "real_execution",
    "bypass_risk",
    "force_execute_trade",
    "convert_paper_to_real_order",
}


def _body(response: Dict[str, Any]) -> Dict[str, Any]:
    return response.get("body", response)


def _base_response(
    response_type: str,
    title: str,
    message: str,
    fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": True,
        "api": API_NAME,
        "api_version": API_VERSION,
        "response_type": response_type,
        "title": title,
        "message": message,
        "safety_notice": SAFETY_NOTICE,
        "fields": fields or {},
    }


def render_paper_fill_success_response(paper_response: Dict[str, Any]) -> Dict[str, Any]:
    body = _body(paper_response)
    data = body.get("data") or {}

    execution_status = data.get("execution_status")
    title = "纸面模拟成交完成"
    if execution_status == "partial_filled":
        title = "纸面模拟部分成交完成"

    message = (
        "本次 paper / sandbox execution 已完成模拟成交处理。"
        "这不是实盘成交，没有连接真实交易所，也没有真实下单。"
    )

    replay = data.get("replay") or {}

    return _base_response(
        response_type="paper_fill_success",
        title=title,
        message=message,
        fields={
            "execution_status": execution_status,
            "event_name": data.get("event_name"),
            "event_count": data.get("event_count"),
            "replay_status": replay.get("status"),
            "replay_event_count": replay.get("event_count"),
            "symbol": data.get("symbol"),
            "asset_class": data.get("asset_class"),
            "side": data.get("side"),
            "order_type": data.get("order_type"),
            "requested_quantity": data.get("requested_quantity"),
            "filled_quantity": data.get("filled_quantity"),
            "remaining_quantity": data.get("remaining_quantity"),
            "fill_price": data.get("fill_price"),
            "notional": data.get("notional"),
            "real_order": data.get("real_order"),
            "real_execution": data.get("real_execution"),
            "real_exchange_api": data.get("real_exchange_api"),
            "real_money_impact": data.get("real_money_impact"),
        },
    )


def render_paper_reject_success_response(paper_response: Dict[str, Any]) -> Dict[str, Any]:
    body = _body(paper_response)
    data = body.get("data") or {}
    replay = data.get("replay") or {}

    message = (
        "本次 paper / sandbox execution 已完成模拟拒单处理。"
        "这不是交易所真实拒单，没有连接真实交易所，也没有真实下单。"
    )

    return _base_response(
        response_type="paper_reject_success",
        title="纸面模拟拒单完成",
        message=message,
        fields={
            "execution_status": data.get("execution_status"),
            "event_name": data.get("event_name"),
            "event_count": data.get("event_count"),
            "replay_status": replay.get("status"),
            "replay_event_count": replay.get("event_count"),
            "symbol": data.get("symbol"),
            "asset_class": data.get("asset_class"),
            "side": data.get("side"),
            "order_type": data.get("order_type"),
            "requested_quantity": data.get("requested_quantity"),
            "reject_reason": data.get("reject_reason"),
            "real_order": data.get("real_order"),
            "real_execution": data.get("real_execution"),
            "real_exchange_api": data.get("real_exchange_api"),
            "real_money_impact": data.get("real_money_impact"),
        },
    )


def render_paper_execution_error_response(paper_response: Dict[str, Any]) -> Dict[str, Any]:
    body = _body(paper_response)
    error = body.get("error") or {}

    error_type = error.get("type", "UnknownError")
    error_message = error.get("message", "unknown error")

    message = (
        "本次 paper execution 输入没有通过校验，因此没有进入模拟执行成功分支。"
        "请根据错误信息修正输入后重新提交。"
        "本次没有连接真实交易所，也没有真实下单。"
    )

    return _base_response(
        response_type="paper_execution_error",
        title="纸面模拟执行校验失败",
        message=message,
        fields={
            "error_type": error_type,
            "error_message": error_message,
        },
    )


def render_paper_safety_refusal(intent: str, reason: Optional[str] = None) -> Dict[str, Any]:
    message = (
        "当前系统只支持 paper / sandbox execution，不能执行该操作。"
        "系统不能连接真实交易所，不能保存真实 API key，不能读取钱包私钥，不能真实下单，"
        "也不能把 paper execution 伪装成 real execution。"
    )

    return _base_response(
        response_type="paper_safety_refusal",
        title="已拒绝不安全的真实执行请求",
        message=message,
        fields={
            "intent": intent,
            "reason": reason or "operation is outside paper-only safe boundary",
            "forbidden_intents": sorted(FORBIDDEN_INTENTS),
        },
    )


def render_paper_execution_user_response(
    paper_response: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
) -> Dict[str, Any]:
    if intent in FORBIDDEN_INTENTS:
        return render_paper_safety_refusal(intent=intent)

    if paper_response is None:
        return render_paper_execution_error_response(
            {
                "ok": False,
                "error": {
                    "type": "MissingResponse",
                    "message": "paper_response is required",
                },
                "data": None,
            }
        )

    body = _body(paper_response)

    if body.get("ok") is not True:
        return render_paper_execution_error_response(paper_response)

    data = body.get("data") or {}
    execution_status = data.get("execution_status")

    if execution_status in {"filled", "partial_filled"}:
        return render_paper_fill_success_response(paper_response)

    if execution_status == "rejected":
        return render_paper_reject_success_response(paper_response)

    return render_paper_execution_error_response(
        {
            "ok": False,
            "error": {
                "type": "UnknownExecutionStatus",
                "message": f"unsupported execution_status: {execution_status}",
            },
            "data": None,
        }
    )
