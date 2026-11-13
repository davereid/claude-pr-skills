# GitLab

Host details for `project-triage` on GitLab (gitlab.com or self-managed), using the `glab` CLI and its `glab api` command for the REST API (`/api/v4`). For drupal.org's GitLab, also read `drupalorg.md`, which changes some of this.

GitLab calls PRs merge requests (MRs) and numbers them per project (`iid`). In API paths, `:id` is the project path URL-encoded (`group%2Fsub%2Fproject`) or its numeric ID.

## Who and where

- Repo: the full project path from the remote URL, which can include subgroups (`group/sub/project`); drop a trailing `.git`. Pass `-R https://<host>/<path>` to `glab` commands and `--hostname <host>` to `glab api`, so commands don't depend on the working directory.
- `ME=$(glab api --hostname <host> user | jq -r .username)`; keep its `id` too.
- If `glab` isn't logged in to the host (`glab auth status --hostname <host>` fails), say so and suggest `glab auth login --hostname <host>`. If the remote's host differs from the API host (an SSH alias), `glab` inside the checkout needs `glab config set api_host <api host> --host <remote host>`.
- Teams: GitLab has no team review requests; reviewers are always users. The user's groups (for CODEOWNERS): `glab api --hostname <host> "groups?min_access_level=10&per_page=100" | jq -r '.[].full_path'`.

## Ownership

A project is owned when any of these is true:

1. It's in the user's personal namespace: `glab api --hostname <host> "projects/:id"` has `namespace.kind` `user` and `namespace.path` `$ME`.
2. The user's access level is Maintainer (40) or Owner (50): the higher of `permissions.project_access.access_level` and `permissions.group_access.access_level` in the same response.
3. The user is a direct member of the project with any role, not through a group: `glab api --hostname <host> "projects/:id/members/<user id>"` succeeds (the `members/all` endpoint would include inherited members; don't use it). A 404 means not a direct member.

## How GitLab maps to the skill's terms

- **Draft:** `draft` is true.
- **Requested reviewers:** `reviewers`. Each reviewer's state comes from `projects/:id/merge_requests/<iid>/reviewers` (`state`: `unreviewed`, `reviewed`, `requested_changes`, `approved`, `unapproved`).
- **The user's latest review:** their latest note on the MR, including the system notes GitLab adds when they approve, unapprove or request changes (`projects/:id/merge_requests/<iid>/notes?sort=desc&per_page=100`, `author.username` = `$ME`). Its state: the reviewer `state` above if the user is a reviewer; otherwise approved if they're in `approved_by` (`projects/:id/merge_requests/<iid>/approvals`), else commented.
- **Reviewed commit:** the `head_commit_sha` of the newest MR version created before that note (`projects/:id/merge_requests/<iid>/versions`, newest first). A diff note's `position.head_sha` gives it directly.
- **Re-requested:** the user's reviewer state is `unreviewed` again although they have a review.
- **Head commit:** `sha`. **Base:** `target_branch`. **Last updated:** `updated_at`.
- **Bot author:** a username like `project_<n>_bot…` or `group_<n>_bot…` (access-token bots), or one that names a bot (`renovate-bot`, `dependabot`). The user API's `bot` field confirms it.

## Fetching MRs

```bash
glab api --hostname <host> "projects/:id/merge_requests?state=opened&per_page=100&order_by=updated_at"
```

Changed files and +/- per MR: `projects/:id/merge_requests/<iid>/diffs?per_page=100` (each entry has `new_path`; count `+`/`-` lines in `diff`).

## Fetching issues

```bash
glab api --hostname <host> "projects/:id/issues?state=opened&per_page=100&order_by=updated_at"
```

In a project the user doesn't own, add `&assignee_username=$ME`. With `--mine`, use `&author_username=$ME` instead. If the project has issues turned off (`issues_enabled` false in the project), say so and skip issues.

Comments: `projects/:id/issues/<iid>/notes?sort=asc&per_page=100`; drop system notes (`system` true). Linked MRs: `projects/:id/issues/<iid>/related_merge_requests` and `.../closed_by`.

## Searching every project (`--all`)

- MRs requesting the user's review: `merge_requests?scope=all&state=opened&reviewer_username=$ME&per_page=100`. MRs they approved: `merge_requests?scope=all&state=opened&approved_by_usernames[]=$ME`. With `--mine`: `merge_requests?scope=all&state=opened&author_username=$ME`.
- Items the user commented on recently (to find MRs and issues they reviewed without being a reviewer): `events?action=commented&after=<date 90 days ago>&per_page=100`, then each note's `noteable_type` and `noteable_iid` with the event's `project_id`. Say the window is 90 days.
- Assigned issues: `issues?scope=assigned_to_me&state=opened&per_page=100`. With `--mine --issues`: `issues?scope=created_by_me&state=opened`.
- Owned projects: `projects?min_access_level=40&archived=false&per_page=100` and `users/<user id>/projects?archived=false&per_page=100`, then fetch each one's open MRs and issues as above. Say how many projects that is, and ask first if it's more than about 20.
- shortcut: projects where the user is a direct member below Maintainer aren't listed; say so, and suggest triaging those one at a time.

## Searching upstream

`glab api --hostname <host> "projects/:id/issues?state=all&per_page=30&search=<url-encoded words>"` (searches titles and descriptions). Public projects can also be read without a login: `curl -sS -G "https://<host>/api/v4/projects/:id/issues" --data-urlencode state=all --data-urlencode "search=<words>"`.

## Profile suggestions

MRs the user reviewed or authored: `merge_requests?scope=all&reviewer_username=$ME&per_page=100` and `author_username=$ME`, then their files.

## CODEOWNERS

`CODEOWNERS`, `docs/CODEOWNERS` or `.gitlab/CODEOWNERS` (the first found wins), read at the MR's target branch: `glab api --hostname <host> "projects/:id/repository/files/<url-encoded path>/raw?ref=<target_branch>"`. GitLab's file can have `[Section]` headers: the last matching pattern wins within each section, and every section applies. Owners can be `@user` or `@group/subgroup`.

## An MR the user reviewed

- Compare: `projects/:id/repository/compare?from=<reviewedSha>&to=<headSha>&straight=true`. The MR's own commits: `projects/:id/merge_requests/<iid>/commits`.
- CI: see "Reading CI results".
- Comments and reviews since the user's review: the MR's notes (above), and the user's own diff notes in `projects/:id/merge_requests/<iid>/discussions?per_page=100`.

## An MR the user hasn't reviewed

`glab mr view <iid> -R <repo> -F json` (description, author, labels), its diffs and commits. File at the head: `projects/:id/repository/files/<path>/raw?ref=<sha>`.

## Unresolved threads

`projects/:id/merge_requests/<iid>/discussions?per_page=100`: count discussions whose notes are `resolvable` and not `resolved`. A diff note is outdated when its `position.head_sha` differs from the MR's head and the lines changed (the MR's diff view shows it as such). Resolve one: `glab api --hostname <host> -X PUT "projects/:id/merge_requests/<iid>/discussions/<discussion id>?resolved=true"`.

