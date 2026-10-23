# -*- coding: utf-8 -*-
"""等价性验证：纯 Python 版 vs numpy 版。

用途：确认 `scripts/plant_lstm.py`（numpy 版）与 `scripts/backup/plant_lstm_pure_*.py`
（原始纯 Python 版）在**同随机种子**下产生完全相同的损失、权重与预测。

做法：两边在构建模型前都重新 `random.seed()`，跑完全相同的流程后逐项对比。
注意：如果不对每个模型重新播种，先跑的模型会把全局随机流前移，造成假差异。

数据：需要一个训练数据 JSON（默认 ./番茄_data.json），可用
      `python3 ../scripts/plant_lstm.py gen_data --plant 番茄 --weeks 40 --out 番茄_data.json` 生成。

用法：python3 verify_equiv.py          （在 dev/ 目录下运行，或设 PLANT_DEV_DATA 指向数据目录）
"""
import glob
import importlib.util
import json
import os
import random
import sys
import types

import numpy as np

DEV_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DEV_DIR)
NEW = os.path.join(BASE, 'scripts/plant_lstm.py')
PURE = sorted(glob.glob(os.path.join(BASE, 'scripts/backup/plant_lstm_pure_*.py')))[-1]
LIB = os.path.join(BASE, '植物生长模型参数库.md')
DATA_DIR = os.environ.get('PLANT_DEV_DATA') or os.getcwd()
DATA = os.path.join(DATA_DIR, '番茄_data.json')
WORK = os.path.join(DATA_DIR, 'verify')
os.makedirs(WORK, exist_ok=True)


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


pure = load_mod(PURE, 'pure')
npv = load_mod(NEW, 'npv')
print('纯 Python 版:', os.path.basename(PURE))
print('numpy   版:', os.path.basename(NEW))

data = json.load(open(DATA, encoding='utf-8'))
cfg = [p for p in pure.load_library(LIB) if p['plant'] == '番茄'][0]

results = {}


def make_args(**kw):
    d = dict(plant='番茄', config=None, library=LIB, layers=None, fc_dim=None, lr=None,
             adaptive=None, window=None, forget=None, global_keep=None)
    d.update(kw)
    return types.SimpleNamespace(**d)


def train_run(mod, seed, adaptive, epochs=40, window=4):
    """完整训练流程，完全由 seed 决定。"""
    random.seed(seed)
    m, _, _ = mod.build_model(cfg, make_args(adaptive=adaptive))
    pairs = []
    for i in range(window, len(data)):
        seq = [mod.spec_to_vec(data[i - window + k], cfg['features']) for k in range(window)]
        pairs.append((seq, mod.spec_to_vec(data[i], cfg['outputs'])))
    hist = []
    for _ in range(epochs):
        random.shuffle(pairs)
        tg = tc = 0.0
        for seq, tgt in pairs:
            lg, lc = m.train_one(seq, tgt, 1.0)
            tg += lg
            tc += lc
        ag, ac = tg / len(pairs), tc / len(pairs)
        m.adapt(ag, ac)
        hist.append((ag, ac))
    return m, hist


def build_run(mod, seed, layers, ops=()):
    """同一随机种子下构建模型并执行若干结构操作（每个模块都重新播种）。"""
    random.seed(seed)
    m = mod.PlantLSTM(cfg['features'], cfg['outputs'], layers=list(layers), fc_dim=20, window=4)
    for op in ops:
        op(m)
    return m


def flat_weights(m):
    out = [np.asarray(m.wfc, float).ravel(), np.asarray(m.wout, float).ravel()]
    for c in m.lstm.cells:
        for a in ('wf', 'wi', 'wc', 'wo', 'bf', 'bi', 'bc', 'bo'):
            out.append(np.asarray(getattr(c, a), float).ravel())
    return out


def predict_all(mod, m, window=4):
    seq = [mod.spec_to_vec(data[-window + k], cfg['features']) for k in range(window)]
    return np.asarray(m.predict(seq), float)


