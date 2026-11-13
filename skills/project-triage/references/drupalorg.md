# drupal.org

Host details for `project-triage` on drupal.org projects. Their code and merge requests are on drupal.org's GitLab (`git.drupalcode.org`), so use `gitlab.md` for everything, with the changes below. Also uses the [drupalorg CLI](https://github.com/mglaman/drupalorg-cli) (`drupalorg`) where it covers something.

## Who and where

- The remote is either SSH (`git@git.drupal.org:project/<name>.git`, usual for maintainers) or HTTPS (`https://git.drupalcode.org/project/<name>.git`, usual for everyone else). Either way the API host is `git.drupalcode.org`: always use `--hostname git.drupalcode.org` and `-R https://git.drupalcode.org/project/<name>`.
- The project path is `project/<name>` (`:id` is `project%2F<name>`). If the remote is an issue fork (`issue/<name>-<nid>`), triage `project/<name>`, where its MRs and issues live.
- If `glab` run inside a checkout with the SSH remote says no remote points to a known GitLab host, it needs `glab config set api_host git.drupalcode.org --host git.drupal.org`. Passing `-R` and `--hostname` as above avoids that.
- `$ME` is the user's GitLab username on `git.drupalcode.org`, which follows their drupal.org username.

## Ownership

Owned when the user's access level on `project/<name>` is Maintainer (40) or higher: drupal.org gives that to the project's maintainers with write access to the repository. Personal namespaces and direct members below Maintainer don't apply. Maintainers without repository access don't get it, so they don't count: say so if the user expected the project to be theirs.

## Two kinds of issue tracker

Check the project's `issues_enabled` (`glab api --hostname git.drupalcode.org "projects/project%2F<name>"`):

- **true:** the project's issues moved to GitLab work items (`https://git.drupalcode.org/project/<name>/-/work_items/<nid>`). The work item's `iid` is the drupal.org issue number (nid). Use `gitlab.md`'s issue commands.
- **false:** issues are still in drupal.org's issue queue (`https://www.drupal.org/project/issues/<name>`), as for Drupal core. The GitLab issue API returns nothing for them. Read them with `drupalorg` instead (below). Writing isn't possible from here.

## Issue status

drupal.org issues have a status, which says whose turn it is. Show it in the issue tables, and use it on top of the comment-based A/B rules:

- Work items carry it as a scoped label (`state::needsReview`, `state::rtbc`, `state::needsWork`, `state::postponed`, `state::toBePorted`, …; no `state::` label means _Active_). Category and priority are `category::…` and `priority::…` labels.
- Issue-queue projects: `field_issue_status` numbers. Open ones: 1 _Active_, 8 _Needs review_, 13 _Needs work_, 14 _RTBC_, 4 _Postponed_, 16 _Postponed (maintainer needs more info)_, 15 _Patch (to be ported)_.

In an owned project, _Needs review_ and _RTBC_ issues are listed as B even if the user has commented, when there's no comment from the user since the status changed: they're waiting on the maintainer. _Needs work_ and _Postponed_ issues whose latest comment is the user's stay hidden.

## Migrated issues

Issues migrated from drupal.org's issue queue to work items are authored by `drupalbot` on GitLab. Find who really opened them, and when, before classifying:

- **Reporter:** the description's `Reported by: [<name>](https://www.drupal.org/user/<uid>)` line. Use it as the issue's author for skipping the user's own issues and for `exclude.authors`. Compare the drupal.org user ID with the user's (their drupal.org profile URL), not the name: the display name ("dave reid") differs from the GitLab username (`davereid`).
- **Comments:** migrated comments keep their real GitLab authors, but `created_at` is the migration time. The original date is in the `_Migrated from comment #N posted <date>_` line: show that date, and say that "last updated" on migrated issues reflects the migration.
- **Ignore** `drupalbot`'s "Issue tools" notes and `System_Message` commit notes when finding the latest comment.

## Merge requests belong to issues

drupal.org MRs are made from issue forks (`issue/<name>-<nid>`, source branch `<nid>-<slug>`) and the issue is where the discussion and status live. MR reviewers and approvals are rarely used.

- List the project's open MRs as in `gitlab.md` (they target `project/<name>`), and find each one's issue from its source project or branch.
- An MR and its issue are excluded together: when the profile's `exclude` drops either one (e.g. the issue's `v7.x-*` version label, or the MR's `7.x-*` target branch), drop both.
- When an MR's issue is also in the triage list, show the MR in that issue's row (MR number, pipeline state) instead of a separate PR row, and handle them together: the PR summary steps for the code, the issue steps for the reply.
- "The user's latest review" includes their latest comment on the issue, not only notes on the MR.
- Pipeline state and failed jobs: `drupalorg mr:status 'project/<name>!<iid>'` and `drupalorg mr:logs 'project/<name>!<iid>'` (quote it in zsh).
- `--mine`: the user's own MRs as in `gitlab.md`; also show the issue's status, since _Needs work_ set by someone else means feedback is waiting.

