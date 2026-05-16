---
name: ai-agent-architect
description: AI 에이전트를 기획·설계·구현하려는 사용자와 ask_user_input_v0 도구로 인터랙티브 12단계 대화를 진행해서 시스템 프롬프트·아키텍처 명세서·코드 스켈레톤을 자동 생성하는 스킬. 엔터프라이즈 루프 8단계, 토폴로지 8종, MSA vs Unified Cognition 철학, 6대 핵심 경쟁력 프레임 기반. **반드시 트리거되어야 하는 상황**: "에이전트 만들어줘", "에이전트 기획", "에이전트 설계", "에이전트 아키텍처", "에이전트 워크시트", "agent 만들어줘", "agent design", "워크시트 채워줘", "에이전트 짜줘", "챗봇 만들고 싶어", "AI 도우미 만들어줘" 등 AI 에이전트/챗봇/자동화 시스템 만들기 관련 모든 요청. **기본 동작은 워크시트 파일 생성이 아니라 ask_user_input_v0 도구를 이용한 인터랙티브 11단계 대화 진행이다.** 사용자가 명시적으로 "빈 양식만 줘"라고 한 경우에만 양식을 제공하고, 그 외 모든 경우 STEP 1부터 맥락 brief + 선택지 버튼으로 즉시 진행을 시작한다.
---

# AI Agent Architect — 인터랙티브 에이전트 설계 진행

> **🛑 가장 중요한 규칙**
> 이 스킬이 트리거되면 **워크시트 파일(.docx/.md)을 만들어서 던지지 마라.** 양식 제공은 **금지**다.
> 대신 `ask_user_input_v0` 도구를 **적극적으로** 사용해서 **즉시 STEP 1부터 인터랙티브 대화**를 시작한다.
> 자유 텍스트가 필요한 경우에도 옵션화 가능한 부분은 모두 선택지로 만들어 `ask_user_input_v0`로 묻는다.
> 사용자가 *"양식만 줘", "빈 시트만"* 같이 명시적으로 양식만 원한다고 말한 경우에만 `assets/worksheet-template.docx`를 제공한다.

---

## 🛑 절대 금지 — 첫 턴 응답에서 하지 말 것

1. **워크시트 docx/md를 만들어서 사용자에게 던지기**
2. **첫 턴에 11개 STEP을 모두 한꺼번에 나열하기**
3. **"강의 N번", "슬라이드", "33장", "교육 장표" 같은 표현 사용** — 이 스킬은 독립 도구다. 외부 강의 컨텍스트를 사용자에게 노출하지 않는다.
4. **자유 텍스트로만 길게 질문 dump하기** — 옵션화 가능하면 무조건 `ask_user_input_v0`로.
5. **`ask_user_input_v0` 호출 없이 STEP을 끝까지 진행하기** — 매 STEP에 최소 1회 이상 호출.

---

## 🚀 스킬 트리거 직후 — 정확히 이렇게 행동한다

### 1단계: 사용자 의도 분류 (속으로만)

| 사용자 입력 | 행동 |
| :---- | :---- |
| **"양식만 줘" / "빈 시트만" / "blank template"** (명시 신호) | → `assets/worksheet-template.docx` 제공하고 끝 |
| 채워진 워크시트 파일을 첨부함 | → 파싱 후 누락 STEP만 인터랙티브 진행 |
| **그 외 모든 트리거** ("에이전트 만들어줘", "워크시트 만들어줘", "기획해줘", 단순 트리거 등) | → **즉시 STEP 1 인터랙티브 시작** ← 99%의 경우 |

기본값은 항상 **인터랙티브 시작**. 트리거 문구가 "워크시트 만들어줘"여도 그건 양식 요청이 아니다 — 함께 채우자는 요청으로 해석한다.

### 2단계: 첫 턴 응답 구조 (이 형식 그대로)

첫 메시지는 다음 3요소만:

**(1) 진입 멘트 (2~3줄, 짧게)**

예시 톤 (그대로 쓰지 말고 비슷한 톤으로):
```
AI 에이전트 설계를 12단계로 함께 진행하겠습니다. 각 단계마다 짧은 맥락 설명 후 선택지를 제시하니 탭으로 답해주시면 됩니다. 모두 끝나면 시스템 프롬프트·아키텍처 명세서·코드 스켈레톤을 자동 생성합니다.
```

**(2) STEP 1 맥락 brief (3~4줄)**

