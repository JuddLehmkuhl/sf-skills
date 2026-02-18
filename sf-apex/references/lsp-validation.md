# LSP-Based Validation (Auto-Fix Loop)

> Extracted from sf-apex SKILL.md for progressive disclosure.
> Return to [SKILL.md](../SKILL.md) for the workflow and scoring.

---

## How It Works

1. **PostToolUse Hook**: After every Write/Edit operation on `.cls` or `.trigger` files, the LSP hook validates syntax
2. **Apex Language Server**: Uses Salesforce's official `apex-jorje-lsp.jar` (from VS Code extension)
3. **Auto-Fix Loop**: If errors are found, Claude receives diagnostics and auto-fixes them (max 3 attempts)
4. **Two-Layer Validation**:
   - **LSP Validation**: Fast syntax checking (~500ms)
   - **150-Point Validation**: Semantic analysis for best practices

## Prerequisites

| Requirement | How to Install |
|-------------|----------------|
| **VS Code Salesforce Extension Pack** | VS Code > Extensions > "Salesforce Extension Pack" |
| **Java 11+ (Adoptium recommended)** | https://adoptium.net/temurin/releases/ |

## Validation Flow

```
User writes Apex code -> Write/Edit tool executes
                              |
                    +-------------------------+
                    |   LSP Validation (fast)  |
                    |   Syntax errors only     |
                    +-------------------------+
                              |
                    +-------------------------+
                    |  150-Point Validation    |
                    |  Semantic best practices |
                    +-------------------------+
                              |
                    Claude sees any errors and auto-fixes
```

## Sample LSP Error Output

```
============================================================
APEX LSP VALIDATION RESULTS
   File: force-app/main/default/classes/MyClass.cls
   Attempt: 1/3
============================================================

Found 1 error(s), 0 warning(s)

ISSUES TO FIX:
----------------------------------------
[ERROR] line 4: Missing ';' at 'System.debug' (source: apex)

ACTION REQUIRED:
Please fix the Apex syntax errors above and try again.
(Attempt 1/3)
============================================================
```

## Graceful Degradation

If LSP is unavailable (no VS Code extension or Java), validation silently skips -- the skill continues to work with only 150-point semantic validation.
