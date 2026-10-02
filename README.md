# OSDU skills for GitHub Copilot

A GitHub Copilot plugin with skills for people who run OSDU on Azure.

| Skill | What it does |
|---|---|
| [`azure-ad`](skills/azure-ad/SKILL.md) | Invite guests, create and delete security groups, manage membership, write access instructions, and remove people when an engagement ends, in a Microsoft Entra ID tenant. |
| [`design-doc`](skills/design-doc/SKILL.md) | Write design documents and audit or review findings as a self-contained HTML page with a consistent voice, diagrams, and evidence. |
| [`gh-voice`](skills/gh-voice/SKILL.md) | Tone and structure for pull request descriptions, issues, and review comments. |

## Install

```bash
copilot plugin install danielscholl-osdu/osdu-skill
```

Update later with `copilot plugin update osdu`.

## Requirements

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), signed in to the tenant you manage: `az login --tenant TENANT_ID`
- Python 3.10 or newer. The skills use only the standard library, so there is nothing to install.
- For `design-doc`, a browser to open the HTML page it writes.

Set the tenant once so Copilot does not have to ask:

```bash
export ENTRA_TENANT_ID=00000000-0000-0000-0000-000000000000
```

Optionally name groups that should never be granted or deleted without a second confirmation:

```bash
export ENTRA_PROTECTED_GROUPS="Subscription Owners,Platform Admins"
```

## Using it

Ask Copilot in plain language:

- "What can I do in this tenant?"
- "Add alex@partner.com and sam@partner.com to my tenant, put them in a new group called Webinar, and write instructions I can send them on how to get in."
- "The webinar is over. Remove the Webinar group and its users."
- "Who is in the Platform Readers group?"
- "I get insufficient privileges when I invite a guest. Why?"
- "Write a design doc for moving the schema loader into its own repository."
- "Audit who can manage users in this tenant and give it to me in the design document format."
- "Tighten this PR description."

Copilot shows a plan before it changes anything in a tenant and waits for your approval. Deleting a group or an account also needs a confirmation code that is tied to the exact plan you approved.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache-2.0](LICENSE)
