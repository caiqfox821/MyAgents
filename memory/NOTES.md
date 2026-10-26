<!-- 长期记忆：由 /remember 追加，/forget 删除；每行一条，形如 - 内容 -->

- 本仓库（MyAgents）是「文本事实来源」的版本化基线：`agent.md` / `SKILL.md` / `references/*.md` / `evals` / `scripts` 入库；PDF 全文、抽取文本、原始谱库等大体积派生物不入库（见 `.gitignore`），可由 `references/*/tools/` 脚本重建。
- 跨会话记忆系统：会话快照与长期记忆都在 `<项目根>/memory/`；架构与运维说明见 `memory/ARCHITECTURE.md`；插件在 `~/.config/opencode/plugins/session-memory.js`（BM25 检索，改后自动热重载）。
- 插件回归测试：`node scripts/memrag/plugin-regression.mjs`（可加 `TESTS_MEM_ROOT=<目录>` 换语料）。
