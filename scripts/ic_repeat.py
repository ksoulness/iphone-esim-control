import json,subprocess,sys
tool=sys.argv[1]; args=json.loads(sys.argv[2]); n=int(sys.argv[3])
p=subprocess.Popen(["iphone-control","mcp"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
def send(o):
    p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
def recv():
    while True:
        ln=p.stdout.readline()
        if not ln: return None
        try:
            d=json.loads(ln)
        except Exception:
            continue
        if d.get("id"): return d
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"rep","version":"1"}}})
recv()
send({"jsonrpc":"2.0","method":"notifications/initialized"})
for i in range(n):
    send({"jsonrpc":"2.0","id":100+i,"method":"tools/call","params":{"name":tool,"arguments":args}})
    r=recv()
    if r is None or "error" in r:
        print("fail at",i,r); break
print("done",n)
