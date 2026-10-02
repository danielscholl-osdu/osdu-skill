# Exemplars

## What the house documents do

Two documents set this style. They are summarized here for their lessons; the summaries are not a source of technical facts about any system.

**Schema Load Ownership Map** is an ownership move across upstream, template, fork, and stack repositories. Its diagrams earn their space: a cross-lane flow shows the path to the service, an assembly shows contributing owners, aligned lanes compare today and the proposal, and a tree shows which forks run or skip. Its main lesson is to organize around responsibility, not a file list. Each branch names who reaches it.

**Deployer Permissions** describes a grant boundary and a pre-deployment check. It places authority beside the grant and non-guarantees beside the check. It distinguishes distinct roles from assignment counts. Its terminal sample was based on actual tool output rather than invented formatting. Its main lesson is that a passing check establishes specific evidence, not a guarantee of deployment success.

Both open with the document in miniature, define owner colors once, give rationale beside behavior, and move exhaustive reference material to lettered appendices.

The three examples below are fictional and deliberately different in kind: a settled design, an exploratory proposal, and a findings report. They show the voice and the level of detail, not a template to copy section by section.

## Complete prose example: ownership

The following is a fictional settled design. Repository names, paths, links, and behavior illustrate the writing standard; they are not evidence about the user's code. It deliberately has no terminal mockup because no real CLI sample is supplied. `assets/ownership-example.html` is the complete rendered counterpart with a mechanism diagram.

# Schema loader ownership

The platform repository currently builds the loader image as part of its application release. A schema-only change therefore waits for an application release even though the application code has not changed.

This change makes the payload repository build a versioned loader image. The environment repository selects an image digest and runs it before starting the service.

The change does not alter schema compatibility rules or retry failed loads automatically. An image build proves that the payload can be packaged, not that a target environment will accept it.

## Ownership

| Repository | Responsibility | Change here when |
|---|---|---|
| Payload | Schema files and loader image | Schema contents or loader behavior changes |
| Environment | Image digest and load job | The selected version or deployment order changes |

The environment selects a digest rather than a mutable tag so a deployment uses the same image when retried. The payload repository does not receive credentials for target environments.

## Load behavior

The deployment checks for a configured loader digest. If none is configured, it skips the load step and starts the service. A failed configuration read stops the deployment; it is not treated as an absent digest.

When a digest is present, the environment runs the loader before starting the service. A successful job allows startup. A failed job stops startup and retains its logs. There is no automatic retry because a repeated load may not be idempotent.

## Compatibility and rollout

The first deployment selects the digest corresponding to the payload already used by the environment. Schema compatibility remains the payload owner's responsibility.

Restoring the previous digest changes what the next load uses. It does not undo schema writes already made to the service. Data rollback remains outside this change.

## Validation

The validation plan covers four paths: absent digest, unreadable configuration, successful load, and failed load. It also checks that a failed load retains logs and prevents startup.

A disposable-environment run will check the deployment order and credential boundary. No environment run has been performed for this illustrative design.

## Appendix A: image selection

The environment configuration contains one immutable image reference:

