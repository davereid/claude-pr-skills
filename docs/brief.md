# fix-dependency-pr: requirements brief

- **Revision** 2
- **Brief approval** Awaiting approval (revision 1 approved 2026-11-04; revision 2 adds `all`, which works through every failing bot PR)

## Job and scope

For developers on DDEV projects that get dependency PRs from Renovate or Dependabot. The skill fixes failing bot PRs: module or package updates that need config or schema updates, dependency changes, patches that no longer apply, test regressions, or other common causes.

- **Covers:** one failing Renovate or Dependabot PR per run, or every failing one in turn with `all`, on any GitHub host (github.com or GitHub Enterprise), in any project that uses DDEV. No project-specific assumptions: the host, repo, commit convention and test commands all come from the project itself.
- **Packaging:** a Composer package, `davereid/fix-dependency-pr` (github.com, assumed public on Packagist), containing the skill, a `Taskfile.yml` and a CI workflow template.
- **Excludes:** Pantheon or other hosting, Tugboat, email, Google Workspace, merging, and any production or remote environment.

## When it runs

- **Locally (main use):** the developer asks in Claude Code, or runs `task <include>:fix` from the project's root Taskfile, which includes the package's Taskfile. The task defaults to `all`: it works through every failing bot PR, oldest first, with each PR's own approvals and 3-attempt limit, then summarizes the results. `PR=<number>` limits it to one PR. With no argument in Claude Code, it lists failing bot PRs and the developer picks one, or all.
- **Where it runs:** on the host (calling `ddev …`), or inside the ddev-claude container (calling `task …`/`composer …` directly). The skill detects which one.
- **CI (comment only):** the project's workflow, copied from the template, runs on `workflow_run` when a listed workflow fails on a matching PR, and on `workflow_dispatch` with a PR number.
- **Preconditions:**
  - The PR matches the eligibility rules (see Access).
  - The project has a `.ddev` folder.
  - In CI, `ANTHROPIC_API_KEY` is set; otherwise the job exits early with a notice.

## Inputs and references

- **Each run:** the PR (metadata, diff, head branch and author), its failed checks and their logs, and the failed workflow's YAML (for the exact commands it ran).
- **Standing references:** the project's README and docs (how to install the site, test commands), its commit convention (from contributing docs and `git log`), its Renovate config (`branchPrefix`), and Dependabot config.

## How it runs

**Workflow** (Q14): fixed steps with known branches, so it's predictable and traceable.

1. Check that the PR is eligible (see Access); otherwise stop.
2. Read the failed workflow's logs and the PR diff.
3. Classify the failure:
   - A. A patch fails to apply
   - B. A schema or config update is needed
   - C. A test regression
   - D. Something else