```
## STEP 1 — 문제 정의 & "정말 에이전트인가" 판별

이 단계의 목적은 두 가지입니다. 하나는 무엇을 만들지 명확히 하는 것, 다른 하나는 *정말 에이전트가 필요한가*를 판별하는 것. 챗봇/워크플로우로 충분한 일을 에이전트로 만들면 운영비가 폭증합니다. 자율적 행동(계획·실행·수정·반성)과 외부 도구 호출이 핵심 판별 기준입니다.
```

**(3) `ask_user_input_v0` 즉시 호출 — Use Case 카테고리 선택**

자유 텍스트로 던지지 않는다. 먼저 광범위한 카테고리부터 선택지로:

```json
{
  "questions": [{
    "question": "어떤 종류의 에이전트인가요?",
    "type": "single_select",
    "options": [
      "고객 응대·CS 자동화",
      "내부 업무 자동화 (RPA형)",
      "리서치·정보 수집·분석",
      "콘텐츠 생성 (글·이미지·영상)",
      "코딩·개발 보조",
      "기타 — 직접 설명"
    ]
  }]
}
```

→ 사용자가 답하면 그 다음 턴에 자유 텍스트로 구체화 받는다.

---

## STEP 1 — 두 번째 턴부터의 진행

### 1-B. Use Case 구체화 (자유 텍스트 + 후속 선택지)

이전 답변을 받고:

```
"고객 응대·CS 자동화"를 선택하셨군요. 조금만 더 구체적으로 알려주세요:

언제·어떤 상황에서 쓰이며, 누가 사용자인가요? (2~3줄)
```

사용자 답변 받으면 →

### 1-C. 성공 기준 — `ask_user_input_v0`

```json
{
  "questions": [{
    "question": "성공의 핵심 지표는?",
    "type": "single_select",
    "options": [
      "처리 속도·응답 시간 단축",
      "처리량·자동화 비율 증가",
      "정확도·품질 향상",
      "비용 절감",
      "사용자 만족도",
      "기타"
    ]
  }]
}
```

이어서 자유 텍스트 한 줄:
```
구체적 목표 수치가 있다면 한 줄로 (예: "응답 시간 10초 → 3초", "오답률 1% 미만"). 없으면 "정성적"이라고 답해주세요.
```

### 1-D. 제약·금지 — `ask_user_input_v0`

```json
{
  "questions": [{
    "question": "절대 하면 안 되는 것은? (해당 모두)",
    "type": "multi_select",
    "options": [
      "개인정보·민감정보 노출",
      "외부 시스템에 영구 변경 (발송·삭제·결제)",
      "사용자 모르게 의사결정",
      "정치·종교·차별적 발언",
      "기타 (다음 메시지에 적어주세요)"
    ]
  }]
}
```

"기타" 선택 시 자유 텍스트로 받음.

### 1-E. Agentic 판별 — `ask_user_input_v0`

```json
{
  "questions": [
    {
      "question": "이 시스템이 *스스로* 하는 것은? (해당 모두)",
      "type": "multi_select",
      "options": [
        "계획 (Planning)",
        "실행 (Execution)",
        "수정 (Self-correction)",
        "반성 (Reflection)"
      ]
    },
    {
      "question": "외부 도구·API·파일 호출이 필요한가요?",
      "type": "single_select",
      "options": ["필수", "필요 없음", "아직 모름"]
    }
  ]
}
```

### 1-F. 게이트 판정

- 자율 행동 3개 미만 + Tool Use "필요 없음" → "이건 챗봇/워크플로우로 충분합니다" 알리고:
  ```json
  {
    "questions": [{
      "question": "그래도 에이전트로 진행할까요?",
      "type": "single_select",
      "options": ["에이전트로 계속 (STEP 2 진행)", "챗봇으로 — 간이 프롬프트만 생성"]
    }]
  }
  ```
- 그 외 → 다음 메시지에서 STEP 2 시작.

---

## STEP 2. 엔터프라이즈 루프 8단계

### 맥락 brief
```
## STEP 2 — 에이전트의 작동 루프 8단계

에이전트는 단발 응답이 아니라 루프로 작동합니다. 기본 GRAM 루프(Goal·Reasoning·Action·Memory)를 엔터프라이즈용으로 확장하면 8단계가 됩니다. 그중 **5번(Evaluator: 결과 검증)·7번(Policy/Governance: 권한·감사)이 비어 있으면 운영 환경 금지**가 업계 컨센서스입니다 — 사고는 항상 여기서 납니다.

(런타임이 Claude Code Native라면 8단계 매핑은 STEP 9 이후 산출물 생성 시 자동 적용. Claude 내부 참조: `references/claude-code-native-mapping.md`)
```

