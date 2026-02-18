#!/usr/bin/env python3
"""
Create an Action Plan Template via Salesforce REST API.

This is a reusable template script. Customize the TEMPLATE_CONFIG and ITEMS
sections for your specific template.

Usage:
    python3 create_action_plan_template.py [--org <org-alias>]

Prerequisites:
    - pip install requests
    - sf CLI authenticated to target org
"""

import json
import subprocess
import sys
import time
import requests

# ---------------------------------------------------------------------------
# Configuration — CUSTOMIZE THESE FOR YOUR TEMPLATE
# ---------------------------------------------------------------------------

ORG_ALIAS = "XSBrokers-Prod"  # Override with --org flag
API_VERSION = "v62.0"

TEMPLATE_CONFIG = {
    "Name": "My Action Plan Template",
    "ActionPlanType": "Industries",     # "Industries" for DCI support, "Standard" for Tasks only
    "TargetEntityType": "Account",      # Account, Lead, Opportunity, Case, etc.
    "Description": "Template description (max 255 characters).",
}

# Items to create on the template.
# Each item is a dict with:
#   type: "DocumentChecklistItem" or "Task"
#   unique_name: stable identifier
#   display_order: integer sequence
#   is_required: boolean
#   values: dict of {FieldName: value} — use short names, script qualifies them
ITEMS = [
    {
        "type": "DocumentChecklistItem",
        "unique_name": "dci_example",
        "display_order": 1,
        "is_required": True,
        "values": {
            "Name": "Example Document",
            "Status": "New",
            "Instruction": "Collect the example document from the agency.",
        },
    },
    {
        "type": "Task",
        "unique_name": "task_example",
        "display_order": 2,
        "is_required": True,
        "values": {
            "Subject": "Example task",
            "Priority": "High",
            "Status": "Not Started",
            "Description": "Detailed instructions for this task.",
        },
    },
]

# ---------------------------------------------------------------------------
# Salesforce connection
# ---------------------------------------------------------------------------

def get_sf_credentials(org_alias):
    """Get access token and instance URL from sf CLI."""
    result = subprocess.run(
        ["sf", "org", "display", "--target-org", org_alias, "--json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: sf org display failed:\n{result.stderr}")
        sys.exit(1)
    data = json.loads(result.stdout)["result"]
    return data["accessToken"], data["instanceUrl"]


def parse_args():
    """Parse --org flag if provided."""
    org = ORG_ALIAS
    args = sys.argv[1:]
    if "--org" in args:
        idx = args.index("--org")
        if idx + 1 < len(args):
            org = args[idx + 1]
    return org


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def sf_post(base_url, headers, sobject, payload, label=""):
    """POST to create an sObject record. Returns the Id or None."""
    url = f"{base_url}/sobjects/{sobject}"
    resp = requests.post(url, headers=headers, json=payload)
    body = resp.json()
    if resp.status_code in (200, 201) and body.get("success"):
        rec_id = body["id"]
        if label:
            print(f"  CREATED {sobject}: {label}  (Id={rec_id})")
        return rec_id
    else:
        print(f"  ERROR creating {sobject} ({label}): {resp.status_code}")
        print(f"    {json.dumps(body, indent=2)}")
        return None


def sf_query(base_url, headers, soql):
    """Run a SOQL query. Returns list of records."""
    url = f"{base_url}/query"
    resp = requests.get(url, headers=headers, params={"q": soql})
    if resp.status_code == 200:
        return resp.json().get("records", [])
    print(f"  ERROR querying: {resp.status_code} {resp.text}")
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    org = parse_args()
    print(f"Connecting to org: {org}")
    access_token, instance_url = get_sf_credentials(org)
    base_url = f"{instance_url}/services/data/{API_VERSION}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    print(f"Connected: {instance_url}\n")

    # 1. Create template
    template_id = sf_post(base_url, headers, "ActionPlanTemplate", TEMPLATE_CONFIG, TEMPLATE_CONFIG["Name"])
    if not template_id:
        sys.exit(1)

    # 2. Query auto-created version
    time.sleep(1)
    versions = sf_query(base_url, headers,
        f"SELECT Id FROM ActionPlanTemplateVersion WHERE ActionPlanTemplateId = '{template_id}'"
    )
    if not versions:
        print("ERROR: No version found")
        sys.exit(1)
    version_id = versions[0]["Id"]
    print(f"  Version: {version_id}\n")

    # 3. Create items and values
    item_count = 0
    value_count = 0
    for item_def in ITEMS:
        item_id = sf_post(base_url, headers, "ActionPlanTemplateItem", {
            "ActionPlanTemplateVersionId": version_id,
            "Name": item_def["values"].get("Name") or item_def["values"].get("Subject", item_def["unique_name"]),
            "DisplayOrder": item_def["display_order"],
            "IsRequired": item_def["is_required"],
            "ItemEntityType": item_def["type"],
            "UniqueName": item_def["unique_name"],
            "IsActive": True,
        }, label=f"#{item_def['display_order']} {item_def['unique_name']}")

        if not item_id:
            continue
        item_count += 1

        # Create values — qualify field names with entity type
        for field_name, value in item_def["values"].items():
            qualified = f"{item_def['type']}.{field_name}"
            # NOTE: Do NOT include ItemEntityType — it is read-only
            val_id = sf_post(base_url, headers, "ActionPlanTemplateItemValue", {
                "ActionPlanTemplateItemId": item_id,
                "ItemEntityFieldName": qualified,
                "ValueLiteral": value,
                "Name": field_name,
                "IsActive": True,
            }, label=f"  → {field_name}")
            if val_id:
                value_count += 1

    # 4. Summary
    print(f"\n{'='*50}")
    print(f"Template: {TEMPLATE_CONFIG['Name']}")
    print(f"  Id:      {template_id}")
    print(f"  Version: {version_id}")
    print(f"  Items:   {item_count}")
    print(f"  Values:  {value_count}")
    print(f"  Status:  Draft")
    print(f"\nNext: Go to Setup > Action Plan Templates > Publish")


if __name__ == "__main__":
    main()
