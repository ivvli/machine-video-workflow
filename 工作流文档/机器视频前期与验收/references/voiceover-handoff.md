# Voiceover Handoff

Use this reference after copy lock when a machine-sales video needs generated or cloned narration. The preflight skill locks a reproducible brief; a voice/TTS workflow generates and verifies the audio.

## Required handoff block

Record in `剪辑前方案.md`:

- Locked narration text and punctuation.
- Pronunciation risks for product terms, polyphones, abbreviations, and tongue-twisting phrases.
- Discourse beats: question, observation, proof, conclusion, and CTA.
- Performance prompt, emphasized phrases, pause plan, and local pace changes.
- Performance-source provider, voice/reference, emotion, strength, initial speed, and seed when supported.
- Voice-identity reference and voice-conversion method.
- Prosody-preservation checks and any conditional compensation.
- Final tempo, loudness, accepted comparison audio, and delivery status.

Any wording or punctuation change reopens copy confirmation. Any change to the performance source, voice identity, conversion method, prosody compensation, or tempo reopens voiceover confirmation. Change one variable at a time and compare with the last accepted version.

## Core method: performance first, identity second

Do not ask a flat personal reference to provide the acting. Separate natural performance from voice identity:

`locked copy -> natural full-take performance source -> source QA -> full-take voice conversion -> converted QA -> conditional prosody recovery -> loudness normalization -> user audition`

The performance source supplies thought process, rhythm, stress, and emotion. The user's clean reference supplies speaker identity. Never substitute a direct emotional clone merely because it is faster to generate.

## Design natural speech

Build delivery from meaning rather than a global instruction such as `更自然、更有感情`.

1. Mark discourse beats: pain/question, observation cue, proof, buyer value, and CTA.
2. Use unequal pauses. Start with roughly `0.1–0.2 s` for micro-pauses, `0.3–0.6 s` for thinking transitions, and `0.6–1.0 s` after a question or conclusion; adjust by listening rather than forcing every boundary into these ranges.
3. Allow short cues such as `你看` to sit between two different pauses when they represent reorientation.
4. Vary pace locally: firmer pain point, slightly lifted reveal, steadier proof, warmer CTA. Do not globally speed up to simulate energy.
5. Emphasize only buyer-value words. Do not stress every phrase, shout, use an announcer voice, drag endings, or insert artificial breaths.
6. Generate one continuous take. Do not synthesize and splice sentence by sentence unless repairing an unavoidable error and the join passes full-playback inspection.

Use the following baseline prompt, then add script-specific beat and pause instructions:

> 用自然、有说服力的短视频产品口播方式表达。像站在机器旁边，边观察成品边把刚想到的重点告诉客户，而不是背稿。整体积极、自信、有把握，但不要喊叫、不要播音腔。问题句明确有力度；提示词像重新组织语言；展示句带出真实发现感；证明句稳下来；结尾自然邀请咨询。整段连贯，句内有快有慢，停顿服从意思，不要逐字往外蹦，不要平均断句，不要拖长句尾，不要添加明显喘气声。

## Performance-source choices

Prefer a provider or local model that can produce a convincing full-take performance before cloning.

- Proven provider starting point: Doubao voice `liuchang`, emotion `happy`, strength `2`, speed ratio `1.03`.
- Local fallback proven in the current workspace: VoxCPM2 conditioned on the accepted A3 performance source, generated as one complete take.
- Use the provider's style controls only to produce the performance source. Do not expect the final voice-identity reference to carry the emotion.

Treat these as starting points, not permanent constants. If a provider fails, report the failure and switch methods; never call the task complete because a job or file was merely created.

## Pronunciation gate

Run ASR and listen to the source before voice conversion. Pay special attention to short function words and industry phrases, which may become ambiguous after conversion.

- If a phrase repeatedly blurs, replace it with a buyer-equivalent, easier spoken phrase and reopen copy confirmation.
- Regenerate the full take after a wording change; do not patch a few words into an otherwise continuous sentence.
- Examples learned in the current project: avoid unstable readings of `用我们`, `小批量`, and `想试样`; clearer alternatives included `我们这台机器`, `订单不多`, and `想领样`.