### 8단계를 묶어서 `ask_user_input_v0`로 — 각 단계 구현 방식 선택

한 번에 전부 묻지 말고 4단계씩 묶음. 첫 번째 4단계:

```json
{
  "questions": [
    {
      "question": "1. Goal — 사용자 요청에서 목표를 어떻게 추출?",
      "type": "single_select",
      "options": ["LLM이 첫 응답에서 추출", "사용자에게 명시적 확인", "구조화 입력 (폼·API)", "TODO"]
    },
    {
      "question": "2. Planner — 단계 분해 방식?",
      "type": "single_select",
      "options": ["LLM이 자동 분해 (ReAct)", "사전 정의 워크플로우", "Hybrid", "TODO"]
    },
    {
      "question": "3. Reasoner — 도구·경로 선택?",
      "type": "single_select",
      "options": ["LLM Tool Use 자동", "규칙 기반 라우팅", "Hybrid", "TODO"]
    }
  ]
}
```

이어서:
```json
{
  "questions": [
    {
      "question": "4. Tool Executor — 외부 호출 방식?",
      "type": "single_select",
      "options": ["함수 직접 호출", "MCP 서버 경유", "API Gateway", "TODO"]
    },
    {
      "question": "5. ⚠️ Evaluator — 결과 검증 방식? (필수)",
      "type": "single_select",
      "options": [
        "LLM self-check (별도 프롬프트)",
        "Critic 에이전트 (다른 LLM)",
        "규칙 기반 (스키마·금지어)",
        "사람 검토 (HITL)",
        "TODO (운영 금지)"
      ]
    }
  ]
}
```

이어서:
```json
{
  "questions": [
    {
      "question": "6. Memory Manager — 무엇을 기억?",
      "type": "multi_select",
      "options": ["단기 (대화 컨텍스트)", "장기 (사용자별 프로필)", "공유 (에이전트 간)", "외부 (RAG·DB)"]
    },
    {
      "question": "7. ⚠️ Policy/Governance — 권한·감사? (필수)",
      "type": "single_select",
      "options": [
        "화이트리스트 + 감사 로그",
        "화이트/블랙리스트 + HITL + 감사",
        "전체 거버넌스 (정책·로그·롤·감사)",
        "TODO (운영 금지)"
      ]
    },
    {
      "question": "8. Replanner — 실패 시 재시도?",
      "type": "single_select",
      "options": ["같은 계획 재시도", "다른 도구로 재시도", "전체 재계획", "Human escalation"]
    }
  ]
}
```

### 5번·7번 TODO 게이트

5번 또는 7번이 TODO면 `ask_user_input_v0`:
```json
{
  "questions": [{
    "question": "⚠️ 5번·7번이 TODO입니다 (운영 환경 금지 조건). 어떻게?",
    "type": "single_select",
    "options": ["지금 다시 선택 (권장)", "TODO 유지 — 산출물에서 ☐로 표시"]
  }]
}
```

---

## STEP 3. 철학 선택

### 맥락 brief
```
## STEP 3 — 어느 철학 진영인가

에이전트 아키텍처에는 두 가지 가설이 정면 충돌합니다:
· **MSA (Multi-Agent System)**: "지능은 협업에서 창발한다" — 작은 전문 에이전트의 분산.
· **Unified Cognition**: "지능은 통합된 인지에서 발생한다" — 분해 비용 > 협업 이득.

실무 표준은 **Hybrid** — 강한 단일 코어 + 분산 실행. 단, *의도된* Hybrid여야 합니다.
```

### `ask_user_input_v0`
```json
{
  "questions": [
    {
      "question": "어느 철학 진영?",
      "type": "single_select",
      "options": [
        "MSA — 작은 전문 에이전트 협업",
        "Unified — 하나의 코어가 모두",
        "Hybrid — 강한 코어 + 분산 (권장)"
      ]
    },
    {
      "question": "이 선택은?",
      "type": "single_select",
      "options": ["의도됨 — 근거 있음", "관성·익숙해서"]
    }
  ]
}
```

