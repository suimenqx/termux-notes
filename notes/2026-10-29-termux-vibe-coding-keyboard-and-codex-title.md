# Termux 手机端 Vibe Coding 配置：虚拟键盘、会话切换与 Codex 标题闪烁修复（2026-10-29）

## TL;DR

最终把 Termux 手机端最常用的操作都放进了拇指区：

```text
第一行：ESC   /   -   SHIFT   ↑   LF   |   »
第二行：⌨    CTRL  ALT  ←    ↓   →   TAB  ☰
```

- `»`：下一个会话；在它上面上滑是 `«`，上一个会话
- `☰`：打开/关闭左侧会话列表，不再需要从左边缘滑动
- `Ctrl+1/2/3/4`：上一个 / 下一个 / 新建 / 重命名会话
- `⌨`、`CTRL`、`ALT`、方向键、`TAB` 全部保留在 extra-keys 行

另外，Codex 的 terminal title spinner 会让 Termux 顶部不停弹 Toast，看起来像“标题闪烁”。在 Codex 的 `/title` 里取消 `activity`，或配置：

```toml
[tui]
terminal_title = ["thread-name", "project-name"]
```

就能让标题保持静态。

---

## 1. 适用场景与环境

这套配置适合：

- Android + Termux，主要用手机软键盘
- 经常在多个 Termux 会话之间切换（pi、codex、shell、日志等）
- 不想每次都从左边缘滑出会话抽屉
- 希望保留 ESC、CTRL、ALT、方向键等 PC 键盘能力

本次实测环境：

| 项目 | 版本 / 说明 |
| --- | --- |
| 设备 | Android 12 / aarch64 |
| Termux | 0.118.3（F-Droid 构建） |
| 终端字体 | `~/.termux/font.ttf` |
| Codex | `@mmmbuto/codex-cli-termux`，CLI 0.163.0 |
| 配置文件 | `~/.termux/termux.properties`、`~/.codex/config.toml` |

不同 Termux 版本的布局和属性解析可能略有差异，升级后建议重新验证一次。

---

## 2. 最终 extra-keys 配置

编辑：

```text
~/.termux/termux.properties
```

把原有的 `extra-keys` 整段替换为：

```properties
extra-keys = [[ \
  {key: ESC, popup: {macro: "CTRL c", display: "C-c"}}, \
  {key: '/', popup: '?'}, \
  {key: '-', popup: '_'}, \
  {key: SHIFT}, \
  {key: UP, popup: PGUP}, \
  {macro: "CTRL j", display: "LF", popup: '$'}, \
  {key: '|', popup: '>'}, \
  {macro: "CTRL 2", display: "»", popup: {macro: "CTRL 1", display: "«"}} \
], [ \
  {key: KEYBOARD}, \
  {key: CTRL, popup: {macro: "CTRL d", display: "C-d"}}, \
  {key: ALT, popup: {macro: "ALT .", display: "A-."}}, \
  {key: LEFT, popup: HOME}, \
  {key: DOWN, popup: PGDN}, \
  {key: RIGHT, popup: END}, \
  {key: TAB, popup: {macro: "CTRL l", display: "C-l"}}, \
  {key: DRAWER} \
]]
```

### 每个键的作用

| 键 | 点击 | 上滑 / Popup |
| --- | --- | --- |
| `ESC` | Escape | `Ctrl+C` |
| `/` | `/` | `?` |
| `-` | `-` | `_` |
| `SHIFT` | Shift | - |
| `↑` | 上方向 | `PgUp` |
| `LF` | `Ctrl+J` / 换行 | `$` |
| `\|` | 管道符 | `>` |
| `»` | 下一个 Termux 会话（`Ctrl+2`） | `«` 上一个会话（`Ctrl+1`） |
| `⌨` | 显示/隐藏软键盘 | - |
| `CTRL` | Ctrl | `Ctrl+D` |
| `ALT` | Alt | `Alt+.` |
| `←` | 左方向 | `Home` |
| `↓` | 下方向 | `PgDn` |
| `→` | 右方向 | `End` |
| `TAB` | Tab | `Ctrl+L` |
| `☰` | 打开/关闭左侧会话抽屉 | - |

