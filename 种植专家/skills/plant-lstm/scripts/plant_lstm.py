# -*- coding: utf-8 -*-
import sys
import os
import re
import json
import math
import random
import argparse

try:
    import numpy as np
except ImportError:
    sys.stderr.write(
        "本脚本的矩阵运算依赖 numpy，当前 Python 环境未安装。\n"
        "  安装：pip3 install numpy\n"
        "  或改用纯 Python 版本：scripts/backup/plant_lstm_pure_*.py（接口相同）\n"
    )
    raise SystemExit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LIBRARY = os.path.join(os.path.dirname(SCRIPT_DIR), "植物生长模型参数库.md")

EPS = 1e-15


# --- 标量版本：numpy 版内部已改用下面的向量化版本，这里保留以兼容外部 import 调用 ---
def sigmoid(x):
    if x < -30:
        return 0.0
    if x > 30:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_deriv(y):
    return max(y * (1.0 - y), EPS)


def tanh(x):
    return math.tanh(x)


def tanh_deriv(y):
    return max(1.0 - y * y, EPS)


# --- 向量化版本（与上面的标量版数学一致，只是作用在 numpy 数组上） ---
def sigmoid_arr(x):
    """批量 sigmoid。截断到 ±30，与标量 sigmoid 的数值行为一致。

    这里用 minimum/maximum 而不是 np.clip：np.clip 会走 _clip_dep_is_scalar_nan
    等一堆 Python 层检查，对小数组来说开销远大于计算本身。
    """
    return 1.0 / (1.0 + np.exp(-np.minimum(np.maximum(x, -30.0), 30.0)))


def sigmoid_deriv_arr(y):
    return np.maximum(y * (1.0 - y), EPS)


def tanh_deriv_arr(y):
    return np.maximum(1.0 - y * y, EPS)


def _as_list(a):
    """numpy 数组 -> 纯 Python 列表，保证模型 JSON 格式与纯 Python 版完全一致。"""
    return a.tolist() if isinstance(a, np.ndarray) else a


def vec_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]


def vec_mul(a, b):
    return [a[i] * b[i] for i in range(len(a))]


def zeros(n):
    return [0.0] * n


def normalize(val, lo, hi):
    if hi <= lo:
        return 0.5
    return max(0.0, min(1.0, (float(val) - lo) / (hi - lo)))


def denormalize(val, lo, hi):
    return val * (hi - lo) + lo


def spec_to_vec(d, specs):
    out = []
    for s in specs:
        lo, hi = s["min"], s["max"]
        v = d.get(s["key"], (lo + hi) * 0.5)
        out.append(normalize(v, lo, hi))
    return out


def vec_to_spec(vec, specs):
    out = {}
    for i, s in enumerate(specs):
        v = max(0.0, min(1.0, vec[i]))
        out[s["key"]] = round(denormalize(v, s["min"], s["max"]), 4)
    return out


class LSTMCell:
    def __init__(self, input_dim, hidden_dim):
        self.inp = input_dim
        self.hid = hidden_dim
        cdim = input_dim + hidden_dim

        def rnd(r, c):
            # 保持与纯 Python 版完全一致的 random.gauss 调用顺序，保证同种子结果可复现；
            # 只是把结果装进 numpy 数组。
            return np.array([[random.gauss(0, 0.08) for _ in range(c)] for _ in range(r)], dtype=float)

        self.wf = rnd(hidden_dim, cdim)
        self.wi = rnd(hidden_dim, cdim)
        self.wc = rnd(hidden_dim, cdim)
        self.wo = rnd(hidden_dim, cdim)
        self.bf = np.zeros(hidden_dim)
        self.bi = np.zeros(hidden_dim)
        self.bc = np.zeros(hidden_dim)
        self.bo = np.zeros(hidden_dim)
        self.h = None
        self.c = None

    def reset(self):
        self.h = None
        self.c = None

    def forward(self, x):
        if self.h is None:
            self.h = np.zeros(self.hid)
            self.c = np.zeros(self.hid)
        cat = np.concatenate((self.h, np.asarray(x, dtype=float)))
        n = cat.shape[0]
        wf, wi, wc, wo = self.wf, self.wi, self.wc, self.wo
        if wf.shape[1] != n:
            # 与纯 Python 版的逐项求和 range(len(cat)) 行为保持一致：
            # 权重列数多于输入时，多余的列不参与计算（多层模型 expand_last 后会出现这种状态）。
            wf, wi, wc, wo = wf[:, :n], wi[:, :n], wc[:, :n], wo[:, :n]
        f = sigmoid_arr(wf @ cat + self.bf)
        i = sigmoid_arr(wi @ cat + self.bi)
        ct = np.tanh(wc @ cat + self.bc)
        o = sigmoid_arr(wo @ cat + self.bo)
        self.c = f * self.c + i * ct
        self.h = o * np.tanh(self.c)
        return self.h

    def total_params(self):
        n = 0
        for w in [self.wf, self.wi, self.wc, self.wo]:
            n += int(w.size)
        n += len(self.bf) * 4
        return n


