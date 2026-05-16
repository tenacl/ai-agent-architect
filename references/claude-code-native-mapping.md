# Claude Code Native 런타임 매핑 가이드 (Claude 내부용)

> 이 문서는 ai-agent-architect 스킬이 산출물 생성 시 참조하는 매핑 표입니다.
> **사용자에게 그대로 노출하지 말고**, 스킬 흐름 안에서 안내·산출물 생성에 녹여 쓰십시오.

---

## 1. STEP 2 — 8단계 루프 ↔ Claude Code Native 구성요소

| 8단계 | Claude Code Native 매핑 | 생성 파일 |
| :---- | :---- | :---- |
| **1. Goal** | `AskUserQuestion` 도구로 명시 확인 / `CLAUDE.md`의 "성공 기준" 섹션 | `SKILL.md` / `CLAUDE.md` |
| **2. Planner** | `SKILL.md`의 "실행 절차" 섹션 (Step 1 → 2 → 3 명시) / 복잡 분기는 슬래시 커맨드로 진입점 분리 | `SKILL.md` / `.claude/commands/` |
| **3. Reasoner** | 메인 Claude가 내장 추론. 별도 코드 없음. 분기가 무거우면 서브에이전트로 분리 | (내장) |
| **4. Tool Executor** | 기본 도구 (Bash·Read·Write·Grep·WebFetch) + MCP 서버 | `mcp__*` 호출 |
| **5. Evaluator** ⚠️ | Critic 역할의 서브에이전트 1개 — 호출자가 결과를 위임하면 PASS/FAIL과 사유 반환 | `.claude/agents/<name>-evaluator.md` |
| **6. Memory Manager** | 단기: 대화 컨텍스트 (자동) / 장기: `memory/` 디렉토리 + `MEMORY.md` 인덱스 / 공유: 파일 시스템 / 외부: MCP RAG·DB | `memory/` 또는 MCP |
| **7. Policy/Governance** ⚠️ | `settings.json`의 `permissions.allow/deny` + `hooks.PreToolUse` (위험 도구 차단) + `hooks.PostToolUse` (감사 로그) | `settings.json` |
| **8. Replanner** | `SKILL.md`에 재시도 횟수·escalation 명시 ("FAIL 시 3회까지 재시도. 초과 시 분석가에게 escalation") | `SKILL.md` 본문 |

### 주의
- 5번·7번은 **반드시 파일로 구체화**. SKILL.md에만 "Evaluator 있음" 적어두고 실제 서브에이전트 파일이 없으면 작동 안 함.
- 7번 hooks의 `command`는 실제 실행 가능한 스크립트여야 함. 없으면 hooks 항목 자체를 빼고 `permissions.deny`만으로 차단.
- Plan Mode (`/plan`) 가 HITL 역할 — 별도 UI 구현 불필요.

---

## 2. STEP 11 — 6대 핵심 경쟁력 ↔ Claude Code Native 기능

| 경쟁력 | Native 구현 |
| :---- | :---- |
| **Bounded Cognition** | 서브에이전트별 책임 범위를 `description:` 에 명확히. 메인 ↔ 서브의 입출력 계약을 SKILL.md에 명시 |
| **Orchestration** | 메인 Claude가 `Agent` 도구로 서브에이전트 위임. 병렬은 한 메시지에 여러 Agent tool call (한 응답 안에서) |
| **Memory Architecture** | `memory/` 폴더 구조 (`user_*.md`, `feedback_*.md`, `project_*.md`, `reference_*.md`) + `MEMORY.md` 인덱스. TTL은 PostToolUse hook으로 강제 |
| **Governance** | `settings.json` permissions + PreToolUse hooks. HITL은 Plan Mode가 그대로 |
| **Observability** | PostToolUse hook으로 `.claude/logs/audit.jsonl`에 모든 도구 호출 기록. Reasoning trace는 conversation log |
| **Adaptive Topology** | SKILL.md 안의 조건 분기로 케이스별 다른 서브에이전트 조합 호출 |

---

## 3. STEP 4 — 토폴로지 ↔ Native 구현 패턴

