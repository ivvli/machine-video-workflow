# 状态机

## 正常状态

`initialized -> preflighting -> analyzing -> copy_review -> awaiting_copy_approval -> voice_generating -> awaiting_voice_approval -> script_generating -> awaiting_script_approval -> editing_framefield -> validating -> awaiting_upload_approval -> exporting -> awaiting_cover_choice -> publishing_prep -> uploading -> awaiting_manual_publish -> published_waiting_72h -> reviewing_72h -> cleanup_pending -> completed`

## 回退

- 文案拒绝：`awaiting_copy_approval -> copy_review`。
- 配音拒绝：`awaiting_voice_approval -> voice_generating`。
- 剪辑脚本拒绝：`awaiting_script_approval -> script_generating`。
- 验收失败且轮次少于3：`validating -> editing_framefield`。
- 用户预览后要求修改：`awaiting_upload_approval -> editing_framefield`，并把上传确认恢复为`pending`。

## 阻塞

任意未完成状态可进入`blocked`，同时保存`blocked_from`和原因。解决后只可恢复到`blocked_from`。

## 幂等规则

- 已锁定文案不得因为续跑而重写。
- 已锁定配音不得因为续跑而重生成。
- 已锁定剪辑脚本不得因为续跑而重生成；实质改变镜头顺序、时间码、文案对应或证据关系时必须重新确认。
- `approve --kind edit_script`进入`editing_framefield`后可以使用合适的本地工具剪辑，但禁止ChatCut；最终候选必须进入正确帧场工程并通过端口、路径、修订和代理检查。
- `editing_framefield -> validating`必须存在非空且写明`帧场剪辑就绪：通过`的`framefield_edit_ready`产物，且报告修订号必须等于当前帧场工程修订号。
- `validating -> awaiting_upload_approval`除本地检查稿外，还必须存在写明`帧场预览就绪：通过`的`framefield_preview_ready`产物，且报告修订号必须等于当前帧场工程修订号。
- 从`validating`或`awaiting_upload_approval`回到`editing_framefield`时，旧检查稿及两份就绪报告全部失效，必须重新生成，不得沿用旧缓存结论。
- `analyzing`没有非空且写明`证据门槛：通过`的`evidence_matrix`产物，不得进入`copy_review`。
- `script_generating`不得越级进入`editing_framefield`。
- `awaiting_upload_approval`只有`approve --kind upload`可以进入`exporting`；普通`transition`不得绕过。
- `exporting`完成4K成片后进入`awaiting_cover_choice`；只有`cover-choice --choice scrapbook|user_provided`可以进入`publishing_prep`，未选择前不得生成封面。
- `publishing_prep -> uploading`必须已登记非空`cover`产物。
- 未达到`uploading`且`confirmations.upload!=approved`时，禁止打开平台上传页或传输文件。
- `awaiting_manual_publish`不得重复上传同一个项目。
- `published_waiting_72h`只等待一次72小时复盘。
- `completed`不可再转换。

`cleanup_pending -> completed`只核验四项正式成果，不移动、改名、删除或重新分类任何文件。

所有变更使用脚本并写入历史记录；不要直接编辑JSON。
