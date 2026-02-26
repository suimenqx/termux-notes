# GH CLI and SSH Agent on Termux (2026-02-27)

## Context
Set up GitHub CLI workflow on Android Termux and verify repository operations.

## Goals
- Install and verify `gh`
- Re-authenticate GitHub account
- Switch Git protocol to SSH
- Validate SSH connectivity
- Create and initialize a practical notes repository

## Commands Run
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

## Key Results
- `gh` available and working (`2.87.3` at setup time)
- GitHub authentication refreshed successfully
- Git operations protocol switched to `ssh`
- SSH connectivity confirmed (`successfully authenticated`)
- Repository created: `https://github.com/suimenqx/termux-notes`

## Local Layout Decision
Repositories should live under:
- `/data/data/com.termux/files/home/github`

This avoids clutter under `$HOME` and keeps project paths consistent.

## Issue Encountered
Git reported `dubious ownership` after moving repo into shared storage path.

### Fix
```sh
git config --global --add safe.directory /storage/emulated/0/xin/code/github/termux-notes
```

## Follow-up
- Add reusable setup script under `scripts/`.
- Add notes for package maintenance and backup strategy.
