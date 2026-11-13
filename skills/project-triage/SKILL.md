---
name: project-triage
description: Triage PRs, merge requests and issues that need your review or a reply.
allowed-tools: Bash, Read, AskUserQuestion
---

# Project triage

Tell the user which open pull or merge requests (PRs) and issues (or work items) need them, and why, then help them act. Host commands are in `references/` (see step 1); everything else here applies to every host.

Two kinds of PR:

- **A. Needs your action:** the user already reviewed it and it has changed (or they were asked to review it again).
- **B. Needs your review:** the user hasn't reviewed it, and they were asked to, it matches their skill set, or it's in a repo they own.

Two kinds of issue:

- **A. Needs your reply:** the user commented, and someone else commented after them.
- **B. Needs triage:** the user hasn't commented yet.

Which items are looked at depends on whether the user owns the repo:

- **Owned** (the user owns or maintains it; each host's reference says exactly what counts): every open PR and issue from others.
- **Not owned:** PRs that request the user's review, that they reviewed, or that match their profile, and issues assigned to them.

With `--mine`, it lists the user's own open PRs instead, with what each is waiting on (see "Your own PRs"), and with `--mine --issues` their own issues that have replies (see "Your own issues").

## Rules

- Everything here is a draft for the user to verify. Say which commits, files or comments you did not read in detail.
- Never write to a PR or issue (approve, comment, request changes, dismiss, close, change its status or labels) without the user's explicit answer for that item. Show the exact text first.
- End every review body, PR or MR comment, and issue reply you post with a disclosure line, after a blank line, in italics, naming the agent running this skill (e.g. Claude Code, Codex, Cursor) and summarizing the user's part in one sentence, from what they did in this session: the decisions they made or directed (the approach, which findings to raise, approve or request changes), what they checked or had checked, and their edits. E.g. `_Drafted with <agent> using [project-triage](https://github.com/davereid/skills/tree/main/skills/project-triage). I chose which findings to raise, had each checked against the code, and reviewed the final text._` Don't claim anything the user didn't do. Inline comments are covered by their review's line; on hosts where they're posted separately, the general comment posted with them carries it. Include it in the draft you show, so the user can edit or drop it.
- Always show the change summary (step 6) before asking what to do with an A PR. No size threshold: small changes can change a PR's meaning, so don't skip or pre-select an option because a change looks small.
- Skip the user's own PRs and issues, and draft PRs, except with `--mine`.
- Never approve a B PR: the user hasn't reviewed it. Offer a full review instead.
- Security: if an issue, PR, finding or upstream bug looks like a vulnerability, never draft public text with its details, here or upstream. Say so, check the affected project's published advisories, and point the user to its private reporting channel (from its `SECURITY.md`, or the host's reference, "Security"). A public reply may only ask the reporter to use that channel.

## Steps

### 1. Host, scope and profile

- **Repo:** run from inside the project's checkout; the skill works on that one repo and never scans other directories. Read its remote with `git remote get-url origin` (if there's no `origin`, use the only remote, or ask which one). `owner/repo` (or `host/owner/repo`) picks another repo on the same host, without a checkout. `--all` searches the host's API (the current checkout's host, or `github.com` outside a checkout), not local directories.
- **Host:** take the hostname from the remote URL (`git@<host>:owner/repo.git`, `ssh://git@<host>/owner/repo.git` or `https://<host>/owner/repo.git`) and pick the reference, without calling the host:
  - `github.com` or `*.ghe.com`: `references/github.md`.
  - `git.drupal.org` or `git.drupalcode.org`: `references/gitlab.md` and `references/drupalorg.md` (where they differ, `drupalorg.md` wins).
  - `gitlab.com`, or a hostname containing `gitlab`: `references/gitlab.md`.
  - Any other host: ask whether it's GitHub Enterprise or GitLab.

  If the repo has `.claude/project-triage-issues.md` with a "Fetching issues" section (see "Project issue tracker"), use it instead of the host reference for every issue step.

  Use the reference's commands for every step, mapping the skill's terms (review, requested reviewers, draft) as the reference says. If a command fails, report the error; don't treat it as an unsupported host.
