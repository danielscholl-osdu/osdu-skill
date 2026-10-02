# Onboarding a partner team

The usual request: several people from another company need to sign in to the tenant and work in one resource group. Tracking them through a dedicated security group means access is granted and later removed in one place.

The Entra steps use `scripts/entra.py`. The Azure steps use the Azure CLI and need rights on the subscription, which are separate from directory roles.

## 1. Confirm what is being asked

Settle these before planning anything, because each one changes the commands:

- The tenant, and the email address of each person.
- The group name. A name that says who and why, such as the company and the engagement, keeps the group traceable later.
- Whether they need Azure resources at all. If they only need to sign in, stop after step 3.
- The subscription, resource group name, region, and role. Reader and Contributor cover most cases; Owner lets them grant access to others.

## 2. Check access

```bash
python3 scripts/entra.py check --tenant TENANT_ID
```

The person needs `invite_guests` and `create_security_groups`. If either is false, [permissions.md](permissions.md) says what to request.

## 3. Create the group and invite the guests

Plan both, show the plans, and apply after approval.

```bash
python3 scripts/entra.py group create --tenant TENANT_ID --name "GROUP_NAME" --description "WHO AND WHY"
python3 scripts/entra.py invite --tenant TENANT_ID --email a@partner.com,b@partner.com --groups "GROUP_NAME"
```

The group has to exist before `invite` can plan against it, so apply `group create` first, then plan `invite`.

## 4. Create the resource group and grant the group access

These commands change Azure resources, so show them and get approval before running them, the same as a plan.

```bash
az group create --subscription SUBSCRIPTION --name RG_NAME --location REGION
az role assignment create --assignee-object-id GROUP_ID --assignee-principal-type Group \
  --role "Contributor" --scope /subscriptions/SUBSCRIPTION_ID/resourceGroups/RG_NAME
```

`GROUP_ID` is the `group_id` in the `group create` result, whether the group was created or already existed. Creating a resource group needs Contributor on the subscription. Assigning a role needs Owner, User Access Administrator, or Role Based Access Control Administrator at that scope.

## 5. Verify and hand over

```bash
python3 scripts/entra.py group show "GROUP_NAME" --tenant TENANT_ID
az role assignment list --assignee GROUP_ID --all -o table
```

Tell the requester what the guests should expect: an invitation email from Microsoft to accept, after which they sign in at the Azure portal and switch to this tenant.

## Removing access later

Removing the role assignment or the group ends the Azure access for everyone at once. Guest accounts remain in the tenant until they are deleted, which is a separate decision.
