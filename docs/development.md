# 开发与发布

主要维护 female-intimacy-coach 下的入口、规范、参考资料、工作流和示例。skill/SKILL.md 是历史版本，保留供对照，新版本以 female-intimacy-coach 为准。

## 构建

Python 3.10+，打包只使用标准库：

```bash
python scripts/build_release.py
python scripts/build_release.py --check
```

第一条同步生成 UNIVERSAL-PROMPT.md，并构建 dist/female-intimacy-coach-0.2.0.zip；第二条检查必需字段、内部链接及通用文件是否同步，不写文件。版本由 VERSION 决定。

脚本仅打包明确列出的 16 个源文件及生成的通用文件。新增模块时需要更新脚本清单。私人记录、旧 ZIP 和父目录不在打包范围。相同输入生成相同 ZIP。

## 验证

静态检查不证明回答质量。[行为评估用例](../evals/scenarios.md) 需在实际使用的模型上执行并记录结果。修改后重新跑受影响用例，不能把“用例已写好”当成“行为测试已通过”。

GitHub Actions 会在推送或拉取请求时检查通用文件同步状态、构建 ZIP，并上传构建产物。工作流仅申请只读仓库权限，不自动发布 Release。

## 发布

参考 [发布清单](../PUBLISHING.md)。远程仓库为 `xiaoming7400/zhenxin-wei-ni`；发布 ZIP 时使用 dist 中本次构建的文件。

## 展示页面

`docs/index.html` 是无依赖静态页面，CSS、JavaScript 与原创 SVG 位于 `docs/assets/`。无在线推理、聊天上传、跟踪代码或外部字体请求。

在仓库根目录运行 `python -m http.server 8080 --bind 127.0.0.1 --directory docs`，访问 `http://127.0.0.1:8080`。检查桌面和手机布局、三个场景按钮、复制成功与拒绝权限提示，以及键盘焦点。减少动态效果跟随系统设置。

启用 GitHub Pages：仓库 Settings → Pages → Deploy from a branch，选择 `main` 分支和 `/docs` 目录并保存。此设置需仓库管理权限，不会仅因提交 HTML 自动开启。部署成功后地址为 `https://xiaoming7400.github.io/zhenxin-wei-ni/`；未验证部署前不要将其标为已上线。

### EVA 意象

- 「冲击之海」使用 CSS 绘制红色海面、月亮、冲击光环与倒影，不加载外部图片。
- 「心之壁 / A.T. FIELD」使用原创 SVG 八边形。切换「保留独处 / 允许靠近」时，双方的边界始终完整，仅调整距离和连接线；同步更新文字和无障碍状态。
- 无 JavaScript 时保留默认独处状态与完整说明；系统减少动态效果设置会关闭力场过渡。
- 这些是视觉与关系沟通隐喻，不是心理测量或对原作设定的科学解释。GitHub README 封面同步使用红海与心之壁图形。
- 回归检查：`python scripts/check_site.py`、`node --check docs/assets/site.js`、`node scripts/check_site_interactions.cjs`。交互测试使用最小 DOM 替身，不替代桌面、移动端浏览器视觉验收。

页面借鉴《新世纪福音战士》的视觉语言，仅使用原创几何图形与排版，不包含动画截图或官方标志，也不声明官方关联。GitHub README 使用 SVG 封面；交互与完整样式需访问独立页面。

当前许可尚未选定，不能标注 MIT 或称为已授权开源。作者需决定授权范围后更新许可文件。
