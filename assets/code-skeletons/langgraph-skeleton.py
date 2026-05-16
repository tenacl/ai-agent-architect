"""
{{프로젝트명}} — LangGraph 기반 Hybrid 토폴로지 에이전트
====================================================================

강의 27번 슬라이드 공식:
    Strong Cognitive Core + Specialized Modular Execution + Shared State / Graph Orchestration

이 스켈레톤은 워크시트의 다음 항목들로 채워진다:
- STEP 1: Use Case, 성공 기준
- STEP 2: 엔터프라이즈 루프 8단계 (각 노드로 구현)
- STEP 5: Cognitive Core (LLM), Modular Execution (도구), Orchestration (그래프)
- STEP 6: 메모리 (state로 구현)
- STEP 7: Governance (정책 노드)
- STEP 8: Evaluator + Replanner (조건부 엣지)
- STEP 9: 도구 목록

설치:
    pip install langgraph langchain-anthropic
"""

from typing import TypedDict, Literal, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# ============================================================
# 1. 공유 상태 정의 (Shared State / Orchestration)
#    — STEP 6 메모리 아키텍처
# ============================================================

class AgentState(TypedDict):
    # 단기 메모리 (대화 컨텍스트)
    messages: Annotated[list, operator.add]

    # 작업 상태
    goal: str                    # 현재 목표 (STEP 2 #1)
    plan: list[str]              # Planner가 생성한 단계 (STEP 2 #2)
    current_step: int            # 진행 중인 단계

    # 도구 실행 결과
    tool_results: list[dict]     # Tool Executor 결과 (STEP 2 #4)

    # 평가
    evaluation: dict             # Evaluator 판정 (STEP 2 #5)
    retry_count: int             # Replanner 카운터 (STEP 2 #8)

    # 거버넌스
    audit_log: Annotated[list, operator.add]   # 감사 로그 (STEP 7 A)
    requires_human_approval: bool              # HITL 플래그

    # 최종 산출물
    final_answer: str


# ============================================================
# 2. Cognitive Core — STEP 5 ①
# ============================================================

# {{STEP 3 모델 선택: Claude / GPT 등}}
llm = ChatAnthropic(
    model="{{모델 ID}}",          # 예: claude-opus-4-7
    temperature={{온도}},          # 워크시트 STEP 3 ③: 창의 0.7 / 일관 0.2
)

# 시스템 프롬프트 — 별도 생성된 system-prompt.md에서 로드
with open("system-prompt.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# ============================================================
# 3. 거버넌스 정의 — STEP 7 A
# ============================================================

WHITELIST_ACTIONS = [
    # {{STEP 7 A 화이트리스트를 액션 이름으로 나열}}
    # 예: "search_web", "read_user_doc", "send_email_draft"
]

BLACKLIST_ACTIONS = [
    # {{STEP 7 A 블랙리스트}}
    # 예: "send_email_send", "delete_file", "post_external_api"
]

HITL_TRIGGERS = [
    # {{STEP 7 A HITL 지점 — 어떤 조건에서 사람 승인 필요한지}}
    # 예: "send_email", "spend > $10", "delete_anything"
]


def check_governance(action: str, context: dict) -> tuple[bool, str]:
    """루프 7단계 — Policy/Governance 게이트"""
    if action in BLACKLIST_ACTIONS:
        return False, f"BLOCKED (blacklist): {action}"
    if action not in WHITELIST_ACTIONS:
        return False, f"BLOCKED (not whitelisted): {action}"
    for trigger in HITL_TRIGGERS:
        if trigger(action, context):     # 사용자 정의 조건 함수
            return False, f"REQUIRES_HUMAN_APPROVAL: {action}"
    return True, "OK"


# ============================================================
# 4. 도구 정의 — STEP 9 A
# ============================================================

# {{STEP 9 A에서 체크된 도구별 정의 — 아래는 예시}}

def tool_web_search(query: str) -> str:
    """{{STEP 9 도구 1 용도}}"""
    # 구현
    pass

def tool_read_file(path: str) -> str:
    """{{STEP 9 도구 2 용도}}"""
    pass

# {{추가 도구...}}

TOOLS = {
    "web_search": tool_web_search,
    "read_file": tool_read_file,
    # {{...}}
}


# ============================================================
# 5. 루프 8단계 — 각 노드로 구현
# ============================================================

def node_goal(state: AgentState) -> dict:
    """1. Goal — 목표 파악"""
    last_message = state["messages"][-1]
    goal = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"다음 요청에서 명확한 목표 한 문장으로 추출: {last_message.content}")
    ]).content
    return {
        "goal": goal,
        "audit_log": [{"step": "goal", "value": goal}]
    }


