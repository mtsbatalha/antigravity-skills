#!/usr/bin/env python3
"""
Skills MCP Server - AI agents call these tools to discover and select relevant skills.

Tools exposed:
  - analyze_project: Scan a project directory and return recommended skills
  - select_skills:   Declare a tech stack and get matching skills
  - list_active:     Show currently active skills

Usage:
  # Run directly (stdio transport for Claude Code / Cursor / etc.)
  python mcp/skills_mcp.py
"""

import sys
import os
import json
from pathlib import Path

# Add scripts/ to path so we can reuse auto_activate logic
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from mcp.server.fastmcp import FastMCP
from auto_activate import (
    analyze_project,
    score_skills,
    load_catalog,
    load_common_skills,
    normalize_signal,
    ProjectContext,
    SKILLS_DIR,
    DISABLED_DIR,
    TECH_TO_SKILLS,
)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("skills_mcp")

CATALOG_PATH = REPO_ROOT / "data" / "catalog.json"
BUNDLES_PATH = REPO_ROOT / "data" / "bundles.json"
DEFAULT_THRESHOLD = 8
DEFAULT_MAX = 50


def _score_and_format(ctx, threshold=DEFAULT_THRESHOLD, max_skills=DEFAULT_MAX):
    """Shared scoring logic. Returns formatted result string."""
    catalog = load_catalog(CATALOG_PATH)
    common = load_common_skills(BUNDLES_PATH)
    scored = score_skills(ctx, catalog, common)

    selected = [s for s in scored if s.score >= threshold][:max_skills]

    if not selected:
        return "No matching skills found for the given context."

    lines = [f"Found {len(selected)} relevant skills:\n"]
    for s in selected:
        lines.append(f"  {s.id:45s} score={s.score:3d}  [{', '.join(s.reasons)}]")

    # Summary of detected signals
    signals = sorted(ctx.all_signals)
    lines.append(f"\nDetected signals: {', '.join(signals)}")
    lines.append(f"\nTo activate these skills, run:")
    lines.append(f'  python scripts/auto_activate.py --stack {" ".join(signals)} --yes')

    return "\n".join(lines)


def _get_active_skills():
    """List skills currently active on disk."""
    if not SKILLS_DIR.exists():
        return []
    return sorted([
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])


def _get_disabled_skills():
    """List skills currently disabled."""
    if not DISABLED_DIR.exists():
        return []
    return sorted([d.name for d in DISABLED_DIR.iterdir() if d.is_dir()])


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def analyze_project(project_path: str, max_skills: int = 50) -> str:
    """Analyze a project directory to discover its tech stack and recommend relevant skills.

    Use this when working on an existing project and you want to know which
    skills are available for the technologies used in that project.

    Args:
        project_path: Absolute path to the project directory to analyze.
        max_skills: Maximum number of skills to return (default 50).
    """
    target = Path(project_path).resolve()
    if not target.is_dir():
        return f"Error: '{project_path}' is not a valid directory."

    # Import the function with a different name to avoid recursion
    from auto_activate import analyze_project as _analyze
    ctx = _analyze(target)

    if ctx.is_empty():
        return f"No technologies detected in {project_path}."

    return _score_and_format(ctx, max_skills=max_skills)


@mcp.tool()
def select_skills(stack: list[str], max_skills: int = 50) -> str:
    """Given a list of technologies, return the most relevant skills.

    Use this when starting a new project or when you know the tech stack
    but don't have project files yet.

    Args:
        stack: List of technologies (e.g. ["react", "typescript", "next", "prisma", "docker"]).
        max_skills: Maximum number of skills to return (default 50).
    """
    if not stack:
        return "Error: provide at least one technology in the stack list."

    ctx = ProjectContext()
    for tech in stack:
        ctx.misc.add(normalize_signal(tech.lower()))

    return _score_and_format(ctx, max_skills=max_skills)


@mcp.tool()
def list_active_skills() -> str:
    """List all currently active and disabled skills.

    Use this to see which skills are available right now and which have
    been disabled by a previous focus operation.
    """
    active = _get_active_skills()
    disabled = _get_disabled_skills()

    lines = [f"Active skills: {len(active)}"]
    if len(active) <= 60:
        for s in active:
            lines.append(f"  * {s}")
    else:
        for s in active[:30]:
            lines.append(f"  * {s}")
        lines.append(f"  ... and {len(active) - 30} more")

    lines.append(f"\nDisabled skills: {len(disabled)}")
    if disabled and len(disabled) <= 30:
        for s in disabled:
            lines.append(f"  - {s}")
    elif disabled:
        lines.append(f"  (use 'python scripts/auto_activate.py restore' to re-enable)")

    # Show available tech keywords
    lines.append(f"\nAvailable tech keywords for select_skills:")
    keywords = sorted(TECH_TO_SKILLS.keys())
    lines.append(f"  {', '.join(keywords)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