- **Who:** find the user's login on that host (`$ME`), as the reference says. Logins can differ between hosts.
- **What:** PRs and issues by default. `--code` limits it to PRs, `--issues` to issues. `--mine` defaults to `--code`; add `--issues` for the user's own issues.
- **Single item:** a number (`/project-triage 1039`, or `owner/repo#1039`): only that item. Skip the profile and classification, find out whether it's a PR or an issue, and go to step 5 for it. A PR the user hasn't reviewed: say so and summarize it as a B PR. An issue: summarize it (step 9). If it's their own, closed or a draft, say so and stop.
- **Which repos:** no number: the current repo (see **Repo**). `--all` searches every repo the user can read (review requests, reviews, issues assigned to them, and the repos they own), and applies the user profile only. If the host's reference says some owned repos can't be found this way, say so, and suggest triaging those one at a time.
- **Owned:** check whether the user owns each repo, with the rule and commands in the host's reference ("Ownership").
- `--mine`: go to "Your own PRs" (and "Your own issues" with `--issues`), with the same repo scope. It doesn't use the profile.
- Load the profile (see "Profile"). Find the user's teams; if that fails, say so and use direct review requests only.

### 2. Fetch once

Fetch the repo's open PRs (unless `--issues`) and open issues (unless `--code`) in one call each, with up to 100 items. In a repo the user doesn't own, fetch only issues assigned to them.

If 100 came back, say the limit was hit. Drop draft PRs and the user's own items. Work out each item's age from its last update with code, not by hand, and show it as "today", "1 day ago", "N days ago", or in weeks ("N weeks ago") from 14 days and months ("N months ago") from 60 days.

### 3. Classify PRs

For each PR, find the user's latest review (by submission time, author = `$ME`; any state: approved, changes requested, dismissed, commented). Its commit is the reviewed commit.

- **A**: the user has a review and either the PR's head commit differs from the reviewed commit, or the user is in the requested reviewers again (re-requested). Always shown, whatever the profile says. Filters `--approved` (latest review approved, or dismissed after an approval) and `--changes-requested` apply here.
- **B**: no review from the user, and one of:
  1. the user or one of their teams is a requested reviewer (always shown; add "outside your profile" if nothing in the profile matches);
  2. the repo is owned by the user (reason "your repo"), and no `exclude` rule matches;
  3. a `match` rule matches and no `exclude` rule does;
  4. no rule matches but the profile's description of the user's skill set fits the PR from its title and file list. Label it "judgment call" and give the reason in a few words.
- **Hidden**: everything else. Count them, and list them only with `--all-prs`.

Rule matching (apply it literally and say which rule matched):
- `paths`: any changed file matches a glob (`**` crosses directories, `*` doesn't).
- `labels`: any label matches one listed, exactly or as a glob where `*` matches any characters (`v7.x-*` matches `v7.x-1.x-dev` and `v7.x-1.9`). `keywords`: any word in the title is a form of a keyword, case-insensitive: plurals, verb forms and related nouns count (`migrate` matches "migrates", "migrated", "migrating", "migration" and "migrations"), but not unrelated words that share letters (`test` doesn't match "latest"). Say which title word matched.
- `codeowners: true`: read the code owners file at the PR's base (where it lives and its syntax are in the host's reference, "CODEOWNERS"); for each changed file the last matching pattern wins; it matches if that entry lists `@$ME` or one of the user's teams.
- `exclude`: `authors` or `labels` match, `branches` matches the PR's base (target) branch as a glob (`*` matches any characters, `7.x-*` matches `7.x-1.x`), or `paths` match **every** changed file. Excludes don't hide requested reviews when `always_show_requested` is true (default).

### 4. Classify issues

Drop issues whose author or labels match the profile's `exclude` (`paths` and `branches` don't apply to issues). For each remaining issue, find the user's latest comment.

- **A**: the user has commented, and someone else commented after the user's latest comment.
- **B**: the user hasn't commented. Say why it's listed: "your repo", or "assigned to you".
- **Hidden**: the user's comment is the latest (waiting on others). Count them, and list them only with `--all-prs`.

### 5. Show the triage list

Up to four tables, in this order, omitting empty ones: A PRs, B PRs, A issues, B issues. Sort each by most recently updated first.