답변 받은 후 자유 텍스트 한 줄:
```
선택 이유를 한 줄로 알려주세요. ("직관적이라서"는 답이 아닙니다)
```

---

## STEP 4. 토폴로지 선택

### 맥락 brief
```
## STEP 4 — 토폴로지 (연결 방식)

에이전트 개수가 아니라 *연결 방식*이 아키텍처를 결정합니다. 4분면 매트릭스 (통제 강도 × 흐름 명시성)로 8종이 있으며, Hybrid가 가로지르는 실무 표준입니다.
```

### 분면 먼저 — `ask_user_input_v0`
```json
{
  "questions": [{
    "question": "4분면 매트릭스에서 어디?",
    "type": "single_select",
    "options": [
      "지휘 통제형 — 중앙 통제 + 명시 흐름",
      "협상형 — 자기조직화 + 명시 흐름",
      "공유 상태형 — 자기조직화 + 묵시 흐름",
      "Hybrid — 4분면 교차 (권장)"
    ]
  }]
}
```

### 분면 결과에 따라 다음 `ask_user_input_v0`
- 지휘 통제형:
  ```json
  {"questions":[{"question":"세부 토폴로지?","type":"single_select","options":["01 Centralized — 단일 코디네이터","02 Hierarchical — 슈퍼바이저 위임 (CrewAI 풍)","07 DAG — 의존성 그래프 (LangGraph 풍)"]}]}
  ```
- 협상형:
  ```json
  {"questions":[{"question":"세부 토폴로지?","type":"single_select","options":["03 Peer-to-Peer — 수평 협업","05 Market-Based — 입찰·계약"]}]}
  ```
- 공유 상태형:
  ```json
  {"questions":[{"question":"세부 토폴로지?","type":"single_select","options":["04 Blackboard — 공유 메모리","06 Swarm — 자기조직화 군집"]}]}
  ```
- Hybrid → 08 Hybrid 자동 선택, STEP 5로.

토폴로지가 헷갈리면 `references/topology-guide.md` 읽고 한 줄 보충 설명.

---

## STEP 5. 최종 공식 — Cognitive Core × Modular × Orchestration

### 맥락 brief
```
## STEP 5 — 시스템 공식

**Strong Cognitive Core + Specialized Modular Execution + Shared State / Graph Orchestration**

한 머리(코어)가 통합 추론하고, 분리할 것만 모듈로 떼고, 모듈을 그래프·공유상태로 조율합니다.
원칙: 도구는 풍부하게, 에이전트는 절제. (도구를 나누는 것 ≠ 에이전트를 나누는 것)
```

### `ask_user_input_v0` — Cognitive Core
```json
{
  "questions": [{
    "question": "Cognitive Core 모델은?",
    "type": "single_select",
    "options": [
      "Claude (Anthropic)",
      "GPT (OpenAI)",
      "Gemini (Google)",
      "오픈소스 (Llama·Qwen 등)",
      "복수 모델 혼용",
      "아직 미정"
    ]
  }]
}
```

### `ask_user_input_v0` — 모듈 분리 대상
```json
{
  "questions": [{
    "question": "무엇을 모듈로 분리?",
    "type": "single_select",
    "options": [
      "도구만 분리 (권장 — 비용 안전)",
      "서브에이전트로 분리",
      "둘 다",
      "분리 없음 — 단일 통합"
    ]
  }]
}
```

### `ask_user_input_v0` — 조율 메커니즘
```json
{
  "questions": [{
    "question": "조율 메커니즘은? (해당 모두)",
    "type": "multi_select",
    "options": [
      "Blackboard (공유 상태)",
      "DAG / Graph (의존성)",
      "Supervisor (위임)",
      "Event Bus (비동기)"
    ]
  }]
}
```

---

## STEP 6. 메모리 아키텍처

### 맥락 brief
```
## STEP 6 — 메모리 (핵심 경쟁력 #3)

단기·장기·공유·외부 — 무엇을 어디에 저장할지가 시스템 성격을 좌우합니다.
TTL·삭제 정책 없는 메모리는 시한폭탄입니다 (개인정보·비용·일관성).
```

