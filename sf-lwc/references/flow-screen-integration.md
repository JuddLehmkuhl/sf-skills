# Flow Screen Integration

LWC components embedded in Flow Screens for custom UI experiences within guided processes.

---

## Key Concepts

| Mechanism | Direction | Purpose |
|-----------|-----------|---------|
| `@api` with `role="inputOnly"` | Flow -> LWC | Pass context data |
| `FlowAttributeChangeEvent` | LWC -> Flow | Return user selections |
| `FlowNavigationFinishEvent` | LWC -> Flow | Programmatic Next/Back/Finish |
| `availableActions` | Flow -> LWC | Check available navigation |

## Example

```javascript
import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';

@api recordId;           // Input from Flow
@api selectedRecordId;   // Output to Flow
@api availableActions = [];

handleSelect(event) {
    this.selectedRecordId = event.detail.id;
    // CRITICAL: Notify Flow of the change
    this.dispatchEvent(new FlowAttributeChangeEvent(
        'selectedRecordId',
        this.selectedRecordId
    ));
}

handleNext() {
    if (this.availableActions.includes('NEXT')) {
        this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
    }
}
```

## Templates & Resources

| Resource | Location |
|----------|----------|
| Flow Screen Component Template | `templates/flow-screen-component/` |
| Flow Integration Guide | [docs/flow-integration-guide.md](../docs/flow-integration-guide.md) |
| Triangle Architecture | [shared/docs/flow-lwc-apex-triangle.md](../../shared/docs/flow-lwc-apex-triangle.md) |
