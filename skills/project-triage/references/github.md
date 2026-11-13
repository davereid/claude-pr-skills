# GitHub and GitHub Enterprise

Host details for `project-triage` on GitHub (`github.com`) and GitHub Enterprise, using the `gh` CLI. Don't hardcode a host.

## Who and where

- Repo: the `owner/repo` path from the remote URL (drop a trailing `.git`). Pass `-R <host>/<owner>/<repo>` to every `gh` command (just `owner/repo` on `github.com`), so commands don't depend on the working directory.
- `ME=$(gh api --hostname <host> user -q .login)`. Logins can differ between hosts, so look it up per host.
- If `gh` isn't logged in to the host (`gh auth status --hostname <host>` fails), say so and suggest `gh auth login --hostname <host>`.
- Teams: `gh api user/teams --jq '.[] | "\(.organization.login)/\(.slug)"'`.
- A single number: `gh pr view <n> -R <repo>` succeeds for a PR; otherwise try `gh issue view <n> -R <repo>`.

## Ownership

A repo is owned when any of these is true:

1. Its owner is `$ME`, or the user's permission is admin or maintain: `gh repo view <repo> --json owner,viewerPermission` (`owner.login`; `viewerPermission` `ADMIN` or `MAINTAIN`).
2. The user is a direct collaborator: added to the repo itself, with any permission, not through an organization team or the organization's default access. `gh api --paginate "repos/<repo>/collaborators?affiliation=direct&per_page=100" -q '.[].login'` lists `$ME`. Listing collaborators needs push access, so a 403 or 404 there means not owned.

Write access through an organization team doesn't count.

## Fetching PRs

```bash
gh pr list -R <repo> --state open --limit 100 \
  --json number,title,url,author,labels,isDraft,reviewRequests,reviews,headRefOid,baseRefName,files,updatedAt
```

Age from `updatedAt` in jq: `((now - (.updatedAt | fromdateiso8601)) / 86400 | floor)` days.

A review's `commit.oid` is the reviewed commit; its state is `APPROVED`, `CHANGES_REQUESTED`, `DISMISSED` or `COMMENTED`. A bot author is a login ending in `[bot]` or starting with `app/`.

## Fetching issues

```bash
gh issue list -R <repo> --state open --limit 100 \
  --json number,title,url,author,labels,assignees,comments,updatedAt
```

In a repo the user doesn't own, add `--assignee @me`. With `--mine`, use `--author @me` instead. `gh issue list` doesn't return PRs. Each comment has `author.login` and `createdAt`.

For one issue: `gh issue view <n> -R <repo> --json title,body,author,labels,assignees,comments,url,closedByPullRequestsReferences` (the last field lists PRs linked to close it).

## Searching every repo (`--all`)

- PRs: `gh search prs --state=open --review-requested=@me` and `--reviewed-by=@me`. With `--mine`: `--author=@me`.
- Owned repos, in two parts, dropping the user's own items:
  - Under the user's account: `gh search prs --state=open --owner=@me` and `gh search issues --state=open --owner=@me`.
  - Repos the user was added to directly: `gh api --paginate "user/repos?affiliation=collaborator&per_page=100" -q '.[] | select((.archived or .fork) | not) | .full_name'`, then fetch each one's open PRs and issues as in "Fetching PRs" and "Fetching issues". Say how many repos that is, and ask first if it's more than about 20.
- Assigned issues: `gh search issues --state=open --assignee=@me`. With `--mine --issues`: `--author=@me`.
- For searches, add `--json number,title,url,repository,author,labels,updatedAt` and `--limit 100`.
- shortcut: org repos the user administers only through a team aren't listed by `affiliation=collaborator`; say so in the output, and suggest triaging those repos one at a time.

## Searching upstream

`gh search issues --repo <owner>/<repo> --state=all --limit 30 --json number,title,state,url,updatedAt -- "<words>"` (searches titles, bodies and comments). Add `--match title` to narrow it. Works for any public repo, not only this one.

## Profile suggestions

