# SLDS 2 & Dark Mode

SLDS 2 validation, dark mode readiness, migration patterns, and global styling hooks reference.

---

## Dark Mode Checklist

- [ ] **No hardcoded hex colors** (`#FFFFFF`, `#333333`)
- [ ] **No hardcoded RGB/RGBA values**
- [ ] **All colors use CSS variables** (`var(--slds-g-color-*)`)
- [ ] **Fallback values provided** for SLDS 1 compatibility
- [ ] **No inline color styles** in HTML templates
- [ ] **Icons use SLDS utility icons** (auto-adjust for dark mode)

## SLDS 1 to SLDS 2 Migration

**Before (SLDS 1 - Deprecated)**:
```css
.my-card {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #dddddd;
    border-radius: 4px;
}
```

**After (SLDS 2 - Dark Mode Ready)**:
```css
.my-card {
    background-color: var(--slds-g-color-surface-container-1, #ffffff);
    color: var(--slds-g-color-on-surface, #181818);
    border: 1px solid var(--slds-g-color-border-1, #c9c9c9);
    border-radius: var(--slds-g-radius-border-2, 0.25rem);
}
```

## Global Styling Hooks Reference

| Category | SLDS 2 Variable | Purpose |
|----------|-----------------|---------|
| **Surface** | `--slds-g-color-surface-1` to `-4` | Background colors |
| **Container** | `--slds-g-color-surface-container-1` to `-3` | Card/section backgrounds |
| **Text** | `--slds-g-color-on-surface` | Primary text |
| **Text Secondary** | `--slds-g-color-on-surface-1`, `-2` | Muted text |
| **Border** | `--slds-g-color-border-1`, `-2` | Borders |
| **Brand** | `--slds-g-color-brand-1`, `-2` | Brand accent |
| **Error** | `--slds-g-color-error-1` | Error states |
| **Success** | `--slds-g-color-success-1` | Success states |
| **Warning** | `--slds-g-color-warning-1` | Warning states |
| **Spacing** | `--slds-g-spacing-0` to `-12` | Margins/padding |
| **Font Size** | `--slds-g-font-size-1` to `-10` | Typography |
| **Radius** | `--slds-g-radius-border-1` to `-4` | Border radius |

**Important**: Component-level hooks (`--slds-c-*`) are NOT supported in SLDS 2 yet. Use only global hooks (`--slds-g-*`).

## SLDS Validator/Linter Commands

```bash
# Install SLDS Linter
npm install -g @salesforce-ux/slds-linter

# Run validation
slds-linter lint force-app/main/default/lwc/myComponent

# Auto-fix issues
slds-linter lint --fix force-app/main/default/lwc/myComponent
```
