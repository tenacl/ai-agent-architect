---
description: {{한 줄 설명 — /help에 노출됨. 예: "분기 재무제표를 분석해 경영진용 요약과 Q&A 생성"}}
argument-hint: {{인자 형식 예시 — 예: <분기> [<파일>]}}
allowed-tools: {{허용 도구 — 예: Bash(ls:*), Read, Write, Agent}}
---

# /{{command-name}} — {{title}}

{{이 커맨드가 무엇을 하는지 1~2줄}}

## 사용법

```
/{{command-name}} {{arg-example-1}}
/{{command-name}} {{arg-example-2}}
```

## 인자

- `{{arg1}}` (필수) — {{설명·형식·예시}}
- `{{arg2}}` (선택) — {{설명. 미지정 시 기본 동작}}

## 동작

1. **{{Step 1}}** — {{무엇을. 사용 도구}}
2. **{{Step 2}}** — {{...}}
3. **{{Step 3}}** — {{최종 산출물 + 저장 위치}}

## 산출물

- `{{output path}}/{{filename pattern}}` — {{설명}}

## 실패 시

{{- Evaluator FAIL → {{N}}회 재시도}}
{{- 초과 시 → 분석가에게 escalation (Plan Mode로 전환)}}

---

받은 인자: $ARGUMENTS

위 인자를 파싱한 후 위 동작 1~3을 순서대로 실행하십시오. 각 단계 결과를 분석가에게 한 줄로 보고하고, 최종 산출물 저장 후 경로를 알립니다.
