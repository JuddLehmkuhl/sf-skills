/**
 * @description Trigger Action: {{ActionDescription}}
 *              Executes during {{Context}} context for {{ObjectName}} records.
 * @author      {{Author}}
 * @date        {{Date}}
 */
public with sharing class TA_{{ObjectName}}_{{ActionName}} implements TriggerAction.BeforeInsert {
    
    /**
     * @description Executes before insert logic for {{ObjectName}} records.
     * @param newList List of new {{ObjectName}} records being inserted.
     */
    public void beforeInsert(List<{{ObjectName}}> newList) {
        // TODO: Implement business logic
        // Delegate to service layer for complex operations:
        // {{ObjectName}}Service.methodName(newList);
        
        for ({{ObjectName}} record : newList) {
            // Direct field manipulation for simple operations
        }
    }
}
