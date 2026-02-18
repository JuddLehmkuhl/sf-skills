# Light DOM vs Shadow DOM

LWC defaults to Shadow DOM. Light DOM is available for scenarios requiring global styling or third-party library integration.

---

## Decision Framework

| Factor | Shadow DOM (Default) | Light DOM |
|--------|---------------------|-----------|
| Style encapsulation | Full isolation | Styles cascade in/out |
| Security | Protected by LWS | Must nest inside shadow DOM parent |
| Third-party CSS libs | Blocked by shadow boundary | Full access |
| Global theming | Per-component hooks only | Inherits page styles |
| DOM querying | `this.template.querySelector()` | `this.querySelector()` |
| Packageable | Yes | No (cannot package) |
| Base components | N/A (always shadow) | N/A (always shadow) |
| Event retargeting | Events retargeted to host | Events not retargeted |

**Default choice**: Shadow DOM. Only use Light DOM when you have a specific need.

## Light DOM Implementation

```javascript
// lightDomComponent.js
import { LightningElement } from 'lwc';

export default class LightDomComponent extends LightningElement {
    static renderMode = 'light'; // Required
}
```

```html
<!-- lightDomComponent.html -->
<template lwc:render-mode="light">
    <div class="custom-styled-content">
        <p>This content renders in the Light DOM.</p>
        <slot></slot>
    </div>
</template>
```

## Scoped Styles for Light DOM

Use `*.scoped.css` to prevent style leakage from Light DOM components:

```css
/* lightDomComponent.scoped.css */
.custom-styled-content {
    padding: var(--slds-g-spacing-4, 1rem);
    background-color: var(--slds-g-color-surface-container-1, #ffffff);
}
```

## Light DOM Restrictions

- **Security**: Top-level light DOM components bypass LWS -- always nest inside a shadow DOM parent
- **Packaging**: Cannot be distributed in managed or unlocked packages
- **Slots**: Lifecycle hooks on slots never fire; slots inside `for:each` not supported
- **Base components**: `lightning-*` components always render in shadow DOM regardless
- **Aura**: Aura components cannot use light DOM directly (but can contain LWC light DOM children)

## Recommended Architecture Pattern

```
shadow-dom-wrapper (shadow)
  +-- light-dom-child-a (light) -- can use global CSS
  +-- light-dom-child-b (light) -- can use third-party libs
  +-- base-component (shadow)   -- always shadow
```
