# 엔터프라이즈 루프 8단계 — 구현 패턴

워크시트 STEP 2의 각 단계를 코드/프롬프트로 어떻게 구현할지에 대한 참조 문서. 강의 슬라이드 4·5번 기반.

> ⚠️ **5번(Evaluator)·7번(Governance)이 없는 에이전트는 운영 환경 금지** — 강의 룰

---

## 단계별 구현 패턴

### 1. Goal — 목표 설정
**역할:** 사용자 요청에서 명확한 목표를 추출

**구현 패턴:**
```
시스템 프롬프트에:
"매 요청 첫 단계에서, 사용자가 달성하려는 목표를 한 문장으로 명확히 한다.
모호하면 한 번에 한 가지만 묻는다."
```

**저장 위치:** State의 `goal` 필드 (단기 메모리)

---

### 2. Planner — 단계 분해
**역할:** 목표를 실행 가능한 단계로 나누기

**구현 패턴:**
- LangGraph: 별도 노드 `node_planner()`
- Claude API: 시스템 프롬프트에 ReAct 패턴 명시
- CrewAI: Manager 에이전트의 첫 태스크

**프롬프트 예시:**
```
목표: {goal}
사용 가능한 도구: {tools}
이 목표를 달성하기 위한 단계를 순서대로 나열하시오.
각 단계는 도구 호출 1개 이내로.
```

---

### 3. Reasoner — 도구·경로 선택
**역할:** 현재 단계에서 어떤 도구를 어떤 인자로 호출할지 결정

**구현 패턴:**
- Claude Tool Use: 자동으로 처리됨 (`tools=` 파라미터)
- LangGraph: `node_reasoner` 또는 Executor와 합침
- ReAct 패턴 활용

**중요:** 거버넌스 체크는 도구 호출 *직전*에 (단계 7과 결합)

---

### 4. Tool Executor — 외부 호출
**역할:** 실제 도구 실행

**구현 패턴:**
```python
def execute_tool(name, input):
    # 1. 거버넌스 게이트 (단계 7)
    if not check_governance(name, input):
        return blocked_response

    # 2. 감사 로그
    log_audit(name, input)

    # 3. 실제 실행
    result = TOOLS[name](**input)

    # 4. 결과 검증 트리거 (단계 5)
    return result
```

**저장 위치:** State의 `tool_results` 배열

---

### 5. Evaluator — 결과 검증 ⚠️ 필수
**역할:** 도구 실행 결과가 목표에 부합하는지 검증

**구현 패턴 3가지:**

**(a) 별도 LLM 호출** (가장 강력)
```
프롬프트: "다음 결과를 검증:
목표: {goal}
결과: {result}
기준: {criteria}
판정 (PASS/FAIL + 이유)"
```

**(b) 규칙 기반** (빠름, 확정적)
```python
def evaluate(result):
    if len(result) < MIN_LENGTH: return False
    if contains_forbidden(result): return False
    if not matches_schema(result, expected): return False
    return True
```

**(c) Self-check via System Prompt** (Unified 진영)
```
시스템 프롬프트에:
"매 응답 직전, 다음을 점검하라:
- 목표에 부합하는가?
- 환각이 없는가?
- 정책을 어기지 않았는가?
하나라도 No면 재계획."
```

**비어있으면 안 됨.** 비어있는 채로 운영 환경 투입 = 강의 룰 위반.

---

### 6. Memory Manager — 상태·경험
**역할:** 단기·장기·공유 메모리 관리

**구현 패턴:**

| 메모리 종류 | 구현 |
| :---- | :---- |
| 단기 (작업 컨텍스트) | LangGraph State, 메시지 배열 |
| 장기 (사용자별) | DB, 벡터스토어, K/V 캐시 |
| 공유 (에이전트 간) | Blackboard 패턴, Redis 등 |
| 외부 참조 (RAG) | 벡터DB, 문서 인덱스 |

**TTL 정책 필수:** 모든 메모리에 만료 기준 명시.

