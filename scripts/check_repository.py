"""Check publishable files for local state, obvious credentials and broken links."""
import argparse
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DIRS = {".venv", "venv", "__pycache__", ".pytest_cache", ".langgraph_api", ".idea", ".vscode"}
LOCAL_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".pyc", ".pem", ".key", ".p12", ".pfx"}
TEXT_SUFFIXES = {".py", ".md", ".sql", ".json", ".yml", ".yaml", ".toml", ".txt", ".mmd", ".svg"}
TOKEN = re.compile(r"(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
LINK = re.compile(r"!?\[[^\]]*\]\(([^\s)]+)\)")


def git(*args):
    env = os.environ.copy()
    # The project root is resolved from this script, scoped to this Git call,
    # and never saved in the user's global Git configuration.
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "safe.directory"
    env["GIT_CONFIG_VALUE_0"] = str(ROOT)
    return subprocess.check_output(["git", *args], cwd=ROOT, env=env)


def check(staged=False):
    args = ["ls-files", "--cached", "-z"]
    if not staged:
        args += ["--others", "--exclude-standard"]
    names = sorted(set(git(*args).decode("utf-8").strip("\0").split("\0")) - {""})
    if not names:
        raise ValueError("No publishable files found; initialize Git or stage the project first")
    problems = []
    text_files = {}
    total = 0
    for name in names:
        path = PurePosixPath(name)
        if (set(path.parts) & LOCAL_DIRS or path.suffix in LOCAL_SUFFIXES
                or (path.name.startswith(".env") and path.name != ".env.example")
                or (path.parts[0] == "data" and name != "data/.gitkeep")
                or re.search(r"\.(?:db|sqlite3?)-(?:wal|shm|journal)$", name)):
            problems.append(f"{name}: local state or credential file must be excluded")
        content = git("show", ":" + name) if staged else (ROOT / name).read_bytes()
        total += len(content)
        if len(content) > 5 * 1024 * 1024:
            problems.append(f"{name}: file exceeds the project's 5 MiB review threshold")
        if path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", ".env.example"}:
            text = content.decode("utf-8-sig")
            text_files[name] = text
            if TOKEN.search(text):
                problems.append(f"{name}: possible credential; value omitted")
    for name, text in text_files.items():
        if not name.endswith(".md"):
            continue
        # Code samples contain illustrative paths rather than documentation links.
        prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for match in LINK.finditer(prose):
            link = urlsplit(match.group(1))
            if link.scheme or link.netloc or not link.path:
                continue
            target = (ROOT / name).parent / unquote(link.path)
            try:
                relative = target.resolve().relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                problems.append(f"{name}: link leaves repository: {link.path}")
                continue
            if relative not in names and not any(n.startswith(relative.rstrip('/') + '/') for n in names):
                problems.append(f"{name}: link target is not publishable: {link.path}")
    if problems:
        raise ValueError("\n".join(problems))
    mode = "staged" if staged else "publishable working-tree"
    print(f"PASS: {len(names)} {mode} files, {total / 1024:.1f} KiB; local links and credential-pattern checks passed.")
    print("This check does not replace reviewing the diff or GitHub's secret scanning.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect index blobs exactly as they would be committed")
    try:
        check(parser.parse_args().staged)
    except (ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