class DynamicLSTM:
    def __init__(self, input_dim):
        self.input_dim = input_dim
        self.cells = []

    def add_cell(self, hidden_dim):
        prev = self.input_dim if not self.cells else self.cells[-1].hid
        self.cells.append(LSTMCell(prev, hidden_dim))

    def expand_last(self, extra=6):
        if not self.cells:
            return
        c = self.cells[-1]
        old = c.hid
        new_h = old + extra
        new_cdim = c.inp + new_h
        for attr in ["wf", "wi", "wc", "wo"]:
            w = getattr(c, attr)
            # 先按原顺序生成新增行的随机数，再做矩阵拼接
            new_rows = np.array(
                [[random.gauss(0, 0.08) for _ in range(new_cdim)] for _ in range(extra)], dtype=float)
            setattr(c, attr, np.vstack([np.hstack([w, np.zeros((old, extra))]), new_rows]))
        for attr in ["bf", "bi", "bc", "bo"]:
            setattr(c, attr, np.concatenate((getattr(c, attr), np.zeros(extra))))
        c.hid = new_h
        for higher in self.cells[1:]:
            inc = extra
            old_in = higher.inp
            higher.inp = old_in + inc
            for attr in ["wf", "wi", "wc", "wo"]:
                w = getattr(higher, attr)
                block = np.array(
                    [[random.gauss(0, 0.01) for _ in range(inc)] for _ in range(len(w))], dtype=float)
                setattr(higher, attr, np.hstack([w[:, :old_in], block, w[:, old_in:]]))

    def prune_weak(self, thresh=0.005, min_hidden=12):
        if not self.cells:
            return
        c = self.cells[-1]
        dim = c.hid
        mx = np.zeros(dim)
        for attr in ["wf", "wi", "wc", "wo"]:
            mx = np.maximum(mx, np.abs(getattr(c, attr)).max(axis=1))
        for attr in ["bf", "bi", "bc", "bo"]:
            mx = np.maximum(mx, np.abs(getattr(c, attr)))
        kept = [j for j in range(dim) if mx[j] >= thresh]
        if len(kept) == dim or len(kept) < min_hidden:
            return
        new_h = len(kept)
        for attr in ["wf", "wi", "wc", "wo"]:
            w = getattr(c, attr)
            # 行、列都要按 kept 筛选：前 inp 列为输入部分，其后为隐藏部分
            setattr(c, attr, np.hstack([w[:, :c.inp], w[:, c.inp:][:, kept]])[kept])
        for attr in ["bf", "bi", "bc", "bo"]:
            setattr(c, attr, getattr(c, attr)[kept])
        c.hid = new_h

    def reset(self):
        for c in self.cells:
            c.reset()

    def forward_seq(self, seq):
        self.reset()
        h = None
        for x in seq:
            h = x
            for c in self.cells:
                h = c.forward(h)
        return h

    def config(self):
        return [c.hid for c in self.cells]


