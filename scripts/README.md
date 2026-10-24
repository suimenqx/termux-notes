# Scripts

Place reusable shell scripts here, such as:
- environment bootstrap
- package update helpers
- backup helpers

## Codex Termux launcher checks

```sh
python scripts/check-codex-termux-launchers.py
# Optional: specify another installed or unpacked package root
python scripts/check-codex-termux-launchers.py /path/to/package
```

Requires Termux Python, Node.js and sh. Copies the four launchers to a temporary
path with spaces and checks package provenance, native binary selection and
argument forwarding, with both absent and stale inherited package roots. Does
not call a model, read credentials or modify the installation.

`codex-termux-provenance.patch` fixes the missing `CODEX_MANAGED_PACKAGE_ROOT`
marker in `@mmmbuto/codex-cli-termux@0.163.0-termux.2`. This is a local packaging
fix, not an official release. Back up the launchers and use a dry-run before
applying; do not apply blindly to newer versions. npm reinstalls overwrite it.
See the [update and troubleshooting note](../notes/2026-10-24-codex-termux-update-and-health-check.md)
for commands, real-model tests and daemon recovery.
