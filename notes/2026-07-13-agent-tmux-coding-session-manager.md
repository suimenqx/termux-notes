# Termux 下使用 agent-tmux 管理编码会话（2026-07-13）

## 动机

在 Termux 中进行编码时，经常需要在多个窗口之间切换：一个窗口运行代码助手（如 pi/copilot），一个窗口管理 git，一个窗口跑测试，一个窗口执行/运行代码。每次手动创建 tmux 会话和窗口十分繁琐。

`agent-tmux` 是一个极简的 tmux 会话启动脚本，一键创建/恢复预设的编码工作区布局。

## 脚本源码

```shell
#!/data/data/com.termux/files/usr/bin/sh
set -eu

SESSION="main"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach -t "$SESSION"
fi

# First time bootstrap
TMUX='' tmux new-session -d -s "$SESSION" -n agent
TMUX='' tmux new-window  -t "$SESSION":2 -n git
TMUX='' tmux new-window  -t "$SESSION":3 -n test
TMUX='' tmux new-window  -t "$SESSION":4 -n run

# Optional: default commands hints (commented by design)
# tmux send-keys -t "$SESSION":2 'git status' C-m
# tmux send-keys -t "$SESSION":3 'echo "run tests here"' C-m

exec tmux attach -t "$SESSION"
```

## 工作原理

### 1. 幂等性：已存在则复用

```shell
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach -t "$SESSION"
fi
```

若名为 `main` 的会话已存在（例如断开重连），直接 attach 进入，不会重复创建。Termux 网络中断、切后台杀进程后重进时尤为实用。

### 2. 首次创建四窗口布局

| 窗口编号 | 窗口名 | 用途 |
|:---:|:---:|---|
| 1 | **agent** | 编码助手（pi/copilot 对话） |
| 2 | **git** | Git 操作（commit、log、push） |
| 3 | **test** | 运行测试/校验 |
| 4 | **run** | 执行项目/启动服务 |

四个窗口覆盖了编码循环的典型环节：**思考 → 版本控制 → 验证 → 运行**。

### 3. `TMUX=''` 嵌套保护

```shell
TMUX='' tmux new-session -d -s "$SESSION" -n agent
```

在 `tmux` 外部运行脚本时，`TMUX` 环境变量为空，可正常 `new-session`。
但如果用户**已在 tmux 内部**运行此脚本，tmux 默认会尝试在当前 session 内嵌套创建，导致混乱。设置 `TMUX=''` 告诉 tmux "当作不在 tmux 内"——即创建独立的**外部 session**，不嵌套。

> 这行设计允许脚本在任何环境下运行而行为一致。

### 4. 注释掉的自动命令

```shell
# tmux send-keys -t "$SESSION":2 'git status' C-m
# tmux send-keys -t "$SESSION":3 'echo "run tests here"' C-m
```

故意保持注释状态——不预设任何项目特定命令。这样 `agent-tmux` 保持通用性，适用于任何项目。需要时取消注释即可。

## 使用方式

### 放置脚本

```shell
mkdir -p ~/bin
# 将 agent-tmux 放入 ~/bin
chmod +x ~/bin/agent-tmux
```

确保 `~/bin` 在 `PATH` 中（通常在 `~/.bashrc` 或 `~/.profile` 中）：

```shell
export PATH="$HOME/bin:$PATH"
```

### 启动

```shell
agent-tmux
```

- 首次：创建 `main` 会话，4 个窗口排好，自动进入 agent 窗口
- 已存在：直接 attach

### 快捷键备忘

| 操作 | 快捷键 |
|---|---|
| 切换下一窗口 | `Ctrl+B n` |
| 切换上一窗口 | `Ctrl+B p` |
| 跳转到窗口 N | `Ctrl+B N`（N = 窗口编号） |
| 水平分割窗格 | `Ctrl+B "` |
| 垂直分割窗格 | `Ctrl+B %` |
| 切换窗格 | `Ctrl+B 方向键` |
| 脱离会话（后台） | `Ctrl+B d` |

## tmux extended-keys 警告修复

如果在 Termux 中看到以下警告：

```
Warning: tmux extended-keys is off. Modified Enter keys may not work.
```

在 `~/.tmux.conf` 中添加一行即可消除：

```
set -g extended-keys on
```

然后执行 `tmux source-file ~/.tmux.conf` 或重启 tmux 使其生效。

---

## 设计哲学

1. **极简** — 仅 20 行，无依赖，纯 POSIX sh
2. **幂等** — 重复执行安全，不产生僵尸 session
3. **通用** — 不嵌入项目特定逻辑，靠窗口命名约定组织工作流
4. **Termux 友好** — 无需 tmux 插件管理器、不依赖 systemd，手机端开箱即用

## 自定义变体

### 按项目增加窗口

```shell
# 为 Python 项目加一个 repl 窗口
TMUX='' tmux new-window -t "$SESSION":5 -n repl
tmux send-keys -t "$SESSION":5 'python3' C-m
```

### 多项目多会话

```shell
# agent-tmux-py
SESSION="py-project"
# ... 其余逻辑相同，窗口名可调整为 lint, pytest, runserver
```

通过复制脚本改 `SESSION` 变量即可复用同一模式管理多个项目。

## 总结

`agent-tmux` 解决的是一个"摩擦"问题：在手机触屏上手工敲 `tmux new-session ...` 太慢，而且每次都要记得窗口顺序。把布局固化为一个可执行文件后，终端编码的启动成本从 30 秒降到了 1 条命令。

结合 Extra Keys 配置，Termux 上的编码环境可以做到接近桌面端的操作效率。