def node_planner(state: AgentState) -> dict:
    """2. Planner — 단계 분해"""
    prompt = f"목표: {state['goal']}\n사용 가능한 도구: {list(TOOLS.keys())}\n실행할 단계를 순서대로 나열:"
    plan_text = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]).content
    plan = [line.strip() for line in plan_text.split("\n") if line.strip()]
    return {
        "plan": plan,
        "current_step": 0,
        "audit_log": [{"step": "plan", "value": plan}]
    }


def node_reasoner_and_executor(state: AgentState) -> dict:
    """3·4. Reasoner + Tool Executor — 도구 선택 및 실행"""
    current_action = state["plan"][state["current_step"]]

    # 거버넌스 체크 (루프 7단계가 여기서 작동)
    ok, msg = check_governance(current_action, dict(state))
    if not ok:
        if "REQUIRES_HUMAN_APPROVAL" in msg:
            return {
                "requires_human_approval": True,
                "audit_log": [{"step": "governance_hitl", "action": current_action}]
            }
        else:
            return {
                "tool_results": [{"action": current_action, "blocked": msg}],
                "audit_log": [{"step": "governance_block", "action": current_action, "reason": msg}]
            }

    # 도구 실행 — Reasoner가 어떤 도구 호출할지 결정
    tool_call = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"이 단계를 실행하려면 어떤 도구를 어떤 인자로 호출해야 하나? '{current_action}'\n사용 가능 도구: {list(TOOLS.keys())}\nJSON으로: {{\"tool\": \"...\", \"args\": {{...}}}}")
    ]).content
    # 실제 구현에서는 tool_call 파싱 후 TOOLS[name](**args) 호출

    return {
        "tool_results": [{"action": current_action, "result": "..."}],
        "current_step": state["current_step"] + 1,
        "audit_log": [{"step": "executed", "action": current_action}]
    }


def node_evaluator(state: AgentState) -> dict:
    """5. Evaluator — 결과 검증 (★ 필수)
    워크시트 STEP 8 ①"""

    # {{STEP 8 ①의 성공/실패 기준을 프롬프트로}}
    criteria = """{{STEP 8 ① 결과 검증 기준}}
    예: 결과가 사용자 목표와 부합하는지, 환각이 없는지, 금지된 행동이 없었는지"""

    judgment = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"다음 결과를 검증:\n목표: {state['goal']}\n결과: {state['tool_results']}\n기준: {criteria}\n판정 (PASS/FAIL과 이유):")
    ]).content

    passed = "PASS" in judgment.upper()
    return {
        "evaluation": {"passed": passed, "reason": judgment},
        "audit_log": [{"step": "evaluation", "passed": passed}]
    }


def node_replanner(state: AgentState) -> dict:
    """8. Replanner — 실패 시 재계획
    워크시트 STEP 8 ②"""

    new_plan_text = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"이전 시도 실패: {state['evaluation']['reason']}\n원 목표: {state['goal']}\n다른 접근을 단계로 제안:")
    ]).content
    new_plan = [line.strip() for line in new_plan_text.split("\n") if line.strip()]

    return {
        "plan": new_plan,
        "current_step": 0,
        "retry_count": state["retry_count"] + 1,
        "audit_log": [{"step": "replan", "retry": state["retry_count"] + 1}]
    }


