#!/usr/bin/env python3
"""MCP server for Claude Code Desktop documentation."""

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DOCS_PATH = Path(__file__).parent / "desktop.mdx"

mcp = FastMCP("claude-code-desktop-docs")


def _load_docs() -> str:
    return DOCS_PATH.read_text(encoding="utf-8")


def _extract_sections(content: str) -> dict[str, str]:
    """Parse markdown into a dict of {heading: section_content}."""
    sections: dict[str, str] = {}
    current_heading = "Introduction"
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


@mcp.resource("docs://desktop.mdx")
def get_full_docs() -> str:
    """Return the full Claude Code Desktop documentation."""
    return _load_docs()


@mcp.resource("docs://sections")
def list_sections() -> str:
    """List all section headings in the documentation."""
    sections = _extract_sections(_load_docs())
    return "\n".join(f"- {heading}" for heading in sections)


@mcp.tool()
def search_docs(query: str) -> str:
    """Search the Claude Code Desktop documentation for a query string.

    Args:
        query: The text to search for (case-insensitive).
    """
    content = _load_docs()
    lines = content.splitlines()
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    matches: list[str] = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = "\n".join(lines[start:end])
            matches.append(f"[Line {i + 1}]\n{context}")

    if not matches:
        return f"No results found for '{query}'."

    return f"Found {len(matches)} match(es) for '{query}':\n\n" + "\n\n---\n\n".join(matches)


@mcp.tool()
def get_section(heading: str) -> str:
    """Retrieve a specific section from the documentation by its heading.

    Args:
        heading: The section heading to retrieve (case-insensitive partial match).
    """
    sections = _extract_sections(_load_docs())
    heading_lower = heading.lower()

    # Exact match first
    for key, value in sections.items():
        if key.lower() == heading_lower:
            return f"## {key}\n\n{value}"

    # Partial match
    matches = [(key, value) for key, value in sections.items() if heading_lower in key.lower()]
    if not matches:
        available = "\n".join(f"- {k}" for k in sections)
        return f"Section '{heading}' not found.\n\nAvailable sections:\n{available}"

    if len(matches) == 1:
        key, value = matches[0]
        return f"## {key}\n\n{value}"

    results = [f"## {key}\n\n{value}" for key, value in matches]
    return f"Found {len(matches)} matching sections:\n\n" + "\n\n---\n\n".join(results)


@mcp.tool()
def list_features() -> str:
    """List the main features of Claude Code Desktop."""
    content = _load_docs()
    # Extract bullet points from the intro
    lines = content.splitlines()
    features: list[str] = []
    in_intro = False
    for line in lines:
        if "Desktop adds these capabilities" in line:
            in_intro = True
            continue
        if in_intro:
            if line.startswith("*") or line.startswith("-"):
                features.append(line.lstrip("*- ").strip())
            elif line.strip() == "" and features:
                continue
            elif features:
                break

    if features:
        return "Claude Code Desktop features:\n" + "\n".join(f"• {f}" for f in features)
    return "Could not extract features list."


if __name__ == "__main__":
    mcp.run()
