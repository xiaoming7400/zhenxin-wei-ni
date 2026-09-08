# 发布清单

本项目处理的是私密聊天记录。发布前必须确认仓库只包含工具代码与 Skill 定义，不包含任何真实聊天内容。

## 可提交的文件

- `female-intimacy-coach/`：当前 Skill 和生成的通用提示词（仅通用内容）。
- `docs/`、`demos/`、`evals/`：文档、封面及虚构示例和评估用例。
- `scripts/build_release.py`、`VERSION`、`CHANGELOG.md`：发布维护文件。
- `scripts/check_site.py`、`docs/index.html`、`docs/assets/`：静态展示页及检查脚本，不含真实聊天数据。
- `.github/workflows/check.yml`：静态检查与构建配置。

- `scripts/build_training_dataset.py`
- `skill/SKILL.md`
- `README.md`
- `requirements.txt`
- `.gitignore`
- `.gitattributes`

## 禁止提交的文件

- 原始 `.xlsx` 聊天导出文件。
- `data/input/` 内除 `.gitkeep` 外的任何文件。
- `outputs/` 内除 `.gitkeep` 外的任何文件。
- 包含姓名、昵称、微信 ID、消息内容或附件的文件。

## 推送前检查

先运行 `python scripts/build_release.py` 和 `python scripts/build_release.py --check`。分享包位于 `dist/`，旧的根目录 ZIP 保留在本地，不提交。GitHub Release 应上传本次 dist 构建产物与同名 SHA-256 文件。

```bash
git status --ignored
git diff --cached --stat
git diff --cached
```

最后一条命令会显示将上传的完整文本。确认没有私人数据后，再执行 `git push`。

## 安全建议

建议先创建 GitHub 私有仓库进行首次推送。准备公开仓库时，只发布通用处理脚本与虚构的脱敏示例，绝不上传真实对话数据。
