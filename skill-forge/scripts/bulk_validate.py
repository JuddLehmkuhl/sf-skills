#!/usr/bin/env python3
"""
Bulk validation for all installed Claude Code skills.

Discovers skills in ~/.claude/skills/ (including nested directories like
sf-skills/, mulesoft/, custom/) and project-local .claude/skills/, then
validates each using Anthropic's official validation rules.

Usage:
    python3 bulk_validate.py [--errors-only] [--format json]
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the canonical validator
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from validate_skill import validate_skill


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'


def discover_skills():
    """
    Discover all skills in global and project-specific locations.
    Handles both flat layouts (skill-name/SKILL.md) and nested layouts
    (sf-skills/skill-name/SKILL.md).

    Returns list of (skill_path, location_type) tuples.
    """
    skills = []

    # Global skills (~/.claude/skills/) — search recursively
    global_dir = Path.home() / ".claude" / "skills"
    if global_dir.exists():
        for skill_md in global_dir.rglob("SKILL.md"):
            # Skip if inside a .git directory
            if ".git" in skill_md.parts:
                continue
            skills.append((skill_md.parent, "global"))

    # Project-local skills (./.claude/skills/)
    project_dir = Path.cwd() / ".claude" / "skills"
    if project_dir.exists():
        for skill_md in project_dir.rglob("SKILL.md"):
            if ".git" in skill_md.parts:
                continue
            skills.append((skill_md.parent, "project"))

    return skills


def validate_one(skill_path, location_type):
    """Validate a single skill, returning structured result."""
    name = skill_path.name
    valid, message = validate_skill(skill_path)
    return {
        "name": name,
        "path": str(skill_path),
        "location": location_type,
        "valid": valid,
        "message": message,
    }


def run_bulk(parallel=True):
    """Discover and validate all skills."""
    start = datetime.now()
    skills = discover_skills()
    results = []

    if parallel and len(skills) > 1:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(validate_one, path, loc): (path, loc)
                for path, loc in skills
            }
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    path, loc = futures[future]
                    results.append({
                        "name": path.name,
                        "path": str(path),
                        "location": loc,
                        "valid": False,
                        "message": f"Exception: {e}",
                    })
    else:
        for path, loc in skills:
            results.append(validate_one(path, loc))

    duration = (datetime.now() - start).total_seconds()
    results.sort(key=lambda r: (r["valid"], r["name"]))

    return {
        "total": len(results),
        "valid": sum(1 for r in results if r["valid"]),
        "invalid": sum(1 for r in results if not r["valid"]),
        "duration_seconds": round(duration, 2),
        "results": results,
    }


def print_console(report, errors_only=False):
    """Print a console report."""
    c = Colors
    total = report["total"]
    valid = report["valid"]
    invalid = report["invalid"]

    print(f"\n{c.MAGENTA}{c.BOLD}{'='*58}{c.NC}")
    print(f"{c.MAGENTA}{c.BOLD}  Skill Forge — Bulk Validation Report{c.NC}")
    print(f"{c.MAGENTA}{c.BOLD}{'='*58}{c.NC}\n")

    print(f"  Total:   {total} skills discovered")
    print(f"  {c.GREEN}Valid:   {valid} ({valid*100//max(total,1)}%){c.NC}")
    if invalid:
        print(f"  {c.RED}Invalid: {invalid} ({invalid*100//max(total,1)}%){c.NC}")
    print(f"  Time:    {report['duration_seconds']}s\n")

    # Invalid skills
    invalid_results = [r for r in report["results"] if not r["valid"]]
    if invalid_results:
        print(f"{c.RED}{c.BOLD}  Failed ({len(invalid_results)}):{c.NC}")
        for r in invalid_results:
            print(f"    {c.RED}✗{c.NC} {r['name']:30s} {c.CYAN}[{r['location']}]{c.NC}")
            print(f"      {r['message']}")
        print()

    # Valid skills
    if not errors_only:
        valid_results = [r for r in report["results"] if r["valid"]]
        if valid_results:
            print(f"{c.GREEN}{c.BOLD}  Passed ({len(valid_results)}):{c.NC}")
            for r in valid_results:
                print(f"    {c.GREEN}✓{c.NC} {r['name']:30s} {c.CYAN}[{r['location']}]{c.NC}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Bulk validate all Claude Code skills")
    parser.add_argument("--errors-only", action="store_true", help="Show only failures")
    parser.add_argument("--format", choices=["console", "json"], default="console")
    parser.add_argument("--no-parallel", action="store_true", help="Sequential validation")
    args = parser.parse_args()

    report = run_bulk(parallel=not args.no_parallel)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print_console(report, errors_only=args.errors_only)

    sys.exit(0 if report["invalid"] == 0 else 1)


if __name__ == "__main__":
    main()
