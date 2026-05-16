"""
{{프로젝트명}} — CrewAI 기반 Hierarchical MAS 에이전트
====================================================================

워크시트 STEP 3에서 "MSA (Multi-Agent System)" 선택 시 사용.
강의 토폴로지 02 Hierarchical + 21번 CrewAI 슬라이드 패턴.

핵심 특징:
- 회사 조직을 AI로 재현 (Manager → Workers)
- 강한 계층 구조, 권한 위임, 책임 경계
- 각 에이전트는 자기 역할만 책임

설치:
    pip install crewai crewai-tools
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import {{STEP 9 A 도구들}}    # 예: SerperDevTool, FileReadTool


# ============================================================
# 1. 도구 정의 — STEP 9 A
# ============================================================

# {{STEP 9 A에서 체크된 도구들}}
search_tool = SerperDevTool()
read_tool = FileReadTool()


# ============================================================
# 2. 에이전트 정의 — 각자 자기 책임 경계 (Bounded Cognition)
#    강의 26번 미래 경쟁력 #01
# ============================================================

# {{STEP 2 페르소나 별로 에이전트 생성}}

manager = Agent(
    role="{{Manager 역할 — 예: 프로젝트 매니저}}",
    goal="{{STEP 1 ① Use Case + STEP 1 ③ 성공 기준}}",
    backstory="{{Manager의 전문성·맥락}}",
    allow_delegation=True,         # 핵심: 위임 권한
    verbose=True,
)

researcher = Agent(
    role="Researcher",
    goal="{{이 에이전트의 책임}}",
    backstory="{{}}",
    tools=[search_tool],            # 도구 분리
    allow_delegation=False,
    verbose=True,
)

writer = Agent(
    role="Writer",
    goal="{{}}",
    backstory="{{}}",
    tools=[read_tool],
    allow_delegation=False,
    verbose=True,
)

reviewer = Agent(
    role="Reviewer (Evaluator)",   # 루프 5단계 = 별도 에이전트로 구현
    goal="{{STEP 8 ① 검증 기준을 goal로}}",
    backstory="당신의 임무는 다른 에이전트들의 결과물을 검증하는 것. "
              "{{STEP 8 ① 기준}}에 부합하지 않으면 거부하고 재작업 요청.",
    allow_delegation=False,
    verbose=True,
)


# ============================================================
# 3. 거버넌스 (STEP 7 A)
#    MAS에서는 Manager의 system prompt에 정책을 박는다
# ============================================================

GOVERNANCE_RULES = """
[정책 (절대 위반 금지)]
- 화이트리스트만 실행: {{STEP 7 A 화이트리스트}}
- 블랙리스트: {{STEP 7 A 블랙리스트}}
- HITL: 다음 상황에서 반드시 사람 승인 요청
  {{STEP 7 A HITL 지점}}
- 감사 로그: 모든 도구 호출 기록
"""

manager.backstory += "\n\n" + GOVERNANCE_RULES


# ============================================================
# 4. 태스크 정의 — 8단계 루프를 태스크 체인으로 매핑
# ============================================================

task_plan = Task(
    description="{{STEP 2 #2 Planner — 사용자 요청을 단계로 분해}}",
    agent=manager,
    expected_output="실행할 단계 목록 (JSON 배열)"
)

task_research = Task(
    description="{{STEP 2 #3·4 — Researcher가 조사 수행}}",
    agent=researcher,
    expected_output="조사 결과 요약",
    context=[task_plan]            # 이전 태스크 결과를 컨텍스트로
)

task_write = Task(
    description="{{Writer가 결과물 작성}}",
    agent=writer,
    expected_output="초안",
    context=[task_research]
)

task_review = Task(
    description=f"""
    Reviewer로서 다음 기준으로 검증:
    {{STEP 8 ① 결과 검증 기준}}

    검증 실패 시: 무엇이 부족한지 명시하고 재작업을 요청.
    검증 성공 시: 최종 승인.
    """,
    agent=reviewer,
    expected_output="검증 결과 (PASS/FAIL + 사유)",
    context=[task_write]
)


# ============================================================
# 5. Crew 조립 — Hierarchical Process
# ============================================================

crew = Crew(
    agents=[manager, researcher, writer, reviewer],
    tasks=[task_plan, task_research, task_write, task_review],
    process=Process.hierarchical,          # 슈퍼바이저 패턴
    manager_llm="{{모델 ID}}",              # Manager가 사용할 LLM
    memory=True,                            # 메모리 활성화 (STEP 6)
    verbose=True,
)


# ============================================================
# 6. Replanner (STEP 8 ②) — Reviewer 실패 시 재실행 루프
# ============================================================

MAX_RETRIES = {{STEP 8 ② 최대 횟수, 기본 3}}

def run_with_replanning(user_input: str) -> dict:
    """Evaluator(Reviewer) 실패 시 Replanner로 재시도"""
    for attempt in range(MAX_RETRIES):
        result = crew.kickoff(inputs={"user_input": user_input})

        # Reviewer의 마지막 출력 파싱
        last_output = str(result)
        if "PASS" in last_output.upper():
            return {"answer": last_output, "attempts": attempt + 1}

        # FAIL → 재시도 (Manager가 새 계획 세움)
        print(f"[Retry {attempt + 1}] Reviewer 거부: {last_output}")

    return {
        "answer": "[최대 재시도 초과 — HITL 필요]",   # {{STEP 8 ② 그래도 안 되면}}
        "attempts": MAX_RETRIES
    }


# ============================================================
# 7. 실행 예시
# ============================================================

if __name__ == "__main__":
    result = run_with_replanning("{{사용자 첫 요청 예시}}")
    print("=" * 60)
    print("최종 응답:", result["answer"])
    print(f"시도 횟수: {result['attempts']}")


# ============================================================
# 운영 환경 투입 전 체크리스트
# ============================================================
#
# 🚦 강의 룰 + MAS 특유 함정:
#
# ☐ Reviewer(Evaluator)가 실제로 거부 권한을 행사하는지 확인
# ☐ Manager의 GOVERNANCE_RULES가 채워짐
# ☐ 각 에이전트의 책임 경계(Bounded Cognition)가 명확함
# ☐ 토큰 비용 — 강의 02번 슬라이드 경고:
#    "과도한 다중 에이전트 분해는 토큰 폭증과 조율 비용으로 직결"
#    → 모니터링 필수
# ☐ Reasoning Trace 저장 (Observability)
# ☐ allow_delegation=True인 에이전트가 무한위임 방지 (max_iter 설정)
#
# 강의 17·20번 경고: "강한 단일 에이전트가 곧 모놀리식이 아님.
# 도구 분리는 OK — 에이전트 분리만 절제하는 것."
# 4명 이상의 에이전트가 정말 필요한지 재고할 것.
