---
name: machine-video-preflight
description: Prepare and quality-gate a machine-sales short video before editing and before final delivery. Use when Codex needs to confirm direction, audit footage, consume an extracted viral-video framework, adapt its audience psychology and proof chain to verified product facts, write and independently review original buyer-facing copy, create a confirmable shot plan, or run final acceptance. Do not use this skill to perform the edit itself.
---

# Machine Video Preflight

Confirm the business direction, adapt a proven persuasion framework to verified evidence, write and lock original copy, prepare the shot plan, then act as the mandatory acceptance gate after editing. Do not generate voiceover, subtitles, an EDL, preview, or final video inside this skill.

## Required References

Read the project database before direction or copy decisions:

1. `<project>/工作流文档/爆款视频参考库/01_视频样本索引.md`
2. `<project>/工作流文档/爆款视频参考库/02_文案策略与作家风格.md`
3. `<project>/工作流文档/爆款视频参考库/03_客户问题与反对意见.md`
4. `<project>/工作流文档/爆款视频参考库/05_文案证据与改写方法.md`
5. `<project>/工作流文档/爆款视频参考库/06_视频框架风格库.md`
6. `references/style-selection.md`
7. `references/copywriting-workflow.md`
8. `references/copy-review.md`
9. `references/preflight-template.md`
10. `references/continuity-check.md`
11. `references/revision-mode.md` for an existing plan or edit.
12. `references/final-acceptance.md` when an edited candidate exists.
13. `references/voiceover-handoff.md` for generated/cloned voiceover or its acceptance.

When a primary reference has a sibling `framework.md`, read it before writing. If a reference or database file is missing, report it and continue with verified evidence; never invent findings.

## State Control

Track in `剪辑前方案.md`:

- Direction: `待确认` or `已确认`.
- Copy and CTA: `待确认`, `已确认`, or `已锁定`.
- Shot plan: `待确认` or `已确认`.

Track final acceptance in `验收报告.md` as exactly `退回修改` or `验收通过，可以交付`.

Use `上游变化，需重新确认` when an approved upstream decision changes. A direction change invalidates framework adaptation, evidence mapping, copy review, and shot plan. New footage reopens copy only if it changes or disproves a claim. Any user copy edit requires full rereading and re-review and invalidates the shot plan. Preserve locked copy and CTA character-for-character downstream.

## Role Pipeline

Run in order; every role consumes the previous output.

| Role | Required output | Return condition |
|---|---|---|
| Direction interviewer | Buyer, buying stage, one question, one core point, style, duration, language, CTA | Missing business decision |
| Buyer-topic strategist | Stop reason, emotional payoff, belief change, consultation value, history difference | Same angle as recent scripts without reason |
| Footage evidence auditor | Timestamped evidence map using `已满足 / 可替代 / 建议补拍` | Claim lacks proof; lower or remove it |
| Reference-framework reader | Mechanism hypothesis, copy-function chain, psychology chain, proof chain, transferable and forbidden content | Analysis is incomplete or only repeats original wording |
| Framework adapter | Every framework position mapped to our buyer, verified fact, proof, concrete buying value, and CTA return | Important slot is empty or unprovable |
| Copy writer | Four-core-law check, writing-process record, draft(s), selected original script, duration | Never self-approve |
| Independent copy reviewer | `通过` or `退回重写`, exact reasons, corrected script when needed | Any critical check fails |
| Continuity and shot designer | Locked-copy shot table, subtitles, continuity anchors, safe ending | Copy is not locked or has no proof shot |
| State controller | Updated confirmation ledger | Upstream change invalidates downstream work |
| Final acceptance reviewer | Full-playback QA, evidence matrix, timing, viewer judgment, final status | Any hard check fails |

The independent reviewer must evaluate fresh and may not use `虽然有问题但可以接受`.

## Workflow

### 1. Detect new-plan or revision mode

Use new-plan mode when there is no confirmed plan. For re-cuts, replacement shots, pacing, subtitles, voice, music, or ending changes, read `references/revision-mode.md` and preserve unaffected locked decisions.

