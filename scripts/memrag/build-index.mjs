#!/usr/bin/env node
// 构建向量索引（#5 P2 本地向量混合检索）。
//
//   node build-index.mjs                      # 为当前目录解析出的记忆根建索引
//   node build-index.mjs --mem ~/workbench/memory
//   node build-index.mjs --url http://127.0.0.1:8787/embed
//
// 产物：<memory>/.index/vectors.json
//   { meta: { model, dim, chunker, built, count, files: { rel: mtimeMs } },
//     items: [ { rel, cid, v: <base64 float32> } ] }
//
// 分块用插件的 chunkSessionBody（import 插件，保证与运行时逐块对齐）；
// 检索时若文件指纹（mtime）与索引不符，插件自动回退 BM25，不会出错。

import { promises as fs, existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";

const args = process.argv.slice(2);
const opt = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : dflt;
};
const URL_ = opt("--url", process.env.SESSION_MEMORY_EMBED_URL || "http://127.0.0.1:8787/embed");
const BATCH = Number(opt("--batch", 64));
const PLUGIN = opt("--plugin", path.join(os.homedir(), ".config/opencode/plugins/session-memory.js"));
const CHUNKER = "v1"; // 分块算法版本；改动 chunkSessionBody 时递增

// ── 载入插件（自带 @opencode/plugin 桩），复用分块与根定位 ──
const HARNESS = await fs.mkdtemp(path.join(os.tmpdir(), "sesmem-idx-"));
const stub = path.join(HARNESS, "node_modules/@opencode/plugin");
await fs.mkdir(stub, { recursive: true });
await fs.writeFile(path.join(stub, "package.json"),
  JSON.stringify({ name: "@opencode/plugin", version: "0.0.0", type: "module", main: "index.js", exports: { ".": "./index.js" } }));
await fs.writeFile(path.join(stub, "index.js"), "export const Plugin = { define: (d) => d };\n");
const SRC = path.join(HARNESS, "session-memory.mjs");
await fs.copyFile(PLUGIN, SRC);
const { __test } = await import(SRC);
const { chunkSessionBody, resolveMemoryRoot } = __test;

// ── 定位记忆目录 ──
const memArg = opt("--mem", "");
const memDir = memArg
  ? path.resolve(memArg.replace(/^~(?=[/\\]|$)/, os.homedir()))
  : path.join(resolveMemoryRoot(null, process.cwd()), "memory");
if (!existsSync(memDir)) {
  console.error(`✗ 记忆目录不存在：${memDir}\n  （先在该项目里跑一次会话，或用 --mem 指定）`);
  await fs.rm(HARNESS, { recursive: true, force: true });
  process.exit(1);
}

// ── 收集片段 ──
const files = [];
for (const e of await fs.readdir(memDir, { withFileTypes: true })) {
  if (!e.isDirectory() || e.name.startsWith(".")) continue;
  for (const n of await fs.readdir(path.join(memDir, e.name)).catch(() => [])) {
    if (n.endsWith(".md")) files.push(`${e.name}/${n}`);
  }
}
files.sort();

const items = [];   // { rel, cid, text }
const fingerprints = {};
for (const rel of files) {
  const full = path.join(memDir, rel);
  const [text, st] = await Promise.all([fs.readFile(full, "utf8").catch(() => ""), fs.stat(full)]);
  fingerprints[rel] = Math.round(st.mtimeMs);
  const body = text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "").trim();
  if (!body) continue;
  for (const c of chunkSessionBody(body)) items.push({ rel, cid: c.cid, text: c.text });
}
if (!items.length) {
  console.error(`✗ ${memDir} 下没有可比对的片段。`);
  await fs.rm(HARNESS, { recursive: true, force: true });
  process.exit(1);
}
console.log(`记忆目录：${memDir}\n会话 ${files.length} 个、片段 ${items.length} 个 → 请求嵌入 ${URL_}`);

// ── 嵌入 ──
const enc = (a) => Buffer.from(new Float32Array(a).buffer, 0, a.length * 4).toString("base64");
const out = [];
let dim = 0, model = "";
const t0 = Date.now();
for (let i = 0; i < items.length; i += BATCH) {
  const slice = items.slice(i, i + BATCH);
  let res;
  try {
    res = await fetch(URL_, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ texts: slice.map((x) => x.text) }),
    });
  } catch (e) {
    console.error(`✗ 连不上嵌入服务（${URL_}）：${e.message}\n  先启动：~/MyAgents/scripts/memrag/embed-server.py`);
    await fs.rm(HARNESS, { recursive: true, force: true });
    process.exit(1);
  }
  if (!res.ok) {
    console.error(`✗ 嵌入服务返回 ${res.status}：${await res.text()}`);
    await fs.rm(HARNESS, { recursive: true, force: true });
    process.exit(1);
  }
  const j = await res.json();
  dim = j.dim || (j.vectors?.[0]?.length ?? 0);
  model = j.model || "";
  slice.forEach((x, k) => out.push({ rel: x.rel, cid: x.cid, v: enc(j.vectors[k]) }));
  process.stdout.write(`  已嵌入 ${Math.min(i + BATCH, items.length)}/${items.length}\r`);
}
console.log(`\n嵌入完成：${out.length} 个片段、${dim} 维、用时 ${((Date.now() - t0) / 1000).toFixed(1)}s`);

// ── 落盘 ──
const indexDir = path.join(memDir, ".index");
await fs.mkdir(indexDir, { recursive: true });
const payload = {
  meta: { model, dim, chunker: CHUNKER, built: new Date().toISOString(), count: out.length, files: fingerprints },
  items: out,
};
const dst = path.join(indexDir, "vectors.json");
await fs.writeFile(dst, JSON.stringify(payload));
const size = (await fs.stat(dst)).size;
console.log(`已写入 ${dst}（${(size / 1024 / 1024).toFixed(2)} MB）`);
console.log(`启用检索：export SESSION_MEMORY_VECTOR=auto   （插件热重载后生效）`);

await fs.rm(HARNESS, { recursive: true, force: true });
