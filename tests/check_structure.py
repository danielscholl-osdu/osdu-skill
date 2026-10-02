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
    for reference in re.findall(r"scripts/[\w.-]+", text):
        if not (skill / reference).exists():
            errors.append(f"{skill.name}: SKILL.md names missing {reference}")

for error in errors:
    print(error)
print(f"{len(skills)} skill(s) checked, {len(errors)} problem(s)")
sys.exit(1 if errors else 0)
