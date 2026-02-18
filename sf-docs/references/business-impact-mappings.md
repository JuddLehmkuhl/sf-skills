# Inferring Business Impact from Code

Use these mappings to connect technical implementation to business outcomes when generating documentation.

## Code Behavior to User Impact

| Code Behavior | User Impact |
|---------------|-------------|
| Sets default field values | Users don't have to fill in every field manually |
| Validates required fields | Prevents incomplete records that cause problems later |
| Auto-creates related records | Setup steps that were manual now happen automatically |
| Sends notification | Users get alerted when [event] without checking manually |
| Updates parent record | Totals and summaries stay up-to-date automatically |
| Assigns owner | Records get routed to the right person without manual intervention |
| Enforces sharing rules | Users see only the records they're supposed to see |

## Object to Business User Mapping

Customize this table for your project's industry/context:

| Salesforce Object | Typical Business Users |
|-------------------|------------------------|
| Lead | Sales team, marketing, business development |
| Account | Account managers, service reps |
| Contact | Sales reps, customer service |
| Opportunity | Sales reps, sales managers |
| Case | Service reps, support team |
| Task/Event | All users with activity management |
| Custom Objects | [Map to your business domain] |
