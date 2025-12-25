# Flow-LWC-Apex Triangle Architecture

The **Triangle Architecture** is a foundational pattern in Salesforce development where Flow, LWC, and Apex work together seamlessly. This guide provides a comprehensive reference for building integrated solutions.

---

## Architecture Overview

```
                         ┌─────────────────────────────────────┐
                         │              FLOW                   │
                         │         (Orchestrator)              │
                         │                                     │
                         │  • Process Logic                    │
                         │  • User Experience                  │
                         │  • Variable Management              │
                         └───────────────┬─────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              │ screens                  │ actionCalls              │
              │ <componentInstance>      │ actionType="apex"        │
              │                          │                          │
              ▼                          ▼                          ▲
┌─────────────────────────┐    ┌─────────────────────────┐         │
│          LWC            │    │         APEX            │         │
│     (UI Component)      │───▶│   (Business Logic)      │─────────┘
│                         │    │                         │
│ • Rich UI/UX            │    │ • @InvocableMethod      │
│ • User Interaction      │    │ • @AuraEnabled          │
│ • FlowAttribute         │    │ • Complex Logic         │
│   ChangeEvent           │    │ • DML Operations        │
│ • FlowNavigation        │    │ • Integration           │
│   FinishEvent           │    │                         │
└─────────────────────────┘    └─────────────────────────┘
              │                          ▲
              │      @AuraEnabled        │
              │      wire / imperative   │
              └──────────────────────────┘
```

---

## Communication Pathways

| From | To | Mechanism | Direction |
|------|-----|-----------|-----------|
| **Flow** | **LWC** | `inputParameters` → `@api (inputOnly)` | One-way |
| **LWC** | **Flow** | `FlowAttributeChangeEvent` → `outputParameters` | Event-based |
| **LWC** | **Flow Nav** | `FlowNavigationFinishEvent` | Command |
| **Flow** | **Apex** | `actionCalls` with `actionType="apex"` | Request/Response |
| **Apex** | **Flow** | `@InvocableVariable` in Response class | Return values |
| **LWC** | **Apex** | `@wire` or `imperative` call | Async |
| **Apex** | **LWC** | Return value / `@wire` refresh | Response |

---

## Decision Matrix: When to Use Each Pattern

| Scenario | Primary | Calls | Why |
|----------|---------|-------|-----|
| Simple record selection | LWC | - | Rich UI, immediate feedback |
| Complex multi-step process | Flow | Apex, LWC | Orchestration strength |
| Bulk data processing | Apex | - | Governor limit handling |
| Custom UI in guided process | Flow | LWC | Best of both |
| External API integration | Apex | - | Authentication, callouts |
| Admin-maintainable logic | Flow | Apex for complex ops | Low-code primary |
| High-volume automation | Apex | - | Performance critical |
| User-facing wizard | Flow + LWC | Apex | Complete solution |

---

## Pattern 1: Flow Screen → LWC → Flow

**Use Case**: Custom UI component for user selection within a guided Flow.

```
┌─────────┐     @api (in)      ┌─────────┐
│  FLOW   │ ────────────────▶ │   LWC   │
│ Screen  │                    │  Screen │
│         │ ◀──────────────── │Component│
│         │  FlowAttribute    │         │
└─────────┘   ChangeEvent     └─────────┘
```

### Flow XML
```xml
<screens>
    <fields>
        <extensionName>c:recordSelector</extensionName>
        <fieldType>ComponentInstance</fieldType>
        <inputParameters>
            <name>recordId</name>
            <value><elementReference>var_ParentId</elementReference></value>
        </inputParameters>
        <outputParameters>
            <assignToReference>var_SelectedId</assignToReference>
            <name>selectedRecordId</name>
        </outputParameters>
    </fields>
</screens>
```

### LWC JavaScript
```javascript
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

@api recordId;           // Input from Flow
@api selectedRecordId;   // Output to Flow

handleSelect(event) {
    this.selectedRecordId = event.detail.id;
    this.dispatchEvent(new FlowAttributeChangeEvent(
        'selectedRecordId',
        this.selectedRecordId
    ));
}
```

---

## Pattern 2: Flow → Apex Invocable

**Use Case**: Complex business logic, DML, or external integrations.

```
┌─────────┐   actionCalls    ┌─────────┐
│  FLOW   │ ───────────────▶ │  APEX   │
│ Auto-   │   List<Request>  │Invocable│
│ mation  │ ◀─────────────── │ Method  │
│         │   List<Response> │         │
└─────────┘                  └─────────┘
```