- PRs: number, title, author, last updated ("3 days ago", from step 2), why it's listed, size (files, +/-). For A, include the user's last review state and date. For a PR authored by a bot or labeled `dependencies` that requests the user, also read its CI results and add "CI failing" to the why column when a check fails.
- Issues: number, title, author, last updated, why it's listed, assignees, number of comments. For A, include the date of the user's last comment.

Under them: "N PRs not matching your profile" (and how many were excluded), "N issues waiting on others" (and how many were excluded), and which profile files were loaded. If the user gave a number, skip the tables.

Then ask which items to handle now (multi-select, with "none"). Handle them strictly one at a time:

- Show one item's summary, review and drafts per message, never several items' together. If the agent can run tasks in the background, start the reviews of the other selected PRs (e.g. `/code-review <n>`) in the background once the user picks them, and keep each result until its item comes up; otherwise run each review when its item comes up.
- At each question about an item, the user can give feedback or ask for more investigation instead of picking an option (offer **Investigate further** alongside the step's options). Do what they ask, show the updated findings or draft, and ask again. Move on only when they've acted on the item or chosen **Skip**.
- Between items, say which one is next and how many are left (e.g. "Next: #42, 2 of 3"), and let the user stop there.

### 6. A PR: summarize what changed since the user's review

Read the comparison between the reviewed commit and the PR's head, the CI results, comments and reviews posted after the user's review, and the user's own inline comments.

The comparison also contains commits merged in from the base branch. Limit the summary to the PR's own changes (its own commits and files), and say so when the comparison is mostly base-branch commits. Read the diff since the reviewed commit; for very large diffs read the most relevant files and say which you didn't. If the comparison fails (force-push, reviewed commit gone), say the review can't be compared and fall back to the PR's full diff.

Show, in this order:

1. PR title, author, link, the user's last review state and date, reviewed commit → current head (7 characters each).
2. **What changed:** plain-language summary, commits one per line, files with +/- counts. Flag when all new commits are base merges.
3. **How it affects the PR:** does it change behavior, scope or purpose; does it touch what the user originally reviewed; or is it only tests, docs, formatting or a base merge.
4. **Your earlier review:** for changes requested and commented, list the user's earlier points (review body and inline comments) and say for each whether the new commits address it, partly address it, or not. Note author replies and thread resolutions. For each of the user's inline threads, read whether it's outdated (its lines changed) or resolved (the reference's "Unresolved review threads"): an outdated thread is a lead, not proof, so read the new code before calling it addressed. When the user approves or keeps requesting changes, offer to resolve the user's own threads you found addressed, listed first.
5. **Tests:** whether the new commits keep the PR's fix or feature covered (see "Test coverage" in step 8). Check the new commits against "Conventions" (step 8); if the PR discloses AI use, review them as "AI-assisted PRs" says.
6. **Linked issue** and **target branch:** see "Linked issue" and "Target branch and backports" in step 8.
7. **Worth a closer look:** anything risky or surprising, new review comments from others, CI state (see "Pending workflow runs" in step 8), other reviewers' open change requests.

Keep it faster to read than the PR itself.

### 7. A PR: ask, then act

Ask, with options by the user's last review (every case also offers **Show full diff**; don't pre-select):