ASR is a diagnostic, not the sole judge. Homophone characters may be harmless, but missing syllables, changed meaning, or repeated disagreement around one phrase require rejection.

## Voice conversion and prosody preservation

1. Convert the complete performance source with CosyVoice voice conversion.
2. Use a clean user reference. The currently verified reference is `<project>/视频工作区/7.28.1仿刺绣/voice/reference_master.wav` when available.
3. Use seed `123` for reproducibility when supported, but verify actual outputs. Some conversion paths are deterministic and multiple seeds may produce identical audio; do not present identical files as real alternatives.
4. Compare source and converted pause timing, local pitch contour, articulation, and perceived speaker identity.
5. Measure voiced pitch activity as supporting evidence, preferably the p10–p90 semitone span around the median and source-to-output log-F0 contour correlation. Natural commercial speech in the observed reference set was roughly `8–12 semitones`, but this is a diagnostic range, not a pass rule by itself.
6. Reject a conversion that preserves the voice but materially flattens the performance. Do not try to hide flattening with global speed.

### Conditional recovery for flattened conversion

Only apply recovery after confirming that voice conversion compressed the source prosody.

- First strengthen median-relative local pitch deviation in the performance source, then reconvert.
- If conversion still flattens the contour, apply a subtle median-relative recovery after conversion while preserving center pitch, duration, and pauses.
- The current project succeeded with `1.35×` source-side deviation compensation followed by `1.18×` post-conversion recovery, yielding about `9.5 semitones` of final activity and about `0.86` source-contour correlation. Use these only as tested starting values, never as universal defaults.
- After any resynthesis, listen for metallic tone, unstable formants, warble, or loss of personal timbre. Reject artifacts even when metrics improve.

If the user requests a different pace after approving the voice and performance, apply one pitch-preserving tempo adjustment from the approved converted master. Never stack repeated tempo conversions. The earlier accepted A5 preset used `atempo=0.94` from A3.

Normalize the delivery master to about `-16 LUFS`, with true peak no higher than `-1.5 dB`, after all performance and tempo decisions.

## Acceptance sequence

Run both gates. Passing source QA does not imply the converted audio passes.

### Gate A: performance source

- Full text is present and intelligible.
- Pauses express a thought sequence rather than uniform punctuation.
- Pace changes locally; the result is not merely globally faster.
- Stress follows buyer value.
- No shouting, announcer tone, word-by-word delivery, dragged endings, or artificial breaths.

### Gate B: converted personal voice

- Full text remains present; ASR disagreements are reviewed by listening.
- It still sounds like the user before judging emotional strength.
- Important pause positions and local pitch direction survive conversion.
- Prosody is not materially flatter than the approved performance source.
- No clipping, added breaths, metallic artifacts, broken syllables, or splice discontinuities.
- Tempo processing, if any, is pitch-preserving and performed once.
- WAV/MP3 decode correctly; record duration, sample rate, channels, loudness, and peak.

Listen to the complete result in real time. Metrics, waveforms, and ASR support but never replace listening. Do not claim equivalence to a reference creator's identity or exact private method; compare only observable natural-speech mechanisms.

## Delivery and status language

- `已生成` means only that a file exists.
- `内部候选` means automated checks or listening still found an issue.
- `可试听候选` means both gates passed internally but the user has not approved it.
- `已确认配音` requires explicit user approval.
- Never report `任务完成` before required full-playback QA and user approval.

Current comparison files when the project tree is available:

- Personal-timbre and pace baseline: `<project>/草稿/配音/新文案_本人音色_情绪测试_20260803/A5版_A3进一步减速_成品.wav`.
- Natural-thought delivery candidate produced by this revised method: `<project>/草稿/配音/新文案_本人音色_情绪测试_20260803/思考型自然口播_v6_本人音色_成品.wav`.
