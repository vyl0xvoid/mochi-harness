"""Reject private paths, secret-like prefixes, binary blobs, and unsafe names."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials",
    "secrets",
}
FORBIDDEN_SUFFIXES = {".key", ".pem", ".p12", ".mochibak"}
PATTERNS = {
    "absolute macOS home path": re.compile("/" + r"Users/[A-Za-z0-9._-]+/"),
    "absolute Linux home path": re.compile("/" + r"home/[A-Za-z0-9._-]+/"),
    "private key block": re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub classic token": re.compile("gh" + r"p_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
    "OpenAI-style secret": re.compile("sk" + r"-[A-Za-z0-9_-]{20,}"),
    "Slack-style token": re.compile("xo" + r"x[baprs]-[A-Za-z0-9-]{10,}"),
    "AWS access key": re.compile("AK" + r"IA[0-9A-Z]{16}"),
}


def tracked_files() -> tuple[Path, ...]:
    result = subprocess.run(
        ("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"),
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return tuple(
        ROOT / entry.decode("utf-8")
        for entry in result.stdout.split(b"\0")
        if entry
    )


def main() -> int:
    failures: list[str] = []
    files = tracked_files()
    for path in files:
        relative = path.relative_to(ROOT)
        lowered = path.name.lower()
        if lowered in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"unsafe tracked filename: {relative}")
        payload = path.read_bytes()
        if b"\0" in payload:
            failures.append(f"binary tracked file: {relative}")
            continue
        text = payload.decode("utf-8")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label}: {relative}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print(f"Privacy scan passed for {len(files)} public-candidate text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
