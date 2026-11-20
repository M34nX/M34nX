from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")
readme = (root / "README.md").read_text(encoding="utf-8")
required = ["BlackTermux", "M34nX/BlackTermux", "termux/termux-app", 'id="stars"', 'id="forks"', 'id="issues"', 'id="sync-status"', "prefers-reduced-motion", "aria-label"]
missing = [item for item in required if item not in html]
if missing:
    print("FAIL: missing required site content: " + ", ".join(missing))
    sys.exit(1)
if "Termux-Shizuku-Bridge" in html or "DIGITAL EMPIRE" in html:
    print("FAIL: unrelated profile-project content remains in the site")
    sys.exit(1)
scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.I | re.S)
if len(scripts) != 1:
    print(f"FAIL: expected one inline script, found {len(scripts)}")
    sys.exit(1)
check = subprocess.run(["node", "--check"], input=scripts[0], text=True, capture_output=True)
if check.returncode:
    print("FAIL: JavaScript syntax check")
    print(check.stderr)
    sys.exit(check.returncode)
if "M34nX/BlackTermux" not in readme or "termux/termux-app" not in readme or "exclusive features" not in readme:
    print("FAIL: README must explain the project and current fork status")
    sys.exit(1)
if re.search(r"gh[pousr]_[A-Za-z0-9]{20,}", html + readme):
    print("FAIL: possible embedded GitHub token")
    sys.exit(1)
print("PASS: BlackTermux project identity and links")
print("PASS: unrelated project sections removed")
print("PASS: JavaScript syntax")
print("PASS: current-state transparency")
print("PASS: no obvious embedded GitHub token")