### `ask_user_input_v0`
```json
{
  "questions": [
    {
      "question": "사용할 메모리 종류는? (해당 모두)",
      "type": "multi_select",
      "options": [
        "단기 (대화 컨텍스트)",
        "장기 (사용자별 프로필)",
        "공유 (에이전트 간 Blackboard)",
        "외부 참조 (RAG · DB)"
      ]
    },
    {
      "question": "메모리 철학은?",
      "type": "single_select",
      "options": ["MSA식 — Memory per Agent", "통합 메모리 — 단일 저장소"]
    }
  ]
}
```

### 자유 텍스트 (선택)
```
저장소·TTL 정책에 특별한 사항이 있다면 한 줄로 (예: "장기 메모리 30일 자동 삭제"). 없으면 "표준"이라고 답해주세요.
```

---

## STEP 7. 거버넌스 & Observability

### 맥락 brief
```
## STEP 7 — 거버넌스 & 추론 추적 (핵심 경쟁력 #4·#5)

· **Governance**: 권한 화이트/블랙리스트, HITL, 감사 로그.
· **Observability**: "왜 이렇게 답했나"에 답하는 능력.

빈 채로 출시한 에이전트는 100% 사고가 납니다.
```

### `ask_user_input_v0` — Governance
```json
{
  "questions": [
    {
      "question": "도입할 거버넌스 수준은?",
      "type": "single_select",
      "options": [
        "최소 — 블랙리스트 + 감사 로그",
        "표준 — 화이트/블랙 + HITL + 로그",
        "엄격 — 전체 정책 + RBAC + 외부 감사",
        "기업 요구사항 (다음에 설명)"
      ]
    },
    {
      "question": "HITL (사람 승인)이 필요한 분기는? (해당 모두)",
      "type": "multi_select",
      "options": [
        "외부 발송 (메일·메시지)",
        "결제·금액 임계 초과",
        "영구 변경 (삭제·DB 수정)",
        "정책 외 도구 호출",
        "없음"
      ]
    }
  ]
}
```

### `ask_user_input_v0` — Observability
```json
{
  "questions": [
    {
      "question": "Reasoning Trace 저장은?",
      "type": "single_select",
      "options": [
        "DB (PostgreSQL 등)",
        "관찰성 도구 (OpenTelemetry·Datadog)",
        "JSONL 파일 (PoC)",
        "TODO"
      ]
    },
    {
      "question": "감사 로그 보관 기간은?",
      "type": "single_select",
      "options": ["30일 미만", "30~90일", "90일~1년", "1년 이상 (규제 산업)"]
    }
  ]
}
```

### 자유 텍스트 — 블랙리스트
```
이 에이전트가 **절대 못 하는 행동** 3가지를 알려주세요 (한 줄씩):
```

---

## STEP 8. Evaluator & Replanner

### 맥락 brief
```
## STEP 8 — 자기수정 루프

챗봇과 에이전트를 가르는 결정적 차이는 *루프*입니다. Evaluator가 검증하고, FAIL이면 Replanner가 재시도합니다.
재시도 횟수가 무한루프 방지 + 비용 통제의 핵심입니다.
```

### `ask_user_input_v0`
```json
{
  "questions": [
    {
      "question": "Evaluator 검증 주체는? (해당 모두)",
      "type": "multi_select",
      "options": ["모델 self-check", "다른 에이전트 (Critic)", "규칙 기반", "사람 (HITL)"]
    },
    {
      "question": "검증 시점은?",
      "type": "single_select",
      "options": ["매 도구 호출 후", "최종 응답 직전", "둘 다"]
    }
  ]
}
```

이어서:
```json
{
  "questions": [
    {
      "question": "최대 재시도 횟수는?",
      "type": "single_select",
      "options": ["1회", "3회 (권장)", "5회", "무제한 (비용 위험)"]
    },
    {
      "question": "재시도 모두 실패 시?",
      "type": "single_select",
      "options": ["Human escalation (권장)", "Fail-safe 응답", "작업 포기 + 로그"]
    }
  ]
}
```

### 자유 텍스트
```
PASS/FAIL을 판정하는 구체적 기준이 있다면 한 줄로 (예: "응답에 출처 URL 포함", "JSON 스키마 일치"). 없으면 "일반"이라고 답해주세요.
```

---

## STEP 9. 런타임 선택

