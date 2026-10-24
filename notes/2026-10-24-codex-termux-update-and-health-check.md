# Termux 中更新 Codex 并验证真实工作流（2026-10-24）

## 结论与环境

本次在 Android ARM64 / Termux 中，将已有的社区适配包 `@mmmbuto/codex-cli-termux` 从 `0.160.0-termux.2` 更新至检查时的 `latest`：`0.163.0-termux.2`。原有 ChatGPT 登录、`gpt-6.1-sol` 模型配置和 hooks 均保留。

新版的模型回复、命令执行和文件读写正常；额外发现并修复了启动器缺失安装来源标记、后台服务遗留不可达 socket 两个问题。最终 `codex doctor` 返回 **21 ok / 0 warn / 0 fail**，独立 tmux 会话中的交互式对话也通过。

| 项目 | 本次实测 |
| --- | --- |
| 平台 | Android 12 / aarch64，原生 Termux，无需 proot |
| Node / npm | v26.12.1 / 11.21.1 |
| npm 包 | `@mmmbuto/codex-cli-termux@0.163.0-termux.2` |
| CLI / app-server | 均为 `0.163.0` |
| 认证 / 模型 | 已有 ChatGPT 登录 / `gpt-6.1-sol` |

这是社区维护的 Android 适配包，不是 OpenAI 官方 npm 包。检查时 `@openai/codex` 的最新版本为 `0.164.0`，与 Termux 适配版发布节奏不同；不能只比较版本号就替换当前可用渠道。本次不改镜像、不全量升级系统或其他全局 npm 包，也不关闭安全检查来通过测试。

## 1. 先确认当前安装，再更新

```sh
command -v codex
readlink -f "$(command -v codex)"
npm list -g --depth=0
codex --version
codex login status
npm view @mmmbuto/codex-cli-termux dist-tags --json
npm view @openai/codex dist-tags.latest
```

本机 `codex` 指向：

```text
$PREFIX/lib/node_modules/@mmmbuto/codex-cli-termux/bin/codex.js
```

更新前，将现有包目录、`~/.codex/config.toml` 和 `hooks.json` 备份到 Termux 私有目录，权限限制为仅当前用户可读。不要把 `auth.json`、令牌、完整会话日志或配置中的凭据提交到仓库。

本次使用明确版本更新，方便复现：

```sh
npm install -g @mmmbuto/codex-cli-termux@0.163.0-termux.2
codex --version
codex login status
```

日后可先查 `dist-tags` 再选版本，而不是长期固定本文版本。`codex --version` 显示上游版本 `0.163.0`，npm 包版本另带 `-termux.2`，两者并不矛盾。

## 2. 故障一：启动器漏传包路径

### 复现与定位

```sh
codex doctor --summary --no-color --ascii
```

更新后出现：

```text
npm-managed launch is missing package-root provenance
Reinstall or update Codex so the JS shim provides CODEX_MANAGED_PACKAGE_ROOT.
```

此时 CLI 和真实模型请求仍可成功，这不是登录失效。用一次性环境变量做单变量验证：

```sh
package="$(npm root -g)/@mmmbuto/codex-cli-termux"
CODEX_MANAGED_PACKAGE_ROOT="$package" codex doctor --summary --no-color --ascii
```

安装告警消失，后台服务告警不变。检查 `bin/codex.js`、`bin/codex-exec.js`、`bin/codex`、`bin/codex-exec` 后确认：四个入口均设置了 `CODEX_MANAGED_BY_NPM`，但没有传入新自检要求的 `CODEX_MANAGED_PACKAGE_ROOT`。

### 本机修复及可重复补丁

JS 入口通过已有的 `dirname` 和 `__dirname` 计算包根目录，shell 入口通过 `SCRIPT_DIR/..` 计算；覆盖继承来的过时路径。不硬编码 npm 安装位置，也不改变 `CODEX_SELF_EXE`、动态库路径、参数转发或审批配置。

仓库保留了版本限定的补丁 `scripts/codex-termux-provenance.patch` 和回归检查 `scripts/check-codex-termux-launchers.py`。在仓库根目录运行：

```sh
python scripts/check-codex-termux-launchers.py
```

检查不调用模型、不修改安装，而是复制四个入口至带空格的临时路径，以替身二进制验证它们实际传递的包路径、原生入口和参数。覆盖环境变量缺失、继承错误路径两种情况。本次修复前 **0/8**，修复后 **8/8**。

**仅当安装版本仍为 `0.163.0-termux.2` 且复现同一问题时**，可按以下方式重放补丁。先备份四个入口；然后确保 dry-run 成功，才执行应用：

```sh
package="$(npm root -g)/@mmmbuto/codex-cli-termux"
patch_file="$PWD/scripts/codex-termux-provenance.patch"
patch --batch --forward --dry-run -p1 -d "$package" < "$patch_file" &&
  patch --batch --forward -p1 -d "$package" < "$patch_file"
python scripts/check-codex-termux-launchers.py "$package"
codex doctor --summary --no-color --ascii
```

若补丁已应用，或新版改变了启动器结构，dry-run 应拒绝；不要强行重复打补丁。**npm 再次安装/升级会覆盖本地修复**，更新后应重跑检查；未来发行版修复后不再需要此补丁。

## 3. 故障二：后台服务 socket 存在但连接被拒绝

自检提示：

