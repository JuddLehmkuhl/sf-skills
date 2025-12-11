#!/usr/bin/env python3
"""
Agent Script Validator for sf-agentforce skill.
Validates Agent Script syntax and best practices.
Scoring: 100 points across 6 categories.

Updated to match official Salesforce Agent Script syntax (Dec 2025):
- Uses agent_name (not developer_name)
- Uses 3-space indentation (not 4-space!)
- Uses instructions: -> (space before arrow)
- Requires label: for all topics
- Requires linked variables (EndUserId, RoutableId, ContactId)
- Requires language: block
- File extension should be .agent (not .agentscript)
"""

import re
import sys
from typing import Dict, List, Any, Optional


class AgentScriptValidator:
    """Validates Agent Script files against best practices."""

    # Required top-level blocks
    REQUIRED_BLOCKS = ["config", "system", "start_agent"]

    # Valid resource prefixes
    VALID_RESOURCES = ["@variables", "@actions", "@topic", "@outputs", "@utils"]

    # Valid variable types
    VALID_TYPES = ["string", "number", "boolean", "list", "object"]

    # Valid action targets
    VALID_TARGETS = ["flow://", "apex://"]

    # Required linked variables for messaging context
    REQUIRED_LINKED_VARS = ["EndUserId", "RoutableId", "ContactId"]

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.scores: Dict[str, Dict[str, int]] = {
            "Structure & Syntax": {"score": 20, "max": 20},
            "Topic Design": {"score": 20, "max": 20},
            "Action Integration": {"score": 20, "max": 20},
            "Variable Management": {"score": 15, "max": 15},
            "Instructions Quality": {"score": 15, "max": 15},
            "Security & Guardrails": {"score": 10, "max": 10},
        }

    def validate(self, content: str, file_path: str = "") -> Dict[str, Any]:
        """
        Validate Agent Script content.

        Args:
            content: The Agent Script content to validate
            file_path: Optional file path for context

        Returns:
            Dictionary with score, categories, and issues
        """
        self.issues = []
        # Reset scores
        for category in self.scores:
            self.scores[category]["score"] = self.scores[category]["max"]

        lines = content.split("\n")

        # Run all validations
        self._validate_file_extension(file_path)
        self._validate_indentation(lines)
        self._validate_blocks(content, lines)
        self._validate_config(content)
        self._validate_language(content)
        self._validate_topics(content, lines)
        self._validate_variables(content, lines)
        self._validate_linked_variables(content)
        self._validate_actions(content, lines)
        self._validate_instructions(content, lines)
        self._validate_security(content, lines)
        self._validate_references(content)

        # Calculate total score
        total_score = sum(cat["score"] for cat in self.scores.values())
        max_score = sum(cat["max"] for cat in self.scores.values())

        return {
            "score": total_score,
            "max_score": max_score,
            "categories": self.scores,
            "issues": self.issues,
            "file_path": file_path,
        }

    def _add_issue(
        self,
        category: str,
        message: str,
        severity: str = "warning",
        line: Optional[int] = None,
        deduction: int = 0,
    ):
        """Add a validation issue and apply score deduction."""
        self.issues.append({
            "category": category,
            "message": message,
            "severity": severity,
            "line": line,
        })

        if deduction > 0 and category in self.scores:
            self.scores[category]["score"] = max(
                0, self.scores[category]["score"] - deduction
            )

    def _validate_file_extension(self, file_path: str):
        """Validate file extension is .agent (preferred) not .agentscript."""
        if file_path and file_path.endswith(".agentscript"):
            self._add_issue(
                "Structure & Syntax",
                "File extension should be .agent (not .agentscript)",
                "warning",
                deduction=2,
            )

    def _validate_indentation(self, lines: List[str]):
        """Validate that indentation uses 3 spaces (not tabs, not 4 spaces)."""
        for i, line in enumerate(lines, 1):
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check for tabs
            if "\t" in line:
                self._add_issue(
                    "Structure & Syntax",
                    "Use spaces, not tabs for indentation",
                    "error",
                    line=i,
                    deduction=3,
                )

            # Check indentation level
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                # Indentation should be multiples of 3
                if leading_spaces % 3 != 0:
                    # Check if it's the common 4-space mistake
                    if leading_spaces % 4 == 0 and leading_spaces % 3 != 0:
                        self._add_issue(
                            "Structure & Syntax",
                            f"Use 3-space indentation, found {leading_spaces} spaces (likely 4-space)",
                            "error",
                            line=i,
                            deduction=3,
                        )
                    else:
                        self._add_issue(
                            "Structure & Syntax",
                            f"Indentation should be multiples of 3, found {leading_spaces} spaces",
                            "warning",
                            line=i,
                            deduction=1,
                        )

    def _validate_blocks(self, content: str, lines: List[str]):
        """Validate required blocks are present."""
        # Check for config block
        if not re.search(r"^config:", content, re.MULTILINE):
            self._add_issue(
                "Structure & Syntax",
                "Missing required 'config:' block",
                "error",
                deduction=5,
            )

        # Check for system block
        if not re.search(r"^system:", content, re.MULTILINE):
            self._add_issue(
                "Structure & Syntax",
                "Missing required 'system:' block",
                "error",
                deduction=5,
            )

        # Check for start_agent block
        if not re.search(r"^start_agent\s+\w+:", content, re.MULTILINE):
            self._add_issue(
                "Structure & Syntax",
                "Missing required 'start_agent' entry point",
                "error",
                deduction=5,
            )

    def _validate_config(self, content: str):
        """Validate config block has correct fields."""
        # Check for agent_name (correct) vs developer_name (incorrect)
        if re.search(r"developer_name:", content) and not re.search(r"agent_name:", content):
            self._add_issue(
                "Structure & Syntax",
                "Use 'agent_name:' instead of 'developer_name:' in config block",
                "error",
                deduction=5,
            )

        if not re.search(r"agent_name:", content):
            self._add_issue(
                "Structure & Syntax",
                "Missing 'agent_name' in config block",
                "error",
                deduction=3,
            )

        # Check for default_agent_user
        if not re.search(r"default_agent_user:", content):
            self._add_issue(
                "Structure & Syntax",
                "Missing 'default_agent_user' in config block (required for deployment)",
                "warning",
                deduction=2,
            )

        # Check for agent_label
        if not re.search(r"agent_label:", content):
            self._add_issue(
                "Structure & Syntax",
                "Missing 'agent_label' in config block",
                "warning",
                deduction=1,
            )

    def _validate_language(self, content: str):
        """Validate language block is present."""
        if not re.search(r"^language:", content, re.MULTILINE):
            self._add_issue(
                "Structure & Syntax",
                "Missing 'language:' block (required for deployment)",
                "warning",
                deduction=2,
            )

    def _validate_topics(self, content: str, lines: List[str]):
        """Validate topic definitions and transitions."""
        # Find all topic definitions
        topic_pattern = r"^(start_agent\s+)?topic\s+(\w+):"
        defined_topics = set()

        # Capture start_agent topics
        start_agent_pattern = r"^start_agent\s+(\w+):"
        for match in re.finditer(start_agent_pattern, content, re.MULTILINE):
            defined_topics.add(match.group(1))

        # Capture regular topics
        regular_topic_pattern = r"^topic\s+(\w+):"
        for match in re.finditer(regular_topic_pattern, content, re.MULTILINE):
            defined_topics.add(match.group(1))

        # Check for topic labels (CRITICAL - required for deployment)
        # Find topic blocks and check for label
        topic_block_pattern = r"^(start_agent\s+)?topic\s+(\w+):\s*\n((?:[ ]{3}.*\n)*)"
        for match in re.finditer(topic_block_pattern, content, re.MULTILINE):
            topic_block = match.group(3)
            topic_name = match.group(2)

            # Check for label (required)
            if "label:" not in topic_block:
                self._add_issue(
                    "Topic Design",
                    f"Topic '{topic_name}' is missing a label (required for deployment)",
                    "error",
                    deduction=3,
                )

            # Check for description
            if "description:" not in topic_block:
                self._add_issue(
                    "Topic Design",
                    f"Topic '{topic_name}' is missing a description",
                    "warning",
                    deduction=2,
                )

        # Also check start_agent block patterns
        start_block_pattern = r"^start_agent\s+(\w+):\s*\n((?:[ ]{3}.*\n)*)"
        for match in re.finditer(start_block_pattern, content, re.MULTILINE):
            topic_block = match.group(2)
            topic_name = match.group(1)

            if "label:" not in topic_block:
                self._add_issue(
                    "Topic Design",
                    f"Entry topic '{topic_name}' is missing a label (required for deployment)",
                    "error",
                    deduction=3,
                )

            if "description:" not in topic_block:
                self._add_issue(
                    "Topic Design",
                    f"Entry topic '{topic_name}' is missing a description",
                    "warning",
                    deduction=2,
                )

        # Check for topic name conventions (snake_case)
        for topic in defined_topics:
            if not re.match(r"^[a-z][a-z0-9_]*$", topic):
                self._add_issue(
                    "Topic Design",
                    f"Topic name '{topic}' should use snake_case",
                    "warning",
                    deduction=2,
                )

        # Find all topic references and check they exist
        topic_refs = re.findall(r"@topic\.(\w+)", content)
        for ref in topic_refs:
            if ref not in defined_topics:
                self._add_issue(
                    "Topic Design",
                    f"Reference to undefined topic '@topic.{ref}'",
                    "error",
                    deduction=5,
                )

    def _validate_variables(self, content: str, lines: List[str]):
        """Validate variable definitions and usage."""
        # Find mutable variable definitions
        var_pattern = r"^\s{3}(\w+):\s*mutable\s+(\w+)"
        defined_vars = set()

        for match in re.finditer(var_pattern, content, re.MULTILINE):
            var_name = match.group(1)
            var_type = match.group(2)
            defined_vars.add(var_name)

            # Check type is valid
            if var_type not in self.VALID_TYPES:
                self._add_issue(
                    "Variable Management",
                    f"Unknown variable type '{var_type}' for '{var_name}'",
                    "warning",
                    deduction=2,
                )

        # Find linked variable definitions
        linked_pattern = r"^\s{3}(\w+):\s*linked\s+(\w+)"
        for match in re.finditer(linked_pattern, content, re.MULTILINE):
            var_name = match.group(1)
            defined_vars.add(var_name)

        # Check for variable descriptions
        var_block_pattern = r"^\s{3}(\w+):\s*(?:mutable|linked)\s+\w+.*\n((?:\s{6}.*\n)*)"
        for match in re.finditer(var_block_pattern, content, re.MULTILINE):
            var_block = match.group(2)
            var_name = match.group(1)
            if "description:" not in var_block:
                self._add_issue(
                    "Variable Management",
                    f"Variable '{var_name}' is missing a description",
                    "warning",
                    deduction=1,
                )

        # Find all variable references and check they exist
        var_refs = re.findall(r"@variables\.(\w+)", content)
        for ref in var_refs:
            if ref not in defined_vars:
                self._add_issue(
                    "Variable Management",
                    f"Reference to undefined variable '@variables.{ref}'",
                    "error",
                    deduction=3,
                )

        # Check for wrong syntax (@variable instead of @variables)
        wrong_var_refs = re.findall(r"@variable\.(\w+)", content)
        if wrong_var_refs:
            self._add_issue(
                "Variable Management",
                "Use '@variables.' (plural), not '@variable.'",
                "error",
                deduction=5,
            )

    def _validate_linked_variables(self, content: str):
        """Validate required linked variables are present."""
        for var_name in self.REQUIRED_LINKED_VARS:
            pattern = rf"^\s{{3}}{var_name}:\s*linked"
            if not re.search(pattern, content, re.MULTILINE):
                self._add_issue(
                    "Variable Management",
                    f"Missing required linked variable '{var_name}' for messaging context",
                    "warning",
                    deduction=2,
                )

    def _validate_actions(self, content: str, lines: List[str]):
        """Validate action definitions and invocations."""
        # Find action definitions
        action_def_pattern = r"^\s{3}(\w+):\s*\n\s{6}description:"
        defined_actions = set()

        for match in re.finditer(action_def_pattern, content, re.MULTILINE):
            action_name = match.group(1)
            defined_actions.add(action_name)

        # Check for target format
        target_pattern = r'target:\s*"([^"]+)"'
        for match in re.finditer(target_pattern, content):
            target = match.group(1)
            if not any(target.startswith(prefix) for prefix in self.VALID_TARGETS):
                self._add_issue(
                    "Action Integration",
                    f"Invalid action target '{target}'. Use 'flow://' or 'apex://'",
                    "error",
                    deduction=5,
                )

        # Find action invocations and check for output capture
        action_invoke_pattern = r"@actions\.(\w+)"
        for match in re.finditer(action_invoke_pattern, content):
            action_name = match.group(1)
            # Check if outputs are being captured (look for 'set' after this action)
            pos = match.end()
            next_100_chars = content[pos:pos + 200]
            if "@outputs." in next_100_chars and "set @variables" not in next_100_chars:
                self._add_issue(
                    "Action Integration",
                    f"Action '{action_name}' outputs may not be captured with 'set'",
                    "warning",
                    deduction=2,
                )

        # Check for nested run statements (not supported)
        run_pattern = r"run @actions\.\w+.*\n(?:\s+.*\n)*?\s+run @actions"
        if re.search(run_pattern, content):
            self._add_issue(
                "Action Integration",
                "Nested 'run' callbacks are not supported. Use sequential 'run' statements instead.",
                "error",
                deduction=5,
            )

    def _validate_instructions(self, content: str, lines: List[str]):
        """Validate reasoning instructions quality."""
        # Check for instructions blocks
        if "instructions:" not in content:
            self._add_issue(
                "Instructions Quality",
                "No reasoning instructions found",
                "warning",
                deduction=5,
            )

        # Check for correct syntax: "instructions: ->" (space before arrow)
        # Incorrect: "instructions:->" (no space)
        if re.search(r"instructions:->\s*\n", content):
            self._add_issue(
                "Instructions Quality",
                "Use 'instructions: ->' (with space before arrow), not 'instructions:->'",
                "error",
                deduction=5,
            )

        # Check for template expression syntax
        # Valid: {!@variables.name}
        # Invalid: {@variables.name} or {{@variables.name}}
        invalid_template = re.findall(r"\{@variables\.\w+\}", content)
        if invalid_template:
            self._add_issue(
                "Instructions Quality",
                "Use '{!@variables.name}' for template expressions, not '{@variables.name}'",
                "error",
                deduction=3,
            )

        double_brace = re.findall(r"\{\{@variables\.\w+\}\}", content)
        if double_brace:
            self._add_issue(
                "Instructions Quality",
                "Use '{!@variables.name}' not '{{@variables.name}}'",
                "error",
                deduction=3,
            )

    def _validate_security(self, content: str, lines: List[str]):
        """Validate security guardrails."""
        # Check for system instructions
        system_block = re.search(
            r"^system:\s*\n((?:\s{3}.*\n)*)", content, re.MULTILINE
        )
        if system_block:
            system_content = system_block.group(1)
            if "instructions:" not in system_content:
                self._add_issue(
                    "Security & Guardrails",
                    "System block should include instructions for guardrails",
                    "warning",
                    deduction=5,
                )
        else:
            self._add_issue(
                "Security & Guardrails",
                "Missing system block for security guardrails",
                "error",
                deduction=10,
            )

        # Check for sensitive data warnings in instructions
        sensitive_patterns = [
            r"password",
            r"credit.?card",
            r"ssn",
            r"social.?security",
            r"api.?key",
            r"secret",
        ]
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Check if there's a warning about not exposing it
                if not re.search(r"never.*(share|expose|reveal)", content, re.IGNORECASE):
                    self._add_issue(
                        "Security & Guardrails",
                        f"Content mentions sensitive data ({pattern}). Ensure guardrails prevent exposure.",
                        "warning",
                        deduction=3,
                    )

    def _validate_references(self, content: str):
        """Validate all @ references are valid."""
        # Find all @ references
        all_refs = re.findall(r"@(\w+)\.", content)

        valid_prefixes = ["variables", "actions", "topic", "outputs", "utils", "MessagingSession", "MessagingEndUser"]

        for ref in all_refs:
            if ref not in valid_prefixes:
                self._add_issue(
                    "Structure & Syntax",
                    f"Invalid resource reference '@{ref}'. Valid: @variables, @actions, @topic, @outputs, @utils",
                    "error",
                    deduction=3,
                )


