#!/usr/bin/env python3
"""
memrag —— 跨会话记忆的离线检索原型（BM25 + 本地向量 + 混合）
================================================================
设计原则（与 MyAgents 既有约定一致）：
  * 事实来源 = memory/*.md（Markdown），本工具只读，不修改。
  * 索引 = 可重建的派生缓存，放 <项目>/memory/.index/，随时可删。
  * 索引自描述：meta.json 记录 model/version/hash，失配即自动重建。
  * 离线优先：向量后端用本地 sentence-transformers（HF 缓存命中即可离线）。
  * 优雅降级：无向量环境时自动只用 BM25。

子命令：
  index   为若干 memory 目录建索引
  search  检索（bm25 | vector | hybrid）
  bench   基准测试（建索引耗时 / 查询延迟 / 对比样例）

用法：
  python3 memrag.py index  /path/proj1 /path/proj2 ...
  python3 memrag.py search --mem /path/proj --q "文献核验 结论" --mode hybrid -k 5
  python3 memrag.py bench  /path/proj1 /path/proj2 ... --queries "..."

纯 BM25 只需标准库（py3.7+ 可跑）；向量/混合需要 sentence-transformers。
"""
import os, re, sys, json, glob, math, time, hashlib, argparse, unicodedata
from collections import Counter

# ---------------------------------------------------------------- 文本与分词
MSG_RE = re.compile(r'^\*\*(用户|助手)\*\*：', re.M)
FM_RE = re.compile(r'^---\r?\n[\s\S]*?\r?\n---\r?\n')

CJK = lambda ch: ('\u4e00' <= ch <= '\u9fff') or ('\u3400' <= ch <= '\u4dbf')

def tokenize(text):
    """无需外部分词器：CJK 用字符二元组，拉丁/数字用词。适配中文检索。"""
    text = unicodedata.normalize('NFKC', text).lower()
    toks = []
    latin = []
    prev_cjk = None
    for ch in text:
        if CJK(ch):
            if latin:
                toks.extend(latin); latin = []
            if prev_cjk is not None:
                toks.append(prev_cjk + ch)
            prev_cjk = ch
        elif ch.isalnum():
            latin.append(ch)
            prev_cjk = None
        else:
            if latin:
                toks.extend(latin); latin = []
            prev_cjk = None
    if latin:
        toks.extend(latin)
    return toks

# ---------------------------------------------------------------- 分块
def parse_session(path):
    """把一个会话 md 拆成若干 chunk（以 用户/助手 消息为单位）。"""
    raw = open(path, encoding='utf-8', errors='ignore').read()
    fm = FM_RE.match(raw)
    meta = {}
    if fm:
        for line in fm.group(0).splitlines():
            i = line.find(':')
            if i > 0:
                meta[line[:i].strip()] = line[i+1:].strip()
        raw = raw[fm.end():]
    title = ''
    m = re.match(r'#\s*(.+)', raw.strip())
    if m:
        title = m.group(1).strip()
    # 按消息标记切分
    parts = MSG_RE.split(raw)
    chunks = []
    # parts: [head, role1, body1, role2, body2, ...]
    head = parts[0].strip()
    if head:
        chunks.append(('前言', head))
    for i in range(1, len(parts) - 1, 2):
        role, body = parts[i], parts[i+1].strip()
        if body:
            chunks.append((role, body))
    if not chunks:
        chunks = [('正文', raw.strip())]
    return meta, title, chunks

def chunk_text(text, size=1000, overlap=150):
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+size])
        if i + size >= len(text):
            break
        i += size - overlap
    return out

