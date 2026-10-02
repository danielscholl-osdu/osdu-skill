# OSDU skills for GitHub Copilot

A GitHub Copilot plugin with skills for people who run OSDU on Azure.

| Skill | What it does |
|---|---|
| [`azure-ad`](skills/azure-ad/SKILL.md) | Invite guests, create and delete security groups, manage membership, write access instructions, and remove people when an engagement ends, in a Microsoft Entra ID tenant. |
| [`design-doc`](skills/design-doc/SKILL.md) | Write design documents and audit or review findings as a self-contained HTML page with a consistent voice, diagrams, and evidence. |
| [`gh-voice`](skills/gh-voice/SKILL.md) | Tone and structure for pull request descriptions, issues, and review comments. |

## Install

### GitHub Copilot app

1. Add the marketplace once. In a terminal:

   ```bash
   copilot plugin marketplace add danielscholl-osdu/osdu-skill
   ```

2. In the app, open **Customize** and select **Add**, then choose to install a plugin.
3. In the **Install plugin** dialog, enter `osdu@osdu-skill` and select **Install**.
4. On the **Skills** tab, make sure `azure-ad`, `design-doc`, and `gh-voice` are switched on.

This installs the latest release. The name is the plugin (`osdu`) followed by the marketplace (`osdu-skill`); the dialog does not accept the repository path.

### Copilot CLI

```bash
copilot plugin marketplace add danielscholl-osdu/osdu-skill
copilot plugin install osdu@osdu-skill
```

Later releases are picked up with:

```bash
copilot plugin marketplace update osdu-skill
copilot plugin update osdu@osdu-skill
```

In an interactive session, `/plugin` shows when a newer release is available and offers to update. Copilot can also update plugins from this marketplace automatically at the start of a session: turn on auto-update for the `osdu-skill` marketplace in your Copilot settings.

To try unreleased work from `main` instead, install the repository directly with `copilot plugin install danielscholl-osdu/osdu-skill`.

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

Ask Copilot in plain language, in the app or the CLI:

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

[MIT](LICENSE)
