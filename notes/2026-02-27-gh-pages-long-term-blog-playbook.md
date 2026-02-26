# GH CLI + GitHub Pages: 长期博客实践总结（2026-02-27）

## 目标
在 Termux 环境下，用 `gh` CLI 搭建一个可长期维护的个人博客发布链路，做到：
- 本地只写 Markdown
- push 后自动部署
- 出问题可快速定位和修复

## 一次性搭建路径
1. 完成 `gh` 登录并确认 token 可用。  
2. 将仓库 Git 协议切到 SSH，保证后续推送稳定。  
3. 在仓库加入 `mkdocs.yml` 与 Pages workflow。  
4. 首次启用仓库 Pages（`build_type=workflow`）。  
5. push 触发 Actions，验证部署 URL 可访问。

## 核心命令（可复用）
```sh
# 认证

gh auth login -h github.com
gh auth status
gh api user --jq '.login, .html_url'

# Git 协议

gh config set git_protocol ssh --host github.com
gh auth setup-git
ssh -T -o StrictHostKeyChecking=accept-new git@github.com

# Pages 状态与启用

gh api repos/<owner>/<repo>/pages
gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow

# workflow 观察

gh run list -R <owner>/<repo> --limit 5
gh run view <run_id> -R <owner>/<repo> --log-failed
gh run watch <run_id> -R <owner>/<repo> --exit-status
```

## 本次踩坑与修复
### 1) 站点 404
现象：Pages URL 访问 404。  
原因：仓库未真正启用 Pages 站点。  
修复：用 `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow` 创建站点。

### 2) Actions 无法创建 Pages
现象：`configure-pages` 报 `Resource not accessible by integration`。  
原因：默认 `GITHUB_TOKEN` 在该仓库上下文无“首次创建 Pages”权限。  
修复：在仓库层先启用 Pages，再让 workflow 执行部署。

### 3) MkDocs strict 模式失败
现象：`mkdocs build --strict` 因 warning 直接失败。  
原因：`notes/README.md` 与 `notes/index.md` 路径冲突。  
修复：重命名 `notes/README.md` 为 `notes/notes-guide.md`。

## 长期维护建议
- 保持 `mkdocs build --strict`，让潜在问题在 CI 提前暴露。  
- 每次新增笔记时，同时更新 `notes/index.md` 与 `mkdocs.yml` 的 nav。  
- 保留 `gh run view --log-failed` 作为首选排错入口。  
- 对首次启用类操作（Pages、环境权限）优先在仓库设置层确认，避免反复重跑 CI。

## 推荐的日常发布流程
1. 新建笔记：`notes/YYYY-MM-DD-topic.md`。  
2. 更新目录导航。  
3. `git add && git commit && git push`。  
4. `gh run watch` 等待部署完成。  
5. 检查线上 URL 与最近一次改动是否一致。

## 当前站点
- Blog URL: https://suimenqx.github.io/termux-notes/
- 部署方式：GitHub Actions + GitHub Pages（workflow）
