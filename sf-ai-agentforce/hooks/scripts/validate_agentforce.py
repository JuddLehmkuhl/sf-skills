#!/usr/bin/env python3
"""
Agent Script Validator for sf-agentforce skill.
Validates Agent Script syntax and best practices.
Scoring: 100 points across 6 categories.

Updated to match official Salesforce Agent Script syntax (Dec 2025):
- Uses agent_name (not developer_name)
- Uses TAB indentation (recommended) or consistent spaces
- CRITICAL: Never mix tabs and spaces (causes parse errors)
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

    # Valid variable types (expanded Dec 2025)
    VALID_TYPES = [
        "string", "number", "integer", "long", "boolean",
        "date", "datetime", "time", "currency", "id",
        "list", "object"
    ]

    # Valid action targets
    VALID_TARGETS = ["flow://", "apex://", "prompt://"]

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
        self._validate_lifecycle_blocks(content, lines)
        self._validate_filter_from_agent(content)

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
        """Validate indentation consistency (tabs recommended, or consistent spaces).

        CRITICAL: Mixing tabs and spaces causes parse errors.
        Either use all tabs (recommended) or all spaces consistently.
        """
        has_tabs = False
        has_spaces = False

        for i, line in enumerate(lines, 1):
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            # Detect indentation type used
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            if '\t' in leading_whitespace:
                has_tabs = True
            if ' ' in leading_whitespace and leading_whitespace.replace('\t', ''):
                # Has spaces in indentation (not just tabs)
                space_only = leading_whitespace.replace('\t', '')
                if space_only:
                    has_spaces = True

            # Check for mixed tabs and spaces on same line (CRITICAL ERROR)
            if '\t' in leading_whitespace and ' ' in leading_whitespace:
                self._add_issue(
                    "Structure & Syntax",
                    "CRITICAL: Mixed tabs and spaces on same line - this causes parse errors",
                    "error",
                    line=i,
                    deduction=5,
                )

        # Check for mixing tabs and spaces across the file
        if has_tabs and has_spaces:
            self._add_issue(
                "Structure & Syntax",
                "CRITICAL: File mixes tabs and spaces for indentation - use one consistently (tabs recommended)",
                "error",
                deduction=5,
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
        # Find topic blocks and check for label (supports tabs or spaces)
        topic_block_pattern = r"^(start_agent\s+)?topic\s+(\w+):\s*\n((?:[ \t]+.*\n)*)"
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

        # Also check start_agent block patterns (supports tabs or spaces)
        start_block_pattern = r"^start_agent\s+(\w+):\s*\n((?:[ \t]+.*\n)*)"
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
        # Find mutable variable definitions (supports tabs or spaces)
        var_pattern = r"^[ \t]+(\w+):\s*mutable\s+(\w+)"
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

        # Find linked variable definitions (supports tabs or spaces)
        linked_pattern = r"^[ \t]+(\w+):\s*linked\s+(\w+)"
        for match in re.finditer(linked_pattern, content, re.MULTILINE):
            var_name = match.group(1)
            defined_vars.add(var_name)

        # Check for variable descriptions (supports tabs or spaces)
        var_block_pattern = r"^[ \t]+(\w+):\s*(?:mutable|linked)\s+\w+.*\n((?:[ \t]+.*\n)*)"
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
            # Support tabs or spaces for indentation
            pattern = rf"^[ \t]+{var_name}:\s*linked"
            if not re.search(pattern, content, re.MULTILINE):
                self._add_issue(
                    "Variable Management",
                    f"Missing required linked variable '{var_name}' for messaging context",
                    "warning",
                    deduction=2,
                )

    def _validate_actions(self, content: str, lines: List[str]):
        """Validate action definitions and invocations."""
        # Find action definitions (supports tabs or spaces)
        action_def_pattern = r"^[ \t]+(\w+):\s*\n[ \t]+description:"
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
        # Check for system instructions (supports tabs or spaces)
        system_block = re.search(
            r"^system:\s*\n((?:[ \t]+.*\n)*)", content, re.MULTILINE
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

    def _validate_lifecycle_blocks(self, content: str, lines: List[str]):
        """Validate lifecycle blocks (before_reasoning/after_reasoning) syntax.

        Critical rules per official Salesforce docs:
        1. Use 'transition to' NOT '@utils.transition to' in lifecycle blocks
        2. Pipe (|) is NOT supported in lifecycle blocks
        """
        # Find before_reasoning and after_reasoning blocks (supports tabs or spaces)
        lifecycle_block_pattern = r"(before_reasoning|after_reasoning):\s*\n((?:[ \t]+.*\n)*)"

        for match in re.finditer(lifecycle_block_pattern, content, re.MULTILINE):
            block_type = match.group(1)
            block_content = match.group(2)

            # Check for @utils.transition in lifecycle blocks (WRONG syntax)
            if "@utils.transition" in block_content:
                self._add_issue(
                    "Structure & Syntax",
                    f"In '{block_type}' block: Use 'transition to' NOT '@utils.transition to'",
                    "error",
                    deduction=3,
                )

            # Check for pipe (|) in lifecycle blocks (NOT SUPPORTED)
            # Only flag actual pipe commands at start of line (after spaces)
            pipe_pattern = r"^\s+\|"
            if re.search(pipe_pattern, block_content, re.MULTILINE):
                self._add_issue(
                    "Structure & Syntax",
                    f"In '{block_type}' block: Pipe (|) command is NOT supported. Use only logic and actions.",
                    "warning",
                    deduction=2,
                )

    def _validate_filter_from_agent(self, content: str):
        """Check if sensitive output fields use filter_from_agent.

        Sensitive fields (ssn, password, credit_card, etc.) in action outputs
        should use filter_from_agent: True to hide from LLM context.
        """
        # Sensitive field patterns
        sensitive_patterns = [
            r"ssn", r"social_security", r"password", r"secret",
            r"credit_card", r"card_number", r"cvv", r"pin",
            r"api_key", r"token", r"private_key"
        ]

        # Find outputs blocks
        outputs_pattern = r"outputs:\s*\n((?:\s{9,}.*\n)*)"
        for match in re.finditer(outputs_pattern, content, re.MULTILINE):
            outputs_block = match.group(1)

            for pattern in sensitive_patterns:
                # Check if sensitive field name exists in outputs
                if re.search(pattern, outputs_block, re.IGNORECASE):
                    # Check if filter_from_agent is used
                    if "filter_from_agent:" not in outputs_block:
                        self._add_issue(
                            "Security & Guardrails",
                            f"Sensitive output field may contain '{pattern}'. Consider using 'filter_from_agent: True'",
                            "warning",
                            deduction=2,
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
