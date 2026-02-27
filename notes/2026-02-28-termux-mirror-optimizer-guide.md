# Termux 下载源优化方案与使用指南（2026-02-28）

## 背景
在 Termux 中执行 `pkg update`、`pkg upgrade` 时，速度和稳定性高度依赖镜像源质量。  
单纯“换源”通常靠经验，容易反复试错。

本方案目标是把换源流程标准化为：
1. 先测速再切换  
2. 只保留最优单源  
3. 验证成功后清理无意义备份

## 方案概览
本地已封装一个 skill：`termux-mirror-optimizer`，核心能力包括：

- 自动发现 Termux 官方镜像候选（来自本机官方镜像定义目录）
- 多轮测速并按稳定性/平均耗时排序
- 自动应用最优源到 `sources.list` 与 `root.list`
- 可选自动清理历史 `.bak-*` 备份文件

脚本目录：
`/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts`

## 一键使用（推荐）
```sh
/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts/optimize_official_mirror.sh -r 3 --groups asia,oceania --limit 12
```

含义：
- `-r 3`：每个候选镜像测速 3 轮（降低抖动）
- `--groups asia,oceania`：优先测亚洲/大洋洲官方镜像
- `--limit 12`：最多测试 12 个候选，加快收敛速度

默认行为：
- 自动选最优镜像
- 应用为单源
- 执行 `pkg update -y` 验证
- 验证成功后清理旧备份

## 分步使用（可控）
### 1) 查看官方候选镜像
```sh
/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts/benchmark_mirrors.sh --official --groups asia --list-official --limit 10
```

### 2) 执行测速并给出推荐
```sh
/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts/benchmark_mirrors.sh --official --groups asia,oceania --limit 12 -r 3
```

输出中会有：
- 每轮耗时和状态
- 汇总表（平均耗时、失败次数）
- `recommended <mirror>`

### 3) 应用推荐镜像并清理备份
```sh
/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts/apply_mirror.sh --cleanup-backups <recommended_mirror_base>
```

示例：
```sh
/data/data/com.termux/files/home/.codex/skills/termux-mirror-optimizer/scripts/apply_mirror.sh --cleanup-backups https://mirror.freedif.org/termux
```

## 验收标准
满足以下条件即可认为切换成功：
1. `pkg update -y` 无错误并返回 `All packages are up to date.` 或正常更新结果
2. `sources.list` / `root.list` 只保留目标单源
3. 若启用清理，输出 `cleanup_backups: removed=N`

## 注意事项
- 速度结论是“当前网络环境下”的结果，建议定期重测。
- 若你需要冗余容灾，可保留主 + 备双源；追求极致速度时优先单源。
- 遇到 TLS 握手错误，通常是镜像链路质量问题，优先换源而不是重复重试同一源。

## 本机本次实测结论
在本机本次测试中，`https://mirror.freedif.org/termux` 表现最佳且稳定，已作为默认单源。
