"""Offline tests for skills/azure-ad/scripts/entra.py. No sign-in, no network."""

import base64
import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "azure-ad" / "scripts"))
import entra  # noqa: E402

TENANT = "11111111-1111-1111-1111-111111111111"
ALICE = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
NEW = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
G_TEAM = "cccccccc-cccc-cccc-cccc-cccccccccccc"
G_ROLE = "dddddddd-dddd-dddd-dddd-dddddddddddd"
G_DYN = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
G_ADMIN = "ffffffff-ffff-ffff-ffff-ffffffffffff"
GINA = "10000000-0000-0000-0000-000000000001"
GARY = "10000000-0000-0000-0000-000000000002"

GROUPS = {
    "Team": {"id": G_TEAM, "displayName": "Team", "securityEnabled": True, "groupTypes": []},
    "RoleHolders": {"id": G_ROLE, "displayName": "RoleHolders", "isAssignableToRole": True, "groupTypes": []},
    "Dynamic": {"id": G_DYN, "displayName": "Dynamic", "groupTypes": ["DynamicMembership"]},
    "Admins": {"id": G_ADMIN, "displayName": "Admins", "groupTypes": []},
}


def make_token(**claims):
    payload = base64.urlsafe_b64encode(json.dumps({"tid": TENANT, **claims}).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


class FakeGraph:
    """Routes Graph calls to canned responses and records every call."""

    def __init__(self):
        self.calls = []
        self.users = {"alice@example.com": {"id": ALICE, "displayName": "Alice", "mail": "alice@example.com",
                                            "userType": "Member", "externalUserState": "Accepted"}}
        self.users["gina@partner.com"] = {"id": GINA, "displayName": "Gina", "mail": "gina@partner.com",
                                          "userType": "Guest", "@odata.type": "#microsoft.graph.user"}
        self.users["gary@partner.com"] = {"id": GARY, "displayName": "Gary", "mail": "gary@partner.com",
                                          "userType": "Guest", "@odata.type": "#microsoft.graph.user"}
        self.memberships = {ALICE: ["Team", "RoleHolders", "Dynamic", "Admins"], GINA: ["Team"],
                            GARY: ["Team", "Admins"]}
        self.roles = {}
        self.group_members = {G_TEAM: [GINA, GARY, ALICE]}
        self.delete_failures = {}
        self.member_failures = []
        self.routes = []

    def transport(self, method, url, headers, body):
        self.calls.append((method, url))
        path = url[len(entra.GRAPH):]
        for route_method, pattern, responder in self.routes:
            if route_method == method and re.match(pattern, path):
                return responder(path, body)
        if method == "GET" and path.startswith("/users?"):
            match = [user for email, user in self.users.items() if email.replace("@", "%40") in path]
            return self.ok({"value": match})
        by_id = {user["id"]: user for user in self.users.values()}
        if method == "GET" and path.startswith("/organization"):
            return self.ok({"value": [{"displayName": "contoso", "verifiedDomains": [
                {"name": "contoso.example", "isDefault": True}]}]})
        if method == "GET" and "/transitiveMemberOf/" in path and path.startswith("/users/"):
            return self.ok({"value": self.roles.get(path.split("/")[2], [])})
        if method == "GET" and re.match(r"/groups/[0-9a-f-]+/members\?", path):
            return self.ok({"value": [{"@odata.type": "#microsoft.graph.user", **by_id[i]}
                                      for i in self.group_members.get(path.split("/")[2], [])]})
        if method == "GET" and re.match(r"/users/[0-9a-f-]{36}\?", path):
            user = by_id.get(path.split("/")[2].split("?")[0])
            return self.ok(user) if user else self.error(404, "not found")
        if method == "DELETE":
            target = path.split("/")[2]
            if target in self.delete_failures:
                return self.delete_failures[target]
            return 204, {}, b""
        if method == "GET" and "/memberOf/" in path:
            user_id = path.split("/")[2]
            return self.ok({"value": [GROUPS[name] for name in self.memberships.get(user_id, [])]})
        if method == "GET" and path.startswith("/groups?"):
            return self.ok({"value": [group for name, group in GROUPS.items() if f"%27{name}%27" in path]})
        if method == "POST" and path == "/invitations":
            return self.ok({"invitedUser": {"id": NEW}, "inviteRedeemUrl": "https://redeem.example"}, 201)
        if method == "POST" and path.endswith("/members/$ref"):
            if self.member_failures:
                return self.member_failures.pop(0)
            return 204, {}, b""
        if method == "POST" and path == "/groups":
            return self.ok({"id": G_TEAM, **json.loads(body)}, 201)
        if method == "GET" and path.startswith("/me?"):
            return self.ok(self.users["alice@example.com"])
        raise AssertionError(f"Unexpected Graph call: {method} {path}")

    @staticmethod
    def ok(payload, status=200):
        return status, {}, json.dumps(payload).encode()

    @staticmethod
    def error(status, message):
        return status, {}, json.dumps({"error": {"message": message}}).encode()

    def writes(self):
        return [call for call in self.calls if call[0] != "GET"]


def session(fake, explicit=True, protected=(), claims=None):
    graph = entra.Graph("token", transport=fake.transport, sleep=lambda seconds: None)
    return entra.Session(graph, TENANT, explicit, claims if claims is not None else {"scp": "x"}, protected)


def invite_args(**overrides):
    values = {"email": ["new@example.com"], "groups": ["Team"], "like": None, "apply": False,
              "allow_protected": False, "redirect_url": "https://myapps.microsoft.com",
              "send_email": True, "message": None}
    return SimpleNamespace(**{**values, **overrides})


class InviteTests(unittest.TestCase):
    def test_plan_makes_no_writes(self):
        fake = FakeGraph()
        result = entra.cmd_invite(session(fake), invite_args())
        self.assertTrue(result["success"])
        self.assertFalse(result["applied"])
        self.assertEqual(result["tenant"], TENANT)
        self.assertEqual(result["users"][0]["invitation"]["status"], "planned")
        self.assertEqual(result["users"][0]["groups"][0]["status"], "planned")
        self.assertEqual(fake.writes(), [])

    def test_apply_invites_then_adds_group(self):
        fake = FakeGraph()
        result = entra.cmd_invite(session(fake), invite_args(apply=True))
        self.assertEqual(result["users"][0]["invitation"], {"status": "invited", "user_id": NEW})
        self.assertEqual(result["users"][0]["groups"][0]["status"], "added")
        self.assertEqual([call[1].rsplit("/v1.0", 1)[1] for call in fake.writes()],
                         ["/invitations", f"/groups/{G_TEAM}/members/$ref"])

    def test_apply_requires_explicit_tenant(self):
        fake = FakeGraph()
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_invite(session(fake, explicit=False), invite_args(apply=True))
        self.assertEqual(caught.exception.code, "missing_tenant")
        self.assertEqual(fake.writes(), [])

    def test_existing_user_is_not_reinvited_and_membership_is_detected(self):
        fake = FakeGraph()
        result = entra.cmd_invite(session(fake), invite_args(email=["alice@example.com"], apply=True))
        user = result["users"][0]
        self.assertEqual(user["invitation"]["status"], "existing")
        self.assertEqual(user["groups"][0]["status"], "already_member")
        self.assertEqual(fake.writes(), [])

    def test_fresh_guest_membership_retries_until_replicated(self):
        fake = FakeGraph()
        fake.member_failures = [fake.error(404, "Resource does not exist"), fake.error(404, "Resource does not exist")]
        result = entra.cmd_invite(session(fake), invite_args(apply=True))
        self.assertEqual(result["users"][0]["groups"][0]["status"], "added")
        self.assertEqual(len(fake.writes()), 4)

    def test_group_failure_is_reported_without_hiding_the_invitation(self):
        fake = FakeGraph()
        fake.member_failures = [fake.error(403, "Insufficient privileges")]
        result = entra.cmd_invite(session(fake), invite_args(apply=True))
        self.assertFalse(result["success"])
        self.assertEqual(result["users"][0]["invitation"]["status"], "invited")
        self.assertEqual(result["users"][0]["groups"][0]["error"], "http_403")

    def test_one_failed_user_does_not_stop_the_others(self):
        fake = FakeGraph()
        fake.routes.append(("POST", r"/invitations", lambda path, body: (
            fake.error(403, "denied") if b"first@" in body else fake.ok({"invitedUser": {"id": NEW}}, 201))))
        result = entra.cmd_invite(session(fake), invite_args(email=["first@example.com,second@example.com"], apply=True))
        self.assertFalse(result["success"])
        self.assertEqual(result["users"][0]["error"], "http_403")
        self.assertEqual(result["users"][1]["invitation"]["status"], "invited")

    def test_lookup_error_is_not_treated_as_a_missing_user(self):
        fake = FakeGraph()
        fake.routes.append(("GET", r"/users\?", lambda path, body: fake.error(403, "denied")))
        result = entra.cmd_invite(session(fake), invite_args(apply=True))
        self.assertEqual(result["users"][0]["error"], "http_403")
        self.assertEqual(fake.writes(), [])

    def test_missing_group_stops_before_any_invitation(self):
        fake = FakeGraph()
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_invite(session(fake), invite_args(groups=["Nope"], apply=True))
        self.assertEqual(caught.exception.code, "group_not_found")
        self.assertEqual(fake.writes(), [])

    def test_no_send_email_returns_redeem_url(self):
        fake = FakeGraph()
        result = entra.cmd_invite(session(fake), invite_args(apply=True, send_email=False))
        self.assertEqual(result["users"][0]["invitation"]["redeem_url"], "https://redeem.example")


class GroupSafetyTests(unittest.TestCase):
    def test_like_leaves_out_protected_and_dynamic_groups(self):
        fake = FakeGraph()
        result = entra.cmd_invite(session(fake, protected=["admins"]),
                                  invite_args(groups=None, like="alice@example.com"))
        self.assertEqual([group["group"] for group in result["users"][0]["groups"]], ["Team"])
        self.assertEqual(result["users"][0]["groups"][0]["source"], "copied from alice@example.com")
        self.assertEqual({item["group"] for item in result["skipped_groups"]}, {"RoleHolders", "Dynamic", "Admins"})

    def test_explicit_protected_group_needs_allow_flag(self):
        fake = FakeGraph()
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_invite(session(fake), invite_args(groups=["RoleHolders"]))
        self.assertEqual(caught.exception.code, "protected_group")
        result = entra.cmd_invite(session(fake), invite_args(groups=["RoleHolders"], allow_protected=True))
        self.assertEqual(result["users"][0]["groups"][0]["protected"], ["role-assignable"])

    def test_explicit_dynamic_group_is_rejected(self):
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_invite(session(FakeGraph()), invite_args(groups=["Dynamic"]))
        self.assertEqual(caught.exception.code, "unsupported_group")

    def test_ambiguous_group_name_is_rejected(self):
        fake = FakeGraph()
        fake.routes.append(("GET", r"/groups\?", lambda path, body: fake.ok({"value": [GROUPS["Team"], GROUPS["Admins"]]})))
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_invite(session(fake), invite_args())
        self.assertEqual(caught.exception.code, "ambiguous_group")


class GroupCommandTests(unittest.TestCase):
    def create_args(self, **overrides):
        return SimpleNamespace(**{"name": "NewGroup", "description": "demo", "owner": None, "apply": False,
                                  "allow_protected": False, **overrides})

    def test_create_plan_defaults_owner_to_caller(self):
        fake = FakeGraph()
        result = entra.cmd_group_create(session(fake), self.create_args())
        self.assertEqual(result["status"], "planned")
        self.assertEqual(result["owners"], ["alice@example.com"])
        self.assertEqual(fake.writes(), [])

    def test_create_apply_posts_a_security_group_with_owner(self):
        fake = FakeGraph()
        bodies = []
        fake.routes.append(("POST", r"/groups$", lambda path, body: (bodies.append(json.loads(body)), fake.ok({"id": G_TEAM}, 201))[1]))
        result = entra.cmd_group_create(session(fake), self.create_args(apply=True))
        self.assertEqual(result["status"], "created")
        self.assertTrue(bodies[0]["securityEnabled"])
        self.assertFalse(bodies[0]["mailEnabled"])
        self.assertEqual(bodies[0]["owners@odata.bind"], [f"{entra.GRAPH}/users/{ALICE}"])

    def test_create_is_idempotent_for_an_existing_name(self):
        fake = FakeGraph()
        result = entra.cmd_group_create(session(fake), self.create_args(name="Team", apply=True))
        self.assertEqual(result["status"], "existing")
        self.assertEqual(result["group_id"], G_TEAM)
        self.assertEqual(fake.writes(), [])

    def test_group_add_rejects_users_outside_the_tenant(self):
        fake = FakeGraph()
        args = SimpleNamespace(group=["Team"], email=["ghost@example.com"], apply=True, allow_protected=False)
        result = entra.cmd_group_add(session(fake), args)
        self.assertFalse(result["success"])
        self.assertEqual(result["users"][0]["error"], "user_not_found")
        self.assertEqual(fake.writes(), [])


def offboard_args(**overrides):
    values = {"email": ["gina@partner.com"], "apply": False, "confirm": None, "allow_internal": False,
              "allow_protected": False}
    return SimpleNamespace(**{**values, **overrides})


def delete_args(**overrides):
    values = {"name": "Team", "delete_guests": False, "apply": False, "confirm": None, "allow_protected": False}
    return SimpleNamespace(**{**values, **overrides})


class OffboardTests(unittest.TestCase):
    def test_plan_returns_a_code_and_deletes_nothing(self):
        fake = FakeGraph()
        result = entra.cmd_offboard(session(fake), offboard_args())
        self.assertEqual(result["users"][0]["status"], "planned")
        self.assertEqual(result["users"][0]["groups"], ["Team"])
        self.assertEqual(len(result["confirm"]), 8)
        self.assertEqual(fake.writes(), [])

    def test_apply_without_the_code_is_refused_and_does_not_reveal_it(self):
        fake = FakeGraph()
        code = entra.cmd_offboard(session(fake), offboard_args())["confirm"]
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_offboard(session(fake), offboard_args(apply=True))
        self.assertEqual(caught.exception.code, "confirmation_required")
        self.assertNotIn(code, str(caught.exception))
        self.assertEqual(fake.writes(), [])

    def test_code_from_a_different_plan_is_rejected(self):
        fake = FakeGraph()
        code = entra.cmd_offboard(session(fake), offboard_args())["confirm"]
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_offboard(session(fake), offboard_args(email=["gary@partner.com"], apply=True, confirm=code))
        self.assertEqual(caught.exception.code, "plan_changed")
        self.assertEqual(fake.writes(), [])

    def test_apply_with_the_code_deletes_the_account(self):
        fake = FakeGraph()
        code = entra.cmd_offboard(session(fake), offboard_args())["confirm"]
        result = entra.cmd_offboard(session(fake), offboard_args(apply=True, confirm=code))
        self.assertTrue(result["success"])
        self.assertEqual(result["users"][0]["status"], "deleted")
        self.assertEqual(fake.writes(), [("DELETE", f"{entra.GRAPH}/users/{GINA}")])

    def test_refuses_self_internal_accounts_and_role_holders(self):
        fake = FakeGraph()
        fake.users["ivan@example.com"] = {"id": NEW, "displayName": "Ivan", "mail": "ivan@example.com", "userType": "Member"}
        fake.roles[GARY] = [{"displayName": "Guest Inviter"}]
        result = entra.cmd_offboard(session(fake), offboard_args(
            email=["alice@example.com,ivan@example.com,gary@partner.com"]))
        reasons = [user["message"] for user in result["users"]]
        self.assertIn("signed-in account", reasons[0])
        self.assertIn("internal account", reasons[1])
        self.assertIn("directory role", reasons[2])
        self.assertIsNone(result["confirm"])
        self.assertFalse(result["success"])

    def test_someone_already_gone_is_not_an_error(self):
        result = entra.cmd_offboard(session(FakeGraph()), offboard_args(email=["ghost@partner.com"]))
        self.assertEqual(result["users"][0]["status"], "not_found")
        self.assertTrue(result["success"])


class GroupDeleteTests(unittest.TestCase):
    def test_plan_keeps_accounts_unless_asked(self):
        fake = FakeGraph()
        result = entra.cmd_group_delete(session(fake), delete_args())
        self.assertEqual(result["status"], "planned")
        self.assertEqual({member["status"] for member in result["members"]}, {"kept"})
        self.assertEqual(fake.writes(), [])

    def test_delete_guests_takes_only_guests_with_no_other_access(self):
        fake = FakeGraph()
        result = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True))
        by_name = {member["name"]: member for member in result["members"]}
        self.assertEqual(by_name["Gina"]["status"], "planned")
        self.assertIn("also a member of: Admins", by_name["Gary"]["reason"])
        self.assertIn("signed-in account", by_name["Alice"]["reason"])

    def test_apply_deletes_accounts_then_the_group(self):
        fake = FakeGraph()
        code = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True))["confirm"]
        result = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True, apply=True, confirm=code))
        self.assertEqual(result["status"], "deleted")
        self.assertEqual(fake.writes(), [("DELETE", f"{entra.GRAPH}/users/{GINA}"),
                                         ("DELETE", f"{entra.GRAPH}/groups/{G_TEAM}")])

    def test_group_is_kept_when_an_account_cannot_be_deleted(self):
        fake = FakeGraph()
        fake.delete_failures[GINA] = fake.error(403, "Insufficient privileges")
        code = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True))["confirm"]
        result = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True, apply=True, confirm=code))
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "kept")
        self.assertEqual(len(fake.writes()), 1)

    def test_membership_change_after_the_plan_invalidates_the_code(self):
        fake = FakeGraph()
        code = entra.cmd_group_delete(session(fake), delete_args(delete_guests=True))["confirm"]
        fake.group_members[G_TEAM] = [GINA]
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_group_delete(session(fake), delete_args(delete_guests=True, apply=True, confirm=code))
        self.assertEqual(caught.exception.code, "plan_changed")
        self.assertEqual(fake.writes(), [])

    def test_protected_group_needs_allow_flag(self):
        with self.assertRaises(entra.EntraError) as caught:
            entra.cmd_group_delete(session(FakeGraph()), delete_args(name="RoleHolders"))
        self.assertEqual(caught.exception.code, "protected_group")

    def test_group_remove_plans_then_removes_only_current_members(self):
        fake = FakeGraph()
        args = SimpleNamespace(group=["Team,Admins"], email=["gina@partner.com"], apply=True, allow_protected=False)
        result = entra.cmd_group_remove(session(fake), args)
        self.assertEqual([item["status"] for item in result["users"][0]["groups"]], ["removed", "not_member"])
        self.assertEqual(fake.writes(), [("DELETE", f"{entra.GRAPH}/groups/{G_TEAM}/members/{GINA}/$ref")])


