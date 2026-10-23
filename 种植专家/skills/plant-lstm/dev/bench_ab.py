# -*- coding: utf-8 -*-
"""A/B 性能对比：纯 Python 版 vs numpy 版。

测量用 **CPU 时间**（user+sys），并让两个引擎交替执行、多轮取最小值。
原因：这台机器上 WeChat/wpsupdate 常驻，load 常年 >4、CPU 会被降到 500MHz 左右，
墙钟时间抖动可达 3–5 倍，完全不可比。

数据：需要 番茄_data.json 与 金线莲_data.json（可用 gen_data 生成）。
用法：python3 bench_ab.py      （在 dev/ 目录运行，或设 PLANT_DEV_DATA 指向数据目录）
"""
import glob
import os
import resource
import subprocess
import sys
import time

DEV_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DEV_DIR)
S = os.path.join(BASE, 'scripts')
LIB = os.path.join(BASE, '植物生长模型参数库.md')
PURE = sorted(glob.glob(os.path.join(S, 'backup/plant_lstm_pure_*.py')))[-1]
NEW = os.path.join(S, 'plant_lstm.py')
D = os.environ.get('PLANT_DEV_DATA') or os.getcwd()
B = os.path.join(D, 'bench_ab')
os.makedirs(B, exist_ok=True)
ROUNDS = 2


def run(cmd):
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    rc = subprocess.run([sys.executable] + cmd, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL).returncode
    t1 = time.time()
    a = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (a.ru_utime - b.ru_utime) + (a.ru_stime - b.ru_stime)
    return rc, cpu, t1 - t0


def sc(script, args):
    return [script, '--library', LIB] + args


def cases(tag, script):
    return [
        ('①番茄训练(默认150轮)', sc(script, ['train', '--plant', '番茄',
                                           '--data', f'{D}/番茄_data.json',
                                           '--model', f'{B}/{tag}_a.json'])),
        ('②番茄2层300轮', sc(script, ['train', '--plant', '番茄',
                                     '--data', f'{D}/番茄_data.json',
                                     '--layers', '16,24', '--epochs', '300', '--window', '6',
                                     '--model', f'{B}/{tag}_b.json'])),
        ('③金线莲训练(100周)', sc(script, ['train', '--plant', '金线莲',
                                          '--data', f'{D}/金线莲_data.json',
                                          '--model', f'{B}/{tag}_c.json'])),
        ('④在线增量学习', sc(script, ['incremental', '--model', f'{B}/{tag}_b.json',
                                     '--data', f'{D}/番茄_data.json',
                                     '--out', f'{B}/{tag}_d.json'])),
        ('⑤预测+绘图', sc(script, ['predict', '--model', f'{B}/{tag}_c.json',
                                  '--data', f'{D}/金线莲_data.json',
                                  '--weeks', '6', '--plot', f'{B}/{tag}_c.png'])),
    ]


engs = [('纯Python', 'pure', PURE), ('numpy版', 'np', NEW)]
best = {}
order = [c[0] for c in cases('x', PURE)]
for rnd in range(1, ROUNDS + 1):
    for i, name in enumerate(order):
        for label, tag, script in engs:
            rc, cpu, wall = run(cases(tag, script)[i][1])
            key = (name, label)
            if key not in best or cpu < best[key][0]:
                best[key] = (cpu, wall, rc)
        p = best.get((name, '纯Python'))
        n = best.get((name, 'numpy版'))
        print(f'  第{rnd}轮 {name}: 纯={p[0]:.2f}s numpy={n[0]:.2f}s', file=sys.stderr)

print()
print(f"{'场景':<24}{'纯Python':>11}{'numpy版':>11}{'加速比':>9}")
print('-' * 57)
tp = tn = 0.0
for name in order:
    p, pw, prc = best[(name, '纯Python')]
    n, nw, nrc = best[(name, 'numpy版')]
    tp += p
    tn += n
    flag = '' if (prc == 0 and nrc == 0) else f'  rc={prc}/{nrc}'
    print(f"{name:<24}{p:>9.2f}s{n:>9.2f}s{p / n:>8.1f}x{flag}")
print('-' * 57)
print(f"{'合计 (CPU 时间)':<22}{tp:>9.2f}s{tn:>9.2f}s{tp / tn:>8.1f}x")
