- This project simulates Role-Based Access Control (RBAC) automation in Microsoft Azure using Python. It allows dynamic role assignments, simulates access attempts based on roles, and manages privilege hierarchy.
- Built as part of a security demo on RBAC, this tool uses the Azure SDK to manage real resources via Azure’s Authorization and Resource Management APIs.

🚀 Features:
- Role Assignment Automation: Assign roles (Reader, Contributor, Owner) to users programmatically
- Real Azure Integration: Uses DefaultAzureCredential and interacts with actual Azure subscriptions
- RBAC Implementation:
   - Properly handles role hierarchy (Reader < Contributor < Owner)
   - Implements Privilege Hierarchy by Auto-upgrading and revokeing old roles when a higher one is assigned
   - Validates against duplicate or lower-ranked role assignments
- Simulates user actions like:
   - 📖 Reading the resource group → allowed for all roles
   - 🛠 Modifying the resource group → requires Contributor or Owner
   - 🗑 Deleting the resource group → requires Owner only
- Error Handling:
   - Includes try-catch blocks for Azure operations with meaningful error messages.
   - Checks if the resource group exists (creates it if not)
- User Experience:
   - Interactive command-line interface
   - Color-coded output for better visibility
   - Clear success/failure messages
  
⚠ Disclaimer: 
   - All values in this repository (user UUIDs, subscription IDs, etc.) are dummy placeholders.
   - No real identities or secrets are exposed.
   - Replace:
     - "AZURE_SUBSCRIPTION_ID" with your real Azure subscription ID
     - "RBACDemo" with your resource group name
     - "UserA/B/C" with actual usernames and their object IDs

📌 Future Improvements:
   - Import users/roles from YAML or CSV file
   - Add logging (e.g., access logs, assignment logs)
   - Export user-role mappings to CSV
   - Support bulk assignment via CLI args
   - Add role expiration (e.g., temporary access window)

Feel free to reach out if you'd like to collaborate, discuss improvements, or have questions about Azure IAM: salmatawfik.39@gmail.com
