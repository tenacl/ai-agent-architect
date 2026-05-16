# 아키텍처 명세서 템플릿

워크시트의 빈칸을 다음 패턴으로 치환해서 아키텍처 명세서를 생성한다.

---

## 출력 형식

```markdown
# {{프로젝트명}} — 아키텍처 명세서
*— 33장 브리핑(MSA vs Unified Cognition · 토폴로지 8종) 프레임 기반 —*

| 작성자 |  | 작성일 |  | 버전 | v1.0 |
| :---- | :---- | :---- | :---- | :---- | :---- |

---

## Executive Summary

{{1단락. 다음 4요소를 한 문장씩 연결:
- 누구를 위한 시스템인가 (STEP 1 ②)
- 어떤 use case를 자율 수행하는가 (STEP 1 ①)
- 어떤 철학·토폴로지로 구성되는가 (STEP 3·4)
- Cognitive Core + Modular Execution + Orchestration 한 줄 (STEP 5)
}}

---

## 1. 철학 선택

**채택 진영:** {{MSA / Unified Cognition / Hybrid}}

**근거:** {{STEP 3 선택 이유}}

**의도된 선택인가?** {{☑ 의도됨 / ☐ 우연}}

---

## 2. 토폴로지

**채택:** {{STEP 4에서 체크된 토폴로지}}

**4분면 위치:** {{좌상 / 우상 / 우하 / 중앙 교차}}

**Mermaid 다이어그램:**

(*아래 다이어그램은 선택한 토폴로지에 따라 다르게 생성. 아래는 Hybrid 예시.*)

\`\`\`mermaid
graph TB
    User[사용자 요청] --> Core[Cognitive Core<br/>{{모델명}}]
    Core --> Planner[Planner]
    Planner --> Tools{Tool Executor}
    Tools --> T1[{{도구1}}]
    Tools --> T2[{{도구2}}]
    Tools --> T3[{{도구3}}]
    T1 --> Eval[Evaluator]
    T2 --> Eval
    T3 --> Eval
    Eval -->|성공| Memory[(Memory)]
    Eval -->|실패| Replan[Replanner]
    Replan --> Planner
    Memory --> Core
    Gov[Policy/Governance] -.감사.-> Tools
    Gov -.감사.-> Eval
\`\`\`

---

## 3. 엔터프라이즈 루프 8단계 매핑

| # | 단계 | 구현 | 비고 |
| :---- | :---- | :---- | :---- |
| 1 | Goal | {{STEP 2 #1}} |  |
| 2 | Planner | {{STEP 2 #2}} |  |
| 3 | Reasoner | {{STEP 2 #3}} |  |
| 4 | Tool Executor | {{STEP 2 #4}} |  |
| 5 | **Evaluator** ⚠️ | {{STEP 2 #5}} | {{비어있으면 "[TODO: 보완 필수]"}} |
| 6 | Memory Manager | {{STEP 2 #6}} |  |
| 7 | **Policy/Governance** ⚠️ | {{STEP 2 #7}} | {{비어있으면 "[TODO: 보완 필수]"}} |
| 8 | Replanner | {{STEP 2 #8}} |  |

---

## 4. 최종 공식 (강의 27번 슬라이드)

> **Strong Cognitive Core** = {{STEP 5 ①}}
>
> **＋ Specialized Modular Execution** = {{STEP 5 ②}}
>
> **＋ Shared State / Graph Orchestration** = {{STEP 5 ③}}

---

## 5. 메모리 아키텍처

| 종류 | 무엇 | 저장소 | TTL/삭제 |
| :---- | :---- | :---- | :---- |
| 단기 (작업 컨텍스트) | {{STEP 6}} | {{}} | {{}} |
| 장기 (사용자별) | {{STEP 6}} | {{}} | {{}} |
| 공유 (에이전트 간) | {{STEP 6}} | {{}} | {{}} |
| 외부 참조 | {{STEP 6}} | {{}} | {{}} |

---

## 6. 거버넌스

### 6.1 화이트리스트 (할 수 있는 것)
{{STEP 7 A 화이트리스트}}

### 6.2 블랙리스트 (절대 금지)
{{STEP 7 A 블랙리스트}}

### 6.3 Human-in-the-loop 지점
{{STEP 7 A HITL}}

### 6.4 감사 로그
다음 항목을 모두 기록한다:
{{STEP 7 A 감사 항목}}

---

## 7. Observability — 추론 추적 설계

{{STEP 7 B 전체}}

- Reasoning Trace 저장: {{}}
- 디버깅 진입점: {{}}
- 재현성 확보 방법: {{}}

---

## 8. 도구 · 인터페이스 · UI

### 도구 (STEP 9 A)
| 도구 | 용도 | 핵심? |
| :---- | :---- | :---- |
| {{체크된 도구1}} | {{}} | {{★/일반}} |
| {{체크된 도구2}} | {{}} | {{}} |

### 인터페이스 (STEP 9 B)
{{체크된 인터페이스 표준}}

### UI 진입점 (STEP 9 C)
{{체크된 UI}}

### 환영 메시지 (STEP 9 D)
> {{환영 메시지}}

---

## 9. 🚦 운영 환경 투입 체크 (자동 채점)

| 항목 | 결과 | 근거 |
| :---- | :---- | :---- |
| 루프 5번 (Evaluator) 명시됨 | {{☑/☐}} | {{STEP 2 #5 내용 또는 "비어있음"}} |
| 루프 7번 (Governance) 명시됨 | {{☑/☐}} | {{STEP 2 #7 내용 또는 "비어있음"}} |
| 6대 경쟁력 3개 이상 답함 | {{☑/☐ (N/6)}} | {{STEP 10 답한 개수}} |
| 토폴로지·철학 의도적 선택 | {{☑/☐}} | {{STEP 3·4 의도 여부}} |

**투입 가능 여부:** {{모두 ☑이면 "✅ 가능" / 하나라도 ☐이면 "⛔ 보류 — 다음 항목 보완 필요: ___"}}

---

## 10. 미래 핵심 경쟁력 6 자가진단 (STEP 10)

| # | 경쟁력 | 우리의 답 | 충족? |
| :---- | :---- | :---- | :---- |
| 01 | Bounded Cognition | {{}} | {{☑/☐}} |
| 02 | Orchestration | {{}} | {{☑/☐}} |
| 03 | Memory Architecture | {{}} | {{☑/☐}} |
| 04 | Governance | {{}} | {{☑/☐}} |
| 05 | Observability | {{}} | {{☑/☐}} |
| 06 | Adaptive Topology | {{}} | {{☑/☐}} |

**충족 개수:** {{N}}/6

---

## 11. 산업 사이클 현 위치 (STEP 11)

**우리 조직 현 위치:** {{Monolith / 과분해 / 복잡성 폭증 / 재통합}}

**다음 단계 예상:** {{STEP 11}}

---

## 12. 변경 이력

| 버전 | 일자 | 변경 내용 |
| :---- | :---- | :---- |
| v1.0 | {{생성일}} | 최초 작성 |
```