| 토폴로지 | Native 패턴 |
| :---- | :---- |
| **01 Centralized** | 메인 Claude 1명 + 도구만. 서브에이전트 없음 |
| **02 Hierarchical** | 메인 Claude (Supervisor) + 역할별 서브에이전트 (Worker). Agent 도구로 위임 |
| **03 Peer-to-Peer** | 메인이 라운드로빈으로 서브에이전트 호출, 서로의 출력을 다음 에이전트 입력으로 |
| **04 Blackboard** | 공유 디렉토리 (예: `data/blackboard/`)에 각 에이전트가 파일 쓰기·읽기 |
| **05 Market-Based** | (Native 비표준) — 메인이 여러 서브에이전트를 동시에 호출 후 결과 비교·채택 |
| **06 Swarm** | 메인이 동일 서브에이전트를 다른 입력으로 N번 병렬 호출 (한 메시지에 N개 Agent tool call) |
| **07 DAG** | SKILL.md에서 의존성 그래프를 명시 ("A 완료 → B·C 병렬 → D 합치기"). 실행은 메인 Claude가 순서 보장 |
| **08 Hybrid** | 위 패턴들을 단계별로 조합 |

---

## 4. STEP 9 — 구성요소 선택별 파일 매핑

| 선택 | 파일 경로 | 주의 |
| :---- | :---- | :---- |
| SKILL.md | `~/.claude/skills/<name>/SKILL.md` (전역) 또는 `.claude/skills/<name>/SKILL.md` (프로젝트) | `name:` 필드와 폴더명 일치 |
| 서브에이전트 | `.claude/agents/<name>.md` 또는 `~/.claude/agents/<name>.md` | `tools:` 필드로 도구 화이트리스트 |
| 슬래시 커맨드 | `.claude/commands/<name>.md` 또는 `~/.claude/commands/<name>.md` | 파일명이 `/<name>` |
| hooks | `.claude/settings.json` 또는 `~/.claude/settings.json` | 시크릿은 `settings.local.json` + .gitignore |
| MCP 서버 | 별도 프로세스 + `.mcp.json` 또는 `claude mcp add` | MCP는 stdio/HTTP 별도 프로세스 |
| CLAUDE.md | 프로젝트 루트 또는 하위 디렉토리 | 자동 로드 — 메인 Claude의 시스템 프롬프트에 포함 |

---

## 5. 빠른 결정 트리

질문: "이건 서브에이전트인가 슬래시 커맨드인가 스킬인가?"

- **사용자가 명시적으로 `/<name>` 타이핑해야 트리거 → 슬래시 커맨드**
- **특정 키워드·상황에서 자동 트리거 → 스킬 (SKILL.md)**
- **메인 Claude가 다른 LLM 호출처럼 격리된 컨텍스트로 위임 → 서브에이전트**
- **외부 시스템 호출 표준화 → MCP**

세 가지를 조합할 수 있음. 예: 슬래시 커맨드로 진입 → 스킬이 절차 안내 → 서브에이전트에 위임 → MCP로 외부 시스템 호출.

---

## 6. 산출물 생성 시 체크리스트

Native 폴더 산출물을 만들기 전에 확인:

- [ ] STEP 9 분기 1에서 선택한 구성요소만 폴더에 포함했는가? (선택 안 한 건 빈 폴더로 두지 말 것)
- [ ] STEP 2 #5 Evaluator 답변이 있으면 → 실제 `.claude/agents/<name>-evaluator.md` 파일 생성했는가?
- [ ] STEP 2 #7 Governance 답변이 있으면 → `settings.json`의 `permissions.deny`와 `hooks` 모두 채워졌는가?
- [ ] SKILL.md의 `description:` 에 트리거 키워드가 한국어/영문 모두 포함됐는가?
- [ ] 서브에이전트의 `tools:` 가 최소 권한 원칙으로 좁혀졌는가? (기본 모든 도구는 위험)
- [ ] `{{...}}` 자리표시자가 한 곳이라도 남아있지 않은가? (모두 사용자 답변으로 치환됐는지 grep으로 확인)
- [ ] 폴더 끝에 설치 안내 한 줄 포함됐는가?
