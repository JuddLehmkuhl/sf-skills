/**
 * @description Trigger Action: {{ActionDescription}}
 *              Executes during Before Update context for {{ObjectName}} records.
 * @author      {{Author}}
 * @date        {{Date}}
 */
public with sharing class TA_{{ObjectName}}_{{ActionName}} implements TriggerAction.BeforeUpdate {
    
    /**
     * @description Executes before update logic for {{ObjectName}} records.
     * @param newList List of {{ObjectName}} records with new values.
     * @param oldList List of {{ObjectName}} records with old values.
     */
    public void beforeUpdate(List<{{ObjectName}}> newList, List<{{ObjectName}}> oldList) {
        Map<Id, {{ObjectName}}> oldMap = new Map<Id, {{ObjectName}}>(oldList);
        
        for ({{ObjectName}} record : newList) {
            {{ObjectName}} oldRecord = oldMap.get(record.Id);
            
            // Check for field changes
            // if (record.SomeField__c != oldRecord.SomeField__c) {
            //     // Handle change
            // }
        }
    }
}