class CheckTests(unittest.TestCase):
    def run_check(self, roles, invites_from, members_create=False):
        fake = FakeGraph()
        fake.routes += [
            ("GET", r"/me/transitiveMemberOf", lambda path, body: fake.ok({"value": roles})),
            ("GET", r"/policies/authorizationPolicy", lambda path, body: fake.ok({
                "allowInvitesFrom": invites_from,
                "defaultUserRolePermissions": {"allowedToCreateSecurityGroups": members_create}})),
        ]
        return entra.cmd_check(session(fake), SimpleNamespace())

    def test_guest_inviter_can_invite_but_not_create_groups(self):
        result = self.run_check([{"displayName": "Guest Inviter", "roleTemplateId": entra.GUEST_INVITER}],
                                "adminsAndGuestInviters")
        self.assertTrue(result["capabilities"]["invite_guests"])
        self.assertFalse(result["capabilities"]["create_security_groups"])

    def test_no_role_cannot_invite_under_restricted_policy(self):
        result = self.run_check([], "adminsAndGuestInviters")
        self.assertFalse(result["capabilities"]["invite_guests"])

    def test_member_can_invite_when_policy_allows_members(self):
        result = self.run_check([], "adminsGuestInvitersAndAllMembers", members_create=True)
        self.assertTrue(result["capabilities"]["invite_guests"])
        self.assertTrue(result["capabilities"]["create_security_groups"])

    def test_groups_administrator_can_create_groups(self):
        result = self.run_check([{"displayName": "Groups Administrator", "roleTemplateId": entra.GROUPS_ADMIN}],
                                "adminsAndGuestInviters")
        self.assertTrue(result["capabilities"]["create_security_groups"])
        self.assertFalse(result["capabilities"]["invite_guests"])


