# 安装与使用

## 普通 AI 聊天工具

打开 [通用提示词](../female-intimacy-coach/UNIVERSAL-PROMPT.md)，将全文粘贴到新会话，或上传文件后请求：

> 请完整读取这份文件，按其中规范担任“真心为你”沟通助手。我的问题是……

这种方法适用于支持相应文本长度或附件读取的工具。ChatGPT、Claude、Gemini 等平台的实际能力、额度和设置可能不同，项目未逐平台实测。ZIP 通常需要先解压；附件不能读取时粘贴正文。

## 支持 Skill 的代理

将整个 female-intimacy-coach 文件夹导入工具的技能目录，保留所有子文件。不同代理的发现方式不同，请使用它自身提供的导入入口或技能目录。

Codex 的个人目录示例：

- Windows：%USERPROFILE%\.codex\skills\female-intimacy-coach
- macOS / Linux：~/.codex/skills/female-intimacy-coach

新建会话后请求“使用 $female-intimacy-coach”。入口仍使用此技术名称，产品名称是“真心为你”。不要只复制 SKILL.md。

## API 或本地模型

将通用提示词作为工具支持的系统指令或初始上下文，问题作为用户消息。项目不提供模型服务，也不内置 API 密钥；模型费用由平台决定。只有使用本地推理环境时，才能按该环境的配置讨论离线处理。

## 更新与卸载

更新时先备份自己改过的技能目录，再手动替换新版文件。卸载时删除自己安装的目录即可。普通聊天中更新文件不会影响旧会话已经加载的内容，请重新加载或新建会话。

## 可选：整理 XLSX

只使用 Skill 无需 Python。整理本地表格需 Python 3.10+：

```bash
python -m pip install -r requirements.txt
python scripts/build_training_dataset.py --source-dir "你的表格目录" --strict-text-only
```

输出在 outputs 中，包括原始消息整理结果、候选对话对与统计报告。它们未经人工质量审核，不能直接称作高质量训练数据。语音、图片内容是否可分析取决于输入中实际提供的信息。
