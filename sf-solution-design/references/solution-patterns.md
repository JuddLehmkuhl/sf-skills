# Solution Patterns

After completing the checklist and decision matrices, use these patterns for common scenarios.

## Account & Relationship Management
```
Hierarchy Visualization  --> ARC relationship graphs (FSC) OR Account Hierarchy (standard)
Individual Tracking      --> Person Accounts
Organization Tracking    --> Business Accounts with Record Types
Relationship Mapping     --> Account-Account Relations OR Contact Roles
Quick Context            --> Einstein Sales Summaries + Record Research
```

## Sales Process
```
Prospecting     --> Sales Engagement cadences OR SDR Agent
Pipeline Mgmt   --> Pipeline Inspection + Forecasting
Activity Logging --> Einstein Activity Capture (automatic)
Deal Progression --> Close Plans + Buying Committee
Follow-ups      --> Meeting Follow-Up Emails (AI-generated)
Coaching        --> Sales Coach agent during calls
```

## Customer Service
```
Support Inquiries --> Service Agent (autonomous)
Response Drafting --> GPT Service Replies
Case Context      --> Work Summaries
Knowledge Lookup  --> Knowledge base + Search Answers
Call Analysis     --> Conversation Insights
Routing           --> Omni-Channel with skill-based routing
```

## Data Integration
```
External System Sync --> Data Cloud pipelines OR Named Credentials + External Services
Real-time Data       --> Context Service in flows OR Platform Events
Record Matching      --> Identity Resolution (Data Cloud) OR Duplicate Rules (standard)
Unified View         --> Customer Data Platform profiles
```
> **Route to:** `sf-integration` for Named Credentials, External Services, REST/SOAP callouts.

## Guided Experiences
```
Multi-step Processes   --> OmniScripts (if available) OR Screen Flows
Dynamic UI Cards       --> FlexCards (if available) OR LWC
Decision Logic         --> Business Rules Engine OR Flow Decision elements
Document Generation    --> DocGen templates OR custom Apex (see sf-apex)
```

## Task & Process Management
```
Templated Task Sequences --> Action Plan Templates (see sf-action-plans)
Required Document Lists  --> Document Checklist Items (see sf-action-plans)
Approval Workflows       --> Approval Processes (standard)
Scheduled Reminders      --> Scheduled Flows (see sf-flow)
```

## Reporting & Analytics
```
Executive Dashboards   --> Tableau
Operational Metrics    --> CRM Analytics
Record-level Insights  --> Embedded Analytics
Standard Reporting     --> Reports & Dashboards (available in ALL orgs)
```