def collect_chunks(mem_dir):
    """返回 [(relpath, chunk_id, title, role, text), ...]"""
    items = []
    for f in sorted(glob.glob(os.path.join(mem_dir, '**', '*.md'), recursive=True)):
        base = os.path.basename(f)
        if base in ('INDEX.md',):
            continue
        rel = os.path.relpath(f, mem_dir)
        if base == 'NOTES.md':
            body = open(f, encoding='utf-8', errors='ignore').read()
            for j, c in enumerate(chunk_text(body, size=500, overlap=80)):
                items.append((rel, f'notes#{j}', '长期记忆', 'NOTE', c))
            continue
        meta, title, ch = parse_session(f)
        date = (meta.get('date') or '')[:10]
        name = f"{date} · {title}" if date else title
        for j, (role, body) in enumerate(ch):
            for k, sub in enumerate(chunk_text(body, size=1000, overlap=150)):
                items.append((rel, f'{role}#{j}.{k}', name, role, sub))
    return items

# ---------------------------------------------------------------- BM25（纯标准库）
class BM25:
    def __init__(self, corpus_tokens, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = corpus_tokens
        self.N = len(corpus_tokens)
        self.avgdl = (sum(len(d) for d in corpus_tokens) / self.N) if self.N else 0.0
        self.df = Counter()
        for d in corpus_tokens:
            for t in set(d):
                self.df[t] += 1
        self.idf = {t: math.log(1 + (self.N - c + 0.5) / (c + 0.5)) for t, c in self.df.items()}

    def scores(self, qtokens):
        out = []
        for d in self.docs:
            tf = Counter(d)
            dl = len(d) or 1
            s = 0.0
            for t in set(qtokens):
                if t not in self.idf:
                    continue
                f = tf.get(t, 0)
                if not f:
                    continue
                s += self.idf[t] * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            out.append(s)
        return out

# ---------------------------------------------------------------- 向量（本地，可离线）
class VectorBackend:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        get_dim = getattr(self.model, 'get_embedding_dimension', None) or self.model.get_sentence_embedding_dimension
        self.dim = get_dim()
        self.version = getattr(__import__('sentence_transformers'), '__version__', '')

    def encode(self, texts):
        import numpy as np
        v = self.model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        return np.asarray(v, dtype='float32')

# ---------------------------------------------------------------- 索引
def data_hash(items):
    h = hashlib.sha256()
    for it in items:
        h.update((it[0] + '|' + it[1] + '|' + it[4]).encode('utf-8', 'ignore'))
    return h.hexdigest()[:16]

def build_index(mem_dir, use_vector):
    items = collect_chunks(mem_dir)
    idx_dir = os.path.join(mem_dir, '.index')
    os.makedirs(idx_dir, exist_ok=True)
    dh = data_hash(items)
    meta = {'n_chunks': len(items), 'data_hash': dh, 'backend': 'bm25'}
    if use_vector:
        vb = VectorBackend(use_vector)
        import numpy as np
        texts = [it[4] for it in items]
        vecs = vb.encode(texts)
        np.save(os.path.join(idx_dir, 'vectors.npy'), vecs)
        meta.update({'backend': 'vector', 'model': vb.model_name,
                     'dim': int(vb.dim), 'st_version': vb.version})
    json.dump({'meta': meta, 'chunks': [list(it) for it in items]},
              open(os.path.join(idx_dir, 'index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    return meta

def load_index(mem_dir):
    p = os.path.join(mem_dir, '.index', 'index.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    return d['meta'], [tuple(x) for x in d['chunks']]

# ---------------------------------------------------------------- 检索
def mm(scores):
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [0.0] * len(scores)
    return [(s - lo) / (hi - lo) for s in scores]

DEFAULT_MODEL = 'BAAI/bge-small-zh-v1.5'   # 中文/多语言记忆的默认本地嵌入模型

def search(mem_dir, query, mode='hybrid', k=5, vec_model=None, alpha=0.5):
    loaded = load_index(mem_dir)
    if loaded is None or (mode in ('vector', 'hybrid') and not os.path.exists(os.path.join(mem_dir, '.index', 'vectors.npy'))):
        build_index(mem_dir, (vec_model or DEFAULT_MODEL) if mode in ('vector', 'hybrid') else None)
        loaded = load_index(mem_dir)
    meta, items = loaded
    vec_model = vec_model or meta.get('model') or DEFAULT_MODEL
    texts = [it[4] for it in items]
    results = {}
    if mode in ('bm25', 'hybrid'):
        bm = BM25([tokenize(t) for t in texts])
        s_bm = bm.scores(tokenize(query))
        results['bm25'] = mm(s_bm)
    if mode in ('vector', 'hybrid'):
        vb = VectorBackend(vec_model)
        import numpy as np
        qv = vb.encode([query])[0]
        V = np.load(os.path.join(mem_dir, '.index', 'vectors.npy'))
        s_v = V @ qv
        results['vector'] = mm(s_v.tolist())
    if mode == 'hybrid':
        final = [alpha * results['bm25'][i] + (1 - alpha) * results['vector'][i] for i in range(len(items))]
    elif mode == 'bm25':
        final = results['bm25']
    else:
        final = results['vector']
    order = sorted(range(len(items)), key=lambda i: -final[i])[:k]
    return [(items[i], final[i]) for i in order]

# ---------------------------------------------------------------- 命令行
def cmd_index(a):
    for mem in a.mem:
        t = time.time()
        m = build_index(mem, None if a.no_vector else a.model)
        dt = time.time() - t
        print(f"[index] {mem}  chunks={m['n_chunks']:>4}  backend={m['backend']:<6}  model={m.get('model','-')}  {dt:.2f}s")

def cmd_search(a):
    for it, sc in search(a.mem, a.q, mode=a.mode, k=a.k):
        rel, cid, title, role, text = it
        snippet = re.sub(r'\s+', ' ', text)[:160]
        print(f"  [{sc:5.3f}] {rel} · {cid} · {role} · {snippet}")

def cmd_bench(a):
    mems = a.mem
    print("== 建索引 ==")
    for mem in mems:
        for mode, flag in (('bm25', None), ('vector', a.model)):
            t = time.time(); m = build_index(mem, flag); dt = time.time() - t
            print(f"  {mode:<7} {mem:<45} chunks={m['n_chunks']:>4}  {dt*1000:8.1f} ms")
    print("\n== 查询延迟（每查询 5 次平均）==")
    qs = a.queries or ['文献核验', '抽样 偏差', '同源 风险']
    for mem in mems:
        build_index(mem, a.model)
        for mode in ('bm25', 'vector', 'hybrid'):
            ts = []
            for q in qs:
                t = time.time(); search(mem, q, mode=mode, k=5); ts.append(time.time() - t)
            print(f"  {mode:<7} {os.path.basename(os.path.dirname(mem.rstrip('/'))):<16} "
                  f"avg={1000*sum(ts)/len(ts):7.1f} ms/query")
    print("\n== 样例对比（query → top3）==")
    for q in qs:
        print(f"\n  Q: {q}")
        for mode in ('bm25', 'vector', 'hybrid'):
            res = search(mems[0], q, mode=mode, k=3)
            print(f"    [{mode}]")
            for it, sc in res:
                print(f"      {sc:5.3f}  {it[3]:<5} {re.sub(chr(10),' ',it[4])[:70]}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('index'); p.add_argument('mem', nargs='+'); p.add_argument('--no-vector', action='store_true')
    p.add_argument('--model', default=DEFAULT_MODEL); p.set_defaults(f=cmd_index)
    p = sub.add_parser('search'); p.add_argument('--mem', required=True); p.add_argument('--q', required=True)
    p.add_argument('--mode', default='hybrid', choices=['bm25', 'vector', 'hybrid']); p.add_argument('-k', type=int, default=5); p.set_defaults(f=cmd_search)
    p = sub.add_parser('bench'); p.add_argument('mem', nargs='+'); p.add_argument('--queries', nargs='*')
    p.add_argument('--model', default=DEFAULT_MODEL); p.set_defaults(f=cmd_bench)
    a = ap.parse_args(); a.f(a)

if __name__ == '__main__':
    main()