def wdiff(ma, mb):
    wa, wb = flat_weights(ma), flat_weights(mb)
    if len(wa) != len(wb) or any(x.shape != y.shape for x, y in zip(wa, wb)):
        return None
    return max(float(np.abs(x - y).max()) for x, y in zip(wa, wb))


def report(tag, ma, mb, ha=None, hb=None, pa=None, pb=None):
    ok = True
    print('\n' + '=' * 72)
    print(tag)
    print('=' * 72)
    sa = [c.hid for c in ma.lstm.cells]
    sb = [c.hid for c in mb.lstm.cells]
    ia = [c.inp for c in ma.lstm.cells]
    ib = [c.inp for c in mb.lstm.cells]
    same = sa == sb and ia == ib
    print('  结构(hid)    : {} vs {}   {}'.format(sa, sb, 'OK' if same else '不一致'))
    ok &= same
    if ha is not None:
        d = float(np.abs(np.asarray(ha, float) - np.asarray(hb, float)).max())
        print('  损失最大偏差 : {:.3e}   {}'.format(d, 'OK' if d < 1e-9 else '偏大'))
        ok &= d < 1e-9
    d = wdiff(ma, mb)
    if d is None:
        print('  权重形状     : 不一致   FAIL')
        return False, False
    print('  权重最大偏差 : {:.3e}   {}'.format(d, 'OK' if d < 1e-9 else '偏大'))
    ok &= d < 1e-9
    if pa is not None:
        d = float(np.abs(pa - pb).max())
        print('  预测最大偏差 : {:.3e}   {}'.format(d, 'OK' if d < 1e-9 else '偏大'))
        ok &= d < 1e-9
    return ok, d


# ---------- 1. 固定结构 ----------
ma, ha = train_run(pure, 2026, adaptive=False)
mb, hb = train_run(npv, 2026, adaptive=False)
ok, _ = report('① 固定结构（adaptive=False，40 轮）', ma, mb, ha, hb,
               predict_all(pure, ma), predict_all(npv, mb))
results['固定结构'] = ok

# ---------- 2. 结构自适应 ----------
ma, ha = train_run(pure, 7, adaptive=True)
mb, hb = train_run(npv, 7, adaptive=True)
ok, _ = report('② 结构自适应（adaptive=True，40 轮，含扩容/剪枝）', ma, mb, ha, hb,
               predict_all(pure, ma), predict_all(npv, mb))
results['自适应训练'] = ok

# ---------- 3. 结构操作 ----------
print('\n' + '=' * 72)
print('③ 结构操作 expand_last / prune_weak')
print('=' * 72)

# 3a: 2 层，扩容两次
ops = (lambda m: m.lstm.expand_last(6), lambda m: m.lstm.expand_last(6))
A = build_run(pure, 99, [12, 16], ops)
B = build_run(npv, 99, [12, 16], ops)
ok, d = report('   3a 两层模型连续扩容两次', A, B)
results['expand_last 2层'] = ok

# 3b: 3 层（cells[1:] 有两个单元，覆盖多高层路径）
A = build_run(pure, 31, [12, 16, 14], (lambda m: m.lstm.expand_last(6),))
B = build_run(npv, 31, [12, 16, 14], (lambda m: m.lstm.expand_last(6),))
ok, d = report('   3b 三层模型扩容（多高层单元）', A, B)
results['expand_last 3层'] = ok


# 3c: 剪枝
def zero_and_prune(m):
    c = m.lstm.cells[-1]
    for a in ('wf', 'wi', 'wc', 'wo'):
        w = getattr(c, a)
        if isinstance(w, np.ndarray):
            w[0, :] = 0.0
            w[1, :] = 0.0
        else:
            w[0] = [0.0] * len(w[0])
            w[1] = [0.0] * len(w[1])
    for a in ('bf', 'bi', 'bc', 'bo'):
        b = getattr(c, a)
        b[0] = 0.0
        b[1] = 0.0
    m.lstm.prune_weak(0.005, 12)


