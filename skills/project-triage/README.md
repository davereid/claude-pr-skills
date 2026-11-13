# project-triage

An agent skill that lists the open pull requests and issues that need your attention, and helps you act on them.

It works on GitHub and GitHub Enterprise (`gh`), GitLab (`glab`), and drupal.org projects (`glab` on `git.drupalcode.org`, plus the `drupalorg` CLI). It picks the host from the checkout's `origin` remote, and keeps each host's commands in `references/`. On drupal.org it groups merge requests with their issues, shows each issue's status, and can set the status with your comment. For projects still on drupal.org's issue queue, such as core, it drafts comments for you to post.

What it looks at depends on the repository:

- **Repositories you own or administer:** every open PR and issue from someone else. On GitHub: you're the owner, have admin or maintain permission, or were added directly as a collaborator (write access through an organization team doesn't count). On GitLab: it's in your namespace, you're a Maintainer or Owner, or you're a direct project member. On drupal.org: you're a maintainer with write access to the repository.
- **Other repositories:** PRs that ask for your review, that you already reviewed, or that match your profile, and issues assigned to you.

It finds two kinds of PR:

- **Needs your action:** you already reviewed it and it has new commits (or you were asked to review it again). The skill summarizes what changed since your review, checks whether your earlier comments were addressed, and offers to approve, request changes, comment or show the full diff.
- **Needs your review:** you haven't reviewed it, and you were asked to, it matches your profile, or it's in your repository. The skill summarizes it and offers to hand off to a full review (`/code-review`), comment, or skip. For a failing bot PR, it also offers `/pr-fix` if that skill is installed.

And two kinds of issue:

- **Needs your reply:** you commented, and someone else replied after you.
- **Needs triage:** you haven't commented yet.

For each issue it summarizes the report and the replies since your last comment, and offers to investigate (reading the code to check what it can), comment, comment and close, or skip. Issues where your comment is the latest are counted as waiting on others.

With `--mine`, it lists your own open PRs instead, with what each is waiting on: changes requested, unresolved threads, failing CI, unchecked tasks in the description, or a review. For a PR with work left, it offers to hand off to `/pr-fix` if that skill is installed. Add `--issues` for your own issues that have new replies.

Everything it drafts is for you to verify. It never approves, comments, requests changes or closes anything without your answer for that item, after showing the exact text.


## Requirements

- An agent that reads `SKILL.md`, such as [Claude Code](https://claude.com/claude-code)
- For GitHub: [GitHub CLI](https://cli.github.com) (`gh`), logged in to the repositories' host. See the token permissions in [references/github.md](references/github.md).
- For GitLab and drupal.org: [GitLab CLI](https://gitlab.com/gitlab-org/cli) (`glab`), logged in to the host (`git.drupalcode.org` for drupal.org). See [references/gitlab.md](references/gitlab.md).
- For drupal.org: the [drupalorg CLI](https://github.com/mglaman/drupalorg-cli), for pipelines, issue statuses and projects still on drupal.org's issue queue. See [references/drupalorg.md](references/drupalorg.md).

Read access is enough to triage; write access is only used for actions you approve.


## Installation

As part of the plugin, with `npx skills` or with Composer: see the [main README](../../README.md#installation). With Composer, `task pr:install-skill` symlinks the skill into `.claude/skills/`.

Optionally, create a profile (see below).


## Usage

```
/project-triage
```

With the plugin install, use `/pr-skills:project-triage` instead of `/project-triage`.

| Command | What it does |
|---|---|
| `/project-triage` | Triage the current repository's PRs and issues |
| `/project-triage 1039` | Only that PR or issue (also `owner/repo#1039`) |
| `/project-triage owner/repo` | Triage another repository |
| `/project-triage --all` | Search every repository, using your user profile only |
| `--code` | Only PRs |
| `--issues` | Only issues |
| `--approved`, `--changes-requested` | Only PRs you last approved, or requested changes on |
| `--all-prs` | Also list the PRs that don't match your profile, and the issues waiting on others |
| `/project-triage --mine` | Your own open PRs and what each is waiting on (add `--all` for every repository, `--issues` for your own issues with new replies) |

Without `--mine`, it skips drafts and your own PRs and issues.

`--all` finds repositories you own or were added to directly, but not organization repositories you administer only through a team: triage those one at a time.


## Profile

The profile says which PRs are yours in repositories you don't own: paths, labels, keywords, CODEOWNERS entries, authors and labels to exclude (these also apply to issues), base branches to exclude (such as an unsupported `7.x-*`; labels and branches accept `*` wildcards), and a plain-language description of your skill set. Copy [profile.example.md](profile.example.md) to one or both of:

1. `~/.config/project-triage/profile.md`: your defaults for every repository.
2. `<repo root>/.claude/project-triage.md`: overrides for one repository. Its lists replace the same lists from your user file.

PRs that request your review, or that you already reviewed, are always shown, whatever the profile says. Without a profile, the skill asks a few questions and offers to write one, and saves nothing until you agree.


## Issues kept somewhere else

A project can commit `.claude/project-triage-issues.md` to tell the skill about issue trackers:

- If its issues aren't on its code host, for example in Jira: how to list, read, comment on and search them. The skill then uses it for issues instead of the host's, and still uses the host for PRs.
- How to search its dependencies' trackers when the skill checks whether a bug is upstream: a vendor's Jira, a private package's tracker, or another place to look. Every section is optional, so a project with GitHub issues can add just this. [issues.example.md](issues.example.md) is a starting point using [jira-cli](https://github.com/ankitpokhrel/jira-cli); adapt the commands to your team's tool.
