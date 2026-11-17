#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在单个 MCP 会话里批量删除捷径：python3 ic_del.py 名字1 名字2 ..."""
import json, os, re, subprocess, sys, time

binary = os.path.expanduser("~/.cargo/bin/iphone-control")
p = subprocess.Popen([binary, "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL, text=True, bufsize=1)
_id = 0

def rpc(method, params):
    global _id
    _id += 1
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": params}) + "\n")
    p.stdin.flush()
    while True:
        line = p.stdout.readline()
        if not line:
            return None
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if msg.get("id") == _id:
            return msg

def call(tool, args=None):
    m = rpc("tools/call", {"name": tool, "arguments": args or {}})
    if not m:
        return ""
    res = m.get("result") or {}
    out = []
    for c in res.get("content") or []:
        if c.get("type") == "text":
            out.append(c["text"])
    return "\n".join(out)

rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "dsh", "version": "1"}})
p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
p.stdin.flush()

POS = re.compile(r"@\((-?\d+),(-?\d+)\)")

def find(label, kind=None):
    txt = call("iphone_list_elements", {"limit": 80})
    for line in txt.splitlines():
        if kind and not line.strip().startswith(kind):
            continue
        if label and label not in line:
            continue
        m = POS.search(line)
        if m:
            return (int(m.group(1)), int(m.group(2)))
    return None

def tap(x, y):
    call("iphone_tap", {"x": x, "y": y})

targets = sys.argv[1:]
print("targets:", targets)
for name in targets:
    ok = False
    for attempt in range(4):
        pos = find(name + ",", "Cell")
        if not pos:
            call("iphone_swipe", {"from_x": 188, "from_y": 560, "to_x": 188, "to_y": 240})
            time.sleep(1.2)
            continue
        call("iphone_long_press", {"x": pos[0], "y": pos[1]})
        time.sleep(1.6)
        if find("移动"):
            # 打开了「移动」说明没删对按钮，先按返回逻辑：点空白取消
            pass
        delpos = find("删除", "Button")
        if not delpos:
            print(name, "no delete menu; abort item")
            call("iphone_press_button", {"button": "home"}) if False else None
            continue
        tap(*delpos)
        time.sleep(1.4)
        conf = find("删除快捷指令", "Button")
        if not conf:
            print(name, "no confirm; skip")
            continue
        tap(*conf)
        time.sleep(1.6)
        left = find(name + ",", "Cell")
        if not left:
            print("DELETED", name)
            ok = True
            break
        print(name, "still present, retry", attempt + 1)
    if not ok:
        print("FAILED", name)
print("done")
