#!/usr/bin/env python3
"""
Trigger Action Generator
Generates all required files for a new trigger action in the Trigger Actions Framework.

Usage:
    python generate_trigger_action.py <ObjectName> <ActionName> <Context> [--order ORDER] [--output-dir DIR]

Examples:
    python generate_trigger_action.py Lead SetDefaults BeforeInsert --order 10
    python generate_trigger_action.py Opportunity ValidateAmount BeforeInsert --order 20 --output-dir force-app/main/default
"""

import argparse
import os
from datetime import date
from pathlib import Path

# Context mapping for interface names
CONTEXT_MAP = {
    'BeforeInsert': 'TriggerAction.BeforeInsert',
    'AfterInsert': 'TriggerAction.AfterInsert',
    'BeforeUpdate': 'TriggerAction.BeforeUpdate',
    'AfterUpdate': 'TriggerAction.AfterUpdate',
    'BeforeDelete': 'TriggerAction.BeforeDelete',
    'AfterDelete': 'TriggerAction.AfterDelete',
    'AfterUndelete': 'TriggerAction.AfterUndelete'
}

CONTEXT_LABEL_MAP = {
    'BeforeInsert': 'Before_Insert',
    'AfterInsert': 'After_Insert',
    'BeforeUpdate': 'Before_Update',
    'AfterUpdate': 'After_Update',
    'BeforeDelete': 'Before_Delete',
    'AfterDelete': 'After_Delete',
    'AfterUndelete': 'After_Undelete'
}

# Method signatures for each context
METHOD_SIGNATURES = {
    'BeforeInsert': 'public void beforeInsert(List<{obj}> newList)',
    'AfterInsert': 'public void afterInsert(List<{obj}> newList)',
    'BeforeUpdate': 'public void beforeUpdate(List<{obj}> newList, List<{obj}> oldList)',
    'AfterUpdate': 'public void afterUpdate(List<{obj}> newList, List<{obj}> oldList)',
    'BeforeDelete': 'public void beforeDelete(List<{obj}> oldList)',
    'AfterDelete': 'public void afterDelete(List<{obj}> oldList)',
    'AfterUndelete': 'public void afterUndelete(List<{obj}> newList)'
}


def generate_trigger_action_class(object_name: str, action_name: str, context: str) -> str:
    """Generate the Apex trigger action class."""
    interface = CONTEXT_MAP[context]
    method_sig = METHOD_SIGNATURES[context].format(obj=object_name)
    
    has_old_list = context in ['BeforeUpdate', 'AfterUpdate', 'BeforeDelete', 'AfterDelete']
    method_name = context[0].lower() + context[1:]
    
    body_lines = []
    if has_old_list and 'Update' in context:
        body_lines.append(f'        Map<Id, {object_name}> oldMap = new Map<Id, {object_name}>(oldList);')
        body_lines.append('')
        body_lines.append(f'        for ({object_name} record : newList) {{')
        body_lines.append(f'            {object_name} oldRecord = oldMap.get(record.Id);')
        body_lines.append('            // Check for field changes')
        body_lines.append('            // if (record.Field__c != oldRecord.Field__c) { }')
        body_lines.append('        }')
    elif 'Delete' in context:
        body_lines.append(f'        for ({object_name} record : oldList) {{')
        body_lines.append('            // Process deleted records')
        body_lines.append('        }')
    else:
        body_lines.append(f'        for ({object_name} record : newList) {{')
        body_lines.append('            // Process records')
        body_lines.append('        }')
    
    body = '\n'.join(body_lines)
    
    return f'''/**
 * @description Trigger Action for {object_name}: {action_name}
 *              Context: {context}
 * @author      PS Advisory
 * @date        {date.today().isoformat()}
 */
public with sharing class TA_{object_name}_{action_name} implements {interface} {{
    
    {method_sig} {{
{body}
    }}
}}
'''


