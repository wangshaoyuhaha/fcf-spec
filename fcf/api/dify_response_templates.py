from typing import Any, Dict, Optional

API_NAME = "dify_response_templates"
API_VERSION = "0.1.0"

SAFETY_NOTICE = (
    "安全边界：当前系统没有连接真实交易所，没有保存真实 API key，"
    "没有读取钱包私钥，也没有真实下单。Dify 只调用 FCF 受控 API wrapper / pipeline。"
)

FORBIDDEN_INTENTS = {
    "place_real_order",
    "connect_exchange",
    "save_api_key",
    "read_wallet_private_key",
    "bypass_risk",
    "force_execute_trade",
}


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


def render_success_response(fcf_response: Dict[str, Any]) -> Dict[str, Any]:
    body = fcf_response.get("body", fcf_response)
    data = body.get("data") or {}

    event_count = data.get("event_count")
    replay = data.get("replay") or {}
    replay_status = replay.get("status")
    replay_event_count = replay.get("event_count")
    persisted = data.get("persisted")
    output_path = data.get("output_path")

    message = (
        "FCF 已接收本次市场输入，并通过受控 pipeline 完成处理。"
        "本次没有连接真实交易所，也没有真实下单。"
    )

    return _base_response(
        response_type="success",
        title="市场输入处理完成",
        message=message,
        fields={
            "event_count": event_count,
            "replay_status": replay_status,
            "replay_event_count": replay_event_count,
            "persisted": persisted,
            "output_path": output_path,
        },
    )


def render_error_response(fcf_response: Dict[str, Any]) -> Dict[str, Any]:
    body = fcf_response.get("body", fcf_response)
    error = body.get("error") or {}

    error_type = error.get("type", "UnknownError")
    error_message = error.get("message", "unknown error")

    message = (
        "这次输入没有通过 FCF 校验，因此没有进入成功处理分支。"
        "请根据错误信息修正输入后重新提交。"
        "本次没有连接真实交易所，也没有真实下单。"
    )

    return _base_response(
        response_type="error",
        title="市场输入校验失败",
        message=message,
        fields={
            "error_type": error_type,
            "error_message": error_message,
        },
    )


def render_safety_refusal(intent: str, reason: Optional[str] = None) -> Dict[str, Any]:
    message = (
        "当前 FCF / Dify 集成不支持该操作。"
        "Dify 不是底层交易内核，不能连接真实交易所，不能保存真实 API key，不能真实下单。"
        "当前只能使用受控 API wrapper / pipeline 做 mock、校验、持久化和 replay。"
    )

    return _base_response(
        response_type="safety_refusal",
        title="已拒绝不安全操作",
        message=message,
        fields={
            "intent": intent,
            "reason": reason or "operation is outside current safe boundary",
            "forbidden_intents": sorted(FORBIDDEN_INTENTS),
        },
    )


def render_dify_user_response(
    fcf_response: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
) -> Dict[str, Any]:
    if intent in FORBIDDEN_INTENTS:
        return render_safety_refusal(intent=intent)

    if fcf_response is None:
        return render_error_response(
            {
                "ok": False,
                "error": {
                    "type": "MissingResponse",
                    "message": "fcf_response is required",
                },
            }
        )

    body = fcf_response.get("body", fcf_response)

    if body.get("ok") is True:
        return render_success_response(fcf_response)

    return render_error_response(fcf_response)
