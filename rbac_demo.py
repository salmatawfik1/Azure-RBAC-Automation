import os
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.authorization import AuthorizationManagementClient

SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
RESOURCE_GROUP_NAME = "RBACDemo"
LOCATION = "eastus"

USERS = {
    "UserA": "11111111-1111-1111-1111-111111111111",
    "UserB": "22222222-2222-2222-2222-222222222222",
    "UserC": "33333333-3333-3333-3333-333333333333"
}

ROLES = {
    "Reader": {"id": "acdd72a7-3385-48ef-bd42-f606fba81ae7", "rank": 1},
    "Contributor": {"id": "b24988ac-6180-42a0-ab88-20f7382dd24c", "rank": 2},
    "Owner": {"id": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635", "rank": 3}
}
user_roles = {user: [] for user in USERS}

credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
auth_client = AuthorizationManagementClient(credential, SUBSCRIPTION_ID)

def create_resource_group():
    print("\033[94mChecking if the Resource Group exists...\033[0m")
    try:
        resource_client.resource_groups.get(RESOURCE_GROUP_NAME)
        print(f"✔ Resource Group '{RESOURCE_GROUP_NAME}' already exists, Using the existing one.")
    except Exception:
        print(f"Creating Resource Group '{RESOURCE_GROUP_NAME}'...")
        resource_client.resource_groups.create_or_update(
            RESOURCE_GROUP_NAME,
            {"location": LOCATION}
        )
        print(f"✔ Resource Group '{RESOURCE_GROUP_NAME}' created successfully.")


def sync_existing_roles():
    print("Syncing existing roles from Azure...\n")
    role_assignments = auth_client.role_assignments.list_for_scope(
        f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}"
    )

    for role in role_assignments:
        role_dict = role.as_dict()
        user_id = role_dict.get("principal_id")
        role_guid = role_dict.get("role_definition_id", "").split("/")[-1]
        role_name = next((name for name, details in ROLES.items() if details["id"] == role_guid), None)
        if role_name:
            for user_name, uid in USERS.items():
                if uid == user_id:
                    user_roles[user_name].append(role_name)

    print("\n✔ Existing roles synchronized:")
    for user, role in user_roles.items():
        print(f"- {user} {role}")


def assign_role(user_name, role_name):
    if role_name not in ROLES:
        print(f"❌ Invalid role: {role_name}\n")
        return

    role_id = ROLES[role_name]["id"]
    role_rank = ROLES[role_name]["rank"]
    current_roles = user_roles[user_name]

    # Check if the user already has a higher or equal role
    highest_role = max(current_roles, key=lambda r: ROLES[r]["rank"], default=None)
    if highest_role and ROLES[highest_role]["rank"] >= role_rank:
        print(f"❌ {user_name} already has {highest_role}, which is equal or higher than {role_name}.\n")
        return

    removed_roles = [r for r in current_roles if ROLES[r]["rank"] < role_rank]
    removed_role = None
    for r in removed_roles:
        try:
            role_assignments = auth_client.role_assignments.list_for_scope(
                f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}"
            )
            for assignment in role_assignments:
                if assignment.principal_id == USERS[user_name] and assignment.role_definition_id.endswith(ROLES[r]["id"]):
                    auth_client.role_assignments.delete(
                        scope=f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}",
                        role_assignment_name=assignment.name
                    )
                    removed_role = r
                    break
        except Exception as e:
            print(f"❌ Failed to remove {r} role: {e}")

    if removed_role:
        print(f"🔄 {user_name} has been upgraded from {removed_role} to {role_name}.\n")

    try:
        auth_client.role_assignments.create(
            scope=f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}",
            role_assignment_name=os.urandom(16).hex(),
            parameters={"properties": {
                "roleDefinitionId": f"/subscriptions/{SUBSCRIPTION_ID}/providers/Microsoft.Authorization/roleDefinitions/{role_id}",
                "principalId": USERS[user_name]
            }}
        )
        user_roles[user_name] = [role_name]
        print(f"✅ {role_name} role assigned to {user_name} successfully.\n")
    except Exception as e:
        print(f"❌ Failed to assign {role_name} role: {e}\n")

def read_resource(user_name):
    print(f"{user_name} is attempting to read Resource Group '{RESOURCE_GROUP_NAME}'...")
    time.sleep(1)
    if any(ROLES[role]["rank"] >= 1 for role in user_roles[user_name]):
        print(f"✅ {user_name} successfully read the resource group: {RESOURCE_GROUP_NAME}\n")
    else:
        print(f"❌ {user_name} doesn't have permission to read the resource group.\n")

def modify_resource(user_name):
    print(f"{user_name} is attempting to modify the Resource Group...")
    time.sleep(1)
    if any(ROLES[role]["rank"] >= 2 for role in user_roles[user_name]):
        print(f"✅ {user_name} successfully modified the resource group.\n")
    else:
        print(f"❌ {user_name} doesn't have permission to modify resources.\n")

def delete_resource(user_name):
    print(f"{user_name} is attempting to delete the Resource Group...")
    time.sleep(1)
    if "Owner" in user_roles[user_name]:
        delete_confirmation = input(
            f"⚠ {user_name}, are you sure you want to delete '{RESOURCE_GROUP_NAME}'? (yes/no): ").strip().lower()
        if delete_confirmation.startswith("y"):
            resource_client.resource_groups.begin_delete(RESOURCE_GROUP_NAME)
            print(f"✅ {user_name} deleted the Resource Group '{RESOURCE_GROUP_NAME}' successfully.\n")
        else:
            print("❌ Deletion cancelled.\n")
    else:
        print(f"❌ {user_name} isn't allowed to delete resources.\n")


if __name__ == "__main__":
    create_resource_group()
    sync_existing_roles()
    while True:
        selected_user = input("\nEnter the user to assign a role (or 'exit' to stop): ").strip()
        if selected_user.lower() == "exit":
            break
        if selected_user not in USERS:
            print("❌ User not found. Try again.")
            continue

        selected_role = input("\nEnter the role to assign: ").strip().title()
        assign_role(selected_user, selected_role)
    print("\n✅ Role assignments completed.")

    for user_name in USERS.keys():
        roles_display = ", ".join(user_roles[user_name]) if user_roles.get(user_name) else "No Role"
        print(f"\n\033[94mSimulating actions for {user_name} ({roles_display})...\033[0m")
        read_resource(user_name)
        modify_resource(user_name)
        delete_resource(user_name)