### 맥락 brief
```
## STEP 9 — 어디서 굴릴 것인가 (런타임)

같은 에이전트라도 어디서 굴리느냐에 따라 산출물이 완전히 달라집니다.
· **Claude Code Native** — Skill·Subagent·Hook·MCP·Slash Command 조합. 추론 루프·도구 호출·메모리·승인 UI(Plan Mode)·인터랙티브 입력(AskUserQuestion)이 이미 내장. 파일 몇 개로 끝.
· **Python SDK 직접** — Anthropic SDK + 자체 while loop. 인프라·배포·UI 모두 자체 책임.
· **Framework (CrewAI / LangGraph / AutoGen)** — 멀티 에이전트 추상화 제공. 학습 곡선·종속성 있음.

이 선택이 산출물 4번(코드 스켈레톤)의 형태를 결정합니다. 같은 8단계 루프라도 Native는 파일 5개로, SDK는 코드 수백 줄로 구현됩니다.
```

### `ask_user_input_v0` — 런타임
```json
{
  "questions": [{
    "question": "어디서 굴릴 건가요?",
    "type": "single_select",
    "options": [
      "Claude Code Native (권장 — 빠름·내장 UI)",
      "Python SDK 직접 (Anthropic SDK)",
      "Framework — CrewAI",
      "Framework — LangGraph",
      "Framework — AutoGen / 기타",
      "아직 미정"
    ]
  }]
}
```

### 분기 1: Claude Code Native 선택 시 — 구성요소 선택

```json
{
  "questions": [{
    "question": "어떤 구성요소를 쓰나요? (해당 모두)",
    "type": "multi_select",
    "options": [
      "SKILL.md — 스킬화 (특정 키워드로 트리거)",
      ".claude/agents/*.md — 서브에이전트 (컨텍스트 격리·전문 역할)",
      ".claude/commands/*.md — 슬래시 커맨드 (/<name> 진입)",
      "settings.json hooks — 거버넌스·감사 (PreToolUse·PostToolUse)",
      "MCP 서버 — 외부 시스템 연결",
      "CLAUDE.md — 프로젝트 행동 규칙"
    ]
  }]
}
```

매핑 가이드: STEP 2의 8단계 루프 → Native 구성요소 매핑은 `references/claude-code-native-mapping.md` 참조 (Claude 내부용, 사용자에게 노출 금지).

### 분기 2: Python SDK 선택 시
추가 질문 없이 다음 STEP 진행. 산출물 4번은 `claude-tool-use-skeleton.py`로 생성.

### 분기 3: Framework 선택 시 — 멀티 에이전트 구조 확인
```json
{
  "questions": [{
    "question": "에이전트 개수는?",
    "type": "single_select",
    "options": [
      "단일 (코어 1개 + 도구)",
      "2~3개 (위임 구조)",
      "4개 이상 (복합 협업)"
    ]
  }]
}
```

CrewAI / LangGraph / AutoGen 중 선택한 것에 해당하는 스켈레톤으로 산출물 4번 생성.

### 분기 4: "아직 미정" 선택 시
산출물 4번을 Native 폴더 + 파이썬 스켈레톤 3종 모두 폴더로 묶어 제공 (사용자 비교용).

---

## STEP 10. 도구 · 인터페이스 · UI

### 맥락 brief
```
## STEP 9 — 도구·인터페이스·UI

원칙: 도구는 풍부하게, 에이전트는 절제.
MCP(Model Context Protocol)는 도구·에이전트 인터페이스 표준 후보입니다.
```

### `ask_user_input_v0` — 도구 (2번 호출)
```json
{
  "questions": [{
    "question": "필요한 도구는? (해당 모두)",
    "type": "multi_select",
    "options": ["웹 검색", "파일 R/W", "외부 API", "DB 조회"]
  }]
}
```

```json
{
  "questions": [{
    "question": "추가 도구는? (해당 모두)",
    "type": "multi_select",
    "options": ["메시지·이메일 발송", "이미지 생성·분석", "코드 실행", "없음"]
  }]
}
```

기타 도구가 있다면 자유 텍스트로 추가 요청.

### `ask_user_input_v0` — 인터페이스 + UI
```json
{
  "questions": [
    {
      "question": "도구 인터페이스 표준은?",
      "type": "single_select",
      "options": ["기본 제공 도구 (Bash·Read·Write·Grep) — Claude Code Native 디폴트", "MCP — 외부 시스템 연결 표준 (Claude Code Native 추천)", "OpenAPI / Function Calling", "자체 함수", "미정"]
    },
    {
      "question": "UI 진입점은? (해당 모두)",
      "type": "multi_select",
      "options": ["채팅 인터페이스", "웹 앱", "Slack·카톡 봇", "음성", "IDE / CLI"]
    }
  ]
}
```