### 2. Ask and lock direction

Ask sequentially rather than making the user fill a blank form:

1. Product/solution, potential buyer, buying stage, platform, duration, language, and desired consultation action.
2. One customer question and one core memory point.
3. Exactly one main style: 成品证据型, 真人讲解型, or 客户答疑型.
4. Zero to two supporting methods.
5. Upload status, must-use/must-avoid footage, and reference videos.

Present a direction summary and stop for confirmation. Do not inspect footage deeply or draft copy before confirmation.

### 3. Build the copy brief and audit evidence

Define who stops and why, the single buyer question, first-three-second emotional payoff, belief change, consultation value, and difference from the three most recent comparable scripts. Inspect footage without modifying `原始素材/`. Every proposed claim must map to footage or verified data.

### 4. Extract or read the reference framework

- Prefer one fully analyzed primary reference and at most one secondary reference.
- Separate the original transcript from its copy-function, audience-psychology, and proof frameworks.
- Use `viral-machine-video-analyzer` first when the chosen reference lacks `framework.md`.
- Do not preserve the reference's sentence count, syntax, rhythm, signature phrase, or exact CTA as a writing target.
- Reject a framework that stops making sense after product names and original sentences are removed.

### 5. Adapt the framework and write original copy

Follow `references/copywriting-workflow.md`.

- Complete the framework-adaptation card before drafting.
- Apply the four core laws: single-point focus; exaggerated emotional hook; establish and break expectation with concrete payoff; low-risk precise CTA.
- Exaggerate attitude and contrast, never unsupported facts, numbers, durability, output, cost, or ROI.
- Write fresh spoken language from our buyer, product, and evidence. A transition shot may use the prior sentence, natural sound, or silence.

### 6. Run independent copy review

Apply `references/copy-review.md`. Review meaning in context, not isolated words. Reject unsupported claims, empty curiosity, weak psychological progression, missing proof, abstract buying value, semantic duplication, copied expression, and an unclear consultation return.

If review fails, return to framework adaptation or choose a better framework, then rewrite and review again. Present the selected topic, extracted mechanism, adaptation, history difference, final copy, and concise review result. Stop for separate copy confirmation.

### 7. Lock copy, then build the shot plan

After explicit copy confirmation:

- mark exact copy and CTA `已锁定`;
- create `视频工作区/<短项目名>/剪辑前方案.md` from `references/preflight-template.md`;
- map locked words to files and timestamps without rewriting;
- include evidence/action, purpose, reason, continuity anchor, transition, subtitle mapping, held action, and safe ending;
- for voiceover, append the locked handoff block from `references/voiceover-handoff.md`; do not synthesize audio here.

Apply `references/continuity-check.md`. If a locked line lacks proof, return to copy review and ask before changing wording.

### 8. Stop at shot-plan approval

End with `待确认：逐镜剪辑脚本`. Editing, TTS, subtitles, music, and rendering require a later explicit request.

### 9. Run mandatory final acceptance

For an edited candidate, read `references/final-acceptance.md`. Inspect the approved plan, locked copy, timeline, voice method, captions, and export; then watch and listen to the entire export at normal speed. Automated checks support but never replace playback.

Write `验收报告.md`. When a hard check fails, send exact timecoded revisions and restart acceptance on the new export. Only `验收通过，可以交付` may be presented as final.

## Core Guardrails

- One video answers one buyer question and carries one core memory point.
- One video has one main visual style.
- Do not use minimal word replacement as the writing method. Reuse psychology and proof mechanisms, then write original expression.
- Do not turn process completeness into a product manual or the database into a phrase bag.
- Do not write unverified speed, cost, output, material, durability, or ROI claims.
- Do not narrow applications without confirmation.
- Do not mechanically ban words. Judge sentence function, context, rhythm, evidence, and buyer value.
- Every line adds a hook, expectation, reversal, proof, concrete buying value, or action.
- The first three seconds provide a supported buyer-relevant emotional payoff; curiosity alone fails.
- Read the whole script aloud as both a potential machine buyer and a scrolling viewer.
