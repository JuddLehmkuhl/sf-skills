/**
 * @description Trigger Action: {{ActionDescription}}
 *              Executes during After Update context for {{ObjectName}} records.
 * @author      {{Author}}
 * @date        {{Date}}
 */
public with sharing class TA_{{ObjectName}}_{{ActionName}} implements TriggerAction.AfterUpdate {
    
    /**
     * @description Executes after update logic for {{ObjectName}} records.
     * @param newList List of {{ObjectName}} records with new values.
     * @param oldList List of {{ObjectName}} records with old values.
     */
    public void afterUpdate(List<{{ObjectName}}> newList, List<{{ObjectName}}> oldList) {
        Map<Id, {{ObjectName}}> oldMap = new Map<Id, {{ObjectName}}>(oldList);
        List<{{ObjectName}}> changedRecords = new List<{{ObjectName}}>();
        
        for ({{ObjectName}} record : newList) {
            {{ObjectName}} oldRecord = oldMap.get(record.Id);
            
            // Filter to only records that changed relevant fields
            // if (record.SomeField__c != oldRecord.SomeField__c) {
            //     changedRecords.add(record);
            // }
        }
        
        if (!changedRecords.isEmpty()) {
            // Delegate to service layer:
            // {{ObjectName}}Service.methodName(changedRecords);
        }
    }
}