`»` / `«` 不是 Termux 内置的特殊键，而是宏：分别发送 `Ctrl+2` 和 `Ctrl+1`，由下面的 `shortcut.*` 接管。

---

## 3. 会话快捷键

在同一个文件里，加入或确认以下四行：

```properties
shortcut.previous-session = ctrl + 1
shortcut.next-session = ctrl + 2
shortcut.create-session = ctrl + 3
shortcut.rename-session = ctrl + 4
```

对应关系：

| 快捷键 | 动作 |
| --- | --- |
| `Ctrl+1` | 上一个会话 |
| `Ctrl+2` | 下一个会话 |
| `Ctrl+3` | 新建会话 |
| `Ctrl+4` | 重命名当前会话 |

虚拟键盘上先点一下 `CTRL`，再按数字即可；按住音量下键再按数字也可以，因为 Termux 默认把音量下键当作 Ctrl。

> 这四个组合会被 Termux 全局拦截，pi、codex 等终端程序收不到 `Ctrl+1..4`。如果某个程序确实需要这些键，换一组快捷键或删除对应配置。

---

## 4. 应用、验证与回滚

### 4.1 修改前先备份

```bash
cp -p ~/.termux/termux.properties \
  ~/.termux/termux.properties.bak-$(date +%Y%m%d-%H%M%S)
```

### 4.2 应用配置

```bash
termux-reload-settings
```

正常情况下返回 0。若 extra-keys 没有变化，把 Termux App 完全退出再重开。

### 4.3 验证清单

- [ ] extra-keys 第一行最右侧是 `»`，第二行最右侧是 `☰`
- [ ] 点 `☰` 能打开/关闭左侧会话列表
- [ ] 点 `»` 切到下一个会话
- [ ] 在 `»` 上向上滑能切到上一个会话
- [ ] `Ctrl+1` / `Ctrl+2` 能切换会话
- [ ] `Ctrl+3` 新建会话，`Ctrl+4` 弹出重命名
- [ ] `Ctrl+C`、方向键、`TAB` 等原有按键仍正常

### 4.4 回滚

```bash
cp -p ~/.termux/termux.properties.bak-YYYYMMDD-HHMMSS \
  ~/.termux/termux.properties
termux-reload-settings
```

---

## 5. 关键原理与容易踩的坑

### 5.1 `extra-keys` 是“两层解析”

`.properties` 文件先解析一次，`extra-keys` 的值再作为 JSON 数组解析。最容易出错的是：

- 每个逻辑行末尾的 `\` 不能漏
- 新增键时，前一个键后面要补逗号
- 最后一个键后面不要多写逗号
- `DRAWER`、`KEYBOARD` 等特殊键名必须大写
- 改完必须执行 `termux-reload-settings`

如果 extra-keys 整行消失，通常是 JSON 解析失败。直接用备份恢复，再逐项检查逗号和反斜杠。

### 5.2 `DRAWER` 是 Termux 原生特殊键

`DRAWER` 不是宏，也不是自己定义的字符串。Termux 的 `TermuxTerminalExtraKeys` 会识别它，并直接调用抽屉的 `openDrawer()` / `closeDrawer()`。

所以这一行就够了：

```properties
{key: DRAWER}
```

显示为 `☰`。这比从左边缘滑动可靠得多，也不需要额外的 App 或悬浮窗。

同类特殊键还有：

- `KEYBOARD`：显示/隐藏软键盘
- `PASTE`：粘贴
- `DRAWER`：打开/关闭会话抽屉

### 5.3 `shortcut.*` 只支持四类动作

Termux 原生的 `shortcut.*` 只有：

```text
create-session
next-session
previous-session
rename-session
```

而且值必须是 `ctrl + 单个字符`：

```properties
shortcut.next-session = ctrl + 2
```

以下写法**不生效**：

```properties
shortcut.next-session = ctrl + UP     # 方向键不支持
shortcut.session-1 = ctrl + 1         # 没有按编号直接跳转的配置
```

内置的 `Ctrl+Alt+1..9` 可以按编号跳会话，但它依赖物理键盘的 Ctrl 和 Alt；虚拟键盘的 CTRL/ALT 按钮不参与这个判断。因此手机上最稳的方案还是：

- 四类动作走 `shortcut.*`
- 直接打开会话列表走 `DRAWER`
- 会话内切换走 `»` / `«`

### 5.4 图标要检查字体覆盖

最初用的是 `S+` / `S-`，意思是 Session + / Session -，但太隐晦。后来换成 `»` / `«`。

选择图标前先确认当前字体有没有对应字形。本次字体支持：

- `»` `«`
- `▶` `◀`
- `→` `←`

不支持：

- `⏭` `⏮`

检查方法：

```bash
python3 -m pip install --quiet fonttools
python3 - <<'PY'
from fontTools.ttLib import TTFont
font = TTFont('/data/data/com.termux/files/home/.termux/font.ttf')
cmap = font.getBestCmap()
for ch in '»«▶◀→←⏭⏮':
    print(repr(ch), ord(ch) in cmap)
