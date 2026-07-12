# Termux Extra Keys 配置完全指南（2026-07-13）

## 概述

Termux 屏幕底部可显示两行**额外按键（Extra Keys）**，即悬浮键盘。它独立于 Android 软键盘，始终可见（可配置），用于弥补手机触屏缺失的 PC 键盘功能。

核心能力：
- 提供软键盘上没有的特殊键（ESC、CTRL、方向键等）
- 支持**上滑（Swipe Up / Popup）**触发第二功能，一键两用
- 支持**宏（Macro）**一键发送组合键序列（如 `Ctrl+C`、`Ctrl+D`）

## 配置位置

```
~/.termux/termux.properties
```

这是标准 Java `.properties` 文件，核心配置行：

```properties
extra-keys = <值>
```

`<值>` 是嵌在 `.properties` 中的 JSON 数组，存在**两层解析**（`.properties` → JSON），这是最容易出错的点。

---

## 语法基础

`extra-keys` 的值是一个**二维 JSON 数组**：

```json
[
  [键1, 键2, ..., 键N],   // 上排
  [键2, 键2, ..., 键M]    // 下排
]
```

每行建议最多 7 个键（屏幕宽度限制）。

---

## 一行格式（无 Popup）

最简形式，无上滑：

```properties
extra-keys = [['ESC','/','-','HOME','UP','END','|'],['KEYBOARD','CTRL','ALT','LEFT','DOWN','RIGHT','TAB']]
```

### 键的三种写法

| 写法 | 示例 | 说明 |
|------|------|------|
| 裸键名（不加引号） | `ESC`, `CTRL`, `TAB`, `UP` | Termux 内置系统键 |
| 单引号字符 | `'/'`, `'-'`, `'\|'` | 单个文本字符 |
| 双引号字符串 | `"/"`, `"\|"` | 同上，注意转义 |

> 推荐：系统键用裸名，普通字符用单引号。

---

## 对象格式（有 Popup）

为键添加上滑功能，需写成 JSON 对象：

```json
{key: 键名, popup: 上滑触发的内容}
```

### 完整配置示例

```properties
extra-keys = [[ \
  {key: ESC, popup: {macro: "CTRL c", display: "C-c"}}, \
  {key: '/', popup: '?'}, \
  {key: '-', popup: '_'}, \
  {key: SHIFT}, \
  {key: UP, popup: PGUP}, \
  {macro: "CTRL j", display: "LF", popup: '$'}, \
  {key: '|', popup: '>'} \
], [ \
  {key: KEYBOARD}, \
  {key: CTRL, popup: {macro: "CTRL d", display: "C-d"}}, \
  {key: ALT, popup: {macro: "ALT .", display: "A-."}}, \
  {key: LEFT, popup: HOME}, \
  {key: DOWN, popup: PGDN}, \
  {key: RIGHT, popup: END}, \
  {key: TAB, popup: {macro: "CTRL l", display: "C-l"}} \
]]
```

### Popup 值的三种类型

| 类型 | 语法 | 示例 | 效果 |
|------|------|------|------|
| 系统键名 | 裸名，不引号 | `HOME`, `PGUP` | 上滑触发系统键 |
| 单字符 | 单引号括起 | `'?'`, `'_'`, `'$'` | 上滑输入字符 |
| 宏对象 | `{macro: "...", display: "..."}` | `{macro: "CTRL c", display: "C-c"}` | 上滑执行组合键 |

---

## Macro 宏按键

用于一键发送组合键序列，可用在物理键或 popup 中。

### 语法

```json
{macro: "组合键序列", display: "显示文本"}
```

| 字段 | 必须 | 说明 |
|------|------|------|
| `macro` | ✅ | 组合键序列，空格分隔 |
| `display` | ✅ | 显示在键上的文字（建议 1-3 个大写字母） |

### 示例

```json
{macro: "CTRL c", display: "C-c"}                        // Ctrl+C，显示 "C-c"
{macro: "CTRL c", display: "C-c", popup: {...}}           // 物理键+popup
{macro: "CTRL j", display: "LF", popup: '$'}              // 换行+popup输出$
```

### 可用的组合键键名

在 macro 字符串中可用：`CTRL` `ALT` `SHIFT` `FN` `ESC` `TAB` `ENTER` `SPACE` `HOME` `END` `PGUP` `PGDN` `UP` `DOWN` `LEFT` `RIGHT` `BKSP` `DEL` `F1-F12`

