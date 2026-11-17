#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把线路清单写进服务端（整体替换）。

用法：
    python3 plans_set.py <base_url> <plans.json>

plans.json 形如：
[
  {"name": "CARD_A", "alias": "CARD_A", "number": "+44 7700 900001", "role": "switch"},
  {"name": "CARD_B",  "alias": "CARD_B",  "number": "+852 9000 0001",   "role": "switch"},
  {"name": "US",  "alias": "US",  "number": "+1 (555) 010-0001","role": "always_on"},
  {"name": "DATA_A", "alias": "DATA_A", "role": "data_only"}
]

role 取值：switch（可切换）/ always_on（常驻，不参与切换）/ data_only（纯流量，不参与切换）。
name 必须与手机「设置 → 蜂窝网络」里显示的线路名**完全一致**，否则捷径的「查找蜂窝号码」匹配不到。
"""
import json
import sys
import urllib.parse
import urllib.request


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    base = sys.argv[1].rstrip("/")
    plans = json.load(open(sys.argv[2], encoding="utf-8"))
    data = urllib.parse.quote(json.dumps(plans, ensure_ascii=False))
    url = "%s/phone/plans?data=%s" % (base, urllib.parse.quote(data, safe=""))
    with urllib.request.urlopen(url, timeout=20) as r:
        out = r.read().decode("utf-8", "replace")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
