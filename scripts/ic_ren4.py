#!/usr/bin/env python3
"""改名（实测配方）：long_press → 菜单重命名(a11y) → 点字段(188,196) → 16×删除(325,572) → 输入 → 完成(263,265)"""
import json, os, subprocess, sys, re, time
old, new = sys.argv[1], sys.argv[2]
B = os.path.expanduser("~/.cargo/bin/iphone-control")

def S(calls, timeout=600):
    msgs = [{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"dsh","version":"1"}}},
            {"jsonrpc":"2.0","method":"notifications/initialized"}]
    for i,(t,a) in enumerate(calls):
        msgs.append({"jsonrpc":"2.0","id":100+i,"method":"tools/call","params":{"name":t,"arguments":a}})
    p = subprocess.run([B,"mcp"], input="\n".join(json.dumps(x) for x in msgs)+"\n",
                       capture_output=True, text=True, timeout=timeout)
    out={}
    for line in p.stdout.strip().splitlines():
        try: m=json.loads(line)
        except Exception: continue
        if isinstance(m.get("id"),int) and m["id"]>=100:
            t=""
            for c in m.get("result",{}).get("content",[]):
                if c.get("type")=="text": t+=c["text"]+"\n"
            out[m["id"]-100]=t
    return out

def cells():
    txt = S([("iphone_list_elements",{"limit":80})]).get(0,"")
    return {m.group(1).split(",")[0].strip():(int(m.group(2)),int(m.group(3)))
            for m in re.finditer(r'Cell "([^"]+)" @\((\d+),(\d+)\)', txt)}

def menu_rename(n=6, gap=0.8):
    for _ in range(n):
        txt = S([("iphone_list_elements",{"limit":40})]).get(0,"")
        m = re.search(r'Button "重新命名" @\((\d+),(\d+)\)', txt)
        if m: return (int(m.group(1)),int(m.group(2)))
        time.sleep(gap)
    return None

pos = cells().get(old) or (time.sleep(1) or cells().get(old))
if not pos: print("NOT_FOUND", old); sys.exit(2)
S([("iphone_long_press",{"x":pos[0],"y":pos[1]})])
rp = menu_rename()
if not rp: print("NO_MENU", old); sys.exit(3)
S([("iphone_tap",{"x":rp[0],"y":rp[1]})])
time.sleep(1.5)
S([("iphone_tap",{"x":188,"y":196})] + [("iphone_tap",{"x":349,"y":593})]*16)
S([("iphone_type_text",{"text":new})])
time.sleep(1)
S([("iphone_tap",{"x":263,"y":265})])
time.sleep(2)
print(("OK " if new in cells() else "FAIL ") + old + " -> " + new)
