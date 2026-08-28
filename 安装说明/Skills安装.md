# Codex Skills安装

仓库包含两套可复用Skill：

- `viral-machine-video-analyzer`：爆款机器销售视频逆向分析。
- `machine-video-preflight`：方向确认、素材证据审计、原创文案、逐镜方案和最终验收。

在macOS或Linux中，从仓库根目录执行：

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R "工作流文档/爆款分析提示词" "$CODEX_HOME/skills/viral-machine-video-analyzer"
cp -R "工作流文档/机器视频前期与验收" "$CODEX_HOME/skills/machine-video-preflight"
```

如果没有设置`CODEX_HOME`，Codex通常使用`~/.codex`。安装后重新打开Codex任务，并确认两套Skill出现在可用Skills列表中。

工作流文档中的备份用于移交；实际执行时以安装到Codex Skills目录中的版本为准。更新Skill后应同步仓库备份并逐文件比较。
