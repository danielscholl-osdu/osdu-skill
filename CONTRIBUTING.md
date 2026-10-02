# Contributing

## Layout

```
plugin.json              Copilot plugin manifest
skills/<name>/SKILL.md   What Copilot reads when the skill triggers
skills/<name>/scripts/   Scripts the skill runs
skills/<name>/references/ Detail Copilot loads only when it needs it
skills/<name>/assets/     Files a skill copies or builds from
tests/                   Offline tests
```

## Run the tests

```bash
python3 -m unittest discover -s tests
python3 tests/check_structure.py
```

The tests never sign in and never touch the network. Graph calls go through a fake transport.

## Try a change in Copilot

```bash
copilot --plugin-dir .
```

## Rules for skills in this repository

- **Standard library only.** Scripts run with the Python the user already has. No package installs.
- **Plan by default.** Anything that changes a tenant, a cluster, or a repository needs an explicit `--apply`, and the plan has to show everything the change will do.
- **JSON out.** One JSON object on stdout, exit 0 on success and 1 on failure, with a stable `error` code on failure.
- **No tenant-specific values.** No tenant IDs, group names, subscription names, or hostnames in skills, scripts, tests, or docs. This repository is public. Configuration comes from flags and environment variables.
- **A lookup error is not an absence.** If a read fails, report the failure. Do not continue as though the thing does not exist.
- **Tests for every write path**, including the case where the plan makes no writes.

## Writing SKILL.md

Copilot reads the `description` to decide whether to load the skill, and the body to decide what to do. Describe categories of intent in the description, not lists of example phrases. In the body, state what the person needs and why each constraint exists; keep exact commands for the steps where only one sequence is safe. Put detail in `references/` and link to it.

## Pull requests

Every change reaches `main` through a pull request, and the six CI jobs (Linux, macOS, and Windows on Python 3.10 and 3.13) have to pass before it can merge. No review approval is required.

Keep each pull request to one skill or one concern. Say what changed in behaviour and how you verified it.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org), because the release notes and the next version number are built from them:

| Prefix | Use for | Effect on the next release |
|---|---|---|
| `feat:` | A new skill, command, or capability | Minor version |
| `fix:` | A behaviour that was wrong | Patch version |
| `docs:` | Skill text, references, README | Listed in the notes, no bump on its own |
| `chore:`, `test:`, `ci:`, `refactor:` | Everything else | Not listed |

A breaking change adds `!` after the type (`feat!:`), and says what breaks in the body.

## Releasing

`main` is where work lands. People who installed the plugin from the marketplace do not get `main`; they get the last release, because the marketplace entry installs from the `release` branch and only the release workflow moves that branch.

1. Every push to `main` opens or updates one pull request titled "chore(main): release X.Y.Z". It holds the changelog and the version bump for everything merged since the last release.
2. To release, review that pull request and merge it. That is the only step, and nothing reaches users until it happens.
3. Merging creates the tag `vX.Y.Z` and the GitHub release, and moves the `release` branch to that tag.

The release pull request changes `CHANGELOG.md` and the version in `plugin.json` and `.github/plugin/marketplace.json`. Do not edit those by hand, and do not push to the `release` branch.

`main` and `release` are protected against deletion and force pushes. The release workflow only ever moves `release` forward, and it is the only thing that pushes to that branch.

CI on the release pull request waits for a maintainer, because the pull request is opened by a workflow. Select "Approve and run" on it before merging.

To hold a change back from a release, keep it off `main`. To release a specific version number, add `Release-As: X.Y.Z` to the body of a commit on `main`.
