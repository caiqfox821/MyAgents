# 记忆系统 · 架构与运维说明

> 本文档描述本机 OpenCode 的「跨会话记忆」系统。最后盘点：**2026-10-27**。
> 说明文档本身放在 `memory/` 根下（插件只扫描 `memory/<年-月>/` 子目录），因此**不会被注入上下文**。

---

## 一、五层结构

| 层 | 载体 | 谁写 | 是否进上下文 |
|---|---|---|---|
| ① 写入（自动） | `memory/<YYYY-MM>/<日期>-<会话ID>.md` | session-memory 插件，会话结束覆盖式快照 | 否 |
| ② 读取（自动注入） | 同上，**BM25 检索 Top-K 片段** | 插件，每次模型请求 | 是，≤12000 字符 |
| ③ 长期记忆（人工 L1） | `memory/NOTES.md` | `/remember`｜`/forget`｜`/memory` | 是，始终注入，≤4000 字符 |
| ④ 索引（给人看） | `memory/INDEX.md` | 插件惰性重建 | 否 |
| ⑤ 知识层（另一套） | `公共知识/书库`、各专家 `references/证据条目`、skill-libraries | 走 search_books.py / TogoMCP / papers MCP | 按需 |

**原则**：Markdown 是**唯一事实来源**；索引与检索是可重建的派生物；整个 `memory/` 目录可以"直接拷贝"迁移。

## 二、插件

- 路径：`~/.config/opencode/plugins/session-memory.js`（单文件、零第三方依赖，只用 Node 内置模块）
- 原版备份：`~/.config/opencode/plugins/session-memory.js.bak-original`（即 git `HEAD` 版本）
- 检索：内置 **BM25** + 免分词器中文切分（CJK 二元组 + 拉丁词）；离线、毫秒级
- OpenCode V2 会自动 `plugin reconciliation`——**改完插件即热重载，无需重启**

### 可调常量

| 常量 | 值 | 含义 |
|---|---|---|
| `MODE`（环境变量 `SESSION_MEMORY_MODE`） | `bm25`（默认）\| `recency` | 检索模式 |
| `MAX_INJECT_CHARS` | 12000 | 注入总预算 |
| `TOP_K` | 8 | 召回片段数上限 |
| `CHUNK_CHARS` / `CHUNK_OVERLAP` | 1000 / 150 | 片段切分 |
| `NOTES_BUDGET` | 4000 | NOTES 注入上限 |
| `MAX_STORED_PER_MSG` | 8000 | 单条消息入库上限 |
| `MAX_SESSIONS` | 6 | 仅 recency 模式：最多注入会话数 |

### 一键回退

```bash
export SESSION_MEMORY_MODE=recency                                   # 切回时间序行为
cp ~/.config/opencode/plugins/session-memory.js.bak-original \
   ~/.config/opencode/plugins/session-memory.js                      # 彻底还原原文件
```
recency 与原始版本的差异：NOTES 上限 12000→4000、多一行模式标注、超预算会话「跳过」而非「中止」。

## 三、回归测试

```bash
node ~/MyAgents/scripts/memrag/plugin-regression.mjs                       # 默认 thesis 语料
TESTS_MEM_ROOT=/home/caiq/workbench node ~/MyAgents/scripts/memrag/plugin-regression.mjs   # 最大语料
```
覆盖：分词 / BM25 排序 / 分块 / 取查询 / 检索 / 端到端注入 / recency 回退 / 当前会话排除 / 迁移一致性 / 写入落盘与截断 / 性能。Python 原型与基准：`scripts/memrag/memrag.py`。

## 四、现状盘点（2026-10-27）

8 个活跃记忆目录，**77 个会话、共 577 KB、无重复**：

| 目录 | 会话 | 大小 |
|---|---|---|
| `workbench/memory` | 31 | 360 KB |
| `~/memory` | 31 | 129 KB |
| `MyAgents/memory` | 3 | 24 KB |
| `workbench/thesis/memory` | 3 | 22 KB |
| `workbench/review`、`workbench/medicinal-plant`、`local-llm`、`.config/opencode` | 9 | 41 KB |
| `project/*` 等 | 0 | 均为 95 字节空 NOTES 模板 |

- 性能：单次注入 thesis ~5 ms、workbench（695 片段）~39 ms。
- BM25 实效：thesis 查询注入 6891 字符 vs 旧 recency 仅 737 字符。

## 五、已知问题 / 待办

1. **记忆按 cwd 碎片化**：插件以「git 根，否则当前工作目录」定位 `memory/`，非 git 目录下换个工作目录就换一套记忆（`~/memory` 与 `~/workbench/memory` 各 31 条、互不可见）。→ 待定「记忆根」策略。
2. **L1 长期记忆基本空转**：多数项目无 `NOTES.md`，`/remember` 很少使用。
3. **会话标题取自首条用户消息**，常与内容不符，影响 INDEX 可读性与召回标签。
4. （可选）**P2 本地向量混合检索**：`BAAI/bge-small-zh-v1.5` + `memory/.index/`（可重建缓存，`meta.json` 记录模型/维度/哈希，失配自动重建，回退 BM25）。已 `.gitignore`。
