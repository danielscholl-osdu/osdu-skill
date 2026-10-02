# Engagements: bring people in, then take them out

A common pair of requests. First: "add these people to my tenant, put them in a new group, and write instructions I can send them." Later: "remove that group and those people."

A dedicated group for the engagement is what makes the second request safe. It records who came in for this purpose, so removal acts on that list and nothing else.

## Bringing people in

1. `check`, to confirm the tenant and that inviting and creating groups should work.
2. Plan and apply `group create --name NAME --description "WHO AND WHY"`. The group has to exist before an invitation can be planned against it.
3. Plan and apply `invite --email A,B --groups NAME`.
4. Write the access instructions (below) from the result.

Show both plans before applying either. One approval can cover both when the person has seen both.

## Access instructions for the people invited

Write these for someone who has never used this tenant. Fill them from the `invite` result: `tenant_info.name`, `tenant_info.default_domain`, and each person's status. Ask the requester what the guests are being given access to and where they should go first, because the script cannot know that.

Cover, in this order:

1. **The invitation email.** It comes from Microsoft Invitations on behalf of the tenant, with the subject line naming the tenant. It can land in junk mail. They select "Accept invitation" and sign in with the email address the invitation was sent to.
2. **First sign-in.** They may be asked to accept permissions and to set up multi-factor authentication. Both are expected.
3. **Where to go.** The link for the system they are there to use. For the Azure portal, `https://portal.azure.com/TENANT_DOMAIN` opens it in this tenant directly, which avoids the most common problem: signing in and landing in their own organization's directory.
4. **If they land in the wrong directory.** In the Azure portal: the account menu at the top right, "Switch directory", then the tenant's name.
5. **Who to contact** when something does not work, and how long the access is expected to last if it is temporary.

Keep it short enough to paste into an email. Use the tenant's name and domain as they appear in the result. Someone whose status is `existing` was not sent a new invitation, so their instructions start at step 3.

When the invitation was created with `--no-send-email`, there is no email from Microsoft: give each person their own `redeem_url` in place of step 1, and send it only to them.

## Taking people out

1. `group show NAME`, to see who is in it now.
2. Plan `group delete --name NAME --delete-guests`.
3. Show the plan: who would be deleted, who would be kept and why, and that the group itself is deleted permanently.
4. On approval, apply with `--confirm CODE`.

What the plan does with each member:

| Member | Result |
|---|---|
| A guest who is in no other group and holds no directory role | Deleted. Restorable for 30 days. |
| A guest who is also in another group | Kept, and named with the other groups |
| Anyone holding a directory role | Kept |
| An internal account | Kept |
| The signed-in account | Kept |

If any account cannot be deleted, the group is kept as well, so the list of who remains is not lost. Fix the cause and plan again.

To end the engagement but keep the accounts, leave out `--delete-guests`: the group is deleted and the people stay in the tenant with whatever other access they have.

To remove one person before the end, `group remove --group NAME --email A` takes them out of the group, and `offboard --email A` deletes their account.

## Before deleting a group that holds Azure access

A role assignment made to the group is not removed when the group is deleted. It stays behind pointing at nothing. Remove it first:

```bash
az role assignment list --assignee GROUP_ID --all -o table
az role assignment delete --assignee GROUP_ID --scope SCOPE
```

`GROUP_ID` comes from `group show`. Show these commands and get approval before running them, the same as a plan.
