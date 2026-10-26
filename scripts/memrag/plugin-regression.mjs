#!/usr/bin/env node
// session-memory 插件回归测试（自包含：自带 @opencode/plugin 桩，不改动全局环境）
//
// 运行：  node plugin-regression.mjs
// 覆盖：分词 / BM25 排序 / 分块 / 取查询 / 检索 / 端到端注入 / recency 回退 /
//       当前会话排除 / 迁移一致性 / 写入落盘与截断 / 性能
//
// 如需指定被测插件路径或记忆目录，用环境变量：
//   SESSION_MEMORY_PLUGIN=/path/to/session-memory.js  TESTS_MEM_ROOT=/path/to/project

import { promises as fs } from "node:fs";
import path from "node:path";
import os from "node:os";

const PLUGIN = process.env.SESSION_MEMORY_PLUGIN ||
  path.join(os.homedir(), ".config/opencode/plugins/session-memory.js");
const MEM_ROOT = process.env.TESTS_MEM_ROOT || "/home/caiq/workbench/thesis";

let pass = 0, fail = 0;
const ok = (cond, name, extra = "") => {
  if (cond) { pass++; console.log(`  ✓ ${name}`); }
  else { fail++; console.log(`  ✗ ${name} ${extra}`); }
};

// ── 自建临时桩环境，使被测插件里的 `import { Plugin } from "@opencode/plugin"` 可解析 ──
const HARNESS = await fs.mkdtemp(path.join(os.tmpdir(), "sesmem-"));
const stubPkg = path.join(HARNESS, "node_modules/@opencode/plugin");
await fs.mkdir(stubPkg, { recursive: true });
await fs.writeFile(path.join(stubPkg, "package.json"),
  JSON.stringify({ name: "@opencode/plugin", version: "0.0.0", type: "module", main: "index.js", exports: { ".": "./index.js" } }));
await fs.writeFile(path.join(stubPkg, "index.js"), "export const Plugin = { define: (d) => d };\n");
const SRC = path.join(HARNESS, "session-memory.mjs");
await fs.copyFile(PLUGIN, SRC);

const mod = await import(SRC);
const { tokenize, BM25, chunkSessionBody, extractQuery, retrieve } = mod.__test;
const plugin = mod.default;

function makeCtx(root) {
  const hooks = {};
  return {
    hooks,
    ctx: {
      location: { directory: root, project: { canonical: root } },
      session: { hook: async (n, f) => { hooks[n] = f; }, context: async () => [] },
      event: { subscribe: async function* () {} },
    },
  };
}

console.log(`\n被测插件: ${PLUGIN}\n记忆目录: ${MEM_ROOT}`);

console.log("\n[1] tokenize（中文二元组 + 拉丁词）");
{
  const t = tokenize("同源偏差 same-source bias 2026");
  ok(t.includes("同源") && t.includes("源偏") && t.includes("偏差"), "中文切出二元组");
  ok(t.includes("same") && t.includes("source") && t.includes("bias"), "拉丁切出单词");
  ok(tokenize("").length === 0, "空串 → 空");
}

console.log("\n[2] BM25 排序");
{
  const docs = [tokenize("同源偏差会导致高估关联"), tokenize("今天天气不错"), tokenize("同源偏差 与 共同方法偏差")];
  const s = new BM25(docs).scores(tokenize("同源偏差"));
  ok(s[0] > s[1] && s[2] > s[1], "相关文档得分高于无关文档");
}

console.log("\n[3] chunkSessionBody");
{
  const body = "# T\n\n**用户**：问题一\n\n**助手**：" + "回答".repeat(900) + "\n\n**助手**：回答二";
  const ch = chunkSessionBody(body);
  ok(ch.some((c) => c.role === "用户") && ch.some((c) => c.role === "助手"), "按消息角色切分");
  ok(ch.every((c) => c.text.length <= 1000), "不超过片段上限");
}

console.log("\n[4] extractQuery（两种消息形态）");
{
  ok(extractQuery([{ role: "user", content: [{ type: "text", text: "hook 形态" }] }]) === "hook 形态", "hook {role,content}");
  ok(extractQuery([{ type: "user", text: "context 形态" }]) === "context 形态", "context {type,text}");
  ok(extractQuery([{ role: "assistant", content: [{ type: "text", text: "x" }] }]) === "", "只看 user");
}

