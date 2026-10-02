#!/usr/bin/env python3
"""Entra ID guest invitations, security groups, and group membership.

Standard library only. Authenticates with the Azure CLI session and prints one
JSON object on stdout. Every write is a plan unless --apply is given.
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from uuid import UUID, uuid4

GRAPH = "https://graph.microsoft.com/v1.0"
TIMEOUT = 30
TENANT_VARS = ("ENTRA_TENANT_ID", "AZURE_TENANT_ID", "AI_OSDU_TENANT_ID")
PROTECTED_VAR = "ENTRA_PROTECTED_GROUPS"
USER_FIELDS = "id,displayName,mail,userPrincipalName,userType,accountEnabled,externalUserState"
GROUP_FIELDS = "id,displayName,description,securityEnabled,isAssignableToRole,groupTypes"
ADVANCED_QUERY = {"ConsistencyLevel": "eventual"}

# Built-in directory role template IDs, identical in every tenant.
GLOBAL_ADMIN = "62e90394-69f5-4237-9190-012177145e10"
USER_ADMIN = "fe930be7-5e62-47db-91af-98c3a49a38b1"
GROUPS_ADMIN = "fdd7a751-b60b-444a-984c-02652fe8fa1c"
GUEST_INVITER = "95e79109-95c0-4d8e-aee3-d01accf2d47b"
DIRECTORY_WRITERS = "9360feb5-f418-4baa-8175-e2a00bac4301"
INVITE_ROLES = {GLOBAL_ADMIN, USER_ADMIN, GUEST_INVITER, DIRECTORY_WRITERS}
GROUP_ROLES = {GLOBAL_ADMIN, USER_ADMIN, GROUPS_ADMIN, DIRECTORY_WRITERS}


class EntraError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def is_uuid(value):
    try:
        UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def quoted(value):
    return value.replace("'", "''")


def split_values(values):
    items = [part.strip() for value in values or [] for part in value.split(",")]
    return list(dict.fromkeys(item for item in items if item))


def valid_email(email):
    if not re.fullmatch(r"[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+", email):
        raise EntraError("invalid_email", f"Invalid email address: {email}")
    return email


def token_claims(token):
    try:
        payload = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (IndexError, ValueError) as error:
        raise EntraError("auth_failed", "Azure CLI returned an unreadable token.") from error
    if not isinstance(claims, dict) or not is_uuid(claims.get("tid")):
        raise EntraError("auth_failed", "Azure CLI token carries no tenant.")
    return claims


def az_token(tenant=None, run=subprocess.run, which=shutil.which):
    az = which("az")
    if not az:
        raise EntraError("az_missing", "Azure CLI (az) is not installed or not on PATH.")
    command = [az, "account", "get-access-token", "--resource", "https://graph.microsoft.com", "-o", "json"]
    if tenant:
        command += ["--tenant", tenant]
    login = "az login" + (f" --tenant {tenant}" if tenant else "")
    try:
        response = run(command, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EntraError("auth_failed", f"Azure CLI did not return a token ({type(error).__name__}).") from error
    if response.returncode != 0:
        raise EntraError("auth_failed", f"Azure CLI has no usable session. Ask the user to run: {login}")
    try:
        token = json.loads(response.stdout)["accessToken"]
    except (ValueError, KeyError, TypeError) as error:
        raise EntraError("auth_failed", "Azure CLI returned invalid token JSON.") from error
    claims = token_claims(token)
    if tenant and claims["tid"].lower() != tenant.lower():
        raise EntraError("tenant_mismatch", f"Azure CLI returned a token for tenant {claims['tid']}, not {tenant}.")
    return token, claims


def http(method, url, headers, body):
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise EntraError("network_error", f"{method} request failed: {type(error).__name__}") from error


class Graph:
    def __init__(self, token, transport=http, sleep=time.sleep):
        self.token = token
        self.transport = transport
        self.sleep = sleep

    def request(self, method, url, params=None, body=None, headers=None):
        if not url.startswith(GRAPH + "/"):
            raise EntraError("invalid_response", "Refusing to send the Graph token to a non-Graph URL.")
        if params:
            url += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json", **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        for attempt in range(3):
            status, response_headers, raw = self.transport(method, url, headers, data)
            if status != 429 or attempt == 2:
                break
            retry_after = {k.lower(): v for k, v in response_headers.items()}.get("retry-after", "")
            self.sleep(min(int(retry_after), 30) if str(retry_after).isdigit() else 2)
        try:
            payload = json.loads(raw) if raw else {}
        except ValueError:
            payload = None
        if not 200 <= status < 300:
            error = payload.get("error") if isinstance(payload, dict) else None
            message = error.get("message") if isinstance(error, dict) else None
            raise EntraError(f"http_{status}", message or f"{method} returned HTTP {status}.")
        if not isinstance(payload, dict):
            raise EntraError("invalid_response", "Graph returned a non-object response.")
        return payload

    def get(self, path, params=None, headers=None):
        return self.request("GET", GRAPH + path, params=params, headers=headers)

    def values(self, path, params=None, headers=None):
        url, items, seen = GRAPH + path, [], set()
        while url:
            if url in seen:
                raise EntraError("invalid_response", "Graph repeated a pagination URL.")
            seen.add(url)
            page = self.request("GET", url, params=params, headers=headers)
            params = None
            if not isinstance(page.get("value"), list):
                raise EntraError("invalid_response", "Graph returned an invalid collection.")
            items += page["value"]
            url = page.get("@odata.nextLink")
        return items

    def user(self, identifier):
        """Return the one matching user, None when absent. Lookup errors are never absence."""
        if is_uuid(identifier):
            try:
                return self.get(f"/users/{identifier}", {"$select": USER_FIELDS})
            except EntraError as error:
                if error.code == "http_404":
                    return None
                raise
        email = quoted(valid_email(identifier))
        users = self.values("/users", {
            "$filter": f"mail eq '{email}' or userPrincipalName eq '{email}' or otherMails/any(x:x eq '{email}')",
            "$select": USER_FIELDS,
        })
        if len(users) > 1:
            raise EntraError("ambiguous_user", f"{len(users)} users match {identifier}; use an object ID.")
        return users[0] if users else None

    def group(self, identifier):
        if is_uuid(identifier):
            try:
                return self.get(f"/groups/{identifier}", {"$select": GROUP_FIELDS})
            except EntraError as error:
                if error.code == "http_404":
                    return None
                raise
        groups = self.values("/groups", {"$filter": f"displayName eq '{quoted(identifier)}'", "$select": GROUP_FIELDS})
        if len(groups) > 1:
            raise EntraError("ambiguous_group", f"{len(groups)} groups are named {identifier}; use an object ID.")
        return groups[0] if groups else None

    def direct_groups(self, user_id):
        return self.values(f"/users/{user_id}/memberOf/microsoft.graph.group",
                           {"$select": GROUP_FIELDS, "$count": "true"}, ADVANCED_QUERY)

    def invite(self, email, redirect_url, send_email, message):
        body = {"invitedUserEmailAddress": email, "inviteRedirectUrl": redirect_url, "sendInvitationMessage": send_email}
        if message:
            body["invitedUserMessageInfo"] = {"customizedMessageBody": message}
        data = self.request("POST", GRAPH + "/invitations", body=body)
        user_id = (data.get("invitedUser") or {}).get("id")
        if not is_uuid(user_id):
            raise EntraError("invalid_response", "Invitation response carries no user ID.")
        return user_id, data.get("inviteRedeemUrl")

    def add_member(self, group_id, user_id, fresh=False):
        """Add a member. Returns False when already a member. A fresh guest may take seconds to replicate."""
        for attempt in range(5 if fresh else 1):
            try:
                self.request("POST", f"{GRAPH}/groups/{group_id}/members/$ref",
                             body={"@odata.id": f"{GRAPH}/directoryObjects/{user_id}"})
                return True
            except EntraError as error:
                if error.code == "http_400" and "already exist" in str(error).lower():
                    return False
                if error.code != "http_404" or attempt == (4 if fresh else 0):
                    raise
                self.sleep(3)

    def create_group(self, name, description, owner_ids):
        body = {"displayName": name, "mailEnabled": False, "securityEnabled": True,
                "mailNickname": (re.sub(r"[^A-Za-z0-9]", "", name)[:40] or "group") + uuid4().hex[:8]}
        if description:
            body["description"] = description
        if owner_ids:
            body["owners@odata.bind"] = [f"{GRAPH}/users/{owner}" for owner in owner_ids]
        return self.request("POST", GRAPH + "/groups", body=body)


class Session:
    def __init__(self, graph, tenant, tenant_explicit, claims=None, protected=()):
        self.graph = graph
        self.tenant = tenant
        self.tenant_explicit = tenant_explicit
        self.claims = claims or {}
        self.protected = {item.lower() for item in protected}

    def require_explicit_tenant(self):
        if not self.tenant_explicit:
            raise EntraError(
                "missing_tenant",
                f"Writes need an explicit tenant. The Azure CLI session is on {self.tenant}; "
                f"re-run with --tenant {self.tenant} or set ENTRA_TENANT_ID once the user confirms it.")

    def protection(self, group):
        reasons = []
        if group.get("isAssignableToRole"):
            reasons.append("role-assignable")
        if group["displayName"].lower() in self.protected or group["id"].lower() in self.protected:
            reasons.append(f"listed in {PROTECTED_VAR}")
        return reasons

    def caller(self):
        if "scp" not in self.claims:
            return None
        return self.graph.get("/me", {"$select": USER_FIELDS})


def describe_user(user):
    return {"id": user["id"], "name": user.get("displayName"), "mail": user.get("mail"),
            "upn": user.get("userPrincipalName"), "type": user.get("userType"),
            "enabled": user.get("accountEnabled"), "invitation_state": user.get("externalUserState")}


def describe_group(session, group):
    return {"id": group["id"], "name": group["displayName"], "security": group.get("securityEnabled"),
            "dynamic": "DynamicMembership" in (group.get("groupTypes") or []),
            "protected": session.protection(group)}


def resolve_groups(session, names, like, allow_protected):
    """Return (groups to assign, groups left out with the reason)."""
    chosen, skipped = {}, []
    for name in names:
        group = session.graph.group(name)
        if group is None:
            raise EntraError("group_not_found", f"No group matches {name}. Create it first with: group create --name \"{name}\"")
        info = describe_group(session, group)
        if info["dynamic"]:
            raise EntraError("unsupported_group", f"{info['name']} has dynamic membership; members cannot be added directly.")
        if info["protected"] and not allow_protected:
            raise EntraError(
                "protected_group",
                f"{info['name']} is protected ({', '.join(info['protected'])}). "
                "Confirm with the user that this privileged group is intended, then add --allow-protected.")
        chosen[info["id"]] = {**info, "source": "requested"}
    if like:
        reference = session.graph.user(like)
        if reference is None:
            raise EntraError("user_not_found", f"Reference user not found: {like}")
        for group in session.graph.direct_groups(reference["id"]):
            info = describe_group(session, group)
            if info["id"] in chosen:
                continue
            if info["dynamic"]:
                skipped.append({"group": info["name"], "reason": "dynamic membership"})
            elif info["protected"]:
                skipped.append({"group": info["name"], "reason": "protected: " + ", ".join(info["protected"]),
                                "to_include": "name it in --groups with --allow-protected"})
            else:
                chosen[info["id"]] = {**info, "source": f"copied from {like}"}
    return list(chosen.values()), skipped


def assign_groups(session, user_id, groups, apply, fresh=False):
    current = set()
    if user_id and not fresh:
        current = {group["id"] for group in session.graph.direct_groups(user_id)}
    results = []
    for group in groups:
        entry = {"group": group["name"], "group_id": group["id"], "source": group["source"]}
        if group["protected"]:
            entry["protected"] = group["protected"]
        if group["id"] in current:
            entry["status"] = "already_member"
        elif not apply:
            entry["status"] = "planned"
        else:
            try:
                added = session.graph.add_member(group["id"], user_id, fresh)
                entry["status"] = "added" if added else "already_member"
            except EntraError as error:
                entry.update(status="failed", error=error.code, message=str(error))
        results.append(entry)
    return results


def finish(result, users):
    result["users"] = users
    failed = [u for u in users if u.get("error") or any(g["status"] == "failed" for g in u.get("groups", []))]
    result["success"] = not failed
    return result


def cmd_invite(session, args):
    emails = [valid_email(email) for email in split_values(args.email)]
    if urllib.parse.urlparse(args.redirect_url).scheme != "https":
        raise EntraError("invalid_redirect", "The redirect URL must be HTTPS.")
    if args.apply:
        session.require_explicit_tenant()
    groups, skipped = resolve_groups(session, split_values(args.groups), args.like, args.allow_protected)
    result = {"command": "invite", "tenant": session.tenant, "applied": args.apply,
              "send_email": args.send_email, "skipped_groups": skipped}
    users = []
    for email in emails:
        entry = {"email": email}
        try:
            user = session.graph.user(email)
            fresh = False
            if user:
                entry["invitation"] = {"status": "existing", "user_id": user["id"],
                                       "invitation_state": user.get("externalUserState")}
                user_id = user["id"]
            elif not args.apply:
                entry["invitation"] = {"status": "planned"}
                user_id = None
            else:
                user_id, redeem_url = session.graph.invite(email, args.redirect_url, args.send_email, args.message)
                entry["invitation"] = {"status": "invited", "user_id": user_id}
                if not args.send_email:
                    entry["invitation"]["redeem_url"] = redeem_url
                fresh = True
            entry["groups"] = assign_groups(session, user_id, groups, args.apply, fresh)
        except EntraError as error:
            entry.update(error=error.code, message=str(error))
        users.append(entry)
    return finish(result, users)


def cmd_group_add(session, args):
    if args.apply:
        session.require_explicit_tenant()
    groups, _ = resolve_groups(session, split_values(args.group), None, args.allow_protected)
    result = {"command": "group add", "tenant": session.tenant, "applied": args.apply}
    users = []
    for identifier in split_values(args.email):
        entry = {"email": identifier}
        try:
            user = session.graph.user(identifier)
            if user is None:
                raise EntraError("user_not_found", f"{identifier} is not in the tenant. Use invite for new guests.")
            entry["user_id"] = user["id"]
            entry["groups"] = assign_groups(session, user["id"], groups, args.apply)
        except EntraError as error:
            entry.update(error=error.code, message=str(error))
        users.append(entry)
    return finish(result, users)


def cmd_group_create(session, args):
    if args.apply:
        session.require_explicit_tenant()
    result = {"command": "group create", "tenant": session.tenant, "applied": args.apply, "name": args.name}
    existing = session.graph.group(args.name)
    if existing:
        return {**result, "success": True, "status": "existing", "group_id": existing["id"],
                "group": describe_group(session, existing)}
    owners = []
    for identifier in split_values(args.owner):
        owner = session.graph.user(identifier)
        if owner is None:
            raise EntraError("user_not_found", f"Owner not found: {identifier}")
        owners.append(owner)
    if not owners:
        caller = session.caller()
        if caller:
            owners.append(caller)
    result["owners"] = [owner.get("mail") or owner.get("userPrincipalName") for owner in owners]
    result["type"] = "security group, assigned membership"
    if not args.apply:
        return {**result, "success": True, "status": "planned"}
    created = session.graph.create_group(args.name, args.description, [owner["id"] for owner in owners])
    return {**result, "success": True, "status": "created", "group_id": created.get("id")}


def cmd_group_show(session, args):
    group = session.graph.group(args.name)
    if group is None:
        raise EntraError("group_not_found", f"No group matches {args.name}.")
    people = {}
    for relation in ("members", "owners"):
        items = session.graph.values(f"/groups/{group['id']}/{relation}",
                                     {"$select": "id,displayName,mail,userPrincipalName", "$top": "999"})
        people[relation] = [{"name": item.get("displayName"), "mail": item.get("mail") or item.get("userPrincipalName"),
                             "kind": item.get("@odata.type", "").rsplit(".", 1)[-1]} for item in items]
    return {"command": "group show", "tenant": session.tenant, "success": True,
            "group": {**describe_group(session, group), "description": group.get("description")}, **people}


def cmd_user(session, args):
    users = []
    for identifier in split_values(args.email):
        entry = {"query": identifier}
        try:
            user = session.graph.user(identifier)
            if user is None:
                entry["found"] = False
            else:
                groups = session.graph.direct_groups(user["id"])
                entry.update(found=True, user=describe_user(user),
                             direct_groups=sorted(group["displayName"] for group in groups))
        except EntraError as error:
            entry.update(error=error.code, message=str(error))
        users.append(entry)
    return {"command": "user", "tenant": session.tenant, "users": users,
            "success": not any(user.get("error") for user in users)}


def cmd_check(session, args):
    graph = session.graph
    organization = graph.values("/organization", {"$select": "id,displayName"})
    result = {"command": "check", "success": True,
              "tenant": {"id": session.tenant, "name": organization[0].get("displayName") if organization else None,
                         "explicit": session.tenant_explicit}}
    caller = session.caller()
    if caller is None:
        result["identity"] = {"kind": "application", "app_id": session.claims.get("appid")}
        result["note"] = "Application identity: capabilities depend on its Graph app permissions and were not derived."
        return result
    roles = graph.values("/me/transitiveMemberOf/microsoft.graph.directoryRole",
                         {"$select": "displayName,roleTemplateId", "$count": "true"}, ADVANCED_QUERY)
    held = {role.get("roleTemplateId") for role in roles}
    policy = graph.get("/policies/authorizationPolicy")
    invites_from = policy.get("allowInvitesFrom")
    members_create = bool((policy.get("defaultUserRolePermissions") or {}).get("allowedToCreateSecurityGroups"))
    is_member = caller.get("userType") == "Member"
    can_invite = invites_from != "none" and (
        invites_from == "everyone" or bool(held & INVITE_ROLES)
        or (invites_from == "adminsGuestInvitersAndAllMembers" and is_member))
    result["identity"] = {"kind": "user", **describe_user(caller)}
    result["directory_roles"] = sorted(
        "Global Administrator" if role.get("roleTemplateId") == GLOBAL_ADMIN else role.get("displayName") or ""
        for role in roles)
    result["tenant_policy"] = {"allow_invites_from": invites_from, "members_can_create_security_groups": members_create}
    result["capabilities"] = {
        "invite_guests": can_invite,
        "create_security_groups": bool(held & GROUP_ROLES) or (members_create and is_member),
        "manage_any_group_membership": bool(held & GROUP_ROLES),
        "manage_owned_group_membership": True,
    }
    result["note"] = ("Capabilities are derived from directory roles and tenant policy; they are an expectation, "
                      "not a write test. Role changes need a fresh sign-in (az logout, az login) to reach the token.")
    return result


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--tenant", help="Tenant ID. Defaults to " + ", then ".join(TENANT_VARS) + ", then the az session (reads only).")
    write = argparse.ArgumentParser(add_help=False)
    write.add_argument("--apply", action="store_true", help="Execute. Without it the command only plans.")
    write.add_argument("--allow-protected", action="store_true",
                       help="Permit a protected group that was named explicitly.")

    parser = argparse.ArgumentParser(prog="entra.py", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", parents=[common], help="Tenant, signed-in identity, roles, and expected capabilities.")
    check.add_argument("--offline", action="store_true", help="Report configuration only; no sign-in, no network.")
    check.set_defaults(handler=cmd_check)

    user = commands.add_parser("user", parents=[common], help="Look up users and their direct groups.")
    user.add_argument("email", nargs="+", help="Email, UPN, or object ID.")
    user.set_defaults(handler=cmd_user)

    invite = commands.add_parser("invite", parents=[common, write], help="Invite guests and add them to groups.")
    invite.add_argument("--email", action="append", required=True, help="Guest email. Repeat or comma-separate.")
    invite.add_argument("--groups", action="append", help="Group names or object IDs. Repeat or comma-separate.")
    invite.add_argument("--like", help="Copy this user's direct groups, leaving out protected and dynamic groups.")
    invite.add_argument("--redirect-url", default="https://myapps.microsoft.com")
    invite.add_argument("--no-send-email", dest="send_email", action="store_false",
                        help="Do not email the guest; the result carries the redeem URL instead.")
    invite.add_argument("--message", help="Text added to the invitation email.")
    invite.set_defaults(handler=cmd_invite)

    group = commands.add_parser("group", help="Create, inspect, and populate security groups.")
    actions = group.add_subparsers(dest="action", required=True)
    show = actions.add_parser("show", parents=[common], help="Group details, members, and owners.")
    show.add_argument("name", help="Group name or object ID.")
    show.set_defaults(handler=cmd_group_show)
    create = actions.add_parser("create", parents=[common, write], help="Create a security group.")
    create.add_argument("--name", required=True)
    create.add_argument("--description")
    create.add_argument("--owner", action="append", help="Owner email or object ID. Defaults to the signed-in user.")
    create.set_defaults(handler=cmd_group_create)
    add = actions.add_parser("add", parents=[common, write], help="Add existing users to groups.")
    add.add_argument("--group", action="append", required=True, help="Group names or object IDs.")
    add.add_argument("--email", action="append", required=True, help="User email, UPN, or object ID.")
    add.set_defaults(handler=cmd_group_add)
    return parser


def main(argv=None, env=None, token_source=az_token):
    env = os.environ if env is None else env
    args = build_parser().parse_args(argv)
    try:
        configured = args.tenant or next((env[name] for name in TENANT_VARS if env.get(name)), None)
        if configured and not is_uuid(configured):
            raise EntraError("invalid_tenant", "The tenant must be a tenant ID (GUID).")
        if getattr(args, "offline", False):
            result = {"command": "check", "success": True, "offline": True, "tenant": configured,
                      "azure_cli_available": shutil.which("az") is not None,
                      "protected_groups": split_values([env.get(PROTECTED_VAR, "")])}
        else:
            token, claims = token_source(configured)
            session = Session(Graph(token), claims["tid"], bool(configured), claims,
                              split_values([env.get(PROTECTED_VAR, "")]))
            result = args.handler(session, args)
    except EntraError as error:
        result = {"success": False, "error": error.code, "message": str(error)}
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