Where the user has reviewed or authored before: `gh search prs --reviewed-by=@me --json repository,title,url --limit 100` (and `--author=@me`), then look at those PRs' files.

## CODEOWNERS

`.github/CODEOWNERS`, `CODEOWNERS` or `docs/CODEOWNERS`, read at the PR's base: `gh api repos/<repo>/contents/<path>?ref=<baseRefName> -q .content | base64 -d`.

## A PR the user reviewed

```bash
gh api repos/<repo>/compare/<reviewedSha>...<headSha>
gh pr checks <n> -R <repo>   # or the fallback in "Reading CI results"
gh pr view <n> -R <repo> --json comments,reviews   # anything after the user's review
gh api repos/<repo>/pulls/<n>/reviews/<review-id>/comments   # the user's own inline comments
```

PR's own changes: `gh pr view <n> -R <repo> --json files,commits`. Re-fetch before drafting: `gh pr view <n> -R <repo> --json reviews,comments`.

## A PR the user hasn't reviewed

`gh pr view <n> -R <repo> --json body,files,commits`. File at the PR's head: `gh api repos/<repo>/contents/<path>?ref=<sha>`.

## Check out a PR

`git fetch origin pull/<n>/head` (works for PRs from forks too), then use `FETCH_HEAD` or the PR's `headRefOid`.

## Unresolved review threads

Use the `reviewThreads` query from `pr-fix`'s "Review feedback" if that skill is installed (only `isResolved` is needed), or:

```bash
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{id isResolved isOutdated path line comments(first:1){nodes{author{login} body}}}}}}}' -F o=<owner> -F r=<name> -F n=<n>
```

The user's threads are those whose first comment's author is `$ME`. Resolve one: `gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -F id=<thread id>`.

Your own PRs: `gh pr list -R <repo> --state open --author @me --limit 100 --json number,title,url,body,isDraft,reviewDecision,reviewRequests,reviews,headRefOid,updatedAt`.

## Out-of-date branch