def node_finalize(state: AgentState) -> dict:
    """최종 응답 합성"""
    final = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"목표: {state['goal']}\n결과들: {state['tool_results']}\n사용자에게 답할 최종 응답 작성:")
    ]).content
    return {
        "final_answer": final,
        "messages": [AIMessage(content=final)]
    }


# ============================================================
# 6. 조건부 엣지 — Evaluator → 성공/실패 분기
# ============================================================

MAX_RETRIES = {{STEP 8 ② 최대 재시도 횟수, 기본 3}}

def route_after_eval(state: AgentState) -> Literal["finalize", "replanner", "give_up"]:
    if state["evaluation"]["passed"]:
        return "finalize"
    if state["retry_count"] >= MAX_RETRIES:
        return "give_up"        # {{STEP 8 ② "그래도 안 되면" 옵션}}
    return "replanner"


def route_after_step(state: AgentState) -> Literal["evaluator", "next_step"]:
    if state["current_step"] >= len(state["plan"]):
        return "evaluator"
    return "next_step"


# ============================================================
# 7. 그래프 조립 — Orchestration (STEP 5 ③)
# ============================================================

workflow = StateGraph(AgentState)

workflow.add_node("goal", node_goal)
workflow.add_node("planner", node_planner)
workflow.add_node("executor", node_reasoner_and_executor)
workflow.add_node("evaluator", node_evaluator)
workflow.add_node("replanner", node_replanner)
workflow.add_node("finalize", node_finalize)
workflow.add_node("give_up", lambda s: {"final_answer": "[작업 실패: 최대 재시도 초과. HITL 필요.]"})

workflow.add_edge(START, "goal")
workflow.add_edge("goal", "planner")
workflow.add_edge("planner", "executor")

workflow.add_conditional_edges(
    "executor",
    route_after_step,
    {"next_step": "executor", "evaluator": "evaluator"}
)
workflow.add_conditional_edges(
    "evaluator",
    route_after_eval,
    {"finalize": "finalize", "replanner": "replanner", "give_up": "give_up"}
)
workflow.add_edge("replanner", "executor")
workflow.add_edge("finalize", END)
workflow.add_edge("give_up", END)

agent = workflow.compile()


# ============================================================
# 8. 실행 예시
# ============================================================

if __name__ == "__main__":
    initial_state = {
        "messages": [HumanMessage(content="{{사용자 첫 요청 예시}}")],
        "goal": "",
        "plan": [],
        "current_step": 0,
        "tool_results": [],
        "evaluation": {},
        "retry_count": 0,
        "audit_log": [],
        "requires_human_approval": False,
        "final_answer": ""
    }

    result = agent.invoke(initial_state)

    print("=" * 60)
    print("최종 응답:", result["final_answer"])
    print("=" * 60)
    print("감사 로그 (Observability):")
    for entry in result["audit_log"]:
        print(" -", entry)


# ============================================================
# 운영 환경 투입 전 체크리스트
# ============================================================
#
# 🚦 다음이 모두 ☑이어야 운영 환경 투입 가능 (강의 룰):
#
# ☐ check_governance() 함수에 화이트/블랙리스트가 실제로 채워짐
# ☐ node_evaluator()의 criteria가 빈 문자열이 아님
# ☐ HITL_TRIGGERS가 실제 함수로 정의됨
# ☐ audit_log가 어딘가 영속 저장됨 (DB, 파일, etc.)
# ☐ MAX_RETRIES가 무한루프 방지하도록 설정됨
# ☐ 도구별 입력 검증(injection 방어) 추가됨
#
# 이 중 하나라도 ☐이면 사고가 난다. 강의 5번 슬라이드 참조.
