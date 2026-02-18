# Transaction Finalizers (Async Job Debugging)

> Parent: [SKILL.md](../SKILL.md) -- Transaction Finalizers section

Transaction Finalizers attach to Queueable jobs and execute regardless of success or failure, making them valuable for debugging async processing.

## Pattern: Capture Queueable Failure Context

```apex
public class MyQueueable implements Queueable {
    public void execute(QueueableContext ctx) {
        // Attach finalizer before any work
        System.attachFinalizer(new MyFinalizer());

        // ... business logic that might fail ...
    }
}

public class MyFinalizer implements Finalizer {
    public void execute(FinalizerContext ctx) {
        String jobId = ctx.getAsyncApexJobId();
        ParentJobResult result = ctx.getResult();

        if (result == ParentJobResult.UNHANDLED_EXCEPTION) {
            String errorMessage = ctx.getException().getMessage();
            System.debug(LoggingLevel.ERROR,
                'Queueable FAILED [' + jobId + ']: ' + errorMessage);

            // Log to custom object for production visibility
            insert new Async_Job_Log__c(
                Job_Id__c = jobId,
                Status__c = 'Failed',
                Error_Message__c = errorMessage.left(32000),
                Timestamp__c = Datetime.now()
            );

            // Optionally re-enqueue (max 5 consecutive retries)
            // System.enqueueJob(new MyQueueable());
        }
    }
}
```

## Finalizer Limits

- A failed Queueable can be re-enqueued up to **5 consecutive times** by its finalizer
- The retry counter resets when a Queueable completes successfully
- Finalizers run in their own execution context (separate governor limits)
- You can enqueue one async job (Queueable, Future, or Batch) from a finalizer
