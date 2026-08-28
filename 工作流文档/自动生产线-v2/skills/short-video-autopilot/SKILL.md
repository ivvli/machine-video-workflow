---
name: short-video-autopilot
description: Run the staged V2 product-short-video autopilot in the 视频制作 workspace. Use when the user says “开始” with pending source media, asks to start or continue the complete workflow, confirms or rejects copy, voice, the edit script, or upload, chooses a cover source, confirms manual publication, or requests the 72-hour review. Orchestrate preflight, evidence-backed 15–20 second copy, VoxCPM2-to-CosyVoice voice approval, mandatory edit-script approval, flexible local editing with ChatCut forbidden, final FrameField presentation, explicit upload authorization, cover choice, manual publish gating, one 72-hour review, and non-destructive artifact tracking. Never edit before script approval, create a cover before the user chooses its source, upload before explicit approval, click publish, or reorganize project files automatically.
---

# 短视频自动生产总控

把聊天中的一次“开始”转成可恢复的项目状态机。正常流程必须停在文案确认、配音确认、剪辑脚本确认、成片预览后上传确认和平台最终发布五个位置，并在制作封面前确认`手帐版 / 用户自行制作`；异常时给出明确阻塞原因。

## V2隔离规则

- 只在 `工作流文档/自动生产线-v2/`、`视频工作区/自动生产线-v2/`、`原始素材/待处理/` 和当前项目已有路径中创建必要产物；不得自动使用垃圾目录整理项目。
- 不覆盖旧工作流文档、不迁移旧项目、不清理历史目录，直至真实项目端到端验收通过并由用户另行批准替换。
- 试运行时不得上传平台、删除、移动、改名或整理文件；发布实测必须由用户明确启动具体项目。

## 必须读取

按当前阶段读取，不要一次加载无关资料：

- 启动或续跑：`references/workflow-v2.md`、`references/state-machine.md`、`references/preflight.md`。
- 写文案：先读`references/copy-evidence-gate.md`，再读`references/copy-prompt.md`。
- 生成或检查配音：`references/voice-voxcpm-cosyvoice.md`。
- 生成或确认剪辑脚本：`references/edit-script-approval.md`。
- 帧场剪辑和验收：`references/framefield-contract.md`。
- 制作封面：`references/cover-template.md`。
- 上传、发布或复盘：`references/publishing-and-review.md`。
- 完成登记或涉及文件整理：`references/retention-policy.md`。

## “开始”入口

1. 扫描 `<workspace>/原始素材/待处理/` 下的直接子目录。
2. 只有一个候选时直接选用；有多个时只让用户选项目；没有候选时说明投递位置。
3. 运行：

```bash
python3 <skill>/scripts/pipeline_state.py init --workspace <workspace>
```

4. 读取新建项目中的 `pipeline-state.json`，先执行环境预检，再从当前状态继续；禁止靠聊天历史猜测。

## 固定编排

严格按以下顺序执行：

`初始化 -> 环境预检 -> 对标/素材/事实审计 -> 文案—证据镜头检查 -> 15–20秒原创文案与独立审稿 -> 文案确认 -> VoxCPM2整段表演与CosyVoice本人音色转换/内验 -> 配音确认 -> 剪辑脚本 -> 剪辑脚本确认 -> 使用合适本地工具剪辑（禁用ChatCut） -> 最终候选进入帧场 -> 完整验收与最多三轮整改 -> 帧场供用户完整检查 -> 明确上传授权 -> 4K成片 -> 封面方案确认 -> 按选择准备封面和发布资料 -> 上传并停在发布前 -> 用户手动发布 -> 等待72小时 -> 一次正式复盘 -> 登记四项成果且不整理文件`

### 环境预检

- 按`references/preflight.md`检查素材路径、帧场服务与端口、导出Python与Pillow、VoxCPM2、CosyVoice 3、本人参考音频、Chrome本地文件权限、抖音登录和目标账号。
- 把结果写入`preflight.md`并登记为产物；任一硬检查失败就进入阻塞，不得开始分析或生成文案。
- 预检必须一次性汇总问题，禁止运行到剪辑或上传阶段才首次暴露可预见的环境错误。

### 分析

- 需要新分析时调用 `viral-machine-video-analyzer`，但V2接受后将长期输出压缩为 `analysis.md` 与 `storyboard.jpg`。
- 把来源、指标、全文、六层分析和中性框架合并进 `analysis.md`；镜头板保留8–16个代表镜头和时间码。
- 使用 `machine-video-preflight` 做我方素材与事实审计、框架适配、原创文案和独立审稿。
- 写文案前执行`references/copy-evidence-gate.md`：逐句建立“主张—所需画面—真实文件/时间码—证据强度—处理”表，并登记`evidence_matrix`产物。核心句没有直接证据时只能补拍或改弱/改写；证据门槛未通过不得进入`copy_review`。
- 已有素材且不能补拍时，先审素材再写只由真实画面支持的文案；可安排拍摄时，先按真实卖点写初稿和补拍清单，拍后重新审片并反向修正文案。禁止为了保住文案强行用无关画面填充。
- 方向由默认配置、素材和知识库自动形成；事实无法可靠确定时进入异常阻塞。剪辑脚本必须在配音确认后生成并单独等待用户确认。

### 文案确认

- 只提交已通过独立审稿的推荐文案。
- 当当前Codex界面提供结构化用户确认控件时，优先弹出`确认文案 / 退回修改`二选一卡片；当前运行模式不支持时，才使用聊天文字确认。不得为了弹卡片伪造权限请求。
- 用户确认后运行 `approve --kind copy`；任何文字或标点变化都重新打开文案确认。
- 文案确认之前不得生成正式配音或剪辑脚本。

