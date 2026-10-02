# Command reference

Run from the skill directory, or give the full path to `scripts/entra.py`. Use `python3` on macOS and Linux, `python` on Windows. `--help` works on every command.

## Configuration

| Setting | Purpose |
|---|---|
| `--tenant ID` | Tenant to act on. Required, here or by environment, for anything run with `--apply`. |
| `ENTRA_TENANT_ID` | Default tenant. `AZURE_TENANT_ID` and `AI_OSDU_TENANT_ID` are read after it. |
| `ENTRA_PROTECTED_GROUPS` | Comma-separated group names or object IDs that need `--allow-protected`. Role-assignable groups are always protected. |

Sign in with `az login --tenant TENANT_ID`. The script asks the Azure CLI for a Microsoft Graph token for that tenant and fails with `tenant_mismatch` if it gets one for another.

## Commands

### `check [--offline] [--tenant ID]`

Reports the tenant, the signed-in identity, its directory roles, the tenant policy for invitations and group creation, and the capabilities those imply. `--offline` reports configuration only and does not sign in.

Capabilities are derived from roles and policy. They say what should work; they are not a write test.

### `user EMAIL... [--tenant ID]`

Looks up each user by mail, user principal name, alternate email, or object ID and lists their direct groups. A user who is not in the tenant comes back as `"found": false`.

### `group show NAME [--tenant ID]`

Group details, protection status, members, and owners. `NAME` is a display name or object ID.

### `group create --name NAME [--description TEXT] [--owner EMAIL]... [--apply]`

Creates a security group with assigned membership. The owner defaults to the signed-in user, which lets them manage membership afterwards without a directory role. An existing group with the same name is reported as `"status": "existing"` and nothing is created.

### `group add --group G... --email E... [--apply] [--allow-protected]`

Adds users who are already in the tenant to one or more groups. Use `invite` for people who are not in the tenant yet.

### `invite --email E... [--groups G...] [--like EMAIL] [--apply]`

| Option | Meaning |
|---|---|
| `--email` | Guest email. Repeat it or separate with commas. |
| `--groups` | Group names or object IDs to add each guest to. |
| `--like EMAIL` | Also add the direct groups of this existing user, minus protected and dynamic groups. |
| `--no-send-email` | Do not email the guest. The result carries a `redeem_url` to pass on instead. |
| `--message TEXT` | Text added to the invitation email. |
| `--redirect-url URL` | Where the guest lands after accepting. Defaults to `https://myapps.microsoft.com`. |
| `--allow-protected` | Permit a protected group named in `--groups`. |

Someone already in the tenant is not invited again; they are reported as `"status": "existing"` and only the group steps run. Groups are resolved before anyone is invited, so a misspelled group stops the command before any email goes out.

## Results

Every command prints one JSON object and exits 0 on success, 1 on failure.

| Field | Meaning |
|---|---|
| `success` | `false` if any user or group step failed. |
| `tenant` | Tenant ID the command ran against. |
| `applied` | `false` for a plan, `true` after `--apply`. |
| `users[].invitation.status` | `planned`, `invited`, or `existing`. |
| `users[].groups[].status` | `planned`, `added`, `already_member`, or `failed`. |
| `users[].groups[].source` | `requested`, or `copied from EMAIL` for `--like`. |
| `skipped_groups[]` | Groups `--like` left out, with the reason. |
| `error`, `message` | Present on a failed command, user, or group step. |

A plan reads the directory but changes nothing. It does not prove the later `--apply` will be permitted; `check` is the better predictor.

## Read-only Azure CLI queries

For questions the script does not cover, the Azure CLI reads the same directory. Confirm the tenant first, since `az` uses its own current session.

```bash
az account show --query tenantId -o tsv
az ad user list --filter "userType eq 'Guest'" --query "[].{name:displayName, mail:mail}" -o table
az ad group list --filter "startswith(displayName,'Team')" --query "[].{name:displayName, id:id}" -o table
```

When the question is about one person or one group, filter for it instead of listing the whole directory.