```json
{
  "loaderImage": "registry.example.invalid/schema-loader@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

## Appendix B: alternatives

| Alternative | Why not |
|---|---|
| Keep the application-release build | Schema changes would still wait for an unrelated release |
| Select a mutable image tag | A retry could load a different payload |
| Retry every failed load | The loader does not establish idempotency |

## Complete prose example: permission proposal

This is a fictional exploratory proposal, not a claim about a real cloud provider or tool. The permission names are illustrative.

# Deployment preflight

The deployment command currently starts resource creation before checking whether the caller can create role assignments. A caller may therefore receive a permission error after some resources already exist.

This proposal adds a permission query before creation. A reported denial stops the command and names the missing operation.

The query does not evaluate conditional restrictions or guarantee that the deployment will succeed. The treatment of an unavailable query service remains an open decision.

## Required authority

The caller needs resource-create authority on the target environment and role-assignment-write authority on the same environment. The second permission allows the caller to grant access to other identities within that scope.

The proposal does not broaden the caller's authority. It reports whether the queried operations are allowed under the permission service's response.

## Preflight behavior

The recommended behavior is to stop on a reported denial and continue on an unavailable query, with a warning. The query adds an early diagnostic; making its availability a new deployment dependency would introduce a failure unrelated to resource creation.

| Query result | Command behavior |
|---|---|
| Both operations allowed | Begin deployment |
| Either operation denied | Stop before creating resources |
| Query unavailable | Warn and continue, pending the decision below |

A successful response does not account for conditional restrictions or permissions changing between the query and creation. The resource API remains authoritative.

## Open decision

The service owner must decide whether deployments may continue when the permission query is unavailable. Blocking would avoid proceeding without a diagnostic result, but it would make the query service part of deployment availability. The command's failure behavior cannot be finalized until this decision is made.

## Validation

Unit tests will cover allowed, denied, and unavailable responses and confirm that denial prevents the first create call. A disposable-environment run will compare the diagnostic with an actual resource API denial. These checks are planned, not completed.

## Appendix A: alternatives

| Alternative | Consequence |
|---|---|
| Stop when the query is unavailable | Makes query availability a deployment requirement |
| Keep the current resource API error only | Does not prevent partially created resources |

## Complete prose example: findings report

This is a fictional findings report. The tenant, people, and applications are invented. `assets/audit-example.html` is the rendered counterpart with its diagram, severity legend, and appendices.

# Who can manage users in the lab tenant

This report examines who can create, invite, change, and remove user accounts in the lab tenant. It is based on directory role assignments, the guest invitation policy, and application permissions, read through the directory API on 2 March 2026.

Two accounts held by one person can manage users fully. One delegate can invite guests. Four service principals can create or change users. There are four findings: one high, two medium, and one note.

Role assignments that are eligible but not activated could not be read with the access used, so a person holding an inactive role would not appear here. Whether the service principals' credentials still work was not checked.

## Findings

| Severity | Finding | Consequence | Recommendation |
|---|---|---|---|
| High | No second person can manage users | If Avery Chen is unavailable, nobody can remove, restore, or change an account | Assign User Administrator to a second person. The tenant owner decides who. |
| Medium | Four service principals hold user-write permission granted between 2021 and 2023 | A leaked credential for any of them can create accounts | Confirm each is unused, then remove the permission |
| Medium | The delegate can invite but cannot finish onboarding | Every invited guest waits for the administrator to add them to a group | Make the delegate an owner of the groups they onboard into |
| Note | Ordinary members cannot invite guests | Invitations stay with named people | None |

## Service principals

Four applications hold a permission that lets them create and change users without a signed-in person. The permissions were granted between May 2021 and July 2023.

They are likely left over from retired deployments, because three of the four are named after environments that no longer exist. That is an inference from the names. Sign-in logs would confirm it and were not read.

What the example shows: the answer comes before the findings count, each finding is a claim a reader could repeat, the inferred cause is labeled as inferred with what would confirm it, and the gap in the audit's own reach is in the opening box.

## Revision exercise

Given the ownership design above, feedback says: "Missing configuration must stop, not skip."

This changes the mechanism, not just wording. First clarify whether "missing" means no digest configured or configuration cannot be read if the feedback does not say. In this exercise it means no digest configured.

Revise the existing file, not a new page. Update the problem box if the new requirement changes its scope; change the absent-digest paragraph to say it stops the deployment and update the validation path. Preserve the immutable-digest rationale, failed-load behavior, and rollback boundary. The example's artifact-path diagram does not depict failure decisions, so it remains unchanged.

Run the full checklist and recheck affected layouts in both themes and at narrow width. If a real document also has a decision diagram, update any skip leaf that now needs to say stop. Do not add "After review..." to explain the revision.
