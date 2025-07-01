- This project simulates Role-Based Access Control (RBAC) automation in Microsoft Azure using Python. It allows dynamic role assignments, simulates access attempts based on roles, and manages privilege hierarchy.
- Built as part of a security demo on RBAC, this tool uses the Azure SDK to manage real resources via Azure’s Authorization and Resource Management APIs.

🚀 Features:
- Role Assignment Automation: Assign roles (Reader, Contributor, Owner) to users programmatically
- Privilege Hierarchy: Auto-upgrades and revokes old roles when a higher one is assigned
- Real Azure Integration: Uses DefaultAzureCredential and interacts with actual Azure subscriptions
- Simulates user actions like:
    - Reading the resource group (All 3 roles can read the resource group)
    - Modifying the resource group (requires a contributor or owner role)
    - Deleting the resource group (only the owner can delete the resource group)

⚠ Disclaimer: 
   - All values in this repository (user UUIDs, subscription IDs, etc.) are dummy placeholders.
   - No real identities or secrets are exposed.
   - Replace "AZURE_SUBSCRIPTION_ID" with your real subscription ID, "RBACDemo" with your resource group name, "USER A/B/C" with real usernames and their subscription IDs.

📌 Possible Improvements:
   - Import users/roles from YAML or CSV file
   - Add logging (e.g., access logs, assignment logs)
   - Export user-role mappings to CSV
   - Support bulk assignment via CLI args
   - Add role expiration (e.g., temporary access window)
