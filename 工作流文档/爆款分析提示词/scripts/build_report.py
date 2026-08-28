#!/usr/bin/env python3
"""Create a Markdown table skeleton for viral machine-video analysis."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--title", default="参考视频")
    parser.add_argument("--product", default="大型工业设备/标签打印机")
    args = parser.parse_args()

    args.analysis_dir.mkdir(parents=True, exist_ok=True)
    metrics = read_json(args.analysis_dir / "metrics.json")
    pose = read_json(args.analysis_dir / "pose_metrics.json")
    scenes = metrics.get("scenes", [])

    shot_rows = []
    for scene in scenes:
        shot_rows.append(
            f"| {scene.get('start', '')}-{scene.get('end', '')}s | 参考关键帧填写动作 | 待标注 | 待补文案 | 待判断 | 待标证据状态 |"
        )
    if not shot_rows:
        shot_rows.append("| 待填 | 待描述 | 待标注 | 待补文案 | 待判断 | 待标证据状态 |")

    pose_summary = ""
    if pose:
        pose_summary = (
            f"\n\n姿态采样提示：人物出现比例 {pose.get('person_presence_ratio', '未知')}，"
            f"手部出现比例 {pose.get('hand_presence_ratio', '未知')}，"
            f"脸部出现比例 {pose.get('face_presence_ratio', '未知')}。这些只是证据，不直接等于肢体表达结论。"
        )

    text = f"""# {args.title} 爆款卖机器视频分析

分析日期：{date.today().isoformat()}  
目标产品：{args.product}  
分析目标：先还原事实，再拆文案、观众心理与声画证据，最后提取不含原产品和原句的可迁移框架。{pose_summary}

## 1. 来源、表现与适配性

| 项目 | 已验证事实 | 推断/限制 |
|---|---|---|
| 来源与发布时间 | 待填 | 待填 |
| 播放与互动 | 待填 | 高流量不等于单一文案因素造成 |
| 评论/询盘信号 | 待填 | 待填 |
| 目标受众与我方适配性 | 待填 | 待填 |

## 2. 视频内容与镜头事实表

| 时间段 | 画面/动作 | 人物/产品 | 原文案/声音 | 信息作用 | 证据状态 |
|---|---|---|---|---|---|
{chr(10).join(shot_rows)}

## 3. 原文案写作结构表

| 原文案单元 | 文案功能 | 写作手法 | 新增信息 | 给下一句制造的期待 | 同期证明 |
|---|---|---|---|---|---|
| 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |

## 4. 观众心理推进表

| 阶段 | 观众听到/看到什么 | 原有认知或防备 | 新心理/情绪 | 下一问题 | 购买意义 |
|---|---|---|---|---|---|
| 停留 | 待填 | 待填 | 待填 | 待填 | 待填 |
| 理解 | 待填 | 待填 | 待填 | 待填 | 待填 |
| 相信 | 待填 | 待填 | 待填 | 待填 | 待填 |
| 心动/行动 | 待填 | 待填 | 待填 | 待填 | 待填 |

心理链：`待提取`

## 5. 声画证据与迁移边界

| 结论/承诺 | 参考证据 | 证据等级 | 我方迁移条件 | 处理 |
|---|---|---|---|---|
| 待填 | 待填 | 画面直接证明/数据确认/可补拍/仅口头/不可迁移 | 待填 | 待填 |

## 6. 五维度逆向拆解表

| 维度 | 参考视频怎么做 | 为什么有效 | 证据/时间点 | 拍机器时怎么借 |
|---|---|---|---|---|
| 全片视觉节奏链 | 待填：人物和产品如何交替 | 待填 | 待绑定时间点 | 用“人吸睛 -> 机器证明 -> 成品背书 -> 人收口”改写 |
| 人物表达与肢体钩子 | 待填：前3秒动作、眼神、定格 | 待填 | 待绑定时间点 | 主播用手指/拍/递/拿样品引导看机器重点 |
| 文案互动与视听卡点 | 待填：关键词如何卡动作和切镜 | 待填 | 待绑定时间点 | 说到产能/效果/订单时切到屏幕、成品、机器动作 |
| 核心共鸣与叙事逻辑 | 待填：认知变化、情绪、买家价值 | 待填 | 文案/字幕/画面证据 | 只迁移被证据支持的买家结果 |
| 手机级产品呈现与拍摄指引 | 待填：手机机位、1x/3x、光线、构图 | 待填 | 关键帧编号 | 手机固定拍人，3x拍细节，横移拍机器和样品堆叠 |

## 待补信息

- 原视频链接：见 `source_link.txt`，如有。
- 原口播/字幕：见 `transcript.txt`，如有。
- 关键帧：见 `keyframes/`。
- 工具指标：见 `metrics.json` 和 `pose_metrics.json`。
"""
    out = args.analysis_dir / "analysis.md"
    out.write_text(text, encoding="utf-8")

    framework = f"""# {args.title} 可迁移框架

## 一句话爆款机制假设

待填。不要把相关性写成确定因果。

## 文案功能框架

`打断注意 -> 立起传统预期 -> 打破预期 -> 物理证明 -> 具体商业价值 -> 低风险行动`

## 观众心理框架

`原有认知 -> 新情绪 -> 疑虑 -> 信任变化 -> 订单代入 -> 行动意愿`

## 证据框架

`首帧结果 -> 机器/工艺动作 -> 细节或测试 -> 应用/订单场景 -> 咨询回报`

## 节奏框架

待填：只记录节拍功能和大致时段，不复制原句数、句法或原话。

## 可迁移内容

- 待填。

## 不可照搬内容

- 原作者的具体表达、句法和节奏。
- 未经我方画面、测试、数据或用户确认支持的承诺。

## 下游输入卡

| 槽位 | 我方待填内容 |
|---|---|
| 目标买家 |  |
| 唯一客户问题 |  |
| 唯一核心重点 |  |
| 买家传统预期 |  |
| 真实的新答案 |  |
| 可见证明 |  |
| 具体钱/件数/门槛/工序价值 |  |
| CTA给客户的回报 |  |
| 不可写的事实边界 |  |
"""
    framework_out = args.analysis_dir / "framework.md"
    framework_out.write_text(framework, encoding="utf-8")
    print(out)
    print(framework_out)


if __name__ == "__main__":
    main()
