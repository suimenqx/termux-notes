# Termux 下配置 GH CLI 与 SSH Agent（2026-02-27）

## 背景
目标是在 Android Termux 中打通 GitHub CLI 工作流，并验证仓库创建与 SSH 推送链路可用。

## 目标
- 安装并验证 `gh`
- 重新完成 GitHub 认证
- 将 Git 协议切换到 SSH
- 验证 SSH 连通性
- 创建并初始化 `termux-notes` 仓库

## 执行命令
```sh
pkg install -y gh
gh --version
gh auth status
gh auth login -h github.com
gh api user --jq '.login, .html_url'
gh config set git_protocol ssh --host github.com
gh auth setup-git
ssh -T -o StrictHostKeyChecking=accept-new git@github.com
gh repo create termux-notes --public --description "Notes and practical learnings from tinkering in Termux on Android" --clone
```

## 结果
- `gh` 可用并工作正常（配置时为 `2.87.3`）
- GitHub 账号认证刷新成功
- Git 协议已切换为 `ssh`
- SSH 握手成功（`successfully authenticated`）
- 仓库创建完成：<https://github.com/suimenqx/termux-notes>

## 路径规范决策
仓库统一放在：
- `/data/data/com.termux/files/home/github`

这样可以避免 `$HOME` 根目录变乱，也便于长期维护。

## 遇到的问题
仓库迁移到共享存储路径后，Git 报错 `dubious ownership`。

### 修复方式
```sh
git config --global --add safe.directory /storage/emulated/0/xin/code/github/termux-notes
```

## 后续计划
- 在 `scripts/` 下增加可复用初始化脚本
- 补充包维护和备份策略笔记
