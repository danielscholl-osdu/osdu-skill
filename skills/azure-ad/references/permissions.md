# What each operation requires

For a person signed in through the Azure CLI, two things decide what works: the directory roles they hold and the tenant's own policy. `check` reports both.

| Operation | Works when |
|---|---|
| Look up users and groups | Any member of the tenant, unless the tenant restricts directory reads. |
| Invite a guest | The tenant's guest invite setting allows it. With the common "admins and guest inviters" setting, the person needs Guest Inviter, User Administrator, Directory Writers, or Global Administrator. |
| Create a security group | The person holds Groups Administrator, User Administrator, Directory Writers, or Global Administrator, or the tenant lets members create security groups. |
| Add a member to a group | The person owns the group, or holds one of the group-creating roles above. |
| Remove a member from a group | Same as adding one. |
| Delete a group | The person owns the group, or holds Groups Administrator, User Administrator, or Global Administrator. |
| Delete a guest account | The person holds User Administrator or Global Administrator. Guest Inviter and Groups Administrator cannot, even for guests they invited. |
| Add a member to a role-assignable group | The person owns the group or holds Privileged Role Administrator or Global Administrator. Other roles cannot. |
| Add a member to a dynamic group | Not possible. Membership follows the group's rule. |

## Azure resources

Azure access is separate from directory roles. Holding User Administrator does not let someone create a resource group.

| Operation | Works when |
|---|---|
| List subscriptions | The person has any role on them. Subscriptions they have no role on do not appear. |
| Create a resource group | Contributor or Owner on the subscription. |
| Assign or remove a role on a resource group | Owner, User Access Administrator, or Role Based Access Control Administrator at that scope or above. |

## Getting a missing capability

These are decisions for a tenant administrator, not steps this skill performs.

- **Invitations only:** the Guest Inviter role. It allows inviting and nothing else.
- **Groups as well:** the Groups Administrator role. Its holder can change the membership of every group that is not role-assignable, including groups that hold powerful Azure roles, so it is a wider grant than the name suggests.
- **Removing guests afterwards:** the User Administrator role. Without it, a person can delete the engagement's group they own but has to ask an administrator to delete the guest accounts.
- **One group only:** make the person an owner of that group. No directory role is needed.
- **Roles through a group:** assigning a directory role to a group requires Microsoft Entra ID P1. Without that licence, roles are assigned to each person directly.

A new role reaches the Azure CLI only after signing in again: `az logout`, then `az login --tenant TENANT_ID`.

## Application identities

When the Azure CLI is signed in as a service principal, directory roles and tenant policy apply differently and `check` does not derive capabilities. The Microsoft Graph application permissions involved are `User.Read.All` and `Group.Read.All` for lookups, `User.Invite.All` for invitations, `Group.Create` for new groups, and `GroupMember.ReadWrite.All` for membership.