class PlantLSTM:
    def __init__(self, features, outputs, layers=None, fc_dim=24, lr=0.05, adaptive=True,
                 min_layers=1, max_layers=3, min_hidden=12, max_hidden=48,
                 window=4, forget=0.95, global_keep=0.98):
        self.features = features
        self.outputs = outputs
        self.input_dim = len(features)
        self.output_dim = len(outputs)
        self.growth_count = len([o for o in outputs if o.get("group") != "component"])
        self.lr = lr
        self.adaptive = adaptive
        self.fc_dim = fc_dim
        self.min_layers = min_layers
        self.max_layers = max_layers
        self.min_hidden = min_hidden
        self.max_hidden = max_hidden
        self.window = window
        self.forget = forget
        self.global_keep = global_keep
        self.season_pairs = []

        layers = layers or [12]
        self.lstm = DynamicLSTM(self.input_dim)
        for hid in layers:
            self.lstm.add_cell(hid)
        self._init_head()

        self.i = 1
        self.week = 0
        self.buf = []
        self.losses = []
        self.no_improve = 0

    def _last_hid(self):
        return self.lstm.cells[-1].hid if self.lstm.cells else 12

    def _init_head(self):
        last_hid = self._last_hid()
        self.wfc = np.array(
            [[random.gauss(0, 0.08) for _ in range(last_hid + 1)] for _ in range(self.fc_dim)], dtype=float)
        self.wout = np.array(
            [[random.gauss(0, 0.08) for _ in range(self.fc_dim + 1)] for _ in range(self.output_dim)], dtype=float)

    def forward(self, seq):
        h = self.lstm.forward_seq(seq)
        fc_in = np.concatenate((np.asarray(h, dtype=float), [1.0]))
        zfc = np.tanh(self.wfc @ fc_in)
        out_in = np.concatenate((zfc, [1.0]))
        zout = sigmoid_arr(self.wout @ out_in)
        self._zfc = zfc
        self._fc_in = fc_in
        return [float(v) for v in zout]

    def train_one(self, seq, target, sample_weight=1.0):
        pred = np.asarray(self.forward(seq), dtype=float)
        tgt = np.asarray(target, dtype=float)
        fc_in = self._fc_in
        zfc = self._zfc
        out_in = np.concatenate((zfc, [1.0]))
        lr = self.lr * sample_weight
        delta_o = (pred - tgt) * sigmoid_deriv_arr(pred)
        self.wout -= lr * np.outer(delta_o, out_in)
        # 与原实现一致：先用新的 wout 反传，再更新 wfc
        delta_f = tanh_deriv_arr(zfc) * (self.wout[:, :self.fc_dim].T @ delta_o)
        self.wfc -= lr * np.outer(delta_f, fc_in)
        d = pred - tgt
        loss_growth = float((d[:self.growth_count] ** 2).sum())
        loss_comp = float((d[self.growth_count:] ** 2).sum())
        return loss_growth, loss_comp

    def incremental_learn(self, record, window=None):
        window = window or self.window
        v = spec_to_vec(record, self.features)
        self.buf.append(v)
        if len(self.buf) > window:
            self.buf.pop(0)
        self.week += 1
        out_keys = [o["key"] for o in self.outputs]
        if len(self.buf) < window or not all(k in record for k in out_keys):
            return False, None, None
        tgt = spec_to_vec(record, self.outputs)
        self.season_pairs.append((list(self.buf), tgt, self.week))
        lg = lc = 0.0
        season_scale = self.global_keep ** max(0, self.i - 1)
        recent = self.season_pairs[-max(1, window):]
        n = len(recent)
        for idx, (seq, t, wk) in enumerate(recent):
            age = n - 1 - idx
            w = (self.forget ** age) * season_scale
            a, b = self.train_one(seq, t, w)
            lg += a
            lc += b
        lg /= n
        lc /= n
        self.adapt(lg, lc)
        return True, lg, lc

    def predict(self, seq):
        return self.forward(seq)

    def predict_future(self, recent, env_plan=None, n_weeks=4):
        seq = [list(x) for x in recent]
        if not seq:
            return []
        last_env = list(seq[-1])
        out = []
        for step in range(n_weeks):
            if env_plan and step < len(env_plan):
                nxt_env = env_plan[step]
            else:
                nxt_env = last_env
            pred = self.forward(seq)
            out.append(list(pred))
            seq.pop(0)
            seq.append(nxt_env)
        return out

    def adapt(self, loss_growth, loss_comp):
        loss_total = loss_growth + loss_comp
        self.losses.append(loss_total)
        if not self.adaptive:
            return
        if len(self.losses) >= 3:
            recent = self.losses[-3:]
            if recent[0] <= recent[1] <= recent[2]:
                self.no_improve += 1
            else:
                self.no_improve = 0
        residual_high = loss_comp > 0.15 or loss_growth > 0.10
        if self.no_improve >= 3 and residual_high:
            if len(self.lstm.cells) < self.max_layers:
                new_dim = min(self._last_hid() + 6, self.max_hidden)
                self.lstm.add_cell(new_dim)
                self._init_head()
                self.no_improve = 0
            elif self._last_hid() < self.max_hidden:
                self.lstm.expand_last(6)
                self._init_head()
                self.no_improve = 0
        if len(self.losses) >= 5 and loss_total < 0.01:
            self.lstm.prune_weak(0.005, self.min_hidden)
            self._init_head()

    def summary(self):
        return {
            "plant": getattr(self, "plant", None),
            "structure": {"input_dim": self.input_dim, "lstm_layers": self.lstm.config(),
                          "fc_dim": self.fc_dim, "output_dim": self.output_dim},
            "growth_outputs": self.growth_count,
            "losses_last": round(self.losses[-1], 6) if self.losses else None,
            "total_params": (sum(c.total_params() for c in self.lstm.cells)
                             + sum(len(r) for r in self.wfc) + sum(len(r) for r in self.wout)),
        }

    def save(self, path):
        s = {
            "plant": getattr(self, "plant", None),
            "features": self.features,
            "outputs": self.outputs,
            "config": {
                "layers": self.lstm.config(), "fc_dim": self.fc_dim, "lr": self.lr,
                "adaptive": self.adaptive, "min_layers": self.min_layers, "max_layers": self.max_layers,
                "min_hidden": self.min_hidden, "max_hidden": self.max_hidden, "window": self.window,
            },
            "season": self.i, "week": self.week, "forget": self.forget, "global_keep": self.global_keep,
            "losses": self.losses, "no_improve": self.no_improve, "buf": self.buf,
            "season_pairs": self.season_pairs,
            "wfc": _as_list(self.wfc), "wout": _as_list(self.wout),
            "cells": [{"inp": c.inp, "hid": c.hid,
                       "wf": _as_list(c.wf), "wi": _as_list(c.wi), "wc": _as_list(c.wc), "wo": _as_list(c.wo),
                       "bf": _as_list(c.bf), "bi": _as_list(c.bi), "bc": _as_list(c.bc), "bo": _as_list(c.bo)}
                      for c in self.lstm.cells],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
        cfg = s.get("config", {})
        m = cls(s["features"], s["outputs"], layers=cfg.get("layers"),
                fc_dim=cfg.get("fc_dim", 24), lr=cfg.get("lr", 0.05),
                adaptive=cfg.get("adaptive", True),
                min_layers=cfg.get("min_layers", 1), max_layers=cfg.get("max_layers", 3),
                min_hidden=cfg.get("min_hidden", 12), max_hidden=cfg.get("max_hidden", 48),
                window=cfg.get("window", 4), forget=s.get("forget", 0.95), global_keep=s.get("global_keep", 0.98))
        m.plant = s.get("plant")
        m.i = s.get("season", 1)
        m.week = s.get("week", 0)
        m.forget = s.get("forget", 0.95)
        m.global_keep = s.get("global_keep", 0.98)
        m.losses = s.get("losses", [])
        m.no_improve = s.get("no_improve", 0)
        m.buf = s.get("buf", [])
        m.season_pairs = s.get("season_pairs", [])
        m.wfc = np.array(s["wfc"], dtype=float)
        m.wout = np.array(s["wout"], dtype=float)
        m.lstm.cells = []
        for cd in s["cells"]:
            c = LSTMCell(cd["inp"], cd["hid"])
            c.wf = np.array(cd["wf"], dtype=float)
            c.wi = np.array(cd["wi"], dtype=float)
            c.wc = np.array(cd["wc"], dtype=float)
            c.wo = np.array(cd["wo"], dtype=float)
            c.bf = np.array(cd["bf"], dtype=float)
            c.bi = np.array(cd["bi"], dtype=float)
            c.bc = np.array(cd["bc"], dtype=float)
            c.bo = np.array(cd["bo"], dtype=float)
            m.lstm.cells.append(c)
        return m


def parse_md_json_blocks(text):
    blocks = []
    for m in re.finditer(r"```json\s*(.*?)```", text, re.S | re.I):
        raw = m.group(1).strip()
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return blocks


def extract_series(obj):
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return obj
    if isinstance(obj, dict):
        for k in ("series", "history", "data", "records", "weeks"):
            v = obj.get(k)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return None


def parse_md_table(text, keys=None):
    rows = []
    lines = text.splitlines()
    header = None
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if "|" in ln and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            cells_next = [c.strip() for c in nxt.strip("|").split("|")]
            if "|" in nxt and cells_next and all(set(c) <= set("-: ") and c for c in cells_next):
                header = [c.strip().lower().replace(" ", "_") for c in ln.strip("|").split("|")]
                i += 2
                continue
        if header and "|" in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) == len(header):
                d = {}
                ok = False
                for h, c in zip(header, cells):
                    try:
                        d[h] = float(c)
                        ok = True
                    except ValueError:
                        d[h] = c
                if ok:
                    rows.append(d)
        i += 1
    return rows or None


