# Platform Events & Change Data Capture

## Platform Event Definition

**Template**: `templates/platform-events/platform-event-definition.object-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <deploymentStatus>Deployed</deploymentStatus>
    <eventType>HighVolume</eventType>
    <label>{{EventLabel}}</label>
    <pluralLabel>{{EventPluralLabel}}</pluralLabel>
    <publishBehavior>PublishAfterCommit</publishBehavior>
    <fields>
        <fullName>{{FieldName}}__c</fullName>
        <label>{{FieldLabel}}</label>
        <type>Text</type>
        <length>255</length>
    </fields>
</CustomObject>
```

**Event Types & Publish Behavior**:

| Property | Options | Guidance |
|----------|---------|----------|
| `eventType` | `StandardVolume`, `HighVolume` | Use `HighVolume` for production integrations (millions/day, 72-hour retention) |
| `publishBehavior` | `PublishAfterCommit`, `PublishImmediately` | Use `PublishAfterCommit` unless you need events even on rollback |

## Event Publisher

**Template**: `templates/platform-events/event-publisher.cls` (full implementation with bulk support, correlation IDs)

Key patterns:
- Always use `EventBus.publish()` (not DML `insert`)
- Check `Database.SaveResult` for each event
- Use correlation IDs for cross-system traceability
- Handle partial failures in bulk publishes

## Event Subscriber Trigger

**Template**: `templates/platform-events/event-subscriber-trigger.trigger`

```apex
trigger {{EventName}}Subscriber on {{EventName}}__e (after insert) {
    String lastReplayId = '';

    for ({{EventName}}__e event : Trigger.new) {
        lastReplayId = event.ReplayId;

        try {
            {{EventName}}Handler.processEvent(event);
        } catch (Exception e) {
            // Log error but do NOT throw - allow other events to process
            System.debug(LoggingLevel.ERROR,
                'Event processing error: ' + e.getMessage() +
                ' ReplayId: ' + event.ReplayId);
        }
    }

    // Set resume checkpoint (high-volume events)
    EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastReplayId);
}
```

## Platform Event Retry with EventBus.RetryableException

For subscriber triggers, the platform provides built-in retry with backoff:

```apex
trigger OrderEventSubscriber on Order_Event__e (after insert) {
    for (Order_Event__e event : Trigger.new) {
        try {
            OrderEventHandler.process(event);
        } catch (Exception e) {
            // Throw RetryableException to have the platform retry
            // Platform retries up to 9 times with increasing backoff
            throw new EventBus.RetryableException(
                'Transient error, retrying: ' + e.getMessage()
            );
        }
    }
}
```

**RetryableException behavior**: The platform re-fires the trigger with the same batch of events. Maximum 9 retries. The delay increases automatically between retries (managed by the platform, not configurable). After 9 retries, the trigger moves to the error state and stops processing.

**Best Practice**: Combine checkpoint + retry:
```apex
// Set checkpoint for successfully processed events BEFORE throwing retry
EventBus.TriggerContext.currentContext().setResumeCheckpoint(lastGoodReplayId);
throw new EventBus.RetryableException('Retry from checkpoint');
```

---

## Change Data Capture (CDC)

### CDC Enablement

Enable CDC via Setup -> Integrations -> Change Data Capture, or via metadata.

**Channel Format**: `{{ObjectAPIName}}ChangeEvent` (e.g., `AccountChangeEvent`, `Order__ChangeEvent`)

### CDC Subscriber Trigger

**Template**: `templates/cdc/cdc-subscriber-trigger.trigger`

```apex
trigger {{ObjectName}}CDCSubscriber on {{ObjectName}}ChangeEvent (after insert) {

    for ({{ObjectName}}ChangeEvent event : Trigger.new) {
        EventBus.ChangeEventHeader header = event.ChangeEventHeader;
        String changeType = header.getChangeType();
        List<String> changedFields = header.getChangedFields();
        List<String> recordIds = header.getRecordIds();

        switch on changeType {
            when 'CREATE' {
                {{ObjectName}}CDCHandler.handleCreate(event, header);
            }
            when 'UPDATE' {
                {{ObjectName}}CDCHandler.handleUpdate(event, header, changedFields);
            }
            when 'DELETE' {
                {{ObjectName}}CDCHandler.handleDelete(recordIds, header);
            }
            when 'UNDELETE' {
                {{ObjectName}}CDCHandler.handleUndelete(event, header);
            }
            when 'GAP_CREATE', 'GAP_UPDATE', 'GAP_DELETE', 'GAP_UNDELETE' {
                {{ObjectName}}CDCHandler.handleGap(recordIds, changeType);
            }
            when 'GAP_OVERFLOW' {
                {{ObjectName}}CDCHandler.handleOverflow(header.getEntityName());
            }
        }
    }
}
```

### CDC Handler Service

**Template**: `templates/cdc/cdc-handler.cls` (full implementation with field filtering, gap handling, overflow detection)

Key patterns from the template:
- Filter updates to only sync relevant fields (`SYNC_FIELDS` set)
- Handle GAP events by re-querying current record state
- Handle OVERFLOW by triggering full sync batch jobs
- Delegate callouts to Queueable jobs (`ExternalSyncQueueable`)
