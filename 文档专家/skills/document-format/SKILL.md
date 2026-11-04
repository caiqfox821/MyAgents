---
name: document-format
description: PPT/Word 文档格式化技能。用于把内容整理成规范幻灯片与 Word 文档，套用公文/科学报告/项目申报书模板，程序化生成 pptx/docx 并校验排版。当生成或编辑演示文稿、报告、公文、申报书时加载。
---

# 文档格式化技能

## 何时使用
用户要求生成/编辑 PPT、Word，套模板、排版、做汇报材料或正式文档时。

## 内置技能优先
本环境已内置，遇到对应任务优先调用：
- `pptx`：创建/编辑/分析 .pptx（PptxGenJS、OOXML、转图片）
- `docx`：创建/编辑/分析 .docx（docx-js、python-docx、修订）
- `official-document`：GB/T 9704 党政公文
- `scientific-report`：IMRAD 科学报告
- `xlsx`：表格与数据
- `mindmap`：思维导图/结构梳理

## 工作流
1. **澄清**：文档类型、对象、篇幅、期限、是否套模板
2. **大纲**：先给页面/章节清单，获得确认
3. **选模板**：见专家目录下的 `templates/`（已迁移为本地实体文件）
4. **生成**：写脚本生成，保证可复现；不手搓二进制
5. **校验**：渲染预览，检查溢出/错位/字体/页码/图表清晰度
6. **交付**：成品 + 生成脚本 + 预览图

## 模板清单（templates/）
- 报告类：`doc-报告格式`、`doc-科学报告`、`doc-内部报告`、`doc-项目报告`、`doc-年中总结报告`、`doc-项目申报书格式`
- 公文类：`doc-党政公文`
- PPT 类：`ppt-长三院简洁模板`、`ppt-长三院简洁生成`、`ppt-长三院简洁生成简版`、`ppt-白底紫标题`、`ppt-配色方案`
- 样式基准：`reference-tnr-simsun.docx`（pandoc `--reference-doc`，中文宋体/英文 Times New Roman/全黑/表头无底纹+黑细线）
- 脚本：`generate_pptx.py`、`make_reference.py`（重建样式基准文件）

## 版式规范速查
- **Word 版式默认规则（2026-10 起，强制）**：除党政公文外，所有 .docx 一律**中文宋体 + 英文/数字 Times New Roman + 全文纯黑 #000000**；标题以字号和加粗分层，不用彩色标题/主题色/彩色底纹；表格表头不加底纹、仅加粗，边框黑色细线（0.5 pt）。
- 生成命令：`pandoc 输入.md -o 输出.docx --from gfm --reference-doc=templates/reference-tnr-simsun.docx --no-highlight`
- 公文 **例外**：GB/T 9704-2012（红头、仿宋/黑体/楷体，页边距、行距、页码），不适用上述黑白规则
- 科学报告：IMRAD（引言-方法-结果-讨论）
- 参考文献：GB/T 7714 或 APA
- 数字单位用国标符号；中英文混排须分别指定 eastAsia 与 ascii/hAnsi 字体

## 质量红线
- 不臆造数据，内容缺口回退给领域专家
- 交付前必须实际生成文件并预览
- 颜色/字体/母版保持一致，长文档自动目录与页码

## 命名规范
`主题-类别-版本-日期`，如 `食药用菌产业技术现状-v2-20261001.pptx`