- Approved or dismissed: **Re-approve**, **Comment: will re-review**, **Withdraw approval** (request changes, or dismiss the user's own review), **Skip**.
- Changes requested: **Approve** (changes addressed), **Keep requesting changes**, **Comment**, **Skip**.
- Commented: **Approve**, **Request changes**, **Comment**, **Skip**.

Before drafting text, apply "Verify before commenting" (in step 8) to each earlier point you're about to call addressed or still open, and to any new finding. Then fetch the PR's reviews and comments again: the user or others may have posted since the summary, e.g. after a `/code-review` hand-off. If the user already posted a review, summarize it and ask what's left instead of drafting a duplicate. Show the exact text and resulting state, get the user's go-ahead, then run. Every review body follows [Conventional Comments](https://conventionalcomments.org): `**<label> (<decorations>):** <subject>`, label in bold. Labels: `praise`, `nitpick`, `suggestion`, `issue`, `todo`, `question`, `thought`, `chore`, `note`. Decorations: `blocking`, `non-blocking`, `if-minor`. One paragraph per point, separated by blank lines: GitHub and GitLab join consecutive lines into one paragraph.

In every review (A or B PRs), post a point that asks for a change to specific code as an inline comment on that line or range of the diff, with the same label and decorations, submitted together with the review (the host's reference, "Actions"). Inline threads show as outdated when the author changes those lines, and can be resolved one by one, so the next review can see what's left. This includes tests to add when the diff has related tests to anchor them to. Keep general points in the review body, such as the overall approach or the title and description. Inline comments can only go on lines the diff shows: a point about other code goes in the body, naming its file and line. Show each inline comment with its file and line in the draft.

- Approve, e.g. `**praise:** My earlier comments are addressed in <new7>.` Warn first if required checks are failing, or another reviewer's change request still blocks the PR.
- Request changes, e.g. `**issue (blocking):** <what's still open>` (the author sees it, and it replaces an earlier approval).
- Comment, e.g. `**note:** New commits landed after my review (<old7>..<new7>). I'll re-review.`
- Dismiss the user's own review, with a reason. If the host refuses, say so and offer request-changes or a comment.

### 8. B PR: summarize and hand off

Read the PR description, file list and commits. Say in a few lines what it does, why it's listed, how big it is, whether it has tests (see "Test coverage"), whether its title follows the project's format (see "PR title"), which issue it closes (see "Linked issue"), missing context links (see "Context and links"), whether it discloses AI use (see "AI-assisted PRs"), whether it follows the conventions (see "Conventions"), what the security review found (see "Security review"), simpler or existing code it could use (see "Simpler or existing code"), whether it targets the default branch (see "Target branch and backports"), CI state, and who else has reviewed. Then ask: **Review it now** (run `/code-review <n>` and the security review, and come back to approve, request changes or comment from that), **Comment**, **Skip**. If the PR is bot-authored or labeled `dependencies`, has failing checks, and the `pr-fix` skill is available (listed as `pr-fix`, or `pr-skills:pr-fix` when installed as a plugin) and supports this host (see its `SKILL.md`), also offer **Fix it** (run it with `<n>`). That skill asks before every commit, push and comment, and only works on PRs opened by a bot or by the user, from a branch in the same repository, so it refuses the PR if it's anyone else's. Never run it unless the user chooses it. Comments follow Conventional Comments, with the text shown first.

#### Test coverage

A PR that changes code should have a test that covers the bug it fixes or the feature it adds. The test doesn't need to be extensive: one test that would fail without the change, or that exercises the new behavior, is enough.

- Use the project's own test setup: find which frameworks it uses (e.g. PHPUnit, Jest, Playwright, pytest) from its test directories, dependencies and CI config, and expect the kind of test the project already writes for similar code.
- Check the PR's changed files for tests that exercise the changed code path, not just any changed test file.
- Don't ask for tests on changes that don't need them: docs, comments, formatting, config or dependency updates with no code change, or a project with no tests at all (then only suggest adding some if the change is risky).
- If a fix or feature has no covering test, include it in the review as `**suggestion:** Add a test that covers <the bug or feature>, e.g. <where, following an existing test>.` Mark it `blocking` only when the project's `AGENTS.md`, contributing docs or PR template requires tests (see "Convention claims" below); otherwise `non-blocking`.

#### Pending workflow runs

In an owned repo, CI runs for PRs from forks (or from first-time contributors) may wait for a maintainer's approval, so the PR shows no results. For every PR you handle, and again after any edit you make that starts new runs (a retitle or description edit), list its runs waiting for approval (the host's reference, "Pending workflow runs"), and ask whether to approve them, naming each workflow. Approved runs execute the PR's code, so first say whether the PR changes CI config, workflows or build scripts, and don't offer approval before the user has seen what the PR changes. Report each run's result once it finishes.

#### PR title

When the project sets a title format (a title check in CI such as Conventional Commits, its contributing docs or `AGENTS.md`, or a release tool that builds the changelog from titles), check the PR's title against it and draft one that follows it, keeping the author's wording where it fits.

- **Owned repo:** offer **Retitle** with the new title shown first, and use the reference's "Retitle a PR" command, instead of asking the author in the review. Do it before posting the review, so the review doesn't ask for it. Say whether a title check re-runs on the edit or still needs a new run.
- **Not owned:** include it in the review as `**chore (blocking):** Could you retitle the PR to `<title>`? <where the format is required>.` Use `non-blocking` when nothing enforces the format.
- With `--mine`, offer **Retitle** for the user's own PRs in any repo.

#### Linked issue

A PR that resolves an issue should say so with the host's closing keyword (e.g. `Closes #<n>` or `Fixes #<n>`; the host's reference, "Closing keywords", gives the form), so merging it closes the issue. Look for the issue in the description, the title and the branch name (e.g. `<n>-<slug>`):

- **Closing reference present:** say which issue it closes.
- **Issue named but no closing keyword:** fine if the description says the PR only partly addresses it, or that follow-ups remain (say so). Otherwise flag "no closing reference for #<n>".
- **No issue found:** say "no linked issue". Fine for small changes; don't ask for one.

When it's flagged, offer **Add closing reference**: in an owned repo, edit the description, adding the line near the top: at the end of its description or summary section (e.g. `## Description`), or as the first line when it has none, never after the testing steps or footer and changing nothing else; show the full new description first and use the reference's "Edit a PR's description" command. Otherwise include it in the review as `**chore:** Add "Closes #<n>" to the description so merging closes the issue.` Check again before merging, when the user asks for a merge.

#### Context and links

A reader of the PR, or of the code years later, should be able to find why it was done this way. Check for the links that context needs:

- **In the description:** the issue it resolves (see "Linked issue"), and for changes that follow or work around something else, a link to it: the upstream issue or release, the documentation or spec it implements, a change record or deprecation notice it follows, a security advisory it fixes.
- **In the code:** a workaround or temporary code has a `@todo` (or the project's equivalent) linking the upstream issue that will make it unnecessary; code that implements a spec, a third-party API's quirk or a non-obvious decision has a comment linking the source; copied code says where it came from.

Report missing links as `**suggestion (non-blocking):** Link <what> so <who> can find <why>.` Suggest the actual link when you found it (e.g. from "Check upstream"). Don't ask for links on self-explanatory changes.

#### AI-assisted PRs

When the description, a commit message or a comment discloses AI use (e.g. an "AI disclosure" section, "Generated with" or "Co-Authored-By" an AI tool), review the code more skeptically, for the whole PR and for an A PR's new commits:

- **Verify every claim:** that the APIs, functions, options and config keys it uses exist in the versions the project supports, that it does what the description says, and that the tests test the change rather than only passing. Apply "Verify before commenting" to each.
- **Simpler or existing code** and **Conventions:** check them as the sections below say, more closely.

Say in the summary that the PR discloses AI use and that it was reviewed this way. A disclosure isn't a problem in itself: never criticize the author for it.

#### Simpler or existing code

In every review, look for code that reimplements something the project, its framework or a dependency already provides (a helper, a service, a base class, a library function), abstractions or options nobody asked for, and code that could be shorter. For a workaround or a copy of upstream code, check whether a newer upstream release already has the fix or API (see "Check upstream" in step 9). Name the existing API or release in the suggestion, as `**suggestion (non-blocking):**`, and say what you checked (e.g. the helper's signature at the PR's base).

#### Security review

Review every PR's changes for security problems: injection (SQL, shell, template), cross-site scripting and missing output escaping, missing access checks, CSRF on state-changing routes, unsafe deserialization or file handling, secrets in code or config, and dependency changes with known advisories (the host's reference, "Security"). Use the agent's security review command or skill if it has one, run in the review checkout (see "Review checkout"), otherwise review the diff yourself. Verify each finding as "Verify before commenting" says.

- A problem the PR **introduces** in unreleased code is an ordinary review finding: comment on the PR, as `**issue (blocking):**`.
- A problem in code that's **already released** (the PR touches it, or reveals it) is a vulnerability: follow the Security rule in "Rules", and don't describe it in the PR.

Say in the summary what was reviewed and that nothing was found, if so.

#### Review checkout

To verify findings locally (read files in context, run `grep`, `git apply --check`, the project's linters or tests), check the PR's head out into a scratch worktree outside the repository, never in the user's working copy: fetch the head (the host's reference, "Check out a PR"), then `git worktree add --detach <scratch dir> <sha>`. Remove it with `git worktree remove` when the item is done.

Reading and static checks are fine. Running anything from the PR (tests, build scripts, Composer or npm scripts, git hooks) runs its author's code: in a repo the user doesn't own, or from an author outside the project, ask first and say so, and prefer the project's isolated environment (e.g. its DDEV or Docker setup) over the host.

#### Conventions

Check every reviewed PR's code against two sources, and report what doesn't follow them, citing the rule and where it's written:

1. **The project's conventions:** its instruction files and docs (`AGENTS.md`, `CLAUDE.md`, contributing docs), linter and coding-standard config, and how its existing code does the same thing.
2. **The user's global instruction files.** Rules only these files have are the user's preferences: word them as such (see "Convention claims" below).

How they combine depends on ownership:

- **Owned repo:** both apply. The user sets the project's direction, so their global rules can be raised like project rules, though still worded as their preference when the repo doesn't write them down.
- **Not owned:** the project's conventions come first. Raise a global rule only where the project has no convention of its own on that point, as a non-blocking suggestion, and drop it where it conflicts with what the project does.

#### Target branch and backports

Changes land on the default branch first, then go to older supported branches. When a PR targets another branch (an older release branch, or a stale one):

1. **Check it still applies** to the default branch, read-only: the changed files and code paths exist there, the bug or missing feature is still present (the fix isn't already in), and the diff applies (`git apply --check` of the PR's diff onto the default branch, in a scratch worktree outside the repository). Say what you checked.
2. **Still applies:** offer **Retarget to <default branch>**: change the PR's base, then rebase it (the reference's "Retarget" and "Rebase" commands), and say the pipeline will now test it there. Both rewrite or change someone else's PR, so show what will happen and ask first; a rebase with conflicts goes back to the author as a comment. In a repo the user doesn't own, suggest it in the review instead (`**suggestion:** Could this target <default branch>? It still applies there.`).
3. **Doesn't apply** (already fixed, or the code is gone): say so, and offer a comment asking the author whether it's still needed on the old branch only.

