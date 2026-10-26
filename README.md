# 商业化日报：GitHub → Obsidian

这是公开仓库，仅用于已公开的日报与通用分析框架。不要上传个人面试回答、简历、论文私密内容、凭证或整个个人 Obsidian 库。

## 云端内容

- `reports.json`：现阶段唯一可编辑的日报主档，保留历史，同日期幂等更新。
- `scripts/sync_obsidian.py`：标准库脚本，将日报生成带双向链接的公开阅读笔记。
- `vault/`：Obsidian阅读副本，包含日报、事件、来源、专题、通用知识、平台公司。生成目录中的修改会被下次生成覆盖；个人注释放在另一个私有库。
- 原始链接迁入不代表本轮重新核实。历史条目在笔记中明确标记；未来任务只有核实后才能设置 verification_status=已核实。
- 同一事件跨期复用 `id`；没有id的旧条目由来源URL与标题生成确定性ID。新增前先匹配旧事件，标题修订时保留旧id。

## 当前架构阶段

先接通公开动态层。通用知识草案与平台入口用于浏览关联，完整私有面试库仍需另建私有仓库。当前不会将已有个人库内容上传。

每次 reports.json 更新将触发 GitHub Actions 生成并提交 vault 笔记。首次运行需要检查 Actions 是否成功。手动维护时也可运行：

```bash
python3 scripts/sync_obsidian.py
```

如果 Actions 失败，检查运行日志后修复；也可以运行脚本后通过GitHub树与提交接口提交笔记作为补救。仓库保存、笔记生成和网站上线分别验证，不得混报成功。

## Mac本地连接（尚需本人操作）

1. 安装并打开 GitHub Desktop，登录自己的账号。
2. `File → Clone Repository → URL` 输入 `https://github.com/2082729953-spec/daliy.git`，选择本地目录并Clone。
3. 在 Obsidian 选择“打开文件夹作为仓库”，打开克隆目录下的 `vault` 文件夹。
4. 用 GitHub Desktop 的 Fetch origin / Pull origin 拉取云端内容，回到 Obsidian 查看首页。
5. 需要自动拉取时再配置 Obsidian Git 插件；注意这里库在Git仓库的子目录内。首次配置先验证手动拉取，不自动提交整个个人库。

电脑关机不妨碍云端定时任务；本地 Obsidian 要在开机并拉取后才看到更新。仅 Clone 不等于已启用自动同步。