### 配音确认

- 默认先用VoxCPM2对锁定文案生成一次完整自然表演源，再用CosyVoice 3 `inference_vc`整段转换为本人音色；不逐句拼接。
- 完成表演源验收、转换后ASR、完整试听、音色相似度、自然度、响度和解码检查。
- MiniMax、Voicebox、CosyVoice直接生成或其他方案不是默认路线；切换前必须说明原因并得到用户确认。
- 当当前Codex界面提供结构化用户确认控件时，优先弹出`确认配音 / 退回重做`二选一卡片；否则使用聊天文字确认。
- 用户确认后运行 `approve --kind voice`。
- 配音确认之前不得生成剪辑脚本或开始任何剪辑。

### 剪辑脚本确认

- 配音确认后按`references/edit-script-approval.md`生成唯一推荐剪辑脚本，登记产物后转入`awaiting_script_approval`。
- 当界面支持结构化确认控件时，优先弹出`确认剪辑脚本 / 退回修改`二选一卡片；否则使用聊天文字确认。
- 用户确认后运行`approve --kind edit_script`；用户退回时运行`reject --kind edit_script`并完整重写或定点修改脚本。
- 未处于`editing_framefield`状态时，不得使用任何工具执行剪辑；该状态名为兼容旧项目保留。

### 剪辑与验收

- 只执行用户已经确认的剪辑脚本；任何改变镜头顺序、核心时间码、文案对应或证据关系的修改，都必须重新打开剪辑脚本确认。
- 剪辑过程可以使用帧场、FFmpeg、Python或其他合适的本地工具，但不得调用ChatCut。
- 最终待确认候选必须进入当前项目的独立帧场工程，并与实际待交付文件一致；可以呈现完整时间线，也可以导入已渲染的最终候选，但不得打开无关旧工程或只展示空界面。
- 最终候选准备好后启动并核验V2隔离帧场，使用预检锁定的API/界面端口；路径或端口不匹配时立即阻塞。
- 外部工具修改画面、字幕或音频后，必须更新帧场中的最终候选，并创建帧场快照。
- 对帧场实际使用的视频素材生成代理，最多并发2个；运行`framefield_readiness.py --mode edit`并登记与当前修订一致的`framefield_edit_ready`。
- 完整验收失败时回到剪辑阶段修改、更新帧场候选，最多三轮；仍失败则阻塞。
- 内部验收通过后把播放头归零，运行`framefield_readiness.py --mode preview`并登记`framefield_preview_ready`；只有工程路径、界面端口、当前修订和代理均通过后，才在帧场中显示给用户完整观看并进入`awaiting_upload_approval`。不得启动浏览器上传或向平台传输文件。

### 成片预览与上传确认

- 用户检查后提出修改：回到剪辑阶段整改，更新帧场候选、重新完整验收并再次打开检查稿。
- 只有用户明确说“下一步上传”“开始上传”“上传这个版本”等包含清晰上传动作的指令，才运行`approve --kind upload`。
- “OK”“可以”“下一步”“没问题”等未明确出现上传意图的回复，只能继续停在`awaiting_upload_approval`并询问下一步，不得推断授权。

### 封面、上传与发布

- 4K成片完成后进入`awaiting_cover_choice`。运行`cover-choice --choice scrapbook`登记手帐版，或运行`cover-choice --choice user_provided`登记用户自行制作；未登记前不得生成封面。
- 选择手帐版时按B版手帐人物3:4参考生成；选择用户自行制作时等待用户提供文件，只做技术与版本检查。两种情况都要登记非空`cover`产物后才能上传。
- 自动准备标题、正文、话题和CTA；禁止使用已否决的实拍底图加红黄标签版式。
- 仅在`confirmations.upload=approved`且状态为`uploading`时，使用合适的已登录浏览器上传并填写页面；停在最终发布按钮前。
- 永远不得自动点击最终发布按钮。
- 用户手动发布并确认成功后，记录作品ID、链接和准确时间。

### 72小时复盘

- 不做24小时和7天复盘。
- 发布未满72小时只记录等待状态，不评分、不下内容结论。
- 满72小时后只做一次正式复盘，并把验收、发布记录和数据结论合并进 `review.md`。

## 状态控制

- 所有阶段变化必须通过 `scripts/pipeline_state.py`，不要直接手改状态。
- 每个产物用 `artifact` 命令登记绝对路径。
- 卡住时用 `block` 写入原因；解决后用 `resume` 回到被阻塞前状态。
- 重跑必须幂等：已经确认的文案和配音不得重新生成，已经上传的作品不得重复上传。

## 完成条件

只有同时满足以下条件才能完成：

- 用户已经手动发布；
- 发布已满72小时并完成正式复盘；
- `final.mp4`、`voice.wav`、`copy.md`、`review.md` 均存在且非空；
- 四项成果的实际路径已经登记。

`finalize_project.py`只用于核验和预览四项成果，禁止使用`--commit`移动或清理文件。项目目录、历史版本和缓存由用户自行整理。

## 异常升级

仅在以下情况打断用户：产品无法识别、事实不明确、关键证明缺失、素材不可用、VoxCPM2/CosyVoice持续失败、三轮验收失败、登录/验证码、上传失败、版权或宣传风险。说明发生了什么、需要用户做什么、解决后从哪一状态恢复。
