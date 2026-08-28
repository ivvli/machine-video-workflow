---
name: viral-machine-video-analyzer
description: Analyze high-performing short-form sales videos for machines and industrial products, including factual video reconstruction, full copy extraction, sentence-function analysis, audience psychology, audiovisual evidence, and reusable framework extraction. Use when Codex is asked to reverse-engineer viral or high-traffic reference videos, diagnose machine-selling short videos, explain why a reference works, or prepare a framework handoff for original machine-sales copy. Do not jump directly from the reference wording to a minimally substituted script.
---

# Viral Machine Video Analyzer

Turn a reference video into evidence-backed analysis and a reusable persuasion framework. Separate observation, interpretation, framework extraction, and later copy creation. Reuse the mechanism, not the reference's protected expression.

## Required References

- Read `references/reverse-analysis-rubric.md` for audiovisual and shooting analysis.
- Read `references/copy-psychology-framework.md` for copy, psychology, framework, and handoff schemas.
- Read `references/copywriting-patterns.md` only when classifying the extracted framework against common machine-sales patterns.

## Workflow

1. Create `视频分析/YYYY-MM-DD_短名称/`. Never overwrite an existing analysis folder; add `-v2` or a clearer suffix.
2. Record source, date, duration, visible metrics, target audience, and evidence status. Do not call a video viral from views alone; distinguish verified metrics, visible comments, and inference.
3. For local video, use evidence scripts when useful. For a link, respect login and platform restrictions; request an authorized local file when full visual analysis is required.
4. Reconstruct facts before interpreting: timestamped content, shots, actions, sound, captions, and full transcript. Mark missing or uncertain text explicitly.
5. Analyze the copy line by line: exact wording, sentence job, technique, information gain, connection to the next line, and proof.
6. Reconstruct the viewer's psychological chain: prior belief, triggered emotion, resolved doubt, new question, buying value, and consultation threshold.
7. Check audiovisual proof. Classify every important claim as `画面直接证明`, `数据/用户确认`, `可补拍证明`, `仅口头声称`, or `不可迁移`.
8. Extract three product-neutral frameworks: copy-function framework, audience-psychology framework, and evidence framework. Remove names, product nouns, models, original sentences, unsupported numbers, and application claims.
9. Write `analysis.md` and a separate `framework.md`. Do not generate the user's final script inside this skill. Hand `framework.md` to `machine-video-preflight` for adaptation and writing.
10. Delete generated keyframes, contact sheets, clips, and manifests after acceptance unless the user requests an audit archive or the source cannot be accessed again.

## Output Folder Contract

```text
视频分析/
  YYYY-MM-DD_参考视频名称/
    参考视频.mp4          # when authorized/local
    source_link.txt       # when available
    metrics.json          # verified page/video metrics
    transcript.txt        # cleaned full copy; uncertainty marked
    analysis.md           # evidence and six-layer analysis
    framework.md          # clean handoff for later copywriting
    keyframes/            # temporary
    clips/                # temporary
```

## Required `analysis.md` Order

### 1. 来源、表现与适配性

Record verified metrics, comments or inquiry signals, target audience, and why the sample is or is not relevant to machine buyers. Separate observed facts from causal hypotheses.

### 2. 视频内容与镜头事实表

| 时间段 | 画面/动作 | 人物/产品 | 原文案/声音 | 信息作用 | 证据状态 |
|---|---|---|---|---|---|

### 3. 原文案写作结构表

| 原文案单元 | 文案功能 | 写作手法 | 新增信息 | 给下一句制造的期待 | 同期证明 |
|---|---|---|---|---|---|

Do not reduce this to labels such as `痛点型`; explain why each unit is placed there and how it earns the next.

### 4. 观众心理推进表

| 阶段 | 观众听到/看到什么 | 原有认知或防备 | 新心理/情绪 | 下一问题 | 购买意义 |
|---|---|---|---|---|---|

End with one concise chain such as `误认 -> 好奇 -> 揭底 -> 怀疑 -> 实证 -> 订单代入 -> 低风险咨询`.

### 5. 声画证据与迁移边界

| 结论/承诺 | 参考证据 | 证据等级 | 我方迁移条件 | 处理 |
|---|---|---|---|---|

### 6. 五维度逆向拆解

Use `references/reverse-analysis-rubric.md`. Bind claims to timestamps, frames, transcript lines, or visible evidence.

## Required `framework.md` Order

1. `一句话爆款机制假设`：state it as a hypothesis, not proven causation.
2. `文案功能框架`：hook, expectation, reversal, proof, buying value, CTA.
3. `观众心理框架`：belief and emotion transitions.
4. `证据框架`：what must be shown or verified at each position.
5. `节奏框架`：approximate beat order and duration, without copying sentence count or syntax.
6. `可迁移内容` and `不可照搬内容`.
7. `下游输入卡`：empty slots for our buyer, one question, one core point, traditional expectation, real reversal, proof, concrete commercial value, CTA return, and factual boundaries.

## Decision Rules

- Treat high traffic as a signal, not proof that one copy choice caused performance. Prefer repeated patterns across comparable samples.
- Distinguish video content, copy mechanism, audience psychology, and framework. Never collapse them into one summary.
- Preserve the complete reference transcript for analysis, but do not preserve its sentence count, syntax, rhythm, or wording as the writing target.
- An extracted framework must remain meaningful after product names and original wording are removed.
- Translate parameters into buyer outcomes only when the result is verified.
- Call visually attractive but commercially unsupported material `好看但不转化`.
- Keep shooting advice executable with a phone and relevant to proof.
