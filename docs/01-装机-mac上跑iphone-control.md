# 01 · 装机：在 Mac / Linux 上跑 iphone-control

对象：[Derrors/iphone-control](https://github.com/Derrors/iphone-control)（Rust，MCP 服务）。
它把一台 USB 连着的 iPhone 暴露成 17 个 MCP 工具：读屏、点按、滑动、长按、打字、按键、起 App、开 URL、批量动作、截图。

## 1. 取源码并编译

官方只发 Linux 与 macOS-arm64 的二进制；**Intel Mac 上没有现成包**，走源码编译（约 9 分钟）。

```bash
# Mac 上没有现成 curl 拉 codeload（exit 35 SSL）时用 gh
gh api repos/Derrors/iphone-control/tarball/v0.2.7 > ic-src.tgz
scp ic-src.tgz mac:/Users/<you>/ && ssh mac 'cd ~ && tar xzf ic-src.tgz'

ssh mac
cd ~/Derrors-iphone-control-*                  # 解出来的目录
cargo install --path apps/iphone-control --locked      # 产出 ~/.cargo/bin/iphone-control
~/.cargo/bin/iphone-control --version                  # iphone-control 0.2.7
```

## 2. 起守护进程

```bash
export PATH=$HOME/.cargo/bin:$PATH
nohup iphone-control daemon > /tmp/ic_daemon.log 2>&1 &
iphone-control status        # 期望：状态 就绪
iphone-control doctor        # 期望下面四项全 ✅
```

`doctor` 的期望输出：

```
usbmuxd                ✅
USB 有设备              ✅
已连接 00008110-xxxxxxxx iPhone14,6 iOS 27.2.1  ✅
原生控制（无障碍可用）   ✅
Apple ID / WDA          ❌（原生控制用不到，忽略）
```

想开机自启：`iphone-control service install`（装 launchd / systemd 用户服务）。

## 3. 三个真实坑（都踩过）

| 现象 | 原因 | 修法 |
| --- | --- | --- |
| `doctor`：`准备手机失败：开发者镜像：cryptexd routine 'install' failed: ... /System/Developer [17: File exists]` | 之前 go-ios 挂过 DDI 没卸 | `~/goios/ios image unmount` → `pkill -f "iphone-control daemon"` → 重启 daemon |
| `status` 一直显示旧报错 | daemon 日志里的首条报错会常驻 status | 不看 status 文字，看 `doctor` + 实际工具调用是否成功 |
| 工具调用报 `rmcp::service: timed out draining in-flight responses` | 守护进程会话卡死（打字时最常见） | `pkill -f "iphone-control daemon"` 后重启，立刻恢复 |

## 4. 验证它能真的动手机

```bash
ssh mac 'python3 ~/ic_call.py iphone_status "{}"'
# 控制方式: 原生 / 锁屏: 未锁屏 / 前台 App: com.apple.shortcuts / 屏幕: 375x667 点 / 守护进程: 就绪

ssh mac 'python3 ~/ic_call.py iphone_screenshot "{}"'
# IMAGE saved /Users/<you>/ic_shot_52168.bin (image/jpeg 52168 bytes)

scp mac:/Users/<you>/ic_shot_52168.bin ./shot.jpg     # 回本地看图
```

## 5. 与 go-ios 的能力边界（为什么不继续用 go-ios）

| 能力 | go-ios（Windows/Mac） | iphone-control（本项目） |
| --- | --- | --- |
| 截图 | ✅ | ✅ |
| 起 App | ✅ | ✅ |
| **点屏幕 / 打字** | ❌ 需要签名的 WDA/DeviceKit runner | ✅ 原生 HID |
| 读界面元素（带文字与坐标） | ❌ | ✅ `iphone_list_elements` |
| 需要 Apple ID / 7 天重签 | 要 | **不要** |

`go-ios` 唯一还有用的地方：`ios image unmount` 清理 DDI 残留。

下一步 → [02 把手机交给脚本与 AI](02-把手机交给脚本与AI.md)
