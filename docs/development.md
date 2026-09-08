# 开发与发布

主要维护 female-intimacy-coach 下的入口、规范、参考资料、工作流和示例。skill/SKILL.md 是历史版本，保留供对照，新版本以 female-intimacy-coach 为准。

## 构建

Python 3.10+，打包只使用标准库：

```bash
python scripts/build_release.py
python scripts/build_release.py --check
```

第一条同步生成 UNIVERSAL-PROMPT.md，并构建 dist/female-intimacy-coach-0.1.0.zip；第二条检查必需字段、内部链接及通用文件是否同步，不写文件。版本由 VERSION 决定。

脚本仅打包明确列出的 16 个源文件及生成的通用文件。新增模块时需要更新脚本清单。私人记录、旧 ZIP 和父目录不在打包范围。相同输入生成相同 ZIP。

## 验证

静态检查不证明回答质量。[行为评估用例](../evals/scenarios.md) 需在实际使用的模型上执行并记录结果。修改后重新跑受影响用例，不能把“用例已写好”当成“行为测试已通过”。

GitHub Actions 会在推送或拉取请求时检查通用文件同步状态、构建 ZIP，并上传构建产物。工作流仅申请只读仓库权限，不自动发布 Release。

## 发布

参考 [发布清单](../PUBLISHING.md)。尚未设置远程仓库地址，不使用虚构的下载链接。创建自己的 GitHub 仓库后再配置 origin；发布 ZIP 时使用 dist 中本次构建的文件。

当前许可尚未选定，不能标注 MIT 或称为已授权开源。作者需决定授权范围后更新许可文件。
