import os
from pathlib import Path

# ==========================
# Configuration
# ==========================

ROOT = Path.cwd()          # Run from your Django project root
OUTPUT = "project_context.md"

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "media",
    "staticfiles",
    ".pytest_cache",
    ".mypy_cache",
}

EXCLUDED_FILES = {
    "db.sqlite3",
}

EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".webp",
    ".pdf",
    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".pyc",
    ".sqlite3",
    ".db",
}

MAX_SIZE = 300000  # Skip files over 300 KB

LANGUAGE_MAP = {
    ".py": "python",
    ".html": "html",
    ".css": "css",
    ".js": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".txt": "text",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".ini": "ini",
    ".env": "",
    ".sql": "sql",
    ".bat": "bat",
    ".ps1": "powershell",
    ".sh": "bash",
}


def should_skip(path: Path):
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True

    if path.name in EXCLUDED_FILES:
        return True

    if path.suffix.lower() in EXCLUDED_EXTENSIONS:
        return True

    try:
        if path.stat().st_size > MAX_SIZE:
            return True
    except Exception:
        return True

    return False


def make_tree(root):
    lines = []

    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted([d for d in dirs if d not in EXCLUDED_DIRS])

        rel = Path(current_root).relative_to(root)
        level = len(rel.parts)

        if rel.parts:
            lines.append("    " * level + f"📁 {rel.name}")
        else:
            lines.append(f"📁 {root.name}")

        for file in sorted(files):
            path = Path(current_root) / file

            if should_skip(path):
                continue

            lines.append("    " * (level + 1) + f"📄 {file}")

    return "\n".join(lines)


with open(OUTPUT, "w", encoding="utf-8") as out:

    out.write(f"# Project Context: {ROOT.name}\n\n")

    out.write(
        "This file contains a snapshot of the project's source code for AI analysis.\n\n"
    )

    out.write("## Project Structure\n\n")
    out.write("```text\n")
    out.write(make_tree(ROOT))
    out.write("\n```\n\n")

    out.write("---\n\n")

    for file in sorted(ROOT.rglob("*")):

        if not file.is_file():
            continue

        if should_skip(file):
            continue

        rel = file.relative_to(ROOT)

        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = file.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue

        lang = LANGUAGE_MAP.get(file.suffix.lower(), "")

        out.write(f"# FILE: `{rel}`\n\n")

        out.write("```" + lang + "\n")
        out.write(text.rstrip())
        out.write("\n```\n\n")

        out.write("---\n\n")

print(f"\n✅ Export complete!\nSaved to: {OUTPUT}")