After a bug fix merges into the default branch (when the user asked for the merge), in an owned repo, offer **Cherry-pick to older branches**: list the other supported branches (the reference's "Supported branches", minus any the profile's `exclude.branches` matches), check the fix applies to each, then cherry-pick it there keeping the original author, with a `(cherry picked from commit <sha>)` line and the branch's commit message convention. Ask before each push. Features don't get cherry-picked unless the user asks.

#### Verify before commenting

Review findings (from `/code-review` or your own reading) are often wrong or unconfirmed, and the user wants to post with certainty. Before drafting, sort each finding into:

- **Cheap to verify:** a claim you can settle in a minute without changing the repo, such as reading the file at the PR's head, reading the framework's or a dependency's code, a `grep` for usages, comparing config with what the code would calculate in memory, or running a small read-only script or an existing test against the project's tooling. Offer to run these (one option per group of checks, plus "skip"), and run them before drafting. Use a scratch directory outside the repository, and delete the scripts afterwards.
- **Not cheap:** needs a browser, a deploy, or a long test run. Don't run it unasked. Draft it as a question to the author, not as a statement.
- **Convention claims:** a finding may cite a rule ("the project requires…") that comes from the reviewer's own instruction files, such as a global `AGENTS.md` or `CLAUDE.md` in the home directory, and not from the repository. Before putting a convention in a comment, find it in the repo (its `AGENTS.md`, `docs/`, linter or coding-standard config, or existing code that follows it). If it isn't there, drop it, or phrase it as the user's own preference ("I'd prefer…") and tell the user it's a personal rule.