### Flow XML
```xml
<actionCalls>
    <name>Process_Records</name>
    <actionName>RecordProcessor</actionName>
    <actionType>apex</actionType>
    <inputParameters>
        <name>recordId</name>
        <value><elementReference>var_RecordId</elementReference></value>
    </inputParameters>
    <outputParameters>
        <assignToReference>var_IsSuccess</assignToReference>
        <name>isSuccess</name>
    </outputParameters>
    <faultConnector>
        <targetReference>Handle_Error</targetReference>
    </faultConnector>
</actionCalls>
```

### Apex Class
```apex
public with sharing class RecordProcessor {

    @InvocableMethod(label='Process Record' category='Custom')
    public static List<Response> execute(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response res = new Response();
            try {
                // Business logic here
                res.isSuccess = true;
                res.processedId = req.recordId;
            } catch (Exception e) {
                res.isSuccess = false;
                res.errorMessage = e.getMessage();
            }
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(required=true)
        public Id recordId;
    }

    public class Response {
        @InvocableVariable
        public Boolean isSuccess;
        @InvocableVariable
        public Id processedId;
        @InvocableVariable
        public String errorMessage;
    }
}
```

---

## Pattern 3: LWC → Apex (Wire/Imperative)

**Use Case**: LWC needs data or operations beyond Flow context.

```
┌─────────┐     @wire         ┌─────────┐
│   LWC   │ ────────────────▶ │  APEX   │
│         │    imperative     │@Aura    │
│         │ ◀──────────────── │Enabled  │
│         │   Promise/data    │         │
└─────────┘                   └─────────┘
```

### LWC JavaScript (Wire)
```javascript
import getRecords from '@salesforce/apex/RecordController.getRecords';

@wire(getRecords, { parentId: '$recordId' })
wiredRecords({ error, data }) {
    if (data) {
        this.records = data;
    } else if (error) {
        this.error = error;
    }
}
```

### LWC JavaScript (Imperative)
```javascript
import processRecord from '@salesforce/apex/RecordController.processRecord';

async handleSubmit() {
    try {
        const result = await processRecord({ recordId: this.recordId });
        if (result.isSuccess) {
            // Notify Flow of success
            this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
        }
    } catch (error) {
        this.error = error.body.message;
    }
}
```

### Apex Controller
```apex
public with sharing class RecordController {

    @AuraEnabled(cacheable=true)
    public static List<Record__c> getRecords(Id parentId) {
        return [
            SELECT Id, Name, Status__c
            FROM Record__c
            WHERE Parent__c = :parentId
            WITH USER_MODE
        ];
    }

    @AuraEnabled
    public static Map<String, Object> processRecord(Id recordId) {
        // Process logic
        return new Map<String, Object>{
            'isSuccess' => true,
            'recordId' => recordId
        };
    }
}
```

---

## Pattern 4: Full Triangle (All Three)

**Use Case**: Complete solution with guided UI, custom interactions, and complex logic.

```
                    ┌─────────────────────┐
                    │       FLOW          │
                    │  (Orchestrator)     │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     │
┌─────────────────┐   ┌─────────────────┐           │
│   LWC Screen    │   │  Apex Invocable │           │
│   Component     │   │     Action      │           │
└────────┬────────┘   └────────┬────────┘           │
         │                     │                     │
         │    @AuraEnabled     │                     │
         └──────────┬──────────┘                     │
                    ▼                                │
         ┌─────────────────────┐                     │
         │   Apex Controller   │─────────────────────┘
         │   (@AuraEnabled)    │   Results back to Flow
         └─────────────────────┘
```

### Example: Custom Quote Builder

1. **Flow** orchestrates the quote creation wizard
2. **LWC** provides interactive product selector with quantity inputs
3. **Apex Invocable** calculates pricing with complex discount rules
4. **LWC** (via @AuraEnabled) fetches real-time inventory data
5. **Flow** handles final quote creation and approval routing

---

## Deployment Order

When deploying integrated solutions, follow this order to avoid dependency errors:

```
1. APEX CLASSES
   └── @InvocableMethod classes
   └── @AuraEnabled controllers

2. LWC COMPONENTS
   └── meta.xml with targets
   └── JavaScript with Flow imports

3. FLOWS
   └── Reference deployed Apex classes
   └── Reference deployed LWC components
```

