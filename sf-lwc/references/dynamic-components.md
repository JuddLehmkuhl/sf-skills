# Dynamic Components (lwc:component)

Dynamically instantiate LWC components at runtime using `lwc:component` with the `lwc:is` directive.

---

## Requirements

- API version 55.0 or later
- Lightning Web Security (LWS) enabled
- Component meta.xml must include: `<capability>lightning__dynamicComponent</capability>`

## Basic Dynamic Component

```javascript
// dynamicLoader.js
import { LightningElement } from 'lwc';

export default class DynamicLoader extends LightningElement {
    componentConstructor;
    componentName = 'c/accountCard';

    async connectedCallback() {
        await this.loadComponent(this.componentName);
    }

    async loadComponent(name) {
        try {
            const { default: ctor } = await import(name);
            this.componentConstructor = ctor;
        } catch (error) {
            console.error(`Failed to load component: ${name}`, error);
            this.componentConstructor = null; // Renders nothing
        }
    }
}
```

```html
<!-- dynamicLoader.html -->
<template>
    <lwc:component lwc:is={componentConstructor}></lwc:component>
</template>
```

## Dynamic Component with Props (lwc:spread)

```javascript
// dynamicWithProps.js
import { LightningElement, api } from 'lwc';

export default class DynamicWithProps extends LightningElement {
    componentConstructor;
    _componentProps = {};

    @api
    async loadComponent(name, props = {}) {
        try {
            const { default: ctor } = await import(name);
            this.componentConstructor = ctor;
            this._componentProps = props;
        } catch (error) {
            console.error('Dynamic component load failed:', error);
        }
    }
}
```

```html
<!-- dynamicWithProps.html -->
<template>
    <lwc:component
        lwc:is={componentConstructor}
        lwc:spread={_componentProps}>
    </lwc:component>
</template>
```

## When to Use Dynamic Components

| Use Case | Recommended |
|----------|-------------|
| Plugin / extension architecture | Yes |
| Configurable dashboard tiles | Yes |
| A/B testing different UIs | Yes |
| Static known components | No (use direct references) |
| Performance-critical paths | No (adds async overhead) |

**Key behavior**: When the constructor changes, the existing component is removed from the DOM with all children, and the new component is rendered fresh.
