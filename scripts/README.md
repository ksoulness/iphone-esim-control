# scripts/

配合 [iphone-control](https://github.com/Derrors/iphone-control) 的 MCP 通道使用。全部是**单文件、无第三方依赖**的 Python 3 脚本，跑在**插着 iPhone 的那台机器**上（macOS / Linux）。

| 脚本 | 作用 | 用法 |
| --- | --- | --- |
| `ic_call.py` | 调一次 MCP 工具，打印返回文本；图片类结果落盘并打印路径 | `python3 ic_call.py iphone_status '{}'`<br>`python3 ic_call.py iphone_tap '{"x":188,"y":314}'` |
| `ic_repeat.py` | 同一个 MCP 会话里重复调同一个工具 N 次（连按删除键等） | `python3 ic_repeat.py iphone_tap '{"x":349,"y":593}' 20` |
| `ic_del.py` | 批量删除捷径：按名单逐个长按 → 删除 → 确认 | `python3 ic_del.py zt4 zt5 号码管控` |
| `ic_ren4.py` | 按「长按 → 重新命名 → 清空 → 输入 → 完成」改名，配 a11y 轮询 | `python3 ic_ren4.py 运行快捷指令 查询当前卡自动` |
| `plans_set.py` | 用一份 JSON 整体替换服务端的线路清单（`role` 三态） | `python3 plans_set.py http://127.0.0.1:3105 plans.json` |

## 约定

- 脚本内部都是 **spawn 一次 `iphone-control mcp`**，把 `initialize` / `notifications/initialized` / `tools/call` 三条 JSON-RPC 打进 stdin，然后解析返回的 `content[].text`。所以：
  - 一次调用 = 一个进程 = 一个新的 MCP 会话，**页面/应用的 UI 状态不会保留在脚本里**，但设备状态当然会保留；
  - 连续动作（点一下再读元素）要放在**同一个脚本**里顺序发，或用 `ic_repeat.py` 那种一次性多调的形式。
- 坐标一律是**设备点**（iPhone SE3 是 375×667），`iphone_screenshot` 返回的图片像素即点坐标。
- **优先用 a11y 而不是截图猜坐标**：`iphone_list_elements` 会给出 `Button "..." @(x,y)` 这类真实中心点。
- 绝不调用 `press_button` 的 `lock`——锁屏后没有自动解锁，只能人工上滑。

## 环境变量

脚本默认从 `~/.cargo/bin/iphone-control` 找二进制。换路径时在脚本顶部改 `BIN` 常量，或把 `iphone-control` 放进 `PATH`。
