import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OPENAI_MAX_TOKENS
from app.services.analysis import compute_summary, compute_statistics

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            client_kwargs["base_url"] = OPENAI_BASE_URL
        _client = OpenAI(**client_kwargs)
    return _client

# ---- 보너스: Function Calling 스키마 ----
# GPT가 필요하다고 판단하면 아래 두 "도구"를 스스로 호출할 수 있음
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_data_statistics",
            "description": "저장된 시계열 데이터의 상세 통계(표준편차, 최근 7개 이동평균 포함)를 조회한다. "
                            "사용자가 '더 자세히', '표준편차', '이동평균' 등 심화 통계를 물을 때 사용.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def build_system_prompt(summary: dict) -> str:
    metrics = summary["metrics"]
    return (
        "당신은 데이터 분석 비서입니다.\n\n"
        "[사용자 데이터 요약]\n"
        f"- 데이터 기간: {summary['period']}\n"
        f"- 총 레코드: {summary['count']}개\n"
        f"- 주요 지표: 합계 {metrics['total']}, 평균 {metrics['average']}, "
        f"최대 {metrics['max']}, 최소 {metrics['min']}\n"
        f"- 최근 트렌드: {summary['trend']}\n\n"
        "위 데이터를 기반으로 맞춤형 답변을 제공하세요. 필요하면 제공된 도구를 호출해 "
        "더 상세한 통계를 확인한 뒤 답변하세요."
    )


def run_chat(history: list, all_data_items: list) -> dict:
    """
    history: [{"role": "user"/"assistant", "content": "..."}, ...] (직전 대화 포함)
    반환: {"reply": str, "used_tools": [str, ...]}
    """
    client = get_client()
    summary = compute_summary(all_data_items)
    system_prompt = build_system_prompt(summary)

    messages = [{"role": "system", "content": system_prompt}] + history
    used_tools = []

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=OPENAI_MAX_TOKENS,
        messages=messages,
        tools=TOOLS,
    )

    # GPT가 도구 호출을 요청한 경우 처리
    if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
        messages.append(choice.message)
        for tool_call in choice.message.tool_calls:
            if tool_call.function.name == "get_data_statistics":
                stats_result = compute_statistics(all_data_items)
                used_tools.append("get_data_statistics")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(stats_result, ensure_ascii=False),
                    }
                )
        # 도구 결과를 반영해 최종 응답 재요청
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            max_tokens=OPENAI_MAX_TOKENS,
            messages=messages,
        )
        choice = response.choices[0]

    reply_text = choice.message.content
    if not reply_text:
        raise RuntimeError(
            f"GPT 응답이 비어 있습니다. finish_reason={choice.finish_reason}, "
            f"model={OPENAI_MODEL}, usage={getattr(response, 'usage', None)}"
        )

    return {"reply": choice.message.content, "used_tools": used_tools}
