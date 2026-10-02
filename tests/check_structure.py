"""Validate the plugin manifest and every skill's frontmatter and links."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

manifest = json.loads((ROOT / "plugin.json").read_text())
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", manifest.get("name", "")):
    errors.append("plugin.json: name must be kebab-case")
for field in ("description", "version"):
    if not manifest.get(field):
        errors.append(f"plugin.json: missing {field}")

market = json.loads((ROOT / ".github/plugin/marketplace.json").read_text())
entry = market["plugins"][0]
if entry["name"] != manifest["name"]:
    errors.append("marketplace.json: plugin name must match plugin.json")
if not (entry["version"] == market["metadata"]["version"] == manifest["version"]):
    errors.append("marketplace.json and plugin.json versions must match")
if entry["source"]["ref"] not in ("main", manifest["version"]):
    errors.append("marketplace.json: ref must be the released version tag")

skills = sorted(path.parent for path in (ROOT / manifest.get("skills", "skills/")).glob("*/SKILL.md"))
if not skills:
    errors.append("no skills found")

for skill in skills:
    text = (skill / "SKILL.md").read_text()
    front = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fields = dict(re.findall(r"^(\w+):\s*(.+)$", front.group(1), re.M)) if front else {}
    if fields.get("name") != skill.name:
        errors.append(f"{skill.name}: frontmatter name must match the directory")
    if not 40 <= len(fields.get("description", "")) <= 1024:
        errors.append(f"{skill.name}: description must be 40 to 1024 characters")
    for document in skill.rglob("*.md"):
        for target in re.findall(r"\]\((?!https?://|#)([^)#]+)", document.read_text()):
            if not (document.parent / target).exists():
                errors.append(f"{document.relative_to(ROOT)}: broken link {target}")
    for document in skill.rglob("*.md"):
        for named in set(re.findall(r"`((?:scripts|references|assets)/[\w./-]+)`", document.read_text())):
            if not (skill / named).exists():
                errors.append(f"{document.relative_to(ROOT)}: names missing {named}")
    for page in skill.rglob("*.html"):
        html = page.read_text()
        if re.search(r"""(?:src|href)=["'](?:https?:)?//""", html) or "@import" in html:
            errors.append(f"{page.relative_to(ROOT)}: loads an external resource")
        ids = re.findall(r"""\bid=["']([^"']+)""", html)
        if len(ids) != len(set(ids)):
            errors.append(f"{page.relative_to(ROOT)}: duplicate id")
        if 'data-theme="dark"' not in html or "prefers-color-scheme:dark" not in html:
            errors.append(f"{page.relative_to(ROOT)}: missing a dark theme")

for error in errors:
    print(error)
print(f"{len(skills)} skill(s) checked, {len(errors)} problem(s)")
sys.exit(1 if errors else 0)
