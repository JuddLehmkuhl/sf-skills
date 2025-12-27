/**
 * @description Trigger Action: {{ActionDescription}}
 *              Executes during After Insert context for {{ObjectName}} records.
 * @author      {{Author}}
 * @date        {{Date}}
 */
public with sharing class TA_{{ObjectName}}_{{ActionName}} implements TriggerAction.AfterInsert {
    
    /**
     * @description Executes after insert logic for {{ObjectName}} records.
     *              Records have IDs at this point. Cannot modify trigger records directly.
     * @param newList List of newly inserted {{ObjectName}} records.
     */
    public void afterInsert(List<{{ObjectName}}> newList) {
        // Records have IDs now - can create related records, make callouts, etc.
        // Cannot modify the records in newList directly
        
        // Delegate to service layer:
        // {{ObjectName}}Service.methodName(newList);
    }
}