```text
background server socket is stale or unreachable
```

进一步复现：

```sh
codex app-server daemon version
```

返回退出码 1，错误为：

```text
failed to connect to .../.codex/app-server-control-termux/app-server-control.sock
Connection refused (os error 111)
```

已有 socket 文件不代表服务仍在运行。优先使用自身的生命周期命令恢复，不要直接删除 `~/.codex`、数据库、锁文件或登录状态：

```sh
codex app-server daemon start
codex app-server daemon version
```

本次启动成功，返回 `status: running`，`cliVersion` 和 `appServerVersion` 均为 `0.163.0`。补齐启动器环境后，对本次新启动且尚无用户任务的服务执行过一次 `daemon restart`，使其继承修复后的环境。已有运行任务时不要随意重启。

Termux 上使用 PID 后台服务，不依赖 systemd。Android 杀后台后仍可能需要重新启动；这里不保证跨重启常驻。默认本机控制 socket 可用，不等于启用了远程控制。

## 4. 验证真正的工作流，而不只是版本号

本次执行了以下检查：

| 检查 | 结果 |
| --- | --- |
| CLI、`codex-exec`、两个 shell 入口启动与语法检查 | 通过 |
| 原有登录、模型配置和 hooks 文件保留 | 通过 |
| `codex exec` 真实模型请求 | 精确返回 `CODEX_OK` |
| 命令工具读取数据、计算、写文件、读回断言 | 命令退出码 0，输出 `CODEX_SHELL_OK` |
| 独立读回结果文件 | `{"count":3,"sum":82}` |
| 四个启动器的环境与参数回归 | 8/8 |
| 后台服务连接与版本一致性 | 通过 |
| 独立 tmux 中启动默认 TUI 并发送真实请求 | 返回 `CODEX_TUI_OK` |
| 最终 `codex doctor` | 21 ok / 0 warn / 0 fail |

### 可复制的命令与文件烟测

需要已登录的账号及可用模型，会消耗少量额度。使用独立目录，不让模型操作真实项目：

```sh
umask 077
test_dir=$(mktemp -d "$PREFIX/tmp/codex-smoke.XXXXXX")
printf '[17,23,42]\n' > "$test_dir/numbers.json"

timeout --signal=TERM --kill-after=5s 120s \
  codex -a never exec --ephemeral --skip-git-repo-check \
  --sandbox workspace-write -C "$test_dir" --json \
  -o "$test_dir/last.txt" \
  'Work only in the current directory. Actually execute Python using your command tool: read numbers.json, compute count and sum, write result.json with those fields, re-read and assert count=3 and sum=82, then print CODEX_SHELL_OK. Reply exactly CODEX_TOOLS_OK after success. If execution fails, stop and report the error; do not change permissions or configuration.' \
  </dev/null > "$test_dir/events.jsonl" 2> "$test_dir/stderr.log"
exec_rc=$?

python - "$test_dir" "$exec_rc" <<'PY'
import json
from pathlib import Path
import sys

p = Path(sys.argv[1])
assert sys.argv[2] == '0', f'codex exit: {sys.argv[2]}'
assert (p / 'last.txt').read_text().strip() == 'CODEX_TOOLS_OK'
assert json.loads((p / 'result.json').read_text()) == {'count': 3, 'sum': 82}
events = [json.loads(line) for line in (p / 'events.jsonl').read_text().splitlines()]
assert any(
    e.get('type') == 'item.completed'
    and (item := e.get('item', {})).get('type') == 'command_execution'
    and item.get('exit_code') == 0
    and 'CODEX_SHELL_OK' in item.get('aggregated_output', '')
    for e in events
), 'No successful command execution found'
print('PASS: model reply, actual command execution, file readback')
PY
```

不要仅凭模型声称完成就判定成功；要检查退出码、工具事件和实际文件。`workspace-write` 是本次请求的策略，以上检查不证明 Android 实现了与桌面 Linux 完全相同的内核沙箱隔离。

`codex exec` 可能尝试附加读取 stdin。在脚本或 heredoc 中调用时显式使用 `</dev/null`，避免吞掉后续脚本内容；需要从 stdin 传提示词时则按 CLI 用法传入。

交互测试使用临时独立 tmux server，验证后只清理该 server，不触碰已有 `main` 会话。判断模型响应时，完整预期字符串不出现在输入提示中，避免将回显误判为回答。

## 覆盖边界与后续维护

- `codex doctor` 可能在有 warning 时仍返回 0；自动化应检查 `--json` 的具体检查状态，不能只看退出码。
- 本次覆盖本机已有账号和 `gpt-6.1-sol`，不代表所有模型、MCP、插件、远程控制或语音均可用。该包 README 明确说明 `/voice` 尚无 Android 音频后端。
- 本地备份和测试记录保存在 Termux 私有维护目录，不作为公开笔记附件。
- 每次升级后重新检查启动器、自检、真实工具操作和交互式会话；不要只运行 `codex --version`。

## 参考

- [Termux 适配包仓库及发布说明](https://github.com/DioNanos/codex-termux)
- [Termux 适配包 npm 页面](https://www.npmjs.com/package/@mmmbuto/codex-cli-termux)
- [OpenAI 官方 Codex 仓库](https://github.com/openai/codex)
- [本仓库的 tmux 编码会话笔记](2026-07-13-agent-tmux-coding-session-manager.md)
