#!/data/data/com.termux/files/usr/bin/python
"""Check launcher provenance without calling a model or changing the installation."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    prefix = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "package_root",
        nargs="?",
        type=Path,
        default=prefix / "lib/node_modules/@mmmbuto/codex-cli-termux",
    )
    package = parser.parse_args().package_root.resolve()
    launchers = ("codex.js", "codex-exec.js", "codex", "codex-exec")
    failures = []

    with tempfile.TemporaryDirectory(prefix="codex-launcher-test-") as tmp:
        # Spaces catch quoting errors in both the JS and shell launchers.
        fixture = Path(tmp) / "package with spaces"
        bin_dir = fixture / "bin"
        bin_dir.mkdir(parents=True)
        (fixture / "package.json").write_text('{"type":"module"}\n')
        for name in launchers:
            shutil.copy2(package / "bin" / name, bin_dir / name)
        binary = bin_dir / "codex.bin"
        binary.write_text(
            f"#!{prefix}/bin/sh\n"
            'printf "%s\\n" "${CODEX_MANAGED_PACKAGE_ROOT-}" '
            '"${CODEX_SELF_EXE-}" "${CODEX_MANAGED_BY_NPM-}" "$@"\n'
        )
        binary.chmod(0o700)

        for name in launchers:
            for inherited in (None, "/stale/package/root"):
                env = os.environ.copy()
                env.pop("CODEX_MANAGED_PACKAGE_ROOT", None)
                if inherited:
                    env["CODEX_MANAGED_PACKAGE_ROOT"] = inherited
                try:
                    result = subprocess.run(
                        [str(bin_dir / name), "--version"],
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                        env=env,
                        timeout=10,
                    )
                    expected = [str(fixture), str(binary), "1"]
                    if name.startswith("codex-exec"):
                        expected.append("exec")
                    expected.append("--version")
                    ok = result.returncode == 0 and result.stdout.splitlines() == expected
                except (OSError, subprocess.TimeoutExpired):
                    ok = False
                case = f"{name} (inherited root: {'stale' if inherited else 'absent'})"
                print(f"{'PASS' if ok else 'FAIL'} {case}")
                if not ok:
                    failures.append(case)

    print(f"{8 - len(failures)}/8 launcher checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