字母键直接写字母：`CTRL c`, `ALT x`, `CTRL ALT DEL`

---

## 完整键名参考表

### 系统键（裸名，无需引号）

| 键名 | 功能 | 默认显示 |
|------|------|----------|
| `ESC` | Escape | ESC |
| `TAB` | 制表符 / 补全 | TAB |
| `CTRL` | Control 修饰键 | CTRL |
| `ALT` | Alt/Meta 修饰键 | ALT |
| `SHIFT` | Shift 修饰键 | SHIFT |
| `ENTER` | 回车 ⚠️ | ↵（极小图标，不推荐） |
| `HOME` | 行首 | HOME |
| `END` | 行尾 | END |
| `PGUP` | 上翻页 | PGUP |
| `PGDN` | 下翻页 | PGDN |
| `UP` | 上方向 | ▲ |
| `DOWN` | 下方向 | ▼ |
| `LEFT` | 左方向 | ◄ |
| `RIGHT` | 右方向 | ► |
| `KEYBOARD` | 切换软键盘 | 键盘图标 |
| `BKSP` | 退格 | BKSP |
| `DEL` | 删除 | DEL |
| `F1`–`F12` | 功能键 | F1–F12 |

> ⚠️ `ENTER` 会被 Termux 用系统图标渲染（极小 `↵`），推荐用 `{macro: "CTRL j", display: "LF"}` 替代。

### SHIFT 修饰键的特殊行为

- `SHIFT` + `'/'` = `?`
- `SHIFT` + `'-'` = `_`
- `SHIFT` + 裸键名 = 无效果
- `SHIFT` 不影响 macro 键输出

---

## 多行续接规则

`.properties` 中行尾 `\` 表示逻辑行延续，下一行前导空白会被吃掉。

### 正确 ✅

```properties
extra-keys = [[ \
  {key: ESC}, \
  {key: TAB} \
]]
```

### 错误 ❌

```properties
extra-keys = [[ \              ← \ 后面不能有空格！
  {key: ESC}, \
  {key: TAB} \
]]
```

规则：
- `\` 必须是该行最后一个字符（换行符之前）
- `\` 前面可以有空格
- `\` 后面不能有任何字符（包括空格）

---

## 生效方式

### 方法一：重新加载设置

```bash
termux-reload-settings
```

> extra-keys 的 UI 变化通常需要**重启 Termux 进程**才能看到。如果看不到变化，彻底划掉 Termux 再重新打开。

### 方法二：强制重启

```
Android 设置 → 应用 → Termux → 强制停止 → 重新打开
```

### 验证配置是否被读取

```bash
grep "extra-keys" ~/.termux/termux.properties | cat -A
```

---


## 相关配置项

| 配置 | 说明 | 可选值 |
|------|------|--------|
| `extra-keys-style` | 键位符号风格 | `default`, `arrows-only`, `arrows-all`, `all`, `none` |
| `extra-keys-text-all-caps` | 强制大写标签 | `true` / `false` |

---

## 转义链陷阱（重要！）

### 问题根源

数据经过**三层解析**：

```
1. .properties 文件字符串
   ↓  Java Properties.load() 转义
2. Termux JSON 解析器
   ↓
最终按键配置
```

### 反斜杠爆炸

要在 popup 中输出字面反斜杠 `\`：

- JSON 层需要 `'\\'`（`\\` → `\`）
- `.properties` 层需要 `'\\\\'`（`\\` → `\`，4 个变 2 个再变 1 个）

结果：**4 个反斜杠**才能表示 1 个字面字符。稍微数错就 JSON 解析失败。

### 血的教训

```json
{key: '/', popup: '\\\\'}   // 4 个反斜杠
// .properties: \\ → \, 结果 '\\'
// JSON: 反斜杠转义了闭合引号 → JSONException
```

### 最佳规避

**不要在 popup 中使用反斜杠**：

| 想表达的 | 替代方案 |
|----------|----------|
| 反斜杠 `\` | 用其他符号（如 `?`）替代 |
| 双引号 `"` | 用单引号字符串避免嵌套 |
| 换行符 | 用 `{macro: "CTRL j", ...}` |

---

## 常见错误与解决

### 错误 1：JSONException 格式不合法