Your own MRs: `projects/:id/merge_requests?state=opened&author_username=$ME&per_page=100`, with `detailed_merge_status` and the reviewer states.

## Actions

- Approve: `glab mr approve <iid> -R <repo>`, then the comment as a note.
- Withdraw an approval: `glab mr revoke <iid> -R <repo>`.
- Request changes: post the blocking comment as a note. Setting GitLab's "Requested changes" reviewer state through the API isn't verified: tell the user to submit the review with **Request changes** in the MR's UI if they want that state.
- Comment on an MR: `glab mr note <iid> -R <repo> -m "<text>"`
- Inline comment on the diff: take `base_commit_sha`, `start_commit_sha` and `head_commit_sha` from the newest entry in `projects/:id/merge_requests/<iid>/versions`, then `glab api --hostname <host> -X POST "projects/:id/merge_requests/<iid>/discussions" -f body="<text>" -f "position[position_type]=text" -f "position[base_sha]=<base>" -f "position[start_sha]=<start>" -f "position[head_sha]=<head>" -f "position[old_path]=<path>" -f "position[new_path]=<path>" -f "position[new_line]=<line>"` (`position[old_line]` instead for a removed line). Post one per point, then the general points as a note. Not verified: check the note shows on the diff line afterwards, and if it doesn't, post it as a note naming the file and line.
- Comment on an issue: `glab issue note <iid> -R <repo> -m "<text>"`
- Close an issue: `glab issue close <iid> -R <repo>` after the comment.
- Edit an MR's description: `glab mr update <iid> -R <repo> --description-file <file>`, after all edits to the file have succeeded.
- Retarget: `glab mr update <iid> -R <repo> --target-branch <branch>`.
- Rebase: `glab api --hostname <host> -X PUT "projects/:id/merge_requests/<iid>/rebase"`, then check `merge_requests/<iid>?include_rebase_in_progress=true` until `rebase_in_progress` is false and `merge_error` is null. Needs push access to the source branch; GitLab refuses it when `has_conflicts` is true.

## Supported branches

The default branch (`default_branch` in `projects/:id`), plus release branches with recent releases (`projects/:id/releases` or tags), or named in the project's docs. Ask the user if it's unclear.

## Closing keywords

`Closes #<iid>` or `Fixes #<iid>` (a colon after the keyword is allowed) in the MR description closes the issue when the MR merges into the default branch, unless the project turned it off; a full issue URL also works. Merging into another branch doesn't close it.

## Security

- Private reporting: the project's `SECURITY.md`. Without one, a confidential issue (only project members can see it) is GitLab's usual channel: tell the user to create it with **This issue is confidential** checked, or `glab issue create -R <repo> --confidential`, after showing the text.
- If the reference for a GitLab-based host gives its own process (as `drupalorg.md` does), use that instead.

## GitLab token permissions

- Read-only triage: a personal access token with `read_api` (plus `read_user`).
- Commenting, approving and closing: `api`.
- The user's role decides what they can do: approving needs a role the project's approval rules allow, and closing others' issues needs Reporter or higher.
- If a read call fails with a 401, 403 or 404 on a project the user can open, suggest checking the token's scopes before assuming the data doesn't exist.

## Reading CI results

The MR's `head_pipeline` (from `projects/:id/merge_requests/<iid>`) has `status`; `failed` is a failure. Failed jobs: `projects/:id/pipelines/<pipeline id>/jobs?scope[]=failed`. A job with `allow_failure` true doesn't block the MR: mention it, but don't call the MR failing for it. A job's log: `glab ci trace <job id> -R <repo>`.
