# OSDU skills for GitHub Copilot

A GitHub Copilot plugin with skills for people who run OSDU on Azure.

| Skill | What it does |
|---|---|
| [`azure-ad`](skills/azure-ad/SKILL.md) | Invite guests, create security groups, manage membership, and explain what your account can do in a Microsoft Entra ID tenant. |
| [`design-doc`](skills/design-doc/SKILL.md) | Write design documents and audit or review findings as a self-contained HTML page with a consistent voice, diagrams, and evidence. |

## Install

```bash
copilot plugin install danielscholl-osdu/osdu-skill
```

Update later with `copilot plugin update osdu`.

## Requirements

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), signed in to the tenant you manage: `az login --tenant TENANT_ID`
- Python 3.10 or newer. The skills use only the standard library, so there is nothing to install.
- For `design-doc`, a browser to open the HTML page it writes. Nothing else.

Set the tenant once so Copilot does not have to ask:

```bash
export ENTRA_TENANT_ID=00000000-0000-0000-0000-000000000000
```

Optionally name groups that should never be granted without a second confirmation:

```bash
export ENTRA_PROTECTED_GROUPS="Subscription Owners,Platform Admins"
```

## Using it

Ask Copilot in plain language:

- "What can I do in this tenant?"
- "Invite alex@partner.com and sam@partner.com and put them in the Partner Demo group."
- "Create a security group called Partner Demo."
- "Who is in the Platform Readers group?"
- "I get insufficient privileges when I invite a guest. Why?"
- "Write a design doc for moving the schema loader into its own repository."
- "Audit who can manage users in this tenant and give it to me in the design document format."

Copilot shows a plan before it changes anything and waits for your approval. Nothing is invited, created, or added until you say so.

## What you need in the tenant

| To do this | You need |
|---|---|
| Invite guests | The Guest Inviter role, or a tenant that lets members invite |
| Create security groups | The Groups Administrator role, or a tenant that lets members create groups |
| Add people to a group | Ownership of that group, or Groups Administrator |

Ask Copilot "what can I do in this tenant?" to see where you stand. Details are in [permissions.md](skills/azure-ad/references/permissions.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache-2.0](LICENSE)