If a finding is about a dependency's behavior, or the PR works around one, apply "Check upstream" (in step 9) and cite the upstream issue in the comment, or suggest a `@todo` linking it.

In the draft, say what you checked for each point, and word anything you didn't check as a question. Drop findings that a check contradicts, and tell the user why. In your message with the draft, list what was verified and how, and what wasn't.

### 9. Issues: summarize, ask, act

Read the issue, its comments and the PRs linked to it. Show:

1. Issue title, author, link, labels, assignees, and for A the date of the user's last comment.
2. **What's reported:** the problem or request in a few lines, and what the reporter expects.
3. **Since your last comment** (A): each new comment, one line each, with its author.
4. **Linked PRs:** number, state and whether they're in this triage list.
5. **Worth a closer look:** whether it looks like a bug in this project, in a dependency or upstream, a duplicate, a support question or a feature request, and what you'd check to be sure.

Then ask: **Investigate** (read the code, apply "Verify before commenting" and, when the cause may be in a dependency, "Check upstream"; then come back to these options), **Comment**, **Comment and close** (e.g. a duplicate, an upstream bug, or answered), **Skip**, plus any options the host's reference adds (such as setting an issue's status). Show the exact text (and the close reason or new status) and get the user's go-ahead first. Issue replies answer the reporter in plain prose, not Conventional Comments. Before posting, fetch the comments again, in case someone replied in the meantime.

