trigger {{ObjectName}}Trigger on {{ObjectName}} (
    before insert,
    before update,
    before delete,
    after insert,
    after update,
    after delete,
    after undelete
) {
    new MetadataTriggerHandler().run();
}
