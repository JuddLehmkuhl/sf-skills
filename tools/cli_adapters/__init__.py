"""
CLI Adapters for sf-skills Multi-CLI Installer.

This package provides adapters for transforming sf-skills to different
agentic coding CLI formats following the Agent Skills open standard.

Supported CLIs:
- OpenCode: .opencode/skill/{name}/ or .claude/skills/{name}/
- Codex CLI: .codex/skills/{name}/
- Gemini CLI: ~/.gemini/skills/{name}/
- Droid CLI: .factory/skills/{name}/ (Claude Code compatible)
- Cursor: .cursor/rules/{name}.mdc (MDC format)
- Agentforce Vibes: .clinerules/{name}.md (Salesforce's Cline fork)
"""

from .base import CLIAdapter, SkillOutput
from .opencode import OpenCodeAdapter
from .codex import CodexAdapter
from .gemini import GeminiAdapter
from .droid import DroidAdapter
from .cursor import CursorAdapter
from .cline import AgentforceVibesAdapter

# Registry of available adapters
ADAPTERS = {
    'opencode': OpenCodeAdapter,
    'codex': CodexAdapter,
    'gemini': GeminiAdapter,
    'droid': DroidAdapter,
    'cursor': CursorAdapter,
    'agentforce-vibes': AgentforceVibesAdapter,
}

__all__ = [
    'CLIAdapter',
    'SkillOutput',
    'OpenCodeAdapter',
    'CodexAdapter',
    'GeminiAdapter',
    'DroidAdapter',
    'CursorAdapter',
    'AgentforceVibesAdapter',
    'ADAPTERS',
]