#### Check upstream

When an issue, or a PR finding or workaround, points at code outside this project (a framework, a module, a library or a tool), look for an existing upstream issue before drafting:

1. **Find the upstream and its tracker:** the package that owns the code path (from a stack trace, a dependency directory such as `vendor/<package>` or `node_modules/<package>`, or the class's namespace), then its tracker: from the repo's "Project issue tracker" file ("Upstream trackers") if it lists the package, otherwise from the package's `composer.json` or `package.json` (`support.issues`, `bugs`, `homepage`, `repository`). Packages from drupal.org (Drupal core and `drupal/*`) use `references/drupalorg.md` (and `references/gitlab.md`, which it builds on), whatever this repo's host is; `drupalorg.md` says how to name them.
2. **Search it** with the "Upstream trackers" commands for that package if the file gives any, otherwise with the commands in the reference for that tracker's host, which may differ from this repo's host: `references/github.md`, `references/gitlab.md` or `references/drupalorg.md` ("Searching upstream"). For the repo's own tracker, use the file's "Searching" section if it has one. For other trackers (Jira, Bugzilla, a forum), search the tracker's site if you can fetch web pages; otherwise give the user a search link with the keywords, and say you couldn't search it. Try a few short keyword sets (the error message, the class or function, the behavior), open and closed issues, and read the likely matches.
3. **Report** each candidate with its link, status, and how well it matches: **same cause** (its description or patch covers the code path you traced), **related**, or **not it**. Say what you searched for, and if nothing matched.

Then offer, as separate choices with the exact text shown first:

- **Comment here** linking the upstream issue, saying what you traced.
- **Comment upstream**, when this report adds something the upstream issue lacks (another way to reproduce it, an affected use case, a version). Write it for the upstream project's readers, without this project's private details. If the reference says comments can't be posted there, give the user the text and the link.
- **Close here** only when confirmed: the upstream issue has the same cause, you verified it (reproduced it, or traced the code path into the upstream code the issue describes), and nothing needs to change in this project. Otherwise leave it open (or use the host's postponed status, if it has one) and say in the comment what would confirm it. A workaround this project could add while upstream is open is a reason to keep it open, with a `@todo` linking the upstream issue in any code.

If no upstream issue exists but you're confident the bug is upstream, draft a new upstream issue (title, steps to reproduce, expected and actual behavior, versions) for the user to file.

After each action, report the result and the item's URL. At the end, list what was approved, changes requested, commented on, closed, handed off and skipped.

### Your own PRs (`--mine`)

Fetch the user's own open PRs, including drafts. For each, count its unresolved review threads and read its CI state. Show one table, most recently updated first: number, title, last updated, size, and what it's waiting on, all that apply:

- **Changes requested** by whom (the overall review decision, and the reviewers whose latest review requests changes).
- **N unresolved threads**.
- **CI failing**, with the failed checks.
- **N remaining tasks** in the description: unchecked task list items (`- [ ]`) and items under a heading such as "Remaining tasks" or "TODO".
- **Waiting for review** from the requested users and teams, or **no reviewer** if there's none and no approval.
- **Approved**, when nothing above applies. Say it's ready to merge, but never merge it.
- **Draft**.

Ask which PRs to handle now (multi-select, with "none"). For each: list the open feedback (reviewer, link, one line each, marking comments from outside the repo's collaborators or from bots), the failed checks, and the remaining tasks, saying for each task whether it looks needed to finish the PR and whether it's a code change. If there's feedback, a failing check or a remaining code task, and the `pr-fix` skill is available and supports this host, offer **Fix it** (run it with `<n>`), **Show the threads** in full, and **Skip**. Never run `pr-fix` unless the user chooses it. Without `pr-fix`, summarize and skip.

### Your own issues (`--mine --issues`)

Fetch the user's own open issues, and keep those where someone else commented after the user's latest comment (or after the issue was opened, if the user hasn't commented). Count the others as "waiting on others". Show one table, most recently updated first: number, title, last updated, who replied and when. Ask which to handle now, then handle each as in step 9 (for **Comment and close**, e.g. because it's resolved).

## Project issue tracker

A project can tell the skill about issue trackers in `<repo root>/.claude/project-triage-issues.md`, committed with the project: where its own issues are, if not on its code host (e.g. in Jira), and how to search its dependencies' trackers. It's a reference like the host ones, with these sections, all optional. "Fetching issues" is what makes the skill use the file instead of the host for the project's own issues; without it, the file only adds upstream searches.

- **Requirements:** the CLI or connector it uses, and how to log in.
- **Who:** how to find the user's account on the tracker (`$ME` for issues).
- **Ownership:** whether the user counts as owning the project's issues (e.g. a Jira project lead or component owner). Without it, use the repo's ownership.
- **Fetching issues:** open issues for an owned project (all from others) and for a not-owned one (assigned to the user), with author, assignees, comments with authors and dates, and last updated time.
- **Comments and actions:** how to comment, change status or close.
- **Searching:** how to search the project's own tracker.
- **Upstream trackers:** for dependencies whose trackers the skill wouldn't find or can't search on its own, such as a vendor's Jira, a private package's tracker, a forum, or a second place to look (a library's mailing list archive, or a vendor's security contact): which packages, where their issues are, and the commands or URLs to search them. Used by "Check upstream" before the package's own metadata.

See `issues.example.md` next to this file. If the file names a tool that isn't available, say so and skip issues; don't fall back to the code host's issues unless the file says to. Writes follow the same rules as everywhere else: exact text first, and the user's go-ahead for each one.

## Profile

A Markdown file with YAML front matter. Two optional files; the repo file wins:

1. `~/.config/project-triage/profile.md`: the user's defaults for every repo.
2. `<repo root>/.claude/project-triage.md`: overrides for one repo.

Merge: mappings merge key by key, and a list in the repo file replaces the same list from the user file. The Markdown body of the repo file replaces the user file's body if it's non-empty. Front matter keys (all optional):

```yaml
match:
  paths: ["src/migrations/**"]    # any changed file matches
  labels: [ci]                    # exact, or globs: ["area-*"]
  keywords: [migrate]             # any form of the word in the title
  codeowners: true                # CODEOWNERS entries naming me or my teams
exclude:
  authors: [renovate[bot], dependabot[bot]]   # PRs and issues
  labels: [dependencies, "v7.x-*"]            # PRs and issues; globs allowed
  branches: ["7.x-*"]             # PRs only: base (target) branch, globs allowed
  paths: ["**/*.lock"]            # PRs only, if ALL changed files match
always_show_requested: true       # requested reviews ignore exclude (default true)
```

`match` applies to PRs in repos the user doesn't own; in owned repos every PR and issue is listed unless `exclude` matches. The body describes the user's skill set in plain language (what they know well, and what they're less involved in). It is used for "judgment call" matches, and teammates can read it. See `profile.example.md` next to this file.

If neither file exists, say so, ask the user 3–4 questions (areas they work on, paths or labels to include or exclude, whether to hide bot PRs), and offer to write a profile after showing it. To suggest paths, look at where they have reviewed or authored before. Don't write any profile file without the user's go-ahead.
