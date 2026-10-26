#!/usr/bin/env node
// 记忆目录收敛工具（#1 收敛碎片）
//
// 默认【只报告】：扫描各处 memory/ 目录，按插件当前的"记忆根"策略给出该迁往何处。
// 真正执行需显式加 --apply；源文件默认保留，加 --delete 才在成功复制后删除。
//
//   node consolidate-memory.mjs                     # 报告（dry-run）
//   node consolidate-memory.mjs --apply             # 复制到目标（保留源）
//   node consolidate-memory.mjs --apply --delete    # 复制校验后删除源
//   node consolidate-memory.mjs --base /some/dir    # 指定扫描根（默认 $HOME，深度 4）
//
// 去向策略与插件完全一致（直接 import 插件的 resolveMemoryRoot）。

import { promises as fs, existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";

const args = process.argv.slice(2);
const APPLY = args.includes("--apply");
const DELETE = args.includes("--delete");
const baseArg = args.indexOf("--base");
const BASE = baseArg >= 0 ? path.resolve(args[baseArg + 1]) : os.homedir();
const PLUGIN = process.env.SESSION_MEMORY_PLUGIN || path.join(os.homedir(), ".config/opencode/plugins/session-memory.js");
const SKIP = /(node_modules|\.cache|skill-libraries|\.codebuddy|\.git)/;

// ── 复用插件里的根定位策略（自带 @opencode/plugin 桩）──
const HARNESS = await fs.mkdtemp(path.join(os.tmpdir(), "sesmem-cons-"));
const stub = path.join(HARNESS, "node_modules/@opencode/plugin");
await fs.mkdir(stub, { recursive: true });
await fs.writeFile(path.join(stub, "package.json"),
  JSON.stringify({ name: "@opencode/plugin", version: "0.0.0", type: "module", main: "index.js", exports: { ".": "./index.js" } }));
await fs.writeFile(path.join(stub, "index.js"), "export const Plugin = { define: (d) => d };\n");
const SRC = path.join(HARNESS, "session-memory.mjs");
await fs.copyFile(PLUGIN, SRC);
const { __test } = await import(SRC);
const { resolveMemoryRoot } = __test;

// ── 扫描 memory 目录 ──
async function findMemoryDirs(dir, depth = 0, out = []) {
  if (depth > 4 || SKIP.test(dir)) return out;
  let entries;
  try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const full = path.join(dir, e.name);
    if (SKIP.test(full)) continue;
    if (e.name === "memory") { out.push(full); continue; }
    await findMemoryDirs(full, depth + 1, out);
  }
  return out;
}

async function sessionFiles(memDir) {
  const out = [];
  for (const e of await fs.readdir(memDir, { withFileTypes: true }).catch(() => [])) {
    if (!e.isDirectory()) continue;
    for (const n of await fs.readdir(path.join(memDir, e.name)).catch(() => [])) {
      if (n.endsWith(".md")) out.push(`${e.name}/${n}`);
    }
  }
  return out;
}

const dirs = (await findMemoryDirs(BASE)).sort();
console.log(`\n扫描根：${BASE}   （--apply=${APPLY}  --delete=${DELETE}）\n`);
console.log("【建议去向】按插件当前策略：项目内 memory/ 保留原位；非项目（家目录/容器目录）汇入中央桶");
console.log("─".repeat(96));

const moves = [];
for (const memDir of dirs) {
  const project = path.dirname(memDir);
  const files = await sessionFiles(memDir);
  const targetRoot = resolveMemoryRoot(null, project);
  const target = path.join(targetRoot, "memory");
  const same = path.resolve(target) === path.resolve(memDir);
  const notes = existsSync(path.join(memDir, "NOTES.md"));
  const tag = same ? "保留" : files.length ? "迁移" : "空目录(忽略)";
  console.log(`${tag.padEnd(12)} ${files.length.toString().padStart(3)} 会话  ${memDir}`);
  if (!same && files.length) {
    console.log(`             → ${target}`);
    moves.push({ memDir, target, files });
  }
}

if (!moves.length) {
  console.log("\n无需迁移。");
} else if (!APPLY) {
  console.log(`\n共 ${moves.length} 处建议迁移。这是 dry-run——加 --apply 才会执行（默认保留源文件）。`);
} else {
  console.log(`\n开始迁移 ${moves.length} 处${DELETE ? "（成功后删除源）" : "（保留源）"}...\n`);
  let copied = 0, skipped = 0, failed = 0;
  for (const { memDir, target, files } of moves) {
    for (const rel of files) {
      const src = path.join(memDir, rel);
      const dst = path.join(target, rel);
      try {
        await fs.access(dst);
        skipped++; // 已存在（按文件名去重），不覆盖
        continue;
      } catch { /* 不存在，继续 */ }
      try {
        await fs.mkdir(path.dirname(dst), { recursive: true });
        await fs.copyFile(src, dst);
        // 校验大小一致
        const [a, b] = [await fs.stat(src), await fs.stat(dst)];
        if (a.size !== b.size) throw new Error("大小不一致");
        copied++;
        if (DELETE) await fs.rm(src);
      } catch (e) {
        failed++;
        console.error(`  ✗ ${rel} → ${target}：${e.message}`);
      }
    }
    // NOTES.md 仅在目标缺失时补一份
    const srcNotes = path.join(memDir, "NOTES.md");
    const dstNotes = path.join(target, "NOTES.md");
    if (existsSync(srcNotes) && !existsSync(dstNotes)) {
      await fs.mkdir(target, { recursive: true });
      await fs.copyFile(srcNotes, dstNotes);
    }
  }
  console.log(`复制 ${copied}、跳过(已存在) ${skipped}、失败 ${failed}`);
  console.log(`INDEX.md 由插件下次读取时惰性重建，无需手工处理。`);
}

await fs.rm(HARNESS, { recursive: true, force: true });
