# QA sign-off checklist and rollback plan

This document contains a concise checklist to validate readiness for merging the `feature/demos` branch changes
into the main line and a short rollback plan in case something regresses in CI or release.

## Quick checklist (pre-merge)

- [ ] Confirm full test suite passes on main CI runners (Linux/Windows/macOS) for supported Python versions.
- [ ] Confirm the guarded PTK integration job runs successfully on `main` (or via manual `workflow_dispatch`) and uploads artifacts.
- [ ] Verify no critical lint/typecheck errors on CI. The repo enforces `ruff`, `mypy`, and `black --check`.
- [ ] Scan PR diff for any accidental inclusion of large binary files, credentials, or secrets.
- [ ] Verify `docs/MIGRATION_SHIMS.md` and `docs/PTK_WIDGETS.md` are included and clear for integrators.
- [ ] If the release is breaking (it is), add a short migration snippet into CHANGELOG and the PR description.

## Post-merge smoke checks

- Ensure packaging/build (`python -m build`) succeeds in the `build` job.
- Confirm a local install of the built wheel in a fresh venv imports `tui_engine` and basic `Page.render()` functions.

## Rollback plan

1. If a CI failure appears after merging and is clearly caused by these changes, revert the merge commit and open a hotfix branch from `main`.
   - Command sequence:

```bash
git checkout main
git pull origin main
git revert <merge-commit-sha>
git push origin main
``` 

2. Open an emergency PR with a minimal fix or revert details. Tag maintainers and include failing CI logs.

3. If urgent security or blocking bug, cut a maintenance branch and optionally publish a patch release only after tests pass.

## What to watch in CI logs

- Unusual timeouts in the PTK integration job (Xvfb or headless display issues on macOS/windows).
- `mypy` errors complaining about Protocol changes — these may require narrow typing adjustments rather than runtime fixes.
- Coverage regression: our repo enforces >=85% coverage; investigate missing tests if CI drops below threshold.

## Who to notify

- Tag core maintainers and release lead in the PR description and link the ChangeLog entry.

---
Generated on October 29, 2025.
