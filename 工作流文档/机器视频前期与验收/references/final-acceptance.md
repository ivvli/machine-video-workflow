# 成片交付前验收

Use this reference whenever an edited candidate exists. Acceptance is a hard delivery gate, not a suggestions list.

## Required inputs

- Confirmed direction, locked copy and CTA, evidence map, and approved shot plan.
- The editable timeline or EDL, voice-generation method, subtitle timing, and exported candidate.
- Any pre-approved interval that intentionally uses meaningful natural sound without voice or subtitles.

If an input is missing, use `退回修改`; do not infer that the candidate passes.

## Required procedure

1. Watch and listen to the entire candidate once at normal speed without interruption, taking timecoded notes.
2. Compare every spoken and subtitled claim with the simultaneous picture and verified facts.
3. Inspect voice, caption, and shot boundaries on the timeline.
4. Run metadata, silence-gap, caption-coverage, and representative-keyframe checks.
5. Rewatch the first three seconds and ending as both a potential buyer and a scrolling viewer.
6. Write `验收报告.md` with one final status: `退回修改` or `验收通过，可以交付`.

Automated checks support but never replace the uninterrupted playback.

## Hard failure checks

Return `退回修改` when any item fails:

| Check | Pass condition |
|---|---|
| Claim evidence | Every factual claim has simultaneous visual proof or user-confirmed data. A person merely standing by a machine does not prove footprint, output, durability, cost, speed, or material range. |
| Picture-caption meaning | Each subtitle describes what the current shot proves; placeholders and adjacent-but-unrelated visuals fail. |
| Voice-caption text | Spoken and subtitled wording match after punctuation-only normalization; locked wording and CTA remain character-for-character. |
| Voice-caption timing | Caption start and end follow the corresponding audible sentence within about 0.2 seconds. |
| Dead interval | No interval longer than 0.4 seconds lacks voice, subtitle, and meaningful natural sound, unless that exact interval was approved in the shot plan. |
| Voice continuity | Delivery sounds like one coherent paragraph: no repeated sentence-level reset, broken breath, abrupt pitch change, abnormal per-line speed, squeezed ending, or audible splice. |
| Voice production | Generate the approved paragraph in one call by default. Do not generate or retime individual sentences to force them into fixed shot windows; align pictures and captions to the natural whole-paragraph delivery. |
| Hook payoff | Within three seconds, the target buyer receives a supported surprise, benefit, risk reduction, desire, or recognition, and the first frame proves or sharpens it. Curiosity alone fails. |
| CTA and ending | CTA is complete and exact; no extra sales wording appears; the final face, product, and gesture settle naturally. |
| Technical output | Correct aspect ratio, frame rate, duration, readable captions, audible voice, and no unintended black, freeze, missing media, clipping, or encode error. |

## Report format

```markdown
# <项目简称>｜验收报告

状态：退回修改 / 验收通过，可以交付
验收文件：
验收时间：

| 检查项 | 通过/失败 | 时间码与证据 | 修改要求 |
|---|---|---|---|

## 潜在客户视角

## 刷视频观众视角

## 修改与复验记录
```

For a failure, give exact timecodes and executable revisions. After a new export, discard the previous pass result and rerun the complete procedure from the beginning. Present the final video to the user only after every hard check passes.
