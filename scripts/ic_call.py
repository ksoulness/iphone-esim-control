#!/usr/bin/env python3
"""调用 iphone-control MCP（stdio）执行一个工具，打印纯文本结果。
用法: python3 ic_call.py <tool> '<json-args>'
"""
import json, os, subprocess, sys

tool = sys.argv[1]
args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
binary = os.path.expanduser("~/.cargo/bin/iphone-control")

init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "dsh", "version": "1"}}}
inited = {"jsonrpc": "2.0", "method": "notifications/initialized"}
call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool, "arguments": args}}

payload = "\n".join(json.dumps(x) for x in (init, inited, call)) + "\n"
p = subprocess.run([binary, "mcp"], input=payload, capture_output=True, text=True, timeout=180)
out = p.stdout.strip().splitlines()
last = None
for line in out:
    try:
        msg = json.loads(line)
    except Exception:
        continue
    if msg.get("id") == 2:
        last = msg
if last is None:
    print("NO_RESULT")
    print(p.stdout[-2000:])
    print(p.stderr[-2000:])
    sys.exit(1)

res = last.get("result", {})
for c in res.get("content", []):
    if c.get("type") == "text":
        print(c["text"])
    elif c.get("type") == "image":
        data = c.get("data", "")
        path = os.path.expanduser("~/ic_shot_%d.bin" % (len(data)))
        with open(path, "wb") as f:
            f.write(__import__("base64").b64decode(data))
        print("IMAGE saved %s (%s %s bytes)" % (path, c.get("mimeType"), len(data)))
if last.get("error"):
    print("ERROR", json.dumps(last["error"], ensure_ascii=False))