**可能原因**：
- 中文引号 `""` 代替英文引号 `""`
- 中文逗号 `，` 代替英文逗号 `,`
- 数组末尾多余逗号（JSON 不允许 trailing comma）
- 单引号嵌套错误（`'it's'`）
- 反斜杠转义链断裂

**排查方法**：

```bash
grep -n "extra-keys" ~/.termux/termux.properties
sed -n '行号范围p' ~/.termux/termux.properties | cat -A
```

### 错误 2：配置没生效

- 确认执行了 `termux-reload-settings`
- extra-keys UI 需要重启 Termux
- JSON 解析失败时 Termux **静默回退默认布局**

### 错误 3：键位显示异常

| 现象 | 原因 | 解决 |
|------|------|------|
| `ENTER` 显示极小符号 | Termux 用图标渲染 | 改用 `{macro: "CTRL j", display: "LF"}` |
| 纯文本键空白 | macro 缺少 `display` | 加上 `display` 字段 |
| `KEYBOARD` 显示图标 | 正常，设计如此 | — |
| 方向键显示三角 | 正常，Android 渲染 | — |

### 错误 4：两行键数不一致

建议两行都放同样数量（通常 7 个），保持视觉对齐。

---

## 设计最佳实践

### 1. 修饰键全集

`SHIFT` + `CTRL` + `ALT` 三个必须全有物理键。缺任何一个都会在特定场景下迫使你唤出软键盘。

### 2. 方向键集群不可拆分

`UP/DOWN/LEFT/RIGHT` 放在一起（通常下排中间），形成空间记忆。

### 3. 物理键 = 高频，Popup = 低频

- 高频键（每天按 100 次级）放物理槽位
- 低频但必须有的功能放 popup
- 每个物理键通过 popup 承载 1 个额外功能 → 实际 28 个功能

### 4. 自然映射

```
UP ↑ = PGUP（向上翻页）
DOWN ↑ = PGDN（向下翻页）
LEFT ↑ = HOME（向左 = 行首）
RIGHT ↑ = END（向右 = 行尾）
```

### 5. 标签清晰

- 裸键名自动大写（`ESC`, `TAB`, `CTRL`）
- macro 用 `display` 指定简短标签（`C-c`, `C-d`, `A-.`）
- 单字符键用符号本身（`/`, `-`, `|`）

### 6. KEYBOARD 键永不删除

这是软键盘无法弹出时的唯一恢复路径，物理键必须保留。

### 7. 测试检查清单

修改配置后逐项验证：

- [ ] `termux-reload-settings` 无报错
- [ ] 重启后两排键正常显示
- [ ] 每个物理键按下功能正确
- [ ] 每个 popup 上滑功能正确
- [ ] `SHIFT` + 字符键产生对应符号
- [ ] `KEYBOARD` 能正常切换软键盘
- [ ] 多行配置无 `\` 后空格
- [ ] 无 JSON trailing comma

---

## 本机最终配置

```
┌─────┬─────┬─────┬──────┬────┬─────┬─────┐
│ ESC │  /  │  -  │SHIFT │ UP │  LF │  |  │
│ C-c │  ?  │  _  │  —   │PGUP│  $  │  >  │
├─────┼─────┼─────┼──────┼────┼─────┼─────┤
│ KEY │CTRL │ ALT │ LEFT │DOWN│RIGHT│ TAB │
│  —  │ C-d │ A-. │ HOME │PGDN│ END │ C-l │
└─────┴─────┴─────┴──────┴────┴─────┴─────┘
```

> 上排 = 物理键，下排 = 上滑 Popup

### 设计要点

- **零肌肉记忆破坏**：方向键集群位置不动
- **修饰键全集**：SHIFT + CTRL + ALT 三个物理键缺一不可
- **换行键**：用 `{macro: "CTRL j", display: "LF"}` 替代 `ENTER`，标签清晰可读
- **HOME/END 降级为 popup**：挂在 LEFT/RIGHT 上，方向一致，腾出槽位给 SHIFT 和 LF
- **PGUP/PGDN 挂 UP/DOWN**：翻页方向直觉对应
- **KEYBOARD 保留**：软键盘兜底

---

## 相关资源

- Termux Wiki: [Terminal Settings](https://wiki.termux.com/wiki/Terminal_Settings)
- 配置仓库: `termux-extra-keys-config`（同目录下）
- `.properties` 规范: [Wikipedia](https://en.wikipedia.org/wiki/.properties)