### Package.xml Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <!-- Deploy Apex first -->
    <types>
        <members>RecordProcessor</members>
        <members>RecordController</members>
        <name>ApexClass</name>
    </types>
    <!-- Then LWC -->
    <types>
        <members>recordSelector</members>
        <name>LightningComponentBundle</name>
    </types>
    <!-- Finally Flows -->
    <types>
        <members>Record_Selection_Flow</members>
        <name>Flow</name>
    </types>
    <version>62.0</version>
</Package>
```

---

## Testing Strategy

### Unit Tests

| Component | Test Type | Framework |
|-----------|-----------|-----------|
| Apex Invocable | Apex Test | `@isTest`, `Test.startTest()` |
| Apex Controller | Apex Test | Mock data, `System.runAs()` |
| LWC | Jest | `@salesforce/sfdx-lwc-jest` |
| Flow | Apex Test | `Flow.Interview` class |

### Apex Invocable Test
```apex
@isTest
private class RecordProcessorTest {
    @isTest
    static void testProcessRecords() {
        Account acc = new Account(Name = 'Test');
        insert acc;

        RecordProcessor.Request req = new RecordProcessor.Request();
        req.recordId = acc.Id;

        Test.startTest();
        List<RecordProcessor.Response> responses =
            RecordProcessor.execute(new List<RecordProcessor.Request>{ req });
        Test.stopTest();

        System.assertEquals(true, responses[0].isSuccess);
    }
}
```

### LWC Jest Test (Flow Integration)
```javascript
import { createElement } from 'lwc';
import RecordSelector from 'c/recordSelector';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

jest.mock('lightning/flowSupport', () => ({
    FlowAttributeChangeEvent: jest.fn(),
    FlowNavigationFinishEvent: jest.fn()
}), { virtual: true });

describe('c-record-selector', () => {
    it('dispatches FlowAttributeChangeEvent on selection', () => {
        const element = createElement('c-record-selector', {
            is: RecordSelector
        });
        document.body.appendChild(element);

        // Simulate selection
        const tile = element.shadowRoot.querySelector('.record-tile');
        tile.click();

        expect(FlowAttributeChangeEvent).toHaveBeenCalled();
    });
});
```

### Flow Interview Test
```apex
@isTest
private class FlowIntegrationTest {
    @isTest
    static void testFlowWithApex() {
        Account acc = new Account(Name = 'Test');
        insert acc;

        Map<String, Object> inputs = new Map<String, Object>{
            'var_ParentRecordId' => acc.Id
        };

        Test.startTest();
        Flow.Interview flow = Flow.Interview.createInterview(
            'Record_Selection_Flow',
            inputs
        );
        flow.start();
        Test.stopTest();

        // Verify outputs
        Object result = flow.getVariableValue('out_SelectedRecordId');
        System.assertNotEquals(null, result);
    }
}
```

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| LWC without FlowAttributeChangeEvent | Outputs never update in Flow | Always dispatch event |
| Non-bulkified Invocable | Fails for multi-record Flows | Use `List<Request>` → `List<Response>` |
| Mixing @wire and @AuraEnabled for same data | Cache/freshness conflicts | Choose one pattern per data need |
| Hardcoded IDs in Flow | Environment-specific failures | Use Custom Metadata or variables |
| LWC calling Apex for Flow-available data | Unnecessary callouts | Pass via inputParameters |
| Not handling faultConnector | Unhandled Apex exceptions crash Flow | Always add fault path |

---

## Templates Reference

| Skill | Template | Purpose |
|-------|----------|---------|
| sf-apex | `templates/invocable-method.cls` | @InvocableMethod with Request/Response |
| sf-lwc | `templates/flow-screen-component/` | Complete Flow screen LWC |
| sf-flow | `templates/apex-action-template.xml` | Flow calling Apex |
| sf-flow | `templates/screen-flow-with-lwc.xml` | Flow embedding LWC |

---

## Related Documentation

| Topic | Location |
|-------|----------|
| Apex @InvocableMethod | [sf-apex/docs/flow-integration.md](../../sf-apex/docs/flow-integration.md) |
| LWC Flow Integration | [sf-lwc/docs/flow-integration-guide.md](../../sf-lwc/docs/flow-integration-guide.md) |
| Flow XML for LWC | [sf-flow/docs/lwc-integration-guide.md](../../sf-flow/docs/lwc-integration-guide.md) |
| Cross-Skill Orchestration | [shared/docs/orchestration.md](orchestration.md) |
