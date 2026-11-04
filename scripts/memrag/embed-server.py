#!/usr/bin/env python3
"""本地嵌入服务（会话记忆向量检索的后端）。

只在本机回环地址上提供两个接口，不联网（模型首次下载后完全离线）：

    GET  /health              -> {"ok": true, "model": ..., "dim": ...}
    POST /embed {"texts":[]}  -> {"model": ..., "dim": ..., "vectors": [[...], ...]}

启动（需要带 sentence-transformers 的解释器，例如 open-webui 的 venv）：

    /home/caiq/open-webui/.venv/bin/python3 ~/MyAgents/scripts/memrag/embed-server.py

可选参数：--model BAAI/bge-small-zh-v1.5  --host 127.0.0.1  --port 8787
"""

import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_NAME = "BAAI/bge-small-zh-v1.5"
_state = {"model": None, "dim": 0}


def get_model(model_name):
    if _state["model"] is None:
        t0 = time.time()
        from sentence_transformers import SentenceTransformer  # 延迟导入，便于 --help

        m = SentenceTransformer(model_name)
        _state["model"] = m
        _state["dim"] = int(m.get_sentence_embedding_dimension())
        print(f"[embed-server] 已加载 {model_name}  dim={_state['dim']}  用时 {time.time()-t0:.1f}s",
              file=sys.stderr, flush=True)
    return _state["model"]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # 更安静的日志
        sys.stderr.write("[embed-server] " + (fmt % args) + "\n")

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/health"):
            self._json(200, {"ok": True, "model": self.server.model_name, "dim": _state["dim"]})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/embed":
            self._json(404, {"error": "not found"})
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(n) or b"{}")
            texts = req.get("texts") or []
            if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
                raise ValueError("texts 必须是字符串数组")
            model = get_model(self.server.model_name)
            vecs = model.encode(texts, normalize_embeddings=True, batch_size=32)
            self._json(200, {
                "model": self.server.model_name,
                "dim": _state["dim"],
                "vectors": [[float(x) for x in v] for v in vecs],
            })
        except Exception as e:  # noqa: BLE001
            self._json(500, {"error": str(e)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=MODEL_NAME)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()

    get_model(args.model)  # 启动即加载，避免首个请求超时
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    srv.model_name = args.model
    print(f"[embed-server] 监听 http://{args.host}:{args.port}  model={args.model}", file=sys.stderr, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