Commits the base has that the PR's branch doesn't: `gh api repos/<repo>/compare/<baseRefName>...<headRefOid> -q .behind_by` (for a fork PR, `<owner>:<headRefName>` in place of the SHA if the SHA isn't found). Conflicts: `gh pr view <n> -R <repo> --json mergeable` is `CONFLICTING`; `UNKNOWN` means GitHub hasn't worked it out yet (often a conflict), so say "may conflict".

## Actions

- Approve: `gh pr review <n> -R <repo> --approve --body "<text>"`
- Request changes: `gh pr review <n> -R <repo> --request-changes --body "<text>"`
- Review with inline comments: `gh pr review` can't add them. Write the review to a JSON file and post it with `gh api -X POST repos/<repo>/pulls/<n>/reviews --input <file>`:
  ```json
  {"commit_id": "<headRefOid>", "event": "REQUEST_CHANGES", "body": "<general points>",
   "comments": [{"path": "src/Foo.php", "line": 51, "side": "RIGHT", "body": "**issue (blocking):** …"}]}
  ```
  `event` is `APPROVE`, `REQUEST_CHANGES` or `COMMENT`. `line` is the line number in the file at `commit_id` (`side: "LEFT"` for a removed line, numbered in the base); add `start_line` for a range. A line outside the diff fails the whole request with a 422: move that point to the body.
- Comment on a PR: `gh pr comment <n> -R <repo> --body "<text>"`
- Dismiss the user's own review: `gh api -X PUT repos/<repo>/pulls/<n>/reviews/<review-id>/dismissals -f message="<reason>"`. Not verified to work on the user's own reviews: if it fails, say so and offer request-changes or a comment.
- Comment on an issue: `gh issue comment <n> -R <repo> --body "<text>"`
- Close an issue: `gh issue close <n> -R <repo> --reason "<completed|not planned>"` after the comment.
- Edit a PR's description: `gh pr edit <n> -R <repo> --body-file <file>`, after all edits to the file have succeeded.
- Retarget: `gh pr edit <n> -R <repo> --base <branch>`.
- Retitle a PR: `gh pr edit <n> -R <repo> --title "<title>"`. A title check workflow re-runs only if it triggers on `pull_request` `edited`. On PRs from forks, the new run may wait for approval (see "Pending workflow runs"). An edit to the description also triggers `edited` runs, so retitle before editing the description.
- Update branch (the PR's **Update branch** button): `gh pr update-branch <n> -R <repo>` merges the base into the PR's branch on GitHub, with no force-push. Needs push access to the head branch. The new head can take a few seconds to show in `gh pr view`.
- Rebase: `gh pr update-branch <n> -R <repo> --rebase`. Needs push access to the head branch (for a fork, "Allow edits from maintainers").

## Supported branches

The default branch (`gh repo view <repo> --json defaultBranchRef`), plus release branches with a recent release (`gh release list -R <repo>`, matched to branches by version) or named in the project's docs (`SECURITY.md`'s supported versions). Ask the user if it's unclear.

## Closing keywords

`Closes #<n>`, `Fixes #<n>` or `Resolves #<n>` in the PR description closes the issue when the PR merges into the default branch; `owner/repo#<n>` for another repo. Merging into another branch doesn't close it.

## Security

- Private reporting: the repo's `SECURITY.md` (root, `.github/` or `docs/`). If the repo has private vulnerability reporting turned on (`gh api repos/<repo>/private-vulnerability-reporting -q .enabled`), it's at `https://github.com/<repo>/security/advisories/new`.
- Published advisories for a package: `gh api "advisories?ecosystem=<composer|npm|pip|…>&affects=<package>"` (GitHub's advisory database), and the repo's own at `https://github.com/<repo>/security/advisories`.

## GitHub token permissions

The `gh` token only needs read access to triage. Write access is needed only for the actions above, which always wait for the user's go-ahead.

- **Classic token:** `repo` (read and write; there's no read-only scope for private repos) and `read:org` (for `gh api user/teams`).
- **Fine-grained token** (repository permissions, on the repos to triage; Metadata read is added automatically and isn't listed):
  - Pull requests: read, for listing, reviews, comments and files. Pull requests: write for approving, requesting changes, commenting and dismissing.
  - Issues: read, for listing issues and their comments. Issues: write for commenting on and closing issues.
  - Contents: read, for the compare API and `CODEOWNERS`.
  - Actions: read and Commit statuses: read, for CI results. Fine-grained tokens can't have Checks: read, so `gh pr checks` fails with them; use the fallback in "Reading CI results".
  - `--all` searches only repos the token can read.
- Team membership (`gh api user/teams`) may be unavailable to a fine-grained token. If it fails, the skill falls back to direct review requests.
- If a read call fails with a 403 or 404 on a repo the user can open, suggest checking the token's permissions and repo access before assuming the data doesn't exist.

## Pending workflow runs

`gh run list -R <repo> --branch <headRefName> --json databaseId,workflowName,event,conclusion,headSha` and keep runs with `conclusion` `action_required` (for a fork PR, `--branch` is the fork's branch name, so also match `headSha` to the PR's head). Approve one: `gh api -X POST repos/<repo>/actions/runs/<id>/approve`. Runs of the same workflow that a newer run superseded show as `cancelled`; only the newest counts.

## Reading CI results

Use `gh pr checks <n> -R <repo>`. If it fails with "Resource not accessible by personal access token", the token is fine-grained and has no Checks: read. Fall back to:

- `gh run list -R <repo> --commit <headRefOid> --json databaseId,workflowName,event,status,conclusion` for GitHub Actions. For each workflow and event, only the newest run (highest `databaseId`) counts. It failed if its `conclusion` is `failure`, `timed_out` or `startup_failure`.
- `gh api repos/<repo>/commits/<headRefOid>/status` for commit statuses from CI outside Actions (e.g. Tugboat). A `failure` or `error` state is a failure. Ignore the combined `state` when `statuses` is empty: it's always `pending` then.

Check runs from other GitHub Apps can't be read this way. When using the fallback, say that only Actions runs and commit statuses were checked.