def load_series(path):
    if path is None:
        text = sys.stdin.read()
        src = "stdin"
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        src = path
    if path and path.endswith(".json"):
        return extract_series(json.loads(text)), src
    for b in parse_md_json_blocks(text):
        s = extract_series(b)
        if s:
            return s, src
    return parse_md_table(text), src


def load_library(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    plants = []
    for b in parse_md_json_blocks(text):
        if isinstance(b, dict) and b.get("plant") and b.get("features") and b.get("outputs"):
            plants.append(b)
    return plants


def resolve_config(args):
    if getattr(args, "config", None):
        with open(args.config, encoding="utf-8") as f:
            return json.load(f)
    lib = load_library(args.library)
    if not getattr(args, "plant", None):
        names = ", ".join(p["plant"] for p in plants_names(lib))
        raise SystemExit("请指定 --plant，可选: " + names)
    for p in lib:
        if p["plant"] == args.plant:
            return p
    raise SystemExit("参数库中未找到植物: {}（可选: {}）".format(
        args.plant, ", ".join(p["plant"] for p in lib)))


def plants_names(lib):
    return lib


def build_model(cfg, args):
    features = cfg["features"]
    outputs = cfg["outputs"]
    net = cfg.get("network", {})
    train = cfg.get("training", {})
    layers = list(net.get("layers") or [net.get("hidden_dim", 12)])
    if getattr(args, "layers", None):
        layers = [int(x) for x in re.split(r"[, ]+", args.layers) if x.strip()]
    fc_dim = getattr(args, "fc_dim", None) or net.get("fc_dim", 24)
    lr = getattr(args, "lr", None)
    lr = lr if lr is not None else net.get("lr", 0.05)
    adaptive = net.get("adaptive", True)
    if getattr(args, "adaptive", None) is not None:
        adaptive = args.adaptive
    window = getattr(args, "window", None) or train.get("window", 4)
    forget = getattr(args, "forget", None)
    forget = forget if forget is not None else train.get("forget", 0.95)
    gkeep = getattr(args, "global_keep", None)
    gkeep = gkeep if gkeep is not None else train.get("global_keep", 0.98)
    m = PlantLSTM(features, outputs, layers=layers, fc_dim=fc_dim, lr=lr, adaptive=adaptive,
                  min_layers=net.get("min_layers", 1), max_layers=net.get("max_layers", 3),
                  min_hidden=net.get("min_hidden", 12), max_hidden=net.get("max_hidden", 48),
                  window=window, forget=forget, global_keep=gkeep)
    m.plant = cfg.get("plant")
    return m, cfg, train


def cmd_list(args):
    lib = load_library(args.library)
    if not lib:
        print(json.dumps({"error": "参数库中未找到任何植物配置", "library": args.library}, ensure_ascii=False))
        return
    out = [{"plant": p["plant"], "features": len(p["features"]), "outputs": len(p["outputs"]),
            "description": p.get("description", "")} for p in lib]
    print(json.dumps({"library": args.library, "plants": out}, ensure_ascii=False, indent=2))


def cmd_config(args):
    cfg = resolve_config(args)
    print(json.dumps(cfg, ensure_ascii=False, indent=2))


def cmd_gen_data(args):
    cfg = resolve_config(args)
    n = args.weeks
    series = []
    for w in range(n):
        row = {}
        for s in cfg["features"]:
            row[s["key"]] = round(random.uniform(s["min"], s["max"]), 3)
        for s in cfg["outputs"]:
            row[s["key"]] = round(random.uniform(s["min"], s["max"]), 3)
        series.append(row)
    out = args.out or "{}_data.json".format(cfg["plant"])
    with open(out, "w", encoding="utf-8") as f:
        json.dump(series, f, ensure_ascii=False, indent=2)
    print(json.dumps({"success": True, "plant": cfg["plant"], "weeks": n, "output": os.path.abspath(out)},
                     ensure_ascii=False))


def cmd_train(args):
    cfg = resolve_config(args)
    series, src = load_series(args.data)
    if not series:
        print(json.dumps({"error": "未能读取到训练数据", "source": src}, ensure_ascii=False))
        sys.exit(1)
    model, cfg, train = build_model(cfg, args)
    window = args.window or train.get("window", 4)
    epochs = args.epochs or train.get("epochs", 100)
    shuffle = args.shuffle if args.shuffle is not None else train.get("shuffle", True)
    sample_weight = args.sample_weight if args.sample_weight is not None else train.get("sample_weight", 1.0)
    if len(series) < window + 1:
        print(json.dumps({"error": "数据不足，至少需要 {} 周".format(window + 1)}, ensure_ascii=False))
        sys.exit(1)
    pairs = []
    for i in range(window, len(series)):
        seq = [spec_to_vec(series[i - window + k], cfg["features"]) for k in range(window)]
        tgt = spec_to_vec(series[i], cfg["outputs"])
        pairs.append((seq, tgt))
    print("植物: {}  数据: {} 周  样本: {}  可调结构: {}".format(
        cfg["plant"], len(series), len(pairs), model.adaptive))
    print("初始结构: {}  lr={}  epochs={}  window={}".format(
        model.lstm.config(), model.lr, epochs, window))
    for ep in range(epochs):
        if shuffle:
            random.shuffle(pairs)
        tg = tc = 0.0
        for seq, tgt in pairs:
            lg, lc = model.train_one(seq, tgt, sample_weight)
            tg += lg
            tc += lc
        avg_g, avg_c = tg / len(pairs), tc / len(pairs)
        model.adapt(avg_g, avg_c)
        if (ep + 1) % max(1, epochs // 10) == 0 or ep == 0:
            print("  周期 {}/{}  growth_loss={:.6f}  comp_loss={:.6f}  结构={}".format(
                ep + 1, epochs, avg_g, avg_c, model.lstm.config()))
    model.week = len(series)
    model.buf = [spec_to_vec(series[-window + k], cfg["features"]) for k in range(window)] if window else []
    out = args.model or "{}_model.json".format(cfg["plant"])
    model.save(out)
    print("\n模型已保存: {}".format(os.path.abspath(out)))
    print("最终结构: {}".format(model.summary()["structure"]))
    print("总参数量: {}".format(model.summary()["total_params"]))


def snapshot_name(plant, season):
    return "{}LSTM模型-第{}季快照.json".format(plant or "植物", season)


def cmd_new_season(args):
    model = PlantLSTM.load(args.model)
    model.i += 1
    model.week = 0
    model.buf = []
    model.season_pairs = []
    out = args.out or snapshot_name(model.plant, model.i)
    model.save(out)
    print(json.dumps({"success": True, "plant": model.plant, "season": model.i,
                      "structure": model.lstm.config(), "output": os.path.abspath(out)},
                     ensure_ascii=False))


def cmd_incremental(args):
    model = PlantLSTM.load(args.model)
    if args.new_season:
        model.i += 1
        model.week = 0
        model.buf = []
        model.season_pairs = []
        print("进入第{}季：继承上一季网络结构与权重，清空本季时序缓冲".format(model.i))
    if args.forget is not None:
        model.forget = args.forget
    if args.global_keep is not None:
        model.global_keep = args.global_keep
    series, src = load_series(args.data)
    if not series:
        print(json.dumps({"error": "未读取到周度增量数据"}, ensure_ascii=False))
        sys.exit(1)
    window = args.window or model.window
    trained = 0
    for rec in series:
        ok, lg, lc = model.incremental_learn(rec, window=window)
        if ok:
            trained += 1
            print("  第{}周: 增量训练完成 growth_loss={:.6f} comp_loss={:.6f} 结构={}".format(
                model.week, lg, lc, model.lstm.config()))
        else:
            print("  第{}周: 已缓存（需{}周窗口+完整输出）".format(model.week, window))
    out = args.out or snapshot_name(model.plant, model.i)
    model.save(out)
    print("\n第{}季模型已保存: {}（窗口{}周，本季已训练{}周，遗忘λ={} 跨季保留={}）".format(
        model.i, os.path.abspath(out), window, trained, model.forget, model.global_keep))


def cmd_predict(args):
    model = PlantLSTM.load(args.model)
    cfg = {"plant": model.plant, "features": model.features, "outputs": model.outputs}
    series, src = load_series(args.data if args.data else None)
    if not series:
        print(json.dumps({"error": "未能读取到预测输入数据"}, ensure_ascii=False))
        sys.exit(1)
    window = args.window or 4
    recent = [spec_to_vec(r, model.features) for r in series[-window:]]
    env_plan = None
    if args.future:
        fut, _ = load_series(args.future)
        env_plan = [spec_to_vec(r, model.features) for r in fut]
    preds = model.predict_future(recent, env_plan=env_plan, n_weeks=args.weeks)
    out = [vec_to_spec(p, model.outputs) for p in preds]
    print(json.dumps({"plant": model.plant, "weeks_ahead": args.weeks, "predictions": out},
                     ensure_ascii=False, indent=2))
    if args.plot:
        save_plot(model, out, args.plot)


def _setup_plot_rc():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def save_plot(model, pred_series, path, title=None):
    plt = _setup_plot_rc()
    groups = []
    seen = set()
    for s in model.outputs:
        g = s.get("group", "growth")
        if g not in seen:
            seen.add(g)
            groups.append(g)
    n = len(groups)
    fig, axes = plt.subplots(n, 1, figsize=(10, 3 * n), squeeze=False)
    weeks = list(range(1, len(pred_series) + 1))
    for gi, g in enumerate(groups):
        ax = axes[gi][0]
        for s in model.outputs:
            if s.get("group", "growth") != g:
                continue
            vals = [row[s["key"]] for row in pred_series]
            ax.plot(weeks, vals, "o-", label="{} ({})".format(s.get("cn", s["key"]), s.get("unit", "")), markersize=4)
        ax.set_title("{} - {} 预测 (未来{}周)".format(model.plant or "", g, len(pred_series)))
        ax.set_xlabel("周")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("预测图已保存: {}".format(os.path.abspath(path)))


def cmd_plot(args):
    model = PlantLSTM.load(args.model)
    pred_series = []
    if args.data:
        series, _ = load_series(args.data)
        window = args.window or 4
        recent = [spec_to_vec(r, model.features) for r in series[-window:]]
        preds = model.predict_future(recent, n_weeks=args.weeks)
        pred_series = [vec_to_spec(p, model.outputs) for p in preds]
    else:
        if len(model.losses) < 2:
            print(json.dumps({"error": "无预测数据且损失记录不足，无法绘图"}, ensure_ascii=False))
            sys.exit(1)
        plt = _setup_plot_rc()
        out = args.out or "{}_loss.png".format(model.plant or "plant")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(1, len(model.losses) + 1), model.losses, "b-o", markersize=3)
        ax.set_title("{} 训练损失收敛曲线".format(model.plant or ""))
        ax.set_xlabel("训练周期")
        ax.set_ylabel("Loss")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print("损失曲线已保存: {}".format(os.path.abspath(out)))
        return
    out = args.out or "{}_prediction.png".format(model.plant or "plant")
    save_plot(model, pred_series, out)


def main():
    p = argparse.ArgumentParser(description="通用植物生长LSTM模型（可配置结构/参数/训练/预测）")
    p.add_argument("--library", default=DEFAULT_LIBRARY, help="植物生长模型参数库.md 路径")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("list", help="列出参数库中的植物")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("config", help="输出指定植物的完整参数配置")
    sp.add_argument("--plant")
    sp.add_argument("--config", help="直接指定配置文件")
    sp.set_defaults(func=cmd_config)

    sp = sub.add_parser("gen_data", help="按参数范围生成模拟训练数据")
    sp.add_argument("--plant")
    sp.add_argument("--config")
    sp.add_argument("--weeks", type=int, default=30)
    sp.add_argument("--out")
    sp.set_defaults(func=cmd_gen_data)

    sp = sub.add_parser("train", help="训练或续训模型")
    sp.add_argument("--plant")
    sp.add_argument("--config")
    sp.add_argument("--data", required=True, help="训练数据 json 或 md")
    sp.add_argument("--model", help="模型输出路径")
    sp.add_argument("--epochs", type=int)
    sp.add_argument("--window", type=int)
    sp.add_argument("--layers", help="自定义每层神经元，如 12,16")
    sp.add_argument("--fc-dim", type=int, dest="fc_dim")
    sp.add_argument("--lr", type=float)
    sp.add_argument("--adaptive", type=lambda x: str(x).lower() in ("1", "true", "yes", "y"))
    sp.add_argument("--shuffle", type=lambda x: str(x).lower() in ("1", "true", "yes", "y"))
    sp.add_argument("--sample-weight", type=float, dest="sample_weight")
    sp.add_argument("--forget", type=float)
    sp.add_argument("--global-keep", type=float, dest="global_keep")
    sp.set_defaults(func=cmd_train)

    sp = sub.add_parser("incremental", help="在线增量学习（每周新增样本微调，可跨季续训）")
    sp.add_argument("--model", required=True)
    sp.add_argument("--data", help="周度数据 json 或 md（省略则读 stdin）")
    sp.add_argument("--new-season", action="store_true", dest="new_season", help="开启新一季并继承上一季模型")
    sp.add_argument("--window", type=int)
    sp.add_argument("--forget", type=float)
    sp.add_argument("--global-keep", type=float, dest="global_keep")
    sp.add_argument("--out", help="模型输出路径（默认第N季快照）")
    sp.set_defaults(func=cmd_incremental)

    sp = sub.add_parser("new_season", help="季末归档并开启新一季（跨季迭代继承）")
    sp.add_argument("--model", required=True)
    sp.add_argument("--out", help="新季快照输出路径")
    sp.set_defaults(func=cmd_new_season)

    sp = sub.add_parser("predict", help="预测未来若干周")
    sp.add_argument("--model", required=True)
    sp.add_argument("--data", help="最近监测数据 json 或 md（省略则读 stdin）")
    sp.add_argument("--future", help="未来环境计划 json 或 md（可选）")
    sp.add_argument("--weeks", type=int, default=12)
    sp.add_argument("--window", type=int)
    sp.add_argument("--plot", help="预测图输出路径")
    sp.set_defaults(func=cmd_predict)

    sp = sub.add_parser("plot", help="绘制预测图或损失曲线")
    sp.add_argument("--model", required=True)
    sp.add_argument("--data", help="预测输入数据（省略则画损失曲线）")
    sp.add_argument("--weeks", type=int, default=12)
    sp.add_argument("--window", type=int)
    sp.add_argument("--out")
    sp.set_defaults(func=cmd_plot)

    args = p.parse_args()
    if getattr(args, "adaptive", None) is not None and hasattr(args, "func"):
        pass
    args.func(args)


if __name__ == "__main__":
    main()
