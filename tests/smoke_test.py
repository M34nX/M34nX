from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
html_path = root / "index.html"
html = html_path.read_text(encoding="utf-8")

required_ids = [
    "stars", "orb", "repos", "followers", "following", "gists",
    "repo-list", "languages", "projects-list", "term-form",
    "term-input", "term-output", "themeBtn", "soundBtn", "topBtn",
]
missing = [item for item in required_ids if not re.search(r'id=["\\']' + re.escape(item) + r'["\\']', html)]
if missing:
    print("FAIL: missing required DOM ids: " + ", ".join(missing))
    sys.exit(1)

modules = re.findall(
    r'<script\\s+type=["\\']module["\\']\\s*>(.*?)</script>',
    html,
    flags=re.IGNORECASE | re.DOTALL,
)
if len(modules) != 1:
    print(f"FAIL: expected exactly one inline module script, found {len(modules)}")
    sys.exit(1)

check = subprocess.run(
    ["node", "--check", "--input-type=module"],
    input=modules[0],
    text=True,
    capture_output=True,
)
if check.returncode:
    print("FAIL: JavaScript module syntax check failed")
    print(check.stderr)
    sys.exit(check.returncode)

checks = {
    "public GitHub API integration": "https://api.github.com/users/" in html,
    "safe terminal output escaping": "function escapeHtml" in html,
    "terminal form handling": "term-form').addEventListener('submit'" in html,
    "reduced-motion support": "prefers-reduced-motion: reduce" in html,
    "no embedded personal access token": not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}', html),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAIL: " + ", ".join(failed))
    sys.exit(1)

print("PASS: required interface elements")
print("PASS: JavaScript module syntax")
for name in checks:
    print("PASS: " + name)
print("NOTE: these are static smoke tests; browser rendering and live API behavior still require a real browser.")