A = build_run(pure, 5, [12, 16], (zero_and_prune,))
B = build_run(npv, 5, [12, 16], (zero_and_prune,))
ok, d = report('   3c 剪枝（清零末层 2 行后）', A, B)
results['prune_weak'] = ok


# 3d: 双层扩容后继续训练（覆盖多层 expand_last 后的“静默截断”路径）
def train_after_expand(mod, seed, epochs=8, window=4):
    random.seed(seed)
    m = mod.PlantLSTM(cfg['features'], cfg['outputs'], layers=[12, 16], fc_dim=20, window=4)
    m.lstm.expand_last(6)
    m._init_head()
    pairs = []
    for i in range(window, min(len(data), window + 12)):
        seq = [mod.spec_to_vec(data[i - window + k], cfg['features']) for k in range(window)]
        pairs.append((seq, mod.spec_to_vec(data[i], cfg['outputs'])))
    for _ in range(epochs):
        random.shuffle(pairs)
        for seq, tgt in pairs:
            m.train_one(seq, tgt, 1.0)
    return m


A = train_after_expand(pure, 77)
B = train_after_expand(npv, 77)
ok, d = report('   3d 双层扩容后继续训练（静默截断路径）', A, B,
               pa=predict_all(pure, A), pb=predict_all(npv, B))
results['扩容后训练'] = ok

# ---------- 4. JSON 格式与存取往返 ----------
print('\n' + '=' * 72)
print('④ 模型 JSON 格式与存取往返')
print('=' * 72)
ma, _ = train_run(pure, 555, adaptive=True)
mb, _ = train_run(npv, 555, adaptive=True)
f_pure = os.path.join(WORK, 'from_pure.json')
f_new = os.path.join(WORK, 'from_numpy.json')
ma.save(f_pure)
mb.save(f_new)
ja = json.load(open(f_pure, encoding='utf-8'))
jb = json.load(open(f_new, encoding='utf-8'))
print('  顶层键一致        : {}'.format('OK' if set(ja) == set(jb) else 'FAIL'))
results['JSON 键'] = set(ja) == set(jb)
print('  文件大小          : pure={}B  numpy={}B'.format(os.path.getsize(f_pure), os.path.getsize(f_new)))

lp = pure.PlantLSTM.load(f_new)
ln = npv.PlantLSTM.load(f_new)
seq = [pure.spec_to_vec(data[-4 + k], cfg['features']) for k in range(4)]
d1 = float(np.abs(np.asarray(lp.predict(seq), float) - np.asarray(ln.predict(seq), float)).max())
print('  numpy 存的模型被两边加载(预测偏差 {:.3e})  {}'.format(d1, 'OK' if d1 < 1e-12 else 'FAIL'))
results['跨版本加载'] = d1 < 1e-12

lp2 = pure.PlantLSTM.load(f_pure)
ln2 = npv.PlantLSTM.load(f_pure)
d2 = float(np.abs(np.asarray(lp2.predict(seq), float) - np.asarray(ln2.predict(seq), float)).max())
print('  纯 Python 存的模型被两边加载(预测偏差 {:.3e})  {}'.format(d2, 'OK' if d2 < 1e-12 else 'FAIL'))
results['反向加载'] = d2 < 1e-12

mm = npv.PlantLSTM.load(f_new)
d3 = wdiff(mb, mm)
print('  numpy 版 存-取 往返权重偏差 {:.3e}  {}'.format(d3, 'OK' if d3 < 1e-15 else 'FAIL'))
results['往返精度'] = d3 < 1e-15

print('\n' + '=' * 72)
allok = all(results.values())
print('总计: ' + ('全部通过 ✅' if allok else '存在失败 ❌'))
for k, v in results.items():
    print('  {:<16} {}'.format(k, 'PASS' if v else 'FAIL'))
print('=' * 72)
sys.exit(0 if allok else 1)