### 자유 텍스트
```
사용자가 처음 보는 **환영 메시지**를 1~2문장으로 작성해주세요.
```

---

## STEP 11. 6대 핵심 경쟁력 자가진단

### 맥락 brief
```
## STEP 10 — 6대 경쟁력 자가진단

미래 에이전트 시스템의 핵심 경쟁력은 이 6가지입니다. 3개 이상에 구체적 답을 못 하면 운영 환경 투입은 보류해야 합니다.
```

### `ask_user_input_v0` (2번 호출)
```json
{
  "questions": [{
    "question": "다음 중 우리 시스템이 *구체적으로 답할 수 있는* 항목은? (해당 모두)",
    "type": "multi_select",
    "options": [
      "Bounded Cognition — 책임 경계 명확",
      "Orchestration — 조율 효율 설계됨",
      "Memory Architecture — 단기·장기·공유 정책"
    ]
  }]
}
```

이어서:
```json
{
  "questions": [{
    "question": "나머지 중 *구체적으로 답할 수 있는* 항목은? (해당 모두)",
    "type": "multi_select",
    "options": [
      "Governance — 권한·정책·감사",
      "Observability — 추론 추적",
      "Adaptive Topology — 상황별 토폴로지 전환"
    ]
  }]
}
```

답한 개수 N/6 자동 계산. 3 미만이면 한 줄 경고 메시지 출력.

---

## STEP 12. 산업 사이클 위치

### 맥락 brief
```
## STEP 11 — 조직 사이클 진단

마이크로서비스가 걸어간 길을 에이전트 시스템도 그대로 따라갑니다. 현 위치를 알면 다음 단계가 보입니다.
```

### `ask_user_input_v0`
```json
{
  "questions": [{
    "question": "우리 조직의 에이전트 전략 현 위치는?",
    "type": "single_select",
    "options": [
      "① Monolith — 거대 단일 시스템",
      "② 과분해 — 마이크로 에이전트 폭주",
      "③ 복잡성 폭증 — 조율 비용 폭발",
      "④ 재통합 — Hybrid로 수렴"
    ]
  }]
}
```

---

## 🏁 STEP 12 끝난 후 — 산출물 자동 생성

모든 답변을 종합해서 산출물을 만들어 `/mnt/user-data/outputs/`에 저장 → `present_files`로 공유:

### 공통 산출물 3종 (런타임 무관)

1. **`<프로젝트명>-worksheet.docx`** — 사용자 답변으로 빈칸이 채워진 워크시트.
   - `assets/worksheet-template.docx` 디자인 그대로 사용 (docx-js로 빌드)
   - 답안 칸에 사용자 답변, 체크박스는 ☑로 변환

2. **`<프로젝트명>-system-prompt.md`** — `assets/system-prompt-template.md` 패턴으로 치환. 빈 STEP은 `[TODO]` 표기.

3. **`<프로젝트명>-architecture-spec.md`** — `assets/architecture-spec-template.md` 패턴. 토폴로지에 맞는 Mermaid 다이어그램 포함.

### 산출물 4번 — STEP 9 런타임 선택에 따라 분기

| 런타임 (STEP 9) | 산출물 4번 |
| :---- | :---- |
| **Claude Code Native** | `<프로젝트명>-claude-code/` 폴더 (아래 4-A 참조) |
| **Python SDK** | `<프로젝트명>-skeleton.py` ← `assets/code-skeletons/claude-tool-use-skeleton.py` |
| **Framework — CrewAI** | `<프로젝트명>-skeleton.py` ← `assets/code-skeletons/crewai-skeleton.py` |
| **Framework — LangGraph** | `<프로젝트명>-skeleton.py` ← `assets/code-skeletons/langgraph-skeleton.py` |
| **Framework — AutoGen / 기타** | LangGraph 스켈레톤 기반 + 헤더 주석으로 변환 가이드 |
| **아직 미정** | Native 폴더 + 파이썬 스켈레톤 3종 모두 묶어 제공 (사용자 비교용) |

스켈레톤의 `{{...}}` 자리표시자를 사용자 답변으로 실제 치환 (시스템 프롬프트 인라인, 도구 목록, 메모리 스키마, Evaluator/Replanner 본문, Governance 화이트/블랙리스트).

#### 4-A. Claude Code Native 폴더 구성

