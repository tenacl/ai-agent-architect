# AI Agent Architect

AI 에이전트를 기획·설계·구현하려는 사용자와 인터랙티브 11단계 대화를 진행해서 **시스템 프롬프트 · 아키텍처 명세서 · 코드 스켈레톤**을 자동 생성하는 Claude Code 스킬입니다.

엔터프라이즈 루프 8단계, 토폴로지 8종, MSA vs Unified Cognition 철학, 6대 핵심 경쟁력 프레임 기반.

## 설치

Claude Code에서 한 줄로 설치:

```bash
/plugin marketplace add ventusion/ai-agent-architect
/plugin install ai-agent-architect
```

업데이트:

```bash
/plugin update ai-agent-architect
```

## 사용법

설치 후 Claude Code에서 다음과 같이 트리거하면 됩니다:

- "에이전트 만들어줘"
- "AI 도우미 만들어줘"
- "에이전트 기획해줘"
- "챗봇 만들고 싶어"
- "워크시트 채워줘"

스킬이 자동으로 트리거되어 STEP 1부터 인터랙티브 대화가 시작됩니다.

빈 양식만 받고 싶다면:

- "양식만 줘" / "빈 시트만 줘"

## 산출물

11단계가 모두 끝나면 다음이 자동 생성됩니다:

1. **시스템 프롬프트** (`assets/system-prompt-template.md` 기반)
2. **아키텍처 명세서** (`assets/architecture-spec-template.md` 기반)
3. **코드 스켈레톤** — Claude Tool Use / LangGraph / CrewAI 중 선택

## 구조

```
ai-agent-architect/
├── .claude-plugin/plugin.json
├── SKILL.md                      # 메인 스킬 정의
├── assets/
│   ├── worksheet-template.docx   # 빈 양식 (오프라인용)
│   ├── worksheet-template.md
│   ├── system-prompt-template.md
│   ├── architecture-spec-template.md
│   └── code-skeletons/
│       ├── claude-tool-use-skeleton.py
│       ├── langgraph-skeleton.py
│       └── crewai-skeleton.py
└── references/
    ├── loop-patterns.md          # 엔터프라이즈 루프 8단계
    ├── topology-guide.md         # 토폴로지 8종
    └── governance-checklist.md   # 거버넌스 체크리스트
```

## 라이선스

MIT
