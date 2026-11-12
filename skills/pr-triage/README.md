# pr-triage

A Claude Code skill that lists the open pull requests that need your attention, filtered to your skill set, and helps you act on them. It uses the `gh` CLI and works on GitHub and GitHub Enterprise.

It finds two kinds of PR:

- **Needs your action:** you already reviewed it and it has new commits (or you were asked to review it again). The skill summarizes what changed since your review, checks whether your earlier comments were addressed, and offers to approve, request changes, comment or show the full diff.
- **Needs your review:** you haven't reviewed it, and you were asked to, or it matches your profile. The skill summarizes it and offers to hand off to a full review (`/code-review`), comment, or skip. For a failing bot PR, it also offers `/pr-fix` if that skill is installed.

With `--mine`, it lists your own open PRs instead, with what each is waiting on: changes requested, unresolved threads, failing CI, unchecked tasks in the description, or a review. For a PR with work left, it offers to hand off to `/pr-fix` if that skill is installed.

Everything it drafts is for you to verify. It never approves, comments or requests changes without your answer for that PR, after showing the exact text.


## Requirements

- [Claude Code](https://claude.com/claude-code)
- [GitHub CLI](https://cli.github.com) (`gh`), logged in to the PRs' GitHub host. See the token permissions in [SKILL.md](SKILL.md): read access is enough to triage, and write access is only used for actions you approve.


## Installation

As part of the plugin, with `npx skills` or with Composer: see the [main README](../../README.md#installation). With Composer, `task pr:install-skill` symlinks the skill into `.claude/skills/`.

Optionally, create a profile (see below).


## Usage

```
/pr-triage
```

With the plugin install, use `/pr-skills:pr-triage` instead of `/pr-triage`.

| Command | What it does |
|---|---|
| `/pr-triage` | Triage the current repository |
| `/pr-triage 1039` | Only that PR (also `owner/repo#1039`) |
| `/pr-triage owner/repo` | Triage another repository |
| `/pr-triage --all` | Search every repository, using your user profile only |
| `--approved`, `--changes-requested` | Only PRs you last approved, or requested changes on |
| `--all-prs` | Also list the PRs that don't match your profile |
| `/pr-triage --mine` | Your own open PRs and what each is waiting on (add `--all` for every repository) |

Without `--mine`, it skips drafts and your own PRs.


## Profile

The profile says which PRs are yours: paths, labels, keywords, CODEOWNERS entries, authors to exclude, and a plain-language description of your skill set. Copy [profile.example.md](profile.example.md) to one or both of:

1. `~/.config/pr-triage/profile.md`: your defaults for every repository.
2. `<repo root>/.claude/pr-triage.md`: overrides for one repository. Its lists replace the same lists from your user file.

PRs that request your review, or that you already reviewed, are always shown, whatever the profile says. Without a profile, the skill asks a few questions and offers to write one, and saves nothing until you agree.
