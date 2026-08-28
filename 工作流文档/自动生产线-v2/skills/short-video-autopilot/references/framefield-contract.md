# 帧场最终呈现契约

- 剪辑过程可以使用帧场、FFmpeg、Python或其他合适的本地工具，但禁止ChatCut参与任何剪辑。
- 剪辑脚本未确认前不得开始任何剪辑。最终待确认版本必须进入帧场，并与实际待交付文件一致，供用户完整播放检查。
- 状态名`editing_framefield`为兼容旧项目保留，表示“已获准剪辑并最终交付到帧场”，不再表示所有中间操作只能发生在帧场。
- 每个V2项目使用独立帧场工程目录 `<运行项目>/framefield/`。先用帧场CLI的 `new` 创建并切换工程，再导入该项目素材；不得复用或覆盖当前旧工程。
- 旧流程未被替换前，真实试跑使用源码启动的并行帧场：API默认`4318`、界面默认`3001`，通过`VIDEO_PROJECT_DIR=<运行项目>/framefield`和`NEXT_PUBLIC_LOCAL_EDITOR_API=http://127.0.0.1:4318`隔离。不得切换当前安装版`4317/3000`所使用的旧工程。
- 并行试跑调用工作区源码中的 `本地剪辑台/bin/editor-cli.mjs`，并设置`LOCAL_EDITOR_API=http://127.0.0.1:4318`；新版本正式安装并由用户批准覆盖后，才改用安装目录CLI。
- 最终候选准备好后启动`4318/3001`、用CLI选择`<运行项目>/framefield/`，确认健康接口返回的`projectFile`等于当前工程，并自动打开`http://127.0.0.1:3001/`。
- 把实际待交付候选放入帧场；可呈现完整时间线，也可导入已经渲染的完整候选。任何外部修改后都必须更新帧场版本。
- 对帧场实际使用的视频素材生成代理，并发上限默认2；代理未就绪时不得声称内容已经加载。
- 使用`scripts/framefield_readiness.py`执行硬检查。最终候选进入帧场后运行`--mode edit`并登记`framefield_edit_ready`；播放头归零后运行`--mode preview`并登记`framefield_preview_ready`。

就绪检查和登记使用以下形式，`<skill>`为本Skill目录，`<项目>`为当前自动生产线运行项目：

```bash
python3 <skill>/scripts/framefield_readiness.py --project <项目> --mode edit --api-port 4318 --web-port 3001
python3 <skill>/scripts/pipeline_state.py artifact --project <项目> --name framefield_edit_ready --path <项目>/framefield-edit-ready.md
python3 <skill>/scripts/framefield_readiness.py --project <项目> --mode preview --api-port 4318 --web-port 3001
python3 <skill>/scripts/pipeline_state.py artifact --project <项目> --name framefield_preview_ready --path <项目>/framefield-preview-ready.md
```
- 帧场至少必须明确显示当前最终候选、正确项目路径、当前修订和可播放代理；不得用旧版本冒充待交付版本。
- 最终候选进入帧场和每轮整改后创建快照。
- 自动验收必须完整播放；关键帧和参数不能替代观看。
- 画面、配音、字幕或时间线发生任何变化后，从头重新验收。
- 最多自动整改三轮，仍失败则阻塞并输出时间码、原因和建议。
- 内部验收通过后导出本地检查稿，播放头归零并打开帧场供用户完整观看；登记检查稿，但不上传。
- “帧场已打开”必须同时表示界面可访问、工程正确且当前播放头对应的代理可播放；只打开网页外壳不算完成。代理准备期间应报告进度，全部完成后才通知用户检查。
- 用户预览提出修改时，回到`editing_framefield`整改、更新帧场候选并从头验收；不得沿用旧的上传授权。