PY
```

如果字体缺字，extra-keys 上会显示方框或空白，换图标即可。

### 5.5 布局取舍

最终布局是：

```text
第一行：ESC   /   -   SHIFT   ↑   LF   |   »
第二行：⌨    CTRL  ALT  ←    ↓   →   TAB  ☰
```

`»` 和 `☰` 都在右手拇指容易够到的右侧：`»` 在右上，`☰` 在右下。

曾尝试把 `☰` 和 `»` 并排塞到右下角，并把 `⌨` 移到第一行。虽然按键都还在，但实际手感不如最终版，已经回退。结论是：不要为了“两个新按钮放在一起”破坏原有的拇指肌肉记忆；`»` 留在右上、`☰` 留在右下更顺。

---

## 6. Codex 顶部“标题闪烁”的定位与修复

这部分和虚拟键盘无关，但它是同一套 vibe coding 工作流里非常影响体验的问题。

### 6.1 现象

- 在某个 Termux 会话里，屏幕顶部不断闪出一条标题
- 切到 Codex 所在的会话窗口后，不闪
- 切到另一个会话窗口后，又开始闪
- 内容类似：

```text
⠦ 分析 dmit 直连 IPv6 | remnawave-vps
```

Braille 字符在 `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏` 之间快速变化。

### 6.2 先排除 codex-pet

第一反应是 codex-pet 的宠物动画，但可以排除：

1. codex-pet daemon 的 `/proc/<pid>/fd` 里没有 `/dev/pts/*`，它没有持有终端，无法写终端标题。
2. 它的源码里没有 `OSC 0`、`setTitle`、`terminal_title` 之类代码，只使用 Termux:GUI overlay 和少量通知。
3. 把 codex-pet 停掉后，Codex 仍然以约 10Hz 写标题；顶部仍然闪。

所以 codex-pet 是无辜的。

### 6.3 抓到真正的写入者

对 Codex 进程做 `strace`：

```bash
timeout 5 strace -tt -p <codex-pid> -f \
  -e trace=write -s 200 -o "$TMPDIR/codex-title.log"

grep -a '\\33\]0;' "$TMPDIR/codex-title.log" | tail
```

可以看到：

```text
write(1, "\33]0;⠧ 分析 dmit 直连 IPv6 | remnawave-vps\7", 48)
```

`fd 1 -> /dev/pts/N`，说明就是 Codex 自己写的 OSC 0 终端标题。5 秒内大约 50 次，约 10Hz。

### 6.4 为什么 Termux 顶部会闪

Termux 0.118.3 的处理链路：

1. 终端收到 OSC 0，更新会话标题。
2. `TermuxTerminalSessionClient.onTitleChanged()` 被调用。
3. 如果标题变化的会话**不是当前会话**，就调用：

   ```java
   mActivity.showToast(toToastTitle(updatedSession), true);
   ```

4. `TermuxActivity.showToast()` 设置了：

   ```java
   toast.setGravity(Gravity.TOP, 0, 0);
   ```

所以后台 Codex 每 100ms 改一次标题，Termux 就取消旧 Toast、在顶部重新弹一次新 Toast。看起来就是“标题一直在闪烁”。

切到 Codex 会话后，它是当前会话，`updatedSession != currentSession` 不成立，不再弹 Toast，所以不闪。这个行为和现象完全吻合。

> `disable-terminal-session-change-toast = true` 只能关闭“切换会话”时的 Toast，管不了标题变化触发的 Toast。

### 6.5 修复 Codex 标题

在 Codex 里执行：

```text
/title
```

在 **Configure Terminal Title** 列表里取消：

```text
[ ] activity    Spinner while working, action-required message while blocked
```

保留：

```text
[x] thread-name
[x] project-name
```

保存后，标题会固定为类似：

```text
分析 dmit 直连 IPv6 | remnawave-vps
```

不再有 Braille spinner。

也可以直接改 `~/.codex/config.toml`：

```toml
[tui]
terminal_title = ["thread-name", "project-name"]
```

如果要完全关闭终端标题：

```toml
[tui]
terminal_title = []
```

注意：

- `activity` 才是 spinner；`run-state` 是静态的 “Ready / Working / Thinking” 文本，不要混淆。
- 当前正在运行的 Codex 不会热加载配置文件；用 `/title` 改会立即生效，改配置文件则需要重启该 Codex 会话。
- 改完可以用 `codex doctor --summary` 检查，正常会看到类似 `✓ title configured`。

---

## 7. 故障排查

### extra-keys 整行消失

原因通常是 JSON 解析失败。恢复备份：

```bash
cp -p ~/.termux/termux.properties.bak-YYYYMMDD-HHMMSS \
  ~/.termux/termux.properties
termux-reload-settings
```

然后检查：

- 每个续行末尾是否有 `\`
- 新增键前一个元素是否有逗号
- 数组最后是否多了逗号
- `DRAWER`、`KEYBOARD` 是否大写

### 点 `☰` 没反应

确认写的是：

```properties
{key: DRAWER}
```

不是 `drawer` 或 `"DRAWER"` 作为普通字符串。改完执行 `termux-reload-settings`；不行就重启 Termux App。

### `Ctrl+1..4` 没反应

确认：

```properties
shortcut.previous-session = ctrl + 1
shortcut.next-session = ctrl + 2
shortcut.create-session = ctrl + 3
shortcut.rename-session = ctrl + 4
```

且没有启用：

```properties
disable-hardware-keyboard-shortcuts = true
```

虚拟键盘先点 `CTRL` 再按数字；或者按住音量下键再按数字。

### `»` / `«` 显示成方框

字体缺字。换成 `▶` / `◀` 或 `S→` / `S←`，或者换一个覆盖更全的 Nerd Font。

### Codex 标题还在闪

按顺序检查：

1. Codex 是否还在写 OSC 0：

   ```bash
   timeout 3 strace -p <codex-pid> -f -e trace=write -s 120 \
     -o "$TMPDIR/title.log"
   grep -a '\\33\]0;' "$TMPDIR/title.log" | tail
   ```

2. `/title` 里的 `activity` 是否已取消。
3. `~/.codex/config.toml` 里的 `terminal_title` 是否包含 `activity`。
4. 如果改的是配置文件，是否重启了 Codex 会话。

---

## 8. 最小分享版

给朋友复现时，只需要三步：

### 第一步：备份

```bash
cp -p ~/.termux/termux.properties \
  ~/.termux/termux.properties.bak-$(date +%Y%m%d-%H%M%S)
```

### 第二步：写入配置

把第 2 节的 `extra-keys` 和第 3 节的四行 `shortcut.*` 放进 `~/.termux/termux.properties`。

### 第三步：应用

```bash
termux-reload-settings
```

然后按第 4 节的清单逐项点一遍。

Codex 用户再加一步：

```text
/title → 取消 activity → 保存
```

---

## 参考

- [Termux Extra Keys 配置完全指南（2026-07-13）](2026-07-13-termux-extra-keys-config.md)
- [Termux 中更新 Codex 并验证真实工作流（2026-10-24）](2026-10-24-codex-termux-update-and-health-check.md)
