---
name: azure-ad
description: Manage people and groups in a Microsoft Entra ID (Azure AD) tenant. Use when someone wants to invite an external guest or partner, onboard a group of collaborators, create a security group, add users to groups, look up a user or a group's members, find out what they are allowed to do in the tenant, or diagnose an "insufficient privileges" error on any of these.
---

# Entra ID users, guests, and groups

`scripts/entra.py` (in this skill's directory) does the work. It uses the person's Azure CLI sign-in, needs only Python 3.10+ and `az`, and prints one JSON object. Run it with `python3`, or `python` on Windows.

| Goal | Command |
|---|---|
| Who am I, which tenant, what can I do here | `check` |
| Look up people and their groups | `user EMAIL...` |
| Group details, members, owners | `group show NAME` |
| Invite guests, optionally into groups | `invite --email A,B --groups G1,G2` |
| Create a security group | `group create --name NAME --description TEXT` |
| Add existing users to groups | `group add --group G --email A,B` |

Full options, output fields, and error codes are in [reference/commands.md](reference/commands.md).

## Changes are planned first, then applied

`invite`, `group create`, and `group add` only plan until `--apply` is added. An invitation emails a real person outside the organization, and group membership often carries access to cloud resources, so the person asking has to see exactly what will happen before it does.

1. Run the command without `--apply`.
2. Show the plan: the tenant, each person and whether they are new or existing, each group and where it came from, anything left out and why, and whether an invitation email will be sent.
3. Once they approve that plan, run the same command with `--apply`. If anything about the request changes, plan again.

A request to look into, test, or troubleshoot something is not approval to change it.

After applying, report what the result says for each person and group: invited, already present, added, or failed. A partial result stays partial in the summary; completed steps are not rolled back, and re-running the same command finishes only what is missing.

## The tenant must be explicit for changes

Reads fall back to whichever tenant the Azure CLI is signed in to. Changes do not, because people with accounts in several tenants would otherwise invite guests into the wrong one. Pass `--tenant TENANT_ID` or have `ENTRA_TENANT_ID` set. When the script reports `missing_tenant`, show the tenant it found and ask whether that is the intended one before adding `--tenant`.

Every result names the tenant it ran against. Include it when showing a plan.

## Groups that grant privilege

Some groups carry directory roles or broad cloud access. The script treats a group as protected when it is role-assignable or is named in `ENTRA_PROTECTED_GROUPS`.

- `--like EMAIL` copies another user's direct groups and leaves protected and dynamic groups out, listing them under `skipped_groups`. It does not copy inherited access, directory roles, or group ownership.
- A protected group named in `--groups` is refused until `--allow-protected` is added. Add it only after the person confirms they mean to grant that group.
- The script cannot see what Azure roles an ordinary group holds. When a plan copies groups with `--like`, show the full list so the person can catch one that grants more than intended.

## Start with `check` when access is in doubt

`check` reports the signed-in identity, its directory roles, the tenant's invitation and group-creation policy, and which operations that combination should allow. Use it before a first change in a tenant and whenever a command fails with `http_403`.

If a capability is missing, say which role or setting would provide it ([reference/permissions.md](reference/permissions.md)) and that a tenant administrator has to grant it. Granting a role, changing tenant policy, or consenting to permissions widens what an account can do across the whole tenant, so none of them is a way past a refused command. Each is its own request for an administrator to make deliberately.

A role granted moments ago is not in the current token. `az logout` followed by `az login --tenant TENANT_ID` picks it up.

## Related work

- Onboarding a partner team end to end, including the Azure resource group and role assignment that usually follow: [reference/partner-onboarding.md](reference/partner-onboarding.md)
- Errors and what to do about each: [reference/troubleshooting.md](reference/troubleshooting.md)
- OSDU or ADME entitlements are separate from Entra groups and are not handled here.