async function loadChunks(root) {
  const memDir = path.join(root, "memory");
  const out = [];
  for (const e of await fs.readdir(memDir, { withFileTypes: true }).catch(() => [])) {
    if (!e.isDirectory()) continue;
    const sub = path.join(memDir, e.name);
    for (const n of await fs.readdir(sub)) {
      if (!n.endsWith(".md")) continue;
      const body = (await fs.readFile(path.join(sub, n), "utf8")).replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "").trim();
      const title = (body.match(/^#\s*(.+)/) || [, n])[1].trim();
      for (const c of chunkSessionBody(body)) out.push({ rel: `${e.name}/${n}`, label: title, role: c.role, cid: c.cid, text: c.text });
    }
  }
  return out;
}

console.log("\n[5] retrieve 在真实 memory 上召回");
{
  const chunks = await loadChunks(MEM_ROOT);
  ok(chunks.length > 0, `载入片段数 = ${chunks.length}`);
  const picked = retrieve(chunks, "同源偏差 风险", { k: 5, budget: 12000 });
  ok(picked.length > 0, "召回非空");
}

async function runHook(root, query, env) {
  if (env) for (const [k, v] of Object.entries(env)) process.env[k] = v;
  const m = await import(SRC + (env ? "?" + Date.now() + Math.random() : ""));
  const { hooks, ctx } = makeCtx(root);
  await m.default.setup(ctx);
  const event = { sessionID: "ses_TEST", messages: [{ role: "user", content: [{ type: "text", text: query }] }], system: [] };
  await hooks.context(event);
  return event.system.map((s) => s.text).join("\n");
}

console.log("\n[6] 端到端：setup + context hook（bm25 模式）");
{
  const out = await runHook(MEM_ROOT, "同源偏差");
  ok(out.includes("bm25"), "标注 bm25 模式");
  ok(out.includes("相关历史记忆"), "注入相关历史记忆块");
}

console.log("\n[6b] recency 回退（开关）");
{
  const fx = await fs.mkdtemp(path.join(os.tmpdir(), "mem-recency-"));
  await fs.mkdir(path.join(fx, "memory", "2026-10"), { recursive: true });
  // 最新一条故意超大（>MAX_INJECT_CHARS）——旧版会 break 导致一条都注入不了
  await fs.writeFile(path.join(fx, "memory/2026-10/2026-10-03-ses_big.md"),
    "---\ndate: 2026-10-03T00:00:00Z\ntitle: 超大\n---\n\n# 2026-10-03 · 超大\n\n**助手**：" + "巨".repeat(13000) + "\n");
  await fs.writeFile(path.join(fx, "memory/2026-10/2026-10-02-ses_bbb.md"),
    "---\ndate: 2026-10-02T00:00:00Z\ntitle: 乙\n---\n\n# 2026-10-02 · 乙\n\n**助手**：乙回答。\n");
  const out = await runHook(fx, "任意", { SESSION_MEMORY_MODE: "recency" });
  ok(out.includes("recency") && out.includes("历史会话记录") && out.includes("乙回答"),
    "recency 模式生效且跳过超大会话（不再 break）");
  await fs.rm(fx, { recursive: true, force: true });
}

console.log("\n[6c] bm25 排除当前会话自身");
{
  const out = await runHook(MEM_ROOT, "同源偏差");
  ok(!out.includes("ses_TEST"), "当前会话未被注入");
}

console.log("\n[6d] NOTES 注入时剥离 HTML 注释");
{
  const fx = await fs.mkdtemp(path.join(os.tmpdir(), "mem-notes-"));
  await fs.mkdir(path.join(fx, "memory", "2026-10"), { recursive: true });
  await fs.writeFile(path.join(fx, "memory/NOTES.md"),
    "<!-- 给人看的注释，不应注入 -->\n- 真正的长期记忆条目。\n");
  const out = await runHook(fx, "任意");
  ok(out.includes("真正的长期记忆条目") && !out.includes("给人看的注释"), "注释被剥离、条目保留");
  await fs.rm(fx, { recursive: true, force: true });
}

console.log("\n[7] 迁移回归：换目录后结果一致");
{
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "mem-migrate-"));
  await fs.cp(path.join(MEM_ROOT, "memory"), path.join(tmp, "memory"), { recursive: true });
  const top = (s) => (s.match(/### \[1\][\s\S]{0,400}/) || [""])[0].replace(/\s+/g, " ").slice(0, 200);
  const a = await runHook(MEM_ROOT, "文献核验");
  const b = await runHook(tmp, "文献核验");
  ok(top(a).length > 0 && top(a) === top(b), "迁移后 top1 完全一致");
  await fs.rm(tmp, { recursive: true, force: true });
}

console.log("\n[8] 写入路径：落盘 + 放宽截断");
{
  const fx = await fs.mkdtemp(path.join(os.tmpdir(), "mem-save-"));
  const m = await import(SRC + "?save=" + Date.now());
  const sess = { id: "ses_SAVE", title: "落盘测试", time: { updated: Date.now() }, location: { directory: fx } };
  const ctx = {
    location: { directory: fx, project: { canonical: fx } },
    session: { hook: async () => {}, get: async () => sess, context: async () => [
      { type: "user", text: "你好" }, { type: "assistant", content: [{ type: "text", text: "长".repeat(3000) }] }] },
    event: { subscribe: async function* () { yield { type: "session.idle", data: { sessionID: "ses_SAVE" }, location: { directory: fx } }; } },
  };
  await m.default.setup(ctx);
  await new Promise((r) => setTimeout(r, 400));
  let saved = null;
  for (const e of await fs.readdir(path.join(fx, "memory"), { withFileTypes: true }).catch(() => [])) {
    if (!e.isDirectory()) continue;
    for (const n of await fs.readdir(path.join(fx, "memory", e.name))) if (n.includes("ses_SAVE")) saved = path.join(fx, "memory", e.name, n);
  }
  ok(!!saved, "会话已原子落盘");
  if (saved) {
    const txt = await fs.readFile(saved, "utf8");
    ok(txt.includes("**用户**：你好"), "格式与旧版一致");
    ok(txt.includes("长".repeat(2900)), "3000 字消息完整存储（截断已放宽）");
  }
  await fs.rm(fx, { recursive: true, force: true });
}

console.log("\n[9] 性能");
{
  const { hooks, ctx } = makeCtx(MEM_ROOT);
  await plugin.setup(ctx);
  const N = 20, t0 = Date.now();
  for (let i = 0; i < N; i++)
    await hooks.context({ sessionID: "ses_PERF", messages: [{ role: "user", content: [{ type: "text", text: "同源偏差 " + i }] }], system: [] });
  const avg = (Date.now() - t0) / N;
  ok(avg < 200, `每次注入平均 ${avg.toFixed(1)} ms`);
}

await fs.rm(HARNESS, { recursive: true, force: true });
console.log(`\n==== 结果：${pass} 通过 / ${fail} 失败 ====`);
process.exit(fail ? 1 : 0);
