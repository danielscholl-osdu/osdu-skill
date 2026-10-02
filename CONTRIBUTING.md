# Contributing

## Layout

```
plugin.json              Copilot plugin manifest
skills/<name>/SKILL.md   What Copilot reads when the skill triggers
skills/<name>/scripts/   Scripts the skill runs
skills/<name>/reference/ Detail Copilot loads only when it needs it
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

Copilot reads the `description` to decide whether to load the skill, and the body to decide what to do. Describe categories of intent in the description, not lists of example phrases. In the body, state what the person needs and why each constraint exists; keep exact commands for the steps where only one sequence is safe. Put detail in `reference/` and link to it.

## Pull requests

Keep each pull request to one skill or one concern. Say what changed in behaviour and how you verified it.
