---
name: pr-triage
description: Triage open PRs that need your review, or your own PRs that need work.
allowed-tools: Bash, Read, AskUserQuestion
---

# PR triage

Tell the user which open PRs need them, and why, then help them act. Uses the `gh` CLI. Works on GitHub and GitHub Enterprise: don't hardcode a host.

Two kinds of PR:

- **A. Needs your action:** the user already reviewed it and it has changed (or they were asked to review it again).
- **B. Needs your review:** the user hasn't reviewed it, and they were asked to, or it matches their skill set.

With `--mine`, it lists the user's own open PRs instead, with what each is waiting on (see "Your own PRs").

## Rules

- Everything here is a draft for the user to verify. Say which commits or files you did not read in detail.
- Never write to a PR (approve, comment, request changes, dismiss) without the user's explicit answer for that PR. Show the exact text first.
- Always show the change summary (step 5) before asking what to do with an A PR. No size threshold: small changes can change a PR's meaning, so don't skip or pre-select an option because a change looks small.
- Skip the user's own PRs and drafts, except with `--mine`.
- Never approve a B PR: the user hasn't reviewed it. Offer a full review instead.

## Steps

### 1. Scope and profile

- `ME=$(gh api user -q .login)`.
- A PR number (`/pr-triage 1039`, or `owner/repo#1039`): only that PR. Skip the profile and classification, and go to step 4 for it. If the user hasn't reviewed it, say so and summarize it as a B PR; if it's their own PR, closed or a draft, say so and stop.
- No PR number: the current repo (`gh repo view --json nameWithOwner -q .nameWithOwner`). `owner/repo` picks another repo (use `-R`). `--all` searches every repo (`gh search prs --state=open --review-requested=@me` and `--reviewed-by=@me`), and applies the user profile only.
- `--mine`: go to "Your own PRs", with the same repo scope (`--all` searches with `gh search prs --state=open --author=@me`). It doesn't use the profile.
- Load the profile (see "Profile"). Teams: `gh api user/teams --jq '.[] | "\(.organization.login)/\(.slug)"'`. If it fails, say so and use direct review requests only.

### 2. Fetch once

```bash
gh pr list -R <repo> --state open --limit 100 \
  --json number,title,url,author,labels,isDraft,reviewRequests,reviews,headRefOid,baseRefName,files,updatedAt
```

If 100 came back, say the limit was hit. Drop drafts and the user's own PRs. Work out each PR's age from `updatedAt` with code, not by hand (e.g. in jq: `((now - (.updatedAt | fromdateiso8601)) / 86400 | floor)` days), and show it as "today", "1 day ago", "N days ago", or in weeks ("N weeks ago") from 14 days and months ("N months ago") from 60 days.

### 3. Classify

For each PR, find the user's latest review (by `submittedAt`, author = `$ME`; any state: `APPROVED`, `CHANGES_REQUESTED`, `DISMISSED`, `COMMENTED`). Its `commit.oid` is the reviewed commit.

- **A**: the user has a review and either `headRefOid` differs from the reviewed commit, or the user is in `reviewRequests` again (re-requested). Always shown, whatever the profile says. Filters `--approved` (latest review `APPROVED`, or `DISMISSED` after an approval) and `--changes-requested` apply here.
- **B**: no review from the user, and one of:
  1. the user or one of their teams is in `reviewRequests` (always shown; add "outside your profile" if nothing in the profile matches);
  2. a `match` rule matches and no `exclude` rule does;
  3. no rule matches but the profile's description of the user's skill set fits the PR from its title and file list. Label it "judgment call" and give the reason in a few words.
- **Hidden**: everything else. Count them, and list them only with `--all-prs`.

