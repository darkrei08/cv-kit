"""Diagrams through Mermaid CLI.

A career timeline is the one graphic that earns its place on a CV: it shows
continuity, which is exactly what a long list of fixed-term contracts hides.

Mermaid CLI needs a browser to render. On a machine without Chrome installed, point
it at one with a Puppeteer configuration file (:func:`write_puppeteer_config`); the
file also needs the browser to be present, which on a bare machine means running
``npx puppeteer browsers install chrome`` once.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .theme import Palette

#: Base theme variables for generated diagrams, so the graphic matches the document
#: it will be printed in. The cScale* families matter: without them Mermaid assigns
#: its default pastel colours at random, which looks like a template.
_THEME = {
    "theme": "base",
    "timeline": {"disableMulticolor": True},
    "themeVariables": {
        "fontFamily": "Calibri, Segoe UI, Arial, sans-serif",
        "fontSize": "17px",
        "primaryColor": "#EEF3F7",
        "primaryTextColor": "#14395F",
        "primaryBorderColor": "#14395F",
        "secondaryColor": "#E3EDF3",
        "tertiaryColor": "#E3EDF3",
        "tertiaryTextColor": "#14395F",
        "lineColor": "#0F6E6E",
        "textColor": "#1F2933",
        "mainBkg": "#FFFFFF",
        "nodeBorder": "#14395F",
        "taskBorderColor": "#14395F",
        "taskBkgColor": "#EEF3F7",
        "taskTextColor": "#14395F",
        "taskTextLightColor": "#14395F",
        "taskTextOutsideColor": "#14395F",
        "activeTaskBorderColor": "#14395F",
        "activeTaskBkgColor": "#0F6E6E",
        "gridColor": "#C7D3DE",
        "todayLineColor": "#0F6E6E",
        **{f"cScale{i}": "#EEF3F7" for i in range(12)},
        **{f"cScaleInv{i}": "#14395F" for i in range(12)},
        **{f"cScaleLabel{i}": "#14395F" for i in range(12)},
    },
}


def _init_block(palette: Palette | None = None, font_size: int = 17) -> str:
    variables = dict(_THEME["themeVariables"])
    if palette:
        variables["primaryBorderColor"] = palette.primary
        variables["primaryTextColor"] = palette.primary
        variables["lineColor"] = palette.accent
        variables["taskBkgColor"] = palette.light
        variables["gridColor"] = palette.rule
    variables["fontSize"] = f"{font_size}px"
    init = {"theme": _THEME["theme"], "timeline": _THEME["timeline"],
            "themeVariables": variables}
    return "%%{init: " + json.dumps(init, separators=(",", ":")) + "}%%"


def find_mmdc() -> str | None:
    return shutil.which("mmdc") or shutil.which("mmdc.cmd")


def find_chrome() -> str | None:
    """Locate a Chromium-family browser Mermaid can drive."""
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("msedge")
    if found:
        return found
    roots = [
        os.path.expanduser("~/.cache/puppeteer"),
        os.path.expanduser("~/Library/Caches/ms-playwright"),
        os.path.expanduser("~/.cache/ms-playwright"),
        os.environ.get("LOCALAPPDATA", ""),
        "/usr/bin",
        "/usr/local/bin",
        "/opt/google/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS",
    ]
    names = ("chrome", "chrome.exe", "chromium", "chromium-browser", "msedge.exe",
             "Google Chrome")
    for root in filter(None, roots):
        root_path = Path(root)
        if not root_path.exists():
            continue
        for name in names:
            direct = root_path / name
            if direct.is_file():
                return str(direct)
        for candidate in root_path.rglob(names[0] + "*"):
            if candidate.is_file() and candidate.name in names:
                return str(candidate)
    return None


def cache_dir() -> Path:
    """A per-user cache directory, per platform convention.

    Generated tool configuration belongs here rather than next to the documents: a
    Puppeteer configuration file contains an absolute path to the browser and, on a
    shared or exported output folder, that is a small piece of information about the
    machine that produced the files.
    """
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\.cache")
    elif sys_platform() == "darwin":
        base = os.path.expanduser("~/Library/Caches")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    path = Path(base) / "cvkit"
    path.mkdir(parents=True, exist_ok=True)
    return path


def sys_platform() -> str:
    import sys
    return sys.platform


def write_puppeteer_config(path: str | Path, chrome: str | None = None) -> Path:
    """Write the JSON file Mermaid CLI needs to find a browser.

    Uses forward slashes in the path: a Windows path with backslashes is not valid
    JSON unless they are escaped, and Node accepts forward slashes on every system.
    """
    chrome = chrome or find_chrome()
    if not chrome:
        raise RuntimeError(
            "no Chromium-family browser found.\n"
            "Install one, or run: npx -y puppeteer browsers install chrome"
        )
    config = {
        "executablePath": str(chrome).replace("\\", "/"),
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    path = Path(path)
    path.write_text(json.dumps(config, indent=1), encoding="utf-8")
    return path


def timeline_source(entries, title: str | None = None) -> str:
    """Build Mermaid source for a career timeline.

    ``entries`` is a sequence of ``(label, description)`` pairs, in the order they
    should appear. Colons inside a label break the Mermaid grammar, so they are
    replaced.
    """
    lines = [_init_block()]
    lines.append("timeline")
    if title:
        lines.append(f"    title {title.replace(':', ' -')}")
    for label, description in entries:
        safe_label = str(label).replace(":", " -")
        safe_description = str(description).replace(":", " -").replace("\n", " ")
        lines.append(f"    {safe_label} : {safe_description}")
    return "\n".join(lines) + "\n"


def render_mermaid(source: str, out_png: str | Path, *, source_path: str | Path | None = None,
                   width: int = 1500, scale: int = 3, background: str = "white",
                   puppeteer_config: str | Path | None = None) -> Path:
    """Render Mermaid source to a PNG. Returns the PNG path."""
    mmdc = find_mmdc()
    if not mmdc:
        raise RuntimeError("Mermaid CLI not found. Install it with:\n"
                           "  npm install -g @mermaid-js/mermaid-cli")
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    source_path = Path(source_path) if source_path else out_png.with_suffix(".mmd")
    source_path.write_text(source, encoding="utf-8")

    if puppeteer_config is None:
        candidate = cache_dir() / "puppeteer.json"
        if not candidate.exists() and find_chrome():
            write_puppeteer_config(candidate)
        puppeteer_config = candidate if candidate.exists() else None

    command = [mmdc, "-i", str(source_path), "-o", str(out_png),
               "-b", background, "-s", str(scale), "-w", str(width)]
    if puppeteer_config:
        command += ["-p", str(puppeteer_config)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if not out_png.exists():
        raise RuntimeError(
            "Mermaid rendering failed.\n" + (result.stderr or result.stdout or "")[:600])
    return out_png