4. Check out the PR's branch, start DDEV, and propose a fix.
5. Test locally by running the same commands as the failed job, through DDEV.
6. If they fail, revise the fix and retest, up to **3 attempts**. Then stop and draft a PR comment with what it found and tried.
7. Show the cause, the diff and the test results, and **ask before updating the PR**.
8. After approval, commit (following the project's convention) and push to the PR's branch. Then, after another confirmation, post a PR comment with the cause and the fix. For Dependabot PRs, note that Dependabot will stop rebasing the PR.
9. Report the check URL and stop. It doesn't wait for CI.

**CI variant:** runs steps 1–6 in the runner (DDEV installed the same way as the project's other workflows), then writes or updates one sticky PR comment with the cause, the proposed diff and the test results. It never pushes.

## Output

- **Locally:** a commit pushed to the bot PR's branch and a PR comment, both after the developer confirms. If it gives up, it drafts a PR comment in the chat for approval.
- **CI:** one sticky PR comment, updated on re-runs.

## Access and runtime boundaries

- **Confirmed access:**
  - Installed locally: `gh` 2.103.3 and DDEV v1.25.5.
  - The md-cms remote is reachable.
  - `gh` is **not logged in** to `state-of-maryland.ghe.com`. That was checked from the sandbox; to verify.
  - The CI key, its owner and whether GHE allows the action are **unknown**.
- **Runtime approvals:** before every commit and push, and before every PR comment. Approving one PR doesn't carry over to the next.
- **Prohibitions and fallback:** never:
  - run without limits
  - touch production or other remote environments
  - merge, approve or close PRs
  - modify any PR that isn't eligible
  - force-push, except `--force-with-lease` after rebasing the user's own PR when their instructions allow it (added 2026-11-13; merging the base in is the default)
  - push to any branch other than the PR's own
  - push from CI

  When unsure, stop and ask. In CI, comment only.
- **Eligible PRs:** the author is any bot (`author.is_bot`, whatever its login: `app/example-renovate[bot]`, `app/dependabot`, `dependabot[bot]`) or the user logged in to `gh`, and the branch is in this repository. The branch name isn't checked, so custom Renovate apps and `branchPrefix` need no setup. In CI, the automatic trigger runs only for `dependabot/` branches whose author, with `app/` and `[bot]` stripped, is `dependabot`. The normalization was seen on the examples above; other GitHub Enterprise setups may format logins differently.
- **State:** none; each run starts fresh. CI uses the sticky comment's header instead of remembering what it posted.

### Setup checklist

| Integration | Purpose | Actions needed and exact scope | Connector or fallback | Status | Allowed tools versus forbidden tools |
|---|---|---|---|---|---|
| GitHub (`gh` CLI) | Read the PR, checks and logs; comment | Read PRs, checks and run logs; post a comment. One repo, with a fine-grained token: Contents R/W, Pull requests R/W, Actions R. | CLI | Installed; not logged in to GHE (to verify) | Allowed: `gh pr view/diff/checks/list`, `gh run view --log-failed`, `gh pr comment`, `gh api` GET. Forbidden: `gh pr merge/review/close/edit`, label, settings and delete calls. |
| git | Commit and push the fix | Push only to the matching PR's head branch | CLI, with the user's SSH key and signing | Reachable | Allowed: `fetch`, `checkout` of the PR branch, `add`, `commit`, `merge` of the PR's base, `push` (not force). Rebase and `push --force-with-lease` only as above. Forbidden: other force-pushes, and pushing to other branches. |
| DDEV | Install the site; run the failed job's commands | Local project only | CLI | v1.25.5 | Allowed: `ddev start`, `ddev composer`, `ddev task`, `ddev drush`/`exec` locally. Forbidden: remote aliases, `sql-sync` or pulls from remotes, Terminus. |
| ddev-claude container (optional) | Run the skill inside the container | Same as DDEV, without the `ddev` prefix | Add-on `marcoscano/ddev-claude` | Unverified, still being set up | Same as above |
| `anthropics/claude-code-action` (CI) | Diagnose and test a fix in CI | Read the repo and logs. Workflow permissions: `contents: read`, `actions: read`, `pull-requests: write`. | GitHub Action, pinned `c0949c50a78c1ec8ce2647db36629b870e715d0c` (v1.0.268) | New dependency; key owner and GHE support unknown | Allowed: read and run DDEV. Forbidden: push, merge. |
| `marocchino/sticky-pull-request-comment` (CI) | One comment per PR | Create or update its own comment | Pinned `5770ad5eb8f42dd2c4f34da00c94c5381e49af88` (v3.0.5) | Already used in md-cms | Only its own header |
| `ddev/github-action-setup-ddev` (CI) | Install DDEV | — | Pinned `fdf2f5c97943bae638f31df6df86f1defa6210c0` (v1.12.1), or the project's own wrapper action | Already used in md-cms | — |

- **Action pins:** always pin actions to a full commit SHA, with the version in a comment.
- **Local files and folders:**
  - `vendor/davereid/fix-dependency-pr/`, from Composer.
  - `.claude/skills/fix-dependency-pr`, a symlink created by the `install-skill` task.
  - `.github/workflows/fix-dependency-pr.yml`, copied by the `install-workflow` task and committed by the project.
  - An `includes:` entry in the root `Taskfile.yml`, added by the developer.
- **Identities and credentials:**
  - The developer's `gh` login for the project's GitHub host.
  - SSH and signing keys.
  - `ANTHROPIC_API_KEY`, as both an Actions secret and a Dependabot secret. For client projects, the client must own or approve it, per Lullabot's AI policy.

## Acceptance cases

| Situation | Expected behavior | Reviewer check |
|---|---|---|
| A Renovate PR fails because a patch no longer applies | Finds the patch in the logs, updates or removes it, reruns the failed job's command, then shows the diff and asks before pushing | The commit follows the project's convention; nothing is pushed before approval |
| A Dependabot PR fails after an update changes config | Runs the database updates, exports the config, retests, then asks before pushing | The comment notes that Dependabot will stop rebasing |
| PR #N was opened by a person, or the branch matches but the author doesn't | Refuses and stops | No checkout, commit or comment |
| The fix still fails after 3 attempts | Stops and drafts a comment with what it found and tried | No fourth attempt; nothing posted without approval |
| CI runs without `ANTHROPIC_API_KEY` | Exits early with a notice | No Claude step runs |
| CI runs again on the same PR | Updates the existing sticky comment | Only one bot comment exists |
| `gh` isn't logged in to the host, or DDEV isn't running or installed, on the first run | Stops and tells the developer how to fix it (`gh auth login --hostname …`, `ddev start`) | Only `gh auth status` and `ddev describe`/`--version` ran; no write was used as a probe |

## Blockers and later work

- **Blockers:** none for generating the files. Before real use: who owns the API key, whether the GHE instance allows the actions, and the `gh` login.
- **Later work:**
  - Push from CI after approval (a label or `/apply-fix` command).
  - Tugboat logs.
  - Email output.
  - Other bots.