class TransportTests(unittest.TestCase):
    def test_token_is_never_sent_outside_graph(self):
        fake = FakeGraph()
        fake.routes.append(("GET", r"/users\?", lambda path, body: fake.ok(
            {"value": [], "@odata.nextLink": "https://evil.example/steal"})))
        with self.assertRaises(entra.EntraError) as caught:
            session(fake).graph.user("alice@example.com")
        self.assertEqual(caught.exception.code, "invalid_response")
        self.assertEqual(len(fake.calls), 1)

    def test_throttling_is_retried(self):
        fake = FakeGraph()
        responses = [(429, {"Retry-After": "1"}, b""), fake.ok({"value": []})]
        fake.routes.append(("GET", r"/users\?", lambda path, body: responses.pop(0)))
        self.assertIsNone(session(fake).graph.user("alice@example.com"))

    def test_apostrophes_in_names_are_escaped(self):
        fake = FakeGraph()
        seen = []
        fake.routes.append(("GET", r"/groups\?", lambda path, body: (seen.append(path), fake.ok({"value": []}))[1]))
        session(fake).graph.group("O'Brien Team")
        self.assertIn("O%27%27Brien", seen[0])


class TokenTests(unittest.TestCase):
    def az(self, stdout="", returncode=0):
        return lambda command, **kwargs: SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")

    def test_requested_tenant_is_enforced(self):
        other = "22222222-2222-2222-2222-222222222222"
        stdout = json.dumps({"accessToken": make_token()})
        with self.assertRaises(entra.EntraError) as caught:
            entra.az_token(other, run=self.az(stdout), which=lambda name: "/usr/bin/az")
        self.assertEqual(caught.exception.code, "tenant_mismatch")

    def test_token_and_tenant_are_returned(self):
        stdout = json.dumps({"accessToken": make_token(scp="user_impersonation")})
        token, claims = entra.az_token(TENANT, run=self.az(stdout), which=lambda name: "/usr/bin/az")
        self.assertEqual(claims["tid"], TENANT)

    def test_missing_cli_and_failed_login_are_distinct(self):
        with self.assertRaises(entra.EntraError) as caught:
            entra.az_token(which=lambda name: None)
        self.assertEqual(caught.exception.code, "az_missing")
        with self.assertRaises(entra.EntraError) as caught:
            entra.az_token(TENANT, run=self.az(returncode=1), which=lambda name: "/usr/bin/az")
        self.assertEqual(caught.exception.code, "auth_failed")
        self.assertIn(f"az login --tenant {TENANT}", str(caught.exception))


class MainTests(unittest.TestCase):
    def run_main(self, argv, env):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = entra.main(argv, env=env, token_source=lambda tenant: self.fail("offline must not sign in"))
        return code, json.loads(output.getvalue())

    def test_offline_check_reports_configuration_without_signing_in(self):
        code, result = self.run_main(["check", "--offline"],
                                     {"ENTRA_TENANT_ID": TENANT, "ENTRA_PROTECTED_GROUPS": "Admins, Owners"})
        self.assertEqual(code, 0)
        self.assertEqual(result["tenant"], TENANT)
        self.assertEqual(result["protected_groups"], ["Admins", "Owners"])

    def test_invalid_tenant_is_rejected(self):
        code, result = self.run_main(["check", "--offline", "--tenant", "contoso.com"], {})
        self.assertEqual(code, 1)
        self.assertEqual(result["error"], "invalid_tenant")


if __name__ == "__main__":
    unittest.main()
