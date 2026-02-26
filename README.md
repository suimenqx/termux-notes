# termux-notes

Notes and practical learnings from tinkering in Termux on Android.

## Structure
- `notes/`: dated notes and troubleshooting logs
- `scripts/`: helper scripts for setup and maintenance

## Quick Start
```sh
git clone git@github.com:suimenqx/termux-notes.git
cd termux-notes
```

## Suggested Note Naming
Use date-first filenames for easy sorting:
- `notes/2026-02-27-initial-setup.md`
- `notes/2026-02-27-gh-and-ssh-agent.md`

## Useful Termux Commands
```sh
pkg update && pkg upgrade -y
pkg install git gh openssh zsh tmux neovim -y
termux-setup-storage
```
