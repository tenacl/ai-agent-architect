"""
{{프로젝트명}} — Claude API 기반 Unified Cognition 에이전트
====================================================================

워크시트 STEP 3에서 "Unified Cognition" 선택 시 사용.
강의 18~20번 슬라이드 철학: 하나의 코어가 모든 것을 한다.

핵심 특징:
- 하나의 LLM이 Planning · Memory · Reflection · Tool Use · Execution 모두 처리
- 외부 조율(Supervisor 등) 없음
- 도구는 분리하되 에이전트는 분리하지 않음 (강의 17·20번)

설치:
    pip install anthropic
"""

import json
from anthropic import Anthropic
from typing import Any


# ============================================================
# 1. Cognitive Core — 하나의 통합 인지
# ============================================================

client = Anthropic()

# 별도 생성된 system-prompt.md에서 로드
with open("system-prompt.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

MODEL = "{{모델 ID}}"   # 예: claude-opus-4-7


# ============================================================
# 2. 도구 정의 — STEP 9 A
#    "도구는 분리, 에이전트는 분리하지 않는다"
# ============================================================

# {{STEP 9 A에서 체크된 도구들을 Claude tool_use schema로 정의}}
TOOLS_SCHEMA = [
    {
        "name": "web_search",
        "description": "{{STEP 9 도구 1 용도}}",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색 쿼리"}
            },
            "required": ["query"]
        }
    },
    # {{추가 도구들...}}
]


def execute_tool(name: str, input: dict) -> str:
    """실제 도구 실행. 거버넌스 체크는 여기서."""

    # ===== 거버넌스 (STEP 7 A) =====
    if name in BLACKLIST:
        return json.dumps({"error": f"BLOCKED: {name} is blacklisted"})
    if requires_hitl(name, input):
        return json.dumps({"status": "REQUIRES_HUMAN_APPROVAL", "action": name, "input": input})

    # ===== 감사 로그 =====
    audit_log.append({"tool": name, "input": input})

    # ===== 실제 실행 =====
    if name == "web_search":
        return _do_web_search(input["query"])
    # {{추가 도구들...}}

    return json.dumps({"error": f"Unknown tool: {name}"})


# ============================================================
# 3. 거버넌스 (STEP 7 A)
# ============================================================

BLACKLIST = [
    # {{STEP 7 A 블랙리스트}}
]

def requires_hitl(name: str, input: dict) -> bool:
    """{{STEP 7 A HITL 지점}}"""
    # 예: 금액이 큰 결제, 외부 발송, 삭제 작업 등
    return False

audit_log: list = []


# ============================================================
# 4. Evaluator + Replanner는 시스템 프롬프트로 통합 (Unified 철학)
#    별도 노드가 아니라 같은 모델이 self-check 한다
# ============================================================

EVALUATION_PROMPT_SUFFIX = """

---
[자기검증 — 매 응답 직전 점검]
{{STEP 8 ① 검증 기준}}

만약 검증을 통과하지 못하면 다른 접근으로 재시도하세요.
재시도 최대 {{STEP 8 ② 최대 횟수}}회.
"""


# ============================================================
# 5. 메인 루프 — 하나의 추론으로 통합
# ============================================================

def run_agent(user_message: str, max_iterations: int = 10) -> dict:
    """
    Unified Cognition 루프:
    같은 모델이 계획·실행·검증·반성을 모두 수행.
    Tool Use가 끝날 때까지 계속 모델에게 돌려준다.
    """

    messages = [
        {"role": "user", "content": user_message}
    ]

    for iteration in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT + EVALUATION_PROMPT_SUFFIX,
            tools=TOOLS_SCHEMA,
            messages=messages
        )

        # 응답에 도구 호출이 없으면 — 최종 답변
        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return {
                "answer": final_text,
                "audit_log": audit_log,
                "iterations": iteration + 1
            }

        # 도구 호출 처리
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})

    return {
        "answer": "[최대 반복 초과 — Replanner 한계 도달]",
        "audit_log": audit_log,
        "iterations": max_iterations
    }


# ============================================================
# 6. 실행 예시
# ============================================================

if __name__ == "__main__":
    result = run_agent("{{사용자 첫 요청 예시}}")

    print("=" * 60)
    print("최종 응답:", result["answer"])
    print(f"반복 횟수: {result['iterations']}")
    print("=" * 60)
    print("감사 로그 (Observability):")
    for entry in result["audit_log"]:
        print(" -", entry)


# ============================================================
# 운영 환경 투입 전 체크리스트
# ============================================================
#
# 🚦 강의 룰 (5번·26번 슬라이드):
#
# ☐ BLACKLIST가 실제로 채워짐
# ☐ requires_hitl()이 실제 조건으로 구현됨
# ☐ EVALUATION_PROMPT_SUFFIX의 검증 기준이 빈 문자열이 아님
# ☐ audit_log가 영속 저장됨 (DB, 파일)
# ☐ max_iterations가 무한루프 방지 (10~20 권장)
# ☐ 도구 입력 sanitization 추가 (특히 코드/쿼리 실행 계열)
# ☐ 거대 컨텍스트 대응 — 강의 18번 단점 ① "Context Collapse" 주의
#
# Unified 진영의 약점은 거대 컨텍스트. 메시지 누적이 길어지면
# 요약/롤링 윈도우 도입 검토.
