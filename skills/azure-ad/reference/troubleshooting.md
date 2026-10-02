# Troubleshooting

Start with `check`. It shows which tenant and identity are in use and what that identity should be able to do, which explains most failures.

| Error | Meaning | Next step |
|---|---|---|
| `az_missing` | The Azure CLI is not installed or not on PATH. | Install it, then `az login --tenant TENANT_ID`. |
| `auth_failed` | The Azure CLI has no usable session for the tenant. | The person runs `az login --tenant TENANT_ID` themselves; sign-in may need a browser and MFA. |
| `tenant_mismatch` | The Azure CLI returned a token for a different tenant than the one requested. | Sign in to the requested tenant. Do not change the tenant to match the session. |
| `missing_tenant` | A change was requested without an explicit tenant. | Confirm the tenant with the person, then pass `--tenant`. |
| `invalid_tenant` | The tenant was given as a name or domain. | Use the tenant ID (a GUID). `check` shows it. |
| `http_403` | The identity is not allowed to do this. | Run `check`, compare with [permissions.md](permissions.md), and tell the person which role or setting is missing. |
| `http_401` | The token expired or was rejected. | Sign in again. |
| `http_400` | The directory rejected the request. | Read `message`; it usually names the cause, such as a policy that blocks the guest's domain. |
| `group_not_found` | No group has that name. | Check the spelling with `group show`, or create it with `group create`. |
| `ambiguous_group`, `ambiguous_user` | More than one match. | Use the object ID. Do not pick one of the matches. |
| `user_not_found` | The person is not in the tenant. | Use `invite` for a new guest. |
| `protected_group` | The group is role-assignable or listed as protected. | Confirm the person intends it, then add `--allow-protected`. |
| `unsupported_group` | The group has dynamic membership. | Membership follows the group's rule and cannot be set directly. |
| `invalid_email`, `invalid_redirect` | An email address or the redirect URL is malformed. | Correct the value; the redirect URL has to be HTTPS. |
| `invalid_response` | Microsoft Graph returned something unexpected. | Stop and report it. Do not continue to the write on a guess. |
| `network_error` | The request did not reach Microsoft Graph. | Check connectivity and retry. Nothing is assumed about the lookup. |

## Things that look like failures but are not

- **A role was just granted and `http_403` continues.** The Azure CLI is still using a token issued before the grant. `az logout`, then `az login --tenant TENANT_ID`.
- **A guest was invited and the group step failed with `http_404`.** A new guest can take a little while to appear everywhere in the directory. The script retries for several seconds; if it still fails, run the same command again. The guest is found as existing and only the group step repeats.
- **A guest says no email arrived.** An invitation that succeeded is not proof of delivery. `user EMAIL` shows `invitation_state`; while it is `PendingAcceptance`, the guest has not redeemed. Sending again is a new outward message, so ask before doing it.
- **`invite` reports `existing` for someone who should be new.** They are already in the tenant, possibly under an older invitation. No second invitation is sent.

## Partial results

Each person and each group is reported separately. When some steps fail, the completed ones remain in place. Fix the cause and run the same command again; steps that already succeeded come back as `existing` or `already_member`.