STEP 9 분기 1에서 선택한 구성요소만 포함:

| 선택 | 생성 파일 | 템플릿 |
| :---- | :---- | :---- |
| SKILL.md | `<프로젝트명>-claude-code/SKILL.md` | `assets/code-skeletons/claude-code-native/SKILL-template.md` |
| 서브에이전트 | `<프로젝트명>-claude-code/agents/<role>.md` (역할당 1개) | `assets/code-skeletons/claude-code-native/subagent-template.md` |
| 슬래시 커맨드 | `<프로젝트명>-claude-code/commands/<name>.md` | `assets/code-skeletons/claude-code-native/slash-command-template.md` |
| hooks | `<프로젝트명>-claude-code/settings.json` | `assets/code-skeletons/claude-code-native/settings-hooks-snippet.json` |
| CLAUDE.md | `<프로젝트명>-claude-code/CLAUDE.md` | `assets/code-skeletons/claude-code-native/CLAUDE-md-template.md` |

매핑 규칙(8단계 루프 ↔ Skill·Subagent·Hook·MCP)은 `references/claude-code-native-mapping.md` 참조 (Claude 내부용).

폴더 끝에 한 줄 설치 안내 포함: "이 폴더를 `~/.claude/` (사용자 전역) 또는 프로젝트 `.claude/`에 복사 후 Claude Code를 재시작하세요."

### 마지막 — 운영 환경 투입 체크

```
🚦 운영 환경 투입 체크
☑/☐ Evaluator 정의됨 — STEP 2 #5
☑/☐ Governance 정의됨 — STEP 2 #7
☑/☐ 런타임 의도적 선택 — STEP 9
☑/☐ 6대 경쟁력 3개 이상 답함 — STEP 11 (N/6)
☑/☐ 토폴로지·철학 의도적 선택 — STEP 3·4

→ 모두 ☑: ✅ 운영 환경 투입 가능
→ 하나라도 ☐: ⛔ 보류. 보완 필요 항목: [구체적 명시]
```

---

## 진행 중 처리 규칙

### 사용자가 "건너뛰자" / "모르겠다"
→ 빈 채로 두고 다음 STEP. 산출물에 `[TODO: STEP X]`.

### 사용자가 "여기까지만"
→ 현재까지 답변으로 부분 산출물 생성.

### 사용자가 이전 STEP 수정 ("STEP 4 다시")
→ 그 STEP만 다시 진행. 이후 STEP은 기존 답변 유지.

### STEP 1에서 챗봇 충분 판정
→ 챗봇이라도 STEP 9(런타임)·10(도구·UI)는 진행. 나머지(STEP 2~8, 11·12) 건너뛰기 옵션을 `ask_user_input_v0`로 제시.

---

## ask_user_input_v0 사용 원칙

**기본 원칙: 옵션화 가능한 모든 것은 ask_user_input_v0로.**

자유 텍스트는 다음 경우에만:
- Use Case 구체 묘사 (선택지로 못 잡음)
- 환영 메시지·블랙리스트 항목 등 답변자의 표현이 그대로 결과물에 들어가는 것
- 사용자가 "기타"를 선택한 후속

옵션은 짧은 라벨로 (30자 이내 권장 — 모바일 사용자 다수).
한 호출에 최대 3개 질문, **STEP 경계는 넘지 말 것**.

---

## 참조 문서 사용 시점 (Claude 내부용)

- 토폴로지 선택이 헷갈리면 → `references/topology-guide.md`
- 8단계 루프 코드 구현 → `references/loop-patterns.md`
- 화이트/블랙리스트 구체화 → `references/governance-checklist.md`
- Claude Code Native 런타임 매핑 (STEP 2 8단계 ↔ Skill·Subagent·Hook·MCP, STEP 10 6대 경쟁력 ↔ Native 기능) → `references/claude-code-native-mapping.md`

사용자에게 그대로 보여주지 말고, 읽은 뒤 안내·질문에 녹여서 쓴다.

---

## 표기 일관성

- 8단계: "Goal · Planner · Reasoner · Tool Executor · Evaluator · Memory Manager · Policy/Governance · Replanner"
- 공식: "Cognitive Core · Modular Execution · Orchestration"
- 경쟁력: "Bounded Cognition · Adaptive Topology"
- 철학: "Strong Single-Agent · Hybrid · MAS"

영문 약어는 한국어로 번역하지 않는다.