Rule matching (apply it literally and say which rule matched):
- `paths`: any changed file matches a glob (`**` crosses directories, `*` doesn't).
- `labels`: any label equals one listed. `keywords`: any word in the title is a form of a keyword, case-insensitive: plurals, verb forms and related nouns count (`migrate` matches "migrates", "migrated", "migrating", "migration" and "migrations"), but not unrelated words that share letters (`test` doesn't match "latest"). Say which title word matched.
- `codeowners: true`: read `CODEOWNERS` (`.github/`, root or `docs/`) at the PR's base; for each changed file the last matching pattern wins; it matches if that entry lists `@$ME` or one of the user's teams.
- `exclude`: `authors` or `labels` match, or `paths` match **every** changed file. Excludes don't hide requested reviews when `always_show_requested` is true (default).

### 4. Show the triage list

Two tables, A then B (omit an empty one), one line per PR: number, title, author, last updated ("3 days ago", from step 2), why it's listed, size (files, +/-). Sort each table by most recently updated first. For A, include the user's last review state and date. For a PR authored by a bot (a login ending in `[bot]`, or starting with `app/`) or labeled `dependencies` that requests the user, also run `gh pr checks <n> -R <repo>` and add "CI failing" to the why column when a check fails (see "Reading CI results" if it fails). Under them: "N PRs not matching your profile" (and how many were excluded), and which profile files were loaded. If the user gave a PR number, skip the tables.

Then ask with AskUserQuestion which PRs to handle now (multi-select, with "none"). Handle them one at a time.

### 5. A PR: summarize what changed since the user's review

```bash
gh api repos/<repo>/compare/<reviewedSha>...<headSha>
gh pr checks <n> -R <repo>   # or the fallback in "Reading CI results"
gh pr view <n> -R <repo> --json comments,reviews   # anything after the user's review
gh api repos/<repo>/pulls/<n>/reviews/<review-id>/comments   # the user's own inline comments
```

The compare range also contains commits merged in from the base branch. Limit the summary to the PR's own changes (its own commits and `gh pr view --json files`), and say so when the compare is mostly base-branch commits. Read the diff since the reviewed commit; for very large diffs read the most relevant files and say which you didn't. If compare fails (force-push, reviewed commit gone), say the review can't be compared and fall back to the PR's full diff.

Show, in this order:

1. PR title, author, link, the user's last review state and date, reviewed commit → current head (7 characters each).
2. **What changed:** plain-language summary, commits one per line, files with +/- counts. Flag when all new commits are base merges.
3. **How it affects the PR:** does it change behavior, scope or purpose; does it touch what the user originally reviewed; or is it only tests, docs, formatting or a base merge.
4. **Your earlier review:** for `CHANGES_REQUESTED` and `COMMENTED`, list the user's earlier points (review body and inline comments) and say for each whether the new commits address it, partly address it, or not. Note author replies and thread resolutions.
5. **Worth a closer look:** anything risky or surprising, new review comments from others, CI state, other reviewers' open `CHANGES_REQUESTED`.

Keep it faster to read than the PR itself.

### 6. A PR: ask, then act

AskUserQuestion, options by the user's last review (every case also offers **Show full diff**; don't pre-select):

- `APPROVED` or `DISMISSED`: **Re-approve**, **Comment: will re-review**, **Withdraw approval** (request changes, or dismiss the user's own review), **Skip**.
- `CHANGES_REQUESTED`: **Approve** (changes addressed), **Keep requesting changes**, **Comment**, **Skip**.
- `COMMENTED`: **Approve**, **Request changes**, **Comment**, **Skip**.

Before drafting text, apply "Verify before commenting" (in step 7) to each earlier point you're about to call addressed or still open, and to any new finding. Then re-fetch the PR's `reviews` and `comments` (`gh pr view <n> -R <repo> --json reviews,comments`): the user or others may have posted since the summary, e.g. after a `/code-review` hand-off. If the user already posted a review, summarize it and ask what's left instead of drafting a duplicate. Show the exact text and resulting state, get the user's go-ahead, then run. Every body follows [Conventional Comments](https://conventionalcomments.org): `**<label> (<decorations>):** <subject>`, label in bold. Labels: `praise`, `nitpick`, `suggestion`, `issue`, `todo`, `question`, `thought`, `chore`, `note`. Decorations: `blocking`, `non-blocking`, `if-minor`. One line per point.

- Approve: `gh pr review <n> -R <repo> --approve --body "<e.g. '**praise:** My earlier comments are addressed in <new7>.'>"` Warn first if required checks are failing, or another reviewer's changes-requested review still blocks the PR.
- Request changes: `gh pr review <n> -R <repo> --request-changes --body "<e.g. '**issue (blocking):** <what's still open>'>"` (the author sees it, and it replaces an earlier approval).
- Comment: `gh pr comment <n> -R <repo> --body "<e.g. '**note:** New commits landed after my review (<old7>..<new7>). I'll re-review.'>"`
- Dismiss the user's own review: `gh api -X PUT repos/<repo>/pulls/<n>/reviews/<review-id>/dismissals -f message="<reason>"`. Not verified to work on the user's own reviews: if it fails, say so and offer request-changes or a comment.

### 7. B PR: summarize and hand off

Read the PR description and file list (`gh pr view <n> -R <repo> --json body,files,commits`). Say in a few lines what it does, why it's listed, how big it is, CI state, and who else has reviewed. Then ask: **Review it now** (run `/code-review <n>`, and come back to approve, request changes or comment from that), **Comment**, **Skip**. If the PR is bot-authored or labeled `dependencies`, has failing checks, and the `pr-fix` skill is available (listed as `pr-fix`, or `pr-skills:pr-fix` when installed as a plugin), also offer **Fix it** (run it with `<n>`). That skill asks before every commit, push and comment, and only works on PRs opened by a bot or by the user, from a branch in the same repository, so it refuses the PR if it's anyone else's. Never run it unless the user chooses it. Comments follow Conventional Comments, with the text shown first.

#### Verify before commenting

Review findings (from `/code-review` or your own reading) are often wrong or unconfirmed, and the user wants to post with certainty. Before drafting, sort each finding into:

- **Cheap to verify:** a claim you can settle in a minute without changing the repo, such as reading the file at the PR's head (`gh api repos/<repo>/contents/<path>?ref=<sha>`), reading core or contrib code, a `grep` for usages, comparing config with what the code would calculate in memory, or running a small read-only script or an existing test against the project's tooling. Offer to run these (AskUserQuestion, one option per group of checks, plus "skip"), and run them before drafting. Use a scratch directory outside the repository, and delete the scripts afterwards.
- **Not cheap:** needs a browser, a deploy, or a long test run. Don't run it unasked. Draft it as a question to the author, not as a statement.
- **Convention claims:** a finding may cite a rule ("the project requires…") that comes from the reviewer's own instruction files, such as a global `AGENTS.md` or `CLAUDE.md` in the home directory, and not from the repository. Before putting a convention in a comment, find it in the repo (its `AGENTS.md`, `docs/`, linter or coding-standard config, or existing code that follows it). If it isn't there, drop it, or phrase it as the user's own preference ("I'd prefer…") and tell the user it's a personal rule.

In the draft, say what you checked for each point, and word anything you didn't check as a question. Drop findings that a check contradicts, and tell the user why. In your message with the draft, list what was verified and how, and what wasn't.

After each action, report the result and the PR URL. At the end, list what was approved, changes requested, commented on, handed off and skipped.

### Your own PRs (`--mine`)

```bash
gh pr list -R <repo> --state open --author @me --limit 100 \
  --json number,title,url,body,isDraft,reviewDecision,reviewRequests,reviews,headRefOid,updatedAt
```

For each PR, count its unresolved review threads with the `reviewThreads` query from `pr-fix`'s "Review feedback" (only `isResolved` is needed), and read its CI state (`gh pr checks <n> -R <repo>`, or "Reading CI results"). Show one table, most recently updated first: number, title, last updated, size, and what it's waiting on, all that apply:

- **Changes requested** by whom (`reviewDecision` `CHANGES_REQUESTED`, and the reviewers whose latest review is `CHANGES_REQUESTED`).
- **N unresolved threads**.
- **CI failing**, with the failed checks.
- **N remaining tasks** in the description: unchecked task list items (`- [ ]`) and items under a heading such as "Remaining tasks" or "TODO".
- **Waiting for review** from the users and teams in `reviewRequests`, or **no reviewer** if there's none and no approval.
- **Approved**, when nothing above applies. Say it's ready to merge, but never merge it.
- **Draft**.

Ask which PRs to handle now (multi-select, with "none"). For each: list the open feedback (reviewer, link, one line each, marking comments from outside the repo's collaborators or from bots), the failed checks, and the remaining tasks, saying for each task whether it looks needed to finish the PR and whether it's a code change. If there's feedback, a failing check or a remaining code task, and the `pr-fix` skill is available, offer **Fix it** (run it with `<n>`), **Show the threads** in full, and **Skip**. Never run `pr-fix` unless the user chooses it. Without `pr-fix`, summarize and skip.

## GitHub token permissions

The `gh` token only needs read access to triage. Write access is needed only for step 6 and 7 actions, which always wait for the user's go-ahead.

- **Classic token:** `repo` (read and write; there's no read-only scope for private repos) and `read:org` (for `gh api user/teams`).
- **Fine-grained token** (repository permissions, on the repos to triage; Metadata read is added automatically and isn't listed):
  - Pull requests: read, for listing, reviews, comments and files. Pull requests: write for approving, requesting changes, commenting and dismissing.
  - Contents: read, for the compare API and `CODEOWNERS`.
  - Actions: read and Commit statuses: read, for CI results. Fine-grained tokens can't have Checks: read, so `gh pr checks` fails with them; use the fallback in "Reading CI results".
  - `--all` searches only repos the token can read.
- Team membership (`gh api user/teams`) may be unavailable to a fine-grained token. If it fails, the skill falls back to direct review requests (step 1).
- If a read call fails with a 403 or 404 on a repo the user can open, suggest checking the token's permissions and repo access before assuming the data doesn't exist.

## Reading CI results

Use `gh pr checks <n> -R <repo>`. If it fails with "Resource not accessible by personal access token", the token is fine-grained and has no Checks: read. Fall back to:

- `gh run list -R <repo> --commit <headRefOid> --json databaseId,workflowName,event,status,conclusion` for GitHub Actions. For each workflow and event, only the newest run (highest `databaseId`) counts. It failed if its `conclusion` is `failure`, `timed_out` or `startup_failure`.
- `gh api repos/<repo>/commits/<headRefOid>/status` for commit statuses from CI outside Actions (e.g. Tugboat). A `failure` or `error` state is a failure. Ignore the combined `state` when `statuses` is empty: it's always `pending` then.

Check runs from other GitHub Apps can't be read this way. When using the fallback, say that only Actions runs and commit statuses were checked.

## Profile

A Markdown file with YAML front matter. Two optional files; the repo file wins:

1. `~/.config/pr-triage/profile.md`: the user's defaults for every repo.
2. `<repo root>/.claude/pr-triage.md`: overrides for one repo.

Merge: mappings merge key by key, and a list in the repo file replaces the same list from the user file. The Markdown body of the repo file replaces the user file's body if it's non-empty. Front matter keys (all optional):

```yaml
match:
  paths: ["src/migrations/**"]    # any changed file matches
  labels: [ci]
  keywords: [migrate]             # any form of the word in the title
  codeowners: true                # CODEOWNERS entries naming me or my teams
exclude:
  authors: [renovate[bot], dependabot[bot]]
  labels: [dependencies]
  paths: ["**/*.lock"]            # only if ALL changed files match
always_show_requested: true       # requested reviews ignore exclude (default true)
```

The body describes the user's skill set in plain language (what they know well, and what they're less involved in). It is used for "judgment call" matches, and teammates can read it. See `profile.example.md` next to this file.

If neither file exists, say so, ask the user 3–4 questions (areas they work on, paths or labels to include or exclude, whether to hide bot PRs), and offer to write a profile after showing it. To suggest paths, look at where they have reviewed or authored before (`gh search prs --reviewed-by=@me`). Don't write any profile file without the user's go-ahead.
