# Advanced Jest Testing Patterns

Based on [James Simone's advanced testing patterns](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/).

---

## Render Cycle Helper

```javascript
// testUtils.js
export const runRenderingLifecycle = async (reasons = ['render']) => {
    while (reasons.length > 0) {
        await Promise.resolve(reasons.pop());
    }
};

// Usage in tests
it('updates after property change', async () => {
    const element = createElement('c-example', { is: Example });
    document.body.appendChild(element);

    element.greeting = 'new value';
    await runRenderingLifecycle(['property change', 'render']);

    expect(element.shadowRoot.querySelector('div').textContent).toBe('new value');
});
```

## Proxy Unboxing (LWS Compatibility)

```javascript
// Lightning Web Security proxifies objects - unbox them for assertions
const unboxedData = JSON.parse(JSON.stringify(component.data));
expect(unboxedData).toEqual(expectedData);
```

## DOM Cleanup Pattern

```javascript
describe('c-my-component', () => {
    afterEach(() => {
        // Clean up DOM to prevent state bleed
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });
});
```

## ResizeObserver Polyfill

```javascript
// jest.setup.js
if (!window.ResizeObserver) {
    window.ResizeObserver = class ResizeObserver {
        constructor(callback) {
            this.callback = callback;
        }
        observe() {}
        unobserve() {}
        disconnect() {}
    };
}
```

## Complete Test Template

```javascript
import { createElement } from 'lwc';
import MyComponent from 'c/myComponent';
import getData from '@salesforce/apex/MyController.getData';

jest.mock('@salesforce/apex/MyController.getData', () => ({
    default: jest.fn()
}), { virtual: true });

const MOCK_DATA = [
    { Id: '001xx000001', Name: 'Test 1' },
    { Id: '001xx000002', Name: 'Test 2' }
];

const runRenderingLifecycle = async (reasons = ['render']) => {
    while (reasons.length > 0) {
        await Promise.resolve(reasons.pop());
    }
};

describe('c-my-component', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('displays data when loaded successfully', async () => {
        getData.mockResolvedValue(MOCK_DATA);

        const element = createElement('c-my-component', { is: MyComponent });
        document.body.appendChild(element);

        await runRenderingLifecycle(['wire data fetch', 'render']);

        const items = element.shadowRoot.querySelectorAll('.item');
        expect(items.length).toBe(2);
    });

    it('displays error when fetch fails', async () => {
        getData.mockRejectedValue(new Error('Failed'));

        const element = createElement('c-my-component', { is: MyComponent });
        document.body.appendChild(element);

        await runRenderingLifecycle(['wire error', 'render']);

        const error = element.shadowRoot.querySelector('.error');
        expect(error).not.toBeNull();
    });

    it('fires event when item clicked', async () => {
        getData.mockResolvedValue(MOCK_DATA);
        const handler = jest.fn();

        const element = createElement('c-my-component', { is: MyComponent });
        element.addEventListener('itemselected', handler);
        document.body.appendChild(element);

        await runRenderingLifecycle();

        const item = element.shadowRoot.querySelector('.item');
        item.click();

        expect(handler).toHaveBeenCalled();
        expect(handler.mock.calls[0][0].detail.id).toBe('001xx000001');
    });
});
```