def generate_test_class(object_name: str, action_name: str, context: str) -> str:
    """Generate the test class for the trigger action."""
    method_name = context[0].lower() + context[1:]
    is_update = 'Update' in context
    is_delete = 'Delete' in context
    
    return f'''/**
 * @description Test class for TA_{object_name}_{action_name}
 * @author      PS Advisory
 * @date        {date.today().isoformat()}
 */
@IsTest
private class TA_{object_name}_{action_name}_Test {{
    
    @TestSetup
    static void makeData() {{
        // Create test data
    }}
    
    @IsTest
    static void test{action_name}_standardScenario_success() {{
        // Arrange
        {object_name} record = new {object_name}(
            // Set required fields
        );
        
        // Act
        Test.startTest();
        insert record;
        Test.stopTest();
        
        // Assert
        {object_name} result = [SELECT Id FROM {object_name} WHERE Id = :record.Id];
        System.assertNotEquals(null, result, 'Record should exist');
    }}
    
    @IsTest
    static void test{action_name}_unitTest_noDb() {{
        // Arrange
        {object_name} record = new {object_name}(
            // Set required fields
        );
        List<{object_name}> records = new List<{object_name}> {{ record }};
        
        // Act
        TA_{object_name}_{action_name} action = new TA_{object_name}_{action_name}();
        action.{method_name}(records{', records' if is_update else ', records' if is_delete and 'Before' in context else ''});
        
        // Assert
        System.assert(true, 'Action executed without error');
    }}
    
    @IsTest
    static void test{action_name}_bulk_handlesLimits() {{
        // Arrange
        List<{object_name}> records = new List<{object_name}>();
        for (Integer i = 0; i < 200; i++) {{
            records.add(new {object_name}(
                // Set required fields
            ));
        }}
        
        // Act
        Test.startTest();
        insert records;
        Test.stopTest();
        
        // Assert
        System.assertEquals(200, [SELECT COUNT() FROM {object_name}], 'All records inserted');
    }}
    
    @IsTest
    static void test{action_name}_bypassed_doesNotRun() {{
        // Arrange
        {object_name} record = new {object_name}(
            // Set required fields
        );
        
        TriggerBase.bypass('TA_{object_name}_{action_name}');
        
        // Act
        Test.startTest();
        try {{
            insert record;
        }} finally {{
            TriggerBase.clearBypass('TA_{object_name}_{action_name}');
        }}
        Test.stopTest();
        
        // Assert - verify action did not run
        System.assert(true, 'Bypass worked');
    }}
}}
'''


def generate_apex_meta() -> str:
    """Generate the Apex class metadata XML."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <status>Active</status>
</ApexClass>
'''


def generate_trigger_action_metadata(object_name: str, action_name: str, context: str, order: int) -> str:
    """Generate the Custom Metadata record for the trigger action."""
    context_label = CONTEXT_LABEL_MAP[context]
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <label>{object_name} {context_label} {order} {action_name}</label>
    <protected>false</protected>
    <values>
        <field>Apex_Class_Name__c</field>
        <value xsi:type="xsd:string">TA_{object_name}_{action_name}</value>
    </values>
    <values>
        <field>Order__c</field>
        <value xsi:type="xsd:double">{order}</value>
    </values>
    <values>
        <field>Bypass_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Required_Permission__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>sObject__c</field>
        <value xsi:type="xsd:string">sObject_Trigger_Setting.{object_name}</value>
    </values>
    <values>
        <field>Flow_Name__c</field>
        <value xsi:nil="true"/>
    </values>
    <values>
        <field>Allow_Flow_Recursion__c</field>
        <value xsi:type="xsd:boolean">false</value>
    </values>
</CustomMetadata>
'''


def main():
    parser = argparse.ArgumentParser(description='Generate Trigger Action files')
    parser.add_argument('object_name', help='Salesforce object name (e.g., Lead, Account)')
    parser.add_argument('action_name', help='Action name (e.g., SetDefaults, ValidateFields)')
    parser.add_argument('context', choices=list(CONTEXT_MAP.keys()),
                        help='Trigger context')
    parser.add_argument('--order', type=int, default=10,
                        help='Execution order (default: 10)')
    parser.add_argument('--output-dir', default='force-app/main/default',
                        help='Output directory (default: force-app/main/default)')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    classes_dir = output_dir / 'classes'
    metadata_dir = output_dir / 'customMetadata'
    
    # Create directories
    classes_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    class_name = f'TA_{args.object_name}_{args.action_name}'
    test_name = f'{class_name}_Test'
    context_label = CONTEXT_LABEL_MAP[args.context]
    metadata_name = f'Trigger_Action.{args.object_name}_{context_label}_{args.order}_{args.action_name}'
    
    files_created = []
    
    # Trigger Action Class
    class_path = classes_dir / f'{class_name}.cls'
    class_path.write_text(generate_trigger_action_class(args.object_name, args.action_name, args.context))
    files_created.append(str(class_path))
    
    # Trigger Action Class Meta
    meta_path = classes_dir / f'{class_name}.cls-meta.xml'
    meta_path.write_text(generate_apex_meta())
    files_created.append(str(meta_path))
    
    # Test Class
    test_path = classes_dir / f'{test_name}.cls'
    test_path.write_text(generate_test_class(args.object_name, args.action_name, args.context))
    files_created.append(str(test_path))
    
    # Test Class Meta
    test_meta_path = classes_dir / f'{test_name}.cls-meta.xml'
    test_meta_path.write_text(generate_apex_meta())
    files_created.append(str(test_meta_path))
    
    # Custom Metadata
    cmd_path = metadata_dir / f'{metadata_name}.md-meta.xml'
    cmd_path.write_text(generate_trigger_action_metadata(
        args.object_name, args.action_name, args.context, args.order
    ))
    files_created.append(str(cmd_path))
    
    print(f'✅ Generated {len(files_created)} files:')
    for f in files_created:
        print(f'   - {f}')
    
    print(f'\n📋 Next steps:')
    print(f'   1. Verify sObject_Trigger_Setting.{args.object_name} exists')
    print(f'   2. Implement business logic in {class_name}.cls')
    print(f'   3. Complete test class {test_name}.cls')
    print(f'   4. Deploy: sf project deploy start --source-dir {output_dir}')


if __name__ == '__main__':
    main()