def main():
    """CLI entry point for direct validation."""
    if len(sys.argv) < 2:
        print("Usage: python validate_agentforce.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    validator = AgentScriptValidator()
    result = validator.validate(content, file_path)

    # Print results
    print("=" * 60)
    print("🤖 AGENTFORCE VALIDATION")
    print("=" * 60)
    print()

    score = result["score"]
    max_score = result["max_score"]
    percentage = (score / max_score) * 100

    if percentage >= 90:
        stars = "⭐⭐⭐⭐⭐"
        rating = "Excellent"
    elif percentage >= 80:
        stars = "⭐⭐⭐⭐"
        rating = "Very Good"
    elif percentage >= 70:
        stars = "⭐⭐⭐"
        rating = "Good"
    elif percentage >= 60:
        stars = "⭐⭐"
        rating = "Needs Work"
    else:
        stars = "⭐"
        rating = "Critical Issues"

    print(f"Score: {score}/{max_score} {stars} {rating}")
    print()

    for category, details in result["categories"].items():
        cat_score = details["score"]
        cat_max = details["max"]
        cat_pct = (cat_score / cat_max) * 100 if cat_max > 0 else 0
        print(f"├─ {category}: {cat_score}/{cat_max} ({cat_pct:.0f}%)")

    print()

    if result["issues"]:
        print("Issues:")
        for issue in result["issues"]:
            severity = issue.get("severity", "warning")
            icon = "❌" if severity == "error" else "⚠️"
            category = issue.get("category", "General")
            message = issue.get("message", "")
            line = issue.get("line")
            line_info = f" (line {line})" if line else ""
            print(f"{icon} [{category}]{line_info} {message}")
    else:
        print("✅ No issues found!")

    print()
    print("=" * 60)

    # Exit with error code if critical issues
    if percentage < 60:
        sys.exit(1)


if __name__ == "__main__":
    main()