## Issue-queue projects (`issues_enabled` false)

- List: `drupalorg project:issues <name> all --limit 100 --format=json 2>/dev/null` (`nid`, `title`, `field_issue_status`). It doesn't return authors, assignees or comments.
- Owned projects only: keep the open statuses, then read each with `drupalorg issue:show <nid> --with-comments --format=llm` to classify it. That's one call per issue: say how many, and ask first if it's more than about 20.
- Projects the user doesn't own, such as Drupal core: their issue queues are too big to read. Only triage MRs the user commented on (from `gitlab.md`'s events search), and say issues aren't covered there.
- `drupalorg` can't comment or change statuses: draft the comment and the new status, and give the user the issue link to post it themselves.

## Searching upstream

For any drupal.org project. Drupal core (`drupal/core`, `web/core`) is the project `drupal`; a `drupal/<name>` package, or code under `modules/contrib/<name>` or `themes/contrib/<name>`, is the project `<name>`.

Searching needs no login or extra tools: the `curl` commands below read public pages and APIs, so they also work when the user's own project is on another host and `glab` or `drupalorg` isn't set up. To tell which tracker a project uses without a login (the API leaves out `issues_enabled` then): `curl -sS -o /dev/null -w '%{http_code} %{redirect_url}' https://www.drupal.org/project/issues/<name>` redirects (301) to `git.drupalcode.org/project/<name>/-/work_items` for work-item projects, and returns 200 for projects still on drupal.org's queue.

- Issue-queue projects (such as core): drupal.org's issue search, which matches words anywhere in the title, in any order: `curl -sSL -G "https://www.drupal.org/project/issues/<project>" --data-urlencode "text=<words>" --data-urlencode status=All | grep -oE 'href="/project/<project>/issues/[0-9]+"[^>]*>[^<]+'`.
- Work-item projects: `gitlab.md`'s "Searching upstream" (`:id` is `project%2F<name>`), which also searches descriptions.
- `drupalorg issue:search <project> "<words>" --limit 50 2>/dev/null` covers both, but only finds exact phrases, and smaller `--limit` values miss matches (drupalorg 0.11.0: `--limit=10` missed an issue that 20 and 50 found). Use it only for an exact identifier, such as a function name, and don't treat an empty result as "no issue".
- Use two or three distinctive words (a class or function name, a key phrase from the error), and try several.
- Read a candidate with `drupalorg issue:show <nid> --with-comments --format=llm`.
- Commenting upstream: work-item projects as in "Actions on work items", which needs `glab` logged in to `git.drupalcode.org`; issue-queue projects (such as core), or without that login, give the user the text and the issue link.

## Actions on work items

- Comment: `glab issue note <nid> -R https://git.drupalcode.org/project/<name> -m "<text>"`.
- Change status: drupal.org changes labels through `/do:` commands in comments. `drupalorg issue:label <nid> state::needsWork` posts one (the new `state::` label replaces the old one). Offer **Comment and set status** alongside **Comment**, with the new status shown first.
- Upstream issue not confirmed yet: `state::postponed` with a comment linking it.
- Close: set the closing state with a reason, e.g. `drupalorg issue:label <nid> state::closed why::duplicate` (reasons: `why::duplicate`, `why::wontFix`, `why::worksAsDesigned`, `why::cannotReproduce`, `why::outdated`, `why::needsInfo`), or `state::fixed`. Not verified: check the label changed afterwards, and if it didn't, give the user the link to change it.
- Don't use `glab issue close` on drupal.org: closing goes through the status labels.

## Security

- Published advisories: `https://www.drupal.org/security` (core and contrib).
- Private reports go to the Drupal Security Team: `https://www.drupal.org/drupal-security-team/security-team-procedures` explains how. Its process covers projects with security advisory coverage; for projects without it, say what the project page says about coverage and let the user decide.

## AI disclosure

drupal.org's [AI policy](https://www.drupal.org/docs/develop/issues/issue-procedures-and-etiquette/policy-on-the-use-of-ai-when-contributing-to-drupal) requires disclosing significant AI-generated text or code in issues and MRs. When a draft comment is more than a short reply, remind the user before posting that they should rewrite it in their own words, or add a disclosure naming the tool and what it produced.

## Token permissions

Same as `gitlab.md`: a `git.drupalcode.org` personal access token with `read_api` to triage, and `api` to comment or post `/do:` commands. `drupalorg` reads drupal.org's public API and needs no token.
