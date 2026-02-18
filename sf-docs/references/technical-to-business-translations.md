# Translating Technical to Business Language

Use these tables when generating Feature Summaries to translate technical concepts into plain language.

## Actions/Behaviors

| Technical Concept | Business Translation |
|-------------------|---------------------|
| Trigger fires on insert | When someone creates a new [record type] |
| Trigger fires on update | When someone edits a [record type] |
| Validation rule prevents save | The system checks that [condition] before saving |
| Flow runs after save | After saving, the system automatically [action] |
| Field default value | The system fills in [field] automatically |
| Required field | You must enter [field] before saving |
| Lookup filter | When selecting [related record], only [criteria] options appear |
| Assignment rule | The system automatically assigns [record] to [owner/queue] |
| Workflow email | The system sends an email when [condition] |
| Scheduled job | Every [frequency], the system [action] |

## Components

| Technical Term | Business Translation |
|----------------|---------------------|
| Apex class | Automatic process |
| Trigger | Automatic process |
| Flow | Automatic process |
| Custom Metadata | Configuration / Settings |
| Permission Set | Access settings |
| Profile | User type settings |
| Custom Object | [Use business name] |
| Custom Field | [Use field label] |
| Page Layout | Screen layout |
| Lightning Component | Screen section / Feature |
| Validation Rule | Data check / Requirement |
| Formula Field | Calculated field |
| Roll-up Summary | Automatic total |

## Patterns

| Technical Pattern | Business Translation |
|-------------------|---------------------|
| "Implemented X framework" | [Omit or] "Added foundation for [capability]" |
| "Refactored for performance" | "Improved speed of [feature]" |
| "Added error handling" | "Better error messages when [scenario]" |
| "Bulkified processing" | [Omit - internal] |
| "Optimized queries" | "[Feature] now loads faster" |
| "Added test coverage" | [Omit - internal] |
| "Metadata-driven configuration" | "Settings can be adjusted without code changes" |
| "Enabled bypass mechanism" | "Can be turned off during data imports" |

## Trigger Actions Framework Translations

When documenting features built with the `salesforce-trigger-framework` skill, apply these specific translations:

| TAF Concept | Business Translation |
|-------------|---------------------|
| TA_Lead_SetDefaults (BeforeInsert) | "When a new lead is created, the system fills in default values" |
| TA_Account_ValidateFields (BeforeUpdate) | "When someone edits an account, the system checks the data is valid" |
| TA_Opportunity_CreateTasks (AfterInsert) | "When a new opportunity is created, the system creates follow-up tasks" |
| sObject_Trigger_Setting__mdt bypass | "This behavior can be temporarily turned off for bulk data imports" |
| Trigger_Action__mdt ordering | [Omit - internal execution detail] |
| MetadataTriggerHandler dispatch | [Omit - internal plumbing] |
