---
name: azure-ad
description: Manage people and groups in a Microsoft Entra ID (Azure AD) tenant. Use when someone wants to invite an external guest or partner, onboard a group of collaborators, create a security group, add or remove group members, write access instructions for the people invited, see which Azure subscriptions are in the tenant, create a resource group and give a group access to it, remove guests or delete a group when an engagement ends, look up a user or a group's members, find out what they are allowed to do in the tenant, or diagnose an "insufficient privileges" error on any of these.
---

# Entra ID users, guests, and groups

`scripts/entra.py` (in this skill's directory) does the work, for the directory and for the Azure access that goes with it. It uses the person's Azure CLI sign-in, needs only Python 3.10+ and `az`, and prints one JSON object. Run it with `python3`, or `python` on Windows.

| Goal | Command |
|---|---|
| Who am I, which tenant, what can I do here | `check` |
| Look up people and their groups | `user EMAIL...` |
| Group details, members, owners | `group show NAME` |
| Invite guests, optionally into groups | `invite --email A,B --groups G1,G2` |
| Create a security group | `group create --name NAME --description TEXT` |
| Add existing users to groups | `group add --group G --email A,B` |
| Remove users from groups | `group remove --group G --email A,B` |
| Delete a group, optionally with its guests | `group delete --name NAME [--delete-guests]` |
| Delete guest accounts | `offboard --email A,B` |
| Subscriptions in the tenant | `azure subscriptions` |
| Give a group a role on a resource group, creating it if needed | `azure grant --subscription S --resource-group RG --group G` |
| Take a group's roles off a resource group | `azure revoke --subscription S --resource-group RG --group G` |
| Azure roles a group holds anywhere in the tenant | `azure access --group G` |

Full options, output fields, and error codes are in [references/commands.md](references/commands.md). A request that covers several of these, such as "add these people to a new group and write their instructions", is in [references/engagements.md](references/engagements.md).

## Changes are planned first, then applied

`invite`, `group create`, `group add`, `group remove`, `group delete`, `offboard`, `azure grant`, and `azure revoke` only plan until `--apply` is added. An invitation emails a real person outside the organization, and group membership often carries access to cloud resources, so the person asking has to see exactly what will happen before it does.

1. Run the command without `--apply`.
2. Show the plan: the tenant, each person and whether they are new or existing, each group and where it came from, anything left out and why, and whether an invitation email will be sent.
3. Once they approve that plan, run the same command with `--apply`. If anything about the request changes, plan again.

A request to look into, test, or troubleshoot something is not approval to change it.

After applying, report what the result says for each person and group: invited, already present, added, or failed. A partial result stays partial in the summary; completed steps are not rolled back, and re-running the same command finishes only what is missing.

## Deleting needs the code from the plan

`group delete` and `offboard` remove things that other people depend on, and a deleted security group cannot be restored. Their plan returns a `confirm` code tied to exactly the group and accounts it listed. Applying requires that code:

1. Run the command without `--apply` and show the plan in full: the group, every account that would be deleted, and every account that would be kept with its reason.
2. When the person approves that list, run the same command with `--apply --confirm CODE`.

If the membership changed in between, the code no longer matches and the script returns `plan_changed`. Plan again and show the new plan; the earlier approval was for a different list.

The script keeps some accounts no matter what is asked: the signed-in account, anyone holding a directory role, and anyone who is not a guest. With `group delete --delete-guests` it also keeps guests who belong to another group, because that membership means someone else still expects them to have access. Report the kept accounts and their reasons. Deleting one of them is a separate, explicit request through `offboard`.

## The tenant must be explicit for changes

Reads fall back to whichever tenant the Azure CLI is signed in to. Changes do not, because people with accounts in several tenants would otherwise invite guests into the wrong one. Pass `--tenant TENANT_ID` or have `ENTRA_TENANT_ID` set. When the script reports `missing_tenant`, show the tenant it found and ask whether that is the intended one before adding `--tenant`.

Every result names the tenant it ran against. Include it when showing a plan.

## Groups that grant privilege

Some groups carry directory roles or broad cloud access. The script treats a group as protected when it is role-assignable or is named in `ENTRA_PROTECTED_GROUPS`.

- `--like EMAIL` copies another user's direct groups and leaves protected and dynamic groups out, listing them under `skipped_groups`. It does not copy inherited access, directory roles, or group ownership.
- A protected group named in `--groups` is refused until `--allow-protected` is added. Add it only after the person confirms they mean to grant that group.
- The script cannot see what Azure roles an ordinary group holds. When a plan copies groups with `--like`, show the full list so the person can catch one that grants more than intended.

## Azure access for a group

`azure grant` gives a group a role on one resource group. The role defaults to Contributor; Reader is the choice when people only need to look. If the resource group does not exist the command creates it, which needs `--location`: ask for the region when the person has not given one. The plan shows the subscription it resolved, whether the resource group exists, and whether the group already holds the role.

Owner, User Access Administrator, and Role Based Access Control Administrator let every member of the group hand out access to others. The script refuses them until `--allow-protected` is added, on the same terms as a protected group.

Use these commands for subscription and access questions instead of `az account list`. They ask Azure for the signed-in tenant only, so they do not trigger a sign-in to the person's other tenants.

`azure revoke` removes the group's roles from the resource group and leaves the resource group and its contents in place. Deleting a resource group destroys what is in it and is not something this skill does.

## Start with `check` when access is in doubt

`check` reports the signed-in identity, its directory roles, the tenant's invitation and group-creation policy, and which operations that combination should allow. Use it before a first change in a tenant and whenever a command fails with `http_403`.

If a capability is missing, say which role or setting would provide it ([references/permissions.md](references/permissions.md)) and that a tenant administrator has to grant it. Granting a role, changing tenant policy, or consenting to permissions widens what an account can do across the whole tenant, so none of them is a way past a refused command. Each is its own request for an administrator to make deliberately.

A role granted moments ago is not in the current token. `az logout` followed by `az login --tenant TENANT_ID` picks it up.

## Related work

- Bringing people in for an engagement and removing them afterwards, including the instructions to send them: [references/engagements.md](references/engagements.md)
- The Azure resource group and role assignment that often follow an onboarding: [references/partner-onboarding.md](references/partner-onboarding.md)
- Errors and what to do about each: [references/troubleshooting.md](references/troubleshooting.md)
- OSDU or ADME entitlements are separate from Entra groups and are not handled here.