---

### 7. Policy / Governance — 권한·감사 ⚠️ 필수
**역할:** 무엇을 할 수 있고, 못 하고, 사람 승인이 필요한지

**구현 3계층:**

**(a) 화이트리스트**
```python
ALLOWED_ACTIONS = ["search_web", "read_doc", ...]
if action not in ALLOWED_ACTIONS:
    block()
```

**(b) HITL 트리거**
```python
HITL_CONDITIONS = [
    lambda a, ctx: a == "send_email",
    lambda a, ctx: ctx.get("amount", 0) > 100_000,
    lambda a, ctx: a.startswith("delete_"),
]
```

**(c) 감사 로그**
모든 도구 호출을 영속 저장:
- 시각
- 에이전트 ID
- 도구 이름
- 입력
- 출력
- 거버넌스 판정

**저장 매체:** DB, 로그 파일, 또는 OpenTelemetry.

---

### 8. Replanner — 실패 시 재시도
**역할:** Evaluator가 FAIL을 내면 다른 접근 시도

**구현 패턴:**
```python
MAX_RETRIES = 3

def replan(state):
    if state.retry_count >= MAX_RETRIES:
        return give_up_with_hitl()       # 사람에게 escalate

    # LLM에게 새 계획 요청 (이전 실패 원인 알려주고)
    new_plan = llm.invoke(
        f"이전 시도 실패: {state.evaluation.reason}"
        f"원 목표: {state.goal}"
        f"다른 접근:"
    )
    state.plan = new_plan
    state.retry_count += 1
    return state
```

**핵심:** 무한 루프 방지 (MAX_RETRIES 필수)

---

## 단계 간 연결 패턴

```
Goal → Planner → Reasoner ⇄ Tool Executor → Evaluator
                                                  ↓
                                         PASS / FAIL
                                          ↓        ↓
                                       Memory   Replanner
                                          ↓        ↓
                                        End    (다시 Planner)

(전 단계에 Governance가 cross-cutting으로 작동)
(모든 단계가 Memory Manager에 read/write)
```

---

## "기본 GRAM은 부족" — 어디서 사고가 나는가

강의 5번 슬라이드 경고. 부족하기 쉬운 5가지:

1. **Observation** — 환경 변화 인식 (단계 4 직후 누락)
2. **Evaluation** — 결과 검증 (단계 5 자체)
3. **Reflection** — 실패 인식·재계획 (단계 8 누락)
4. **Governance** — 권한·정책 (단계 7 누락)
5. **Orchestration** — 루프 자체의 조정

이 5가지가 빈 채로 출시한 에이전트는 사고가 난다. 산출물 생성 시 빈 단계가 있으면 사용자에게 명시적으로 알린다.

---

## 산출물 생성 시 적용

워크시트 STEP 2의 각 칸을 다음으로 매핑:

| 워크시트 칸 | 시스템 프롬프트 섹션 | 코드 위치 |
| :---- | :---- | :---- |
| #1 Goal | "## 목표 (Goal)" | `node_goal()` 또는 시스템 프롬프트 |
| #2 Planner | "## 루프 작동 원칙 - 2단계" | `node_planner()` |
| #3 Reasoner | "## 루프 작동 원칙 - 3단계" | `node_reasoner_and_executor()` |
| #4 Tool Executor | "## 루프 작동 원칙 - 4단계" + 도구 목록 | `TOOLS` dict |
| **#5 Evaluator** | "## 루프 작동 원칙 - 5단계" | `node_evaluator()` |
| #6 Memory Manager | "## 루프 작동 원칙 - 6단계" | `AgentState` typed dict |
| **#7 Governance** | "## 루프 작동 원칙 - 7단계" | `check_governance()` |
| #8 Replanner | "## 루프 작동 원칙 - 8단계" | `node_replanner()` + `MAX_RETRIES` |

빈 칸은 **추측하지 말고** `[TODO]` 표기로 산출물에 명시 → 사용자가 보완.