---

## 다이어그램 분기 가이드

토폴로지에 따라 다이어그램이 달라진다. 다음 패턴 중 워크시트 STEP 4에서 선택된 것을 사용:

### Centralized
\`\`\`mermaid
graph TB
    User --> Coordinator
    Coordinator --> A1[Agent 1]
    Coordinator --> A2[Agent 2]
    Coordinator --> A3[Agent 3]
\`\`\`

### Hierarchical
\`\`\`mermaid
graph TB
    User --> Supervisor
    Supervisor --> Manager1
    Supervisor --> Manager2
    Manager1 --> Worker1
    Manager1 --> Worker2
    Manager2 --> Worker3
\`\`\`

### DAG (LangGraph 스타일)
\`\`\`mermaid
graph LR
    Start --> A[Node A]
    A --> B[Node B]
    A --> C[Node C]
    B --> D[Node D]
    C --> D
    D --> End
\`\`\`

### Blackboard
\`\`\`mermaid
graph TB
    A1 -.read/write.-> BB[(Blackboard<br/>공유 메모리)]
    A2 -.read/write.-> BB
    A3 -.read/write.-> BB
    BB --> Output
\`\`\`

### Hybrid (실무 표준 — 기본값)
강한 코어 + 분산 실행. 본문 예시 다이어그램이 이 패턴.

토폴로지 선택 근거는 `references/topology-guide.md`에서 확인.
