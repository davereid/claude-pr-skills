# pr-fix

A Claude Code skill that diagnoses and fixes failing pull requests in DDEV projects: ones opened by bots such as Renovate and Dependabot, and your own. It reads the failed workflow's logs, classifies the cause (a patch that no longer applies, a config or schema update, a test regression, or something else), tests a fix locally with the failed job's own commands, and commits and pushes only after you approve.

An optional GitHub workflow runs the same diagnosis in CI and posts the proposed fix as a PR comment. It never pushes. It runs automatically on failing Dependabot PRs, and on any PR in the repository when you run it manually or add the `fix-my-pr` label.

The design and its decisions are in [docs/brief.md](../../docs/brief.md).

The brief for this skill was written during a workshop at the 2026 Lullabot Retreat by the following team:
- [@davereid](https://github.com/davereid)
- [@HammerHankinson](https://github.com/HammerHankinson)
- [@mtift](https://github.com/mtift)
- [@quicksketch](https://github.com/quicksketch)


## Requirements

- [Claude Code](https://claude.com/claude-code)
- [DDEV](https://ddev.com) in the project
- [GitHub CLI](https://cli.github.com) (`gh`), logged in to the project's GitHub host. The skill uses it to read PRs and workflow logs. If you run Claude Code inside DDEV with the [ddev-claude](https://github.com/marcoscano/ddev-claude) add-on, also install the GitHub CLI add-on there: `ddev add-on get plopesc/ddev-gh-cli`
- For CI: an `ANTHROPIC_API_KEY` secret


## Installation

With [`npx skills`](https://github.com/vercel-labs/skills), the recommended way for the skill alone. It installs the repository's skills (not the Taskfile or CI workflow) and the command is `/pr-fix`:

```
npx skills add https://github.com/davereid/claude-pr-skills
```

Choose Claude Code when it asks which agents to install for. It installs the skill into `.claude/skills/pr-fix/` in the project, or `~/.claude/skills/` with `-g`. Update it later with `npx skills update`.

Or with Composer, which also provides the Taskfile tasks and the CI workflow template:

```
composer require --dev davereid/claude-pr-skills
```

On Drupal sites, `drupal/core-composer-scaffold` can copy the skill into `.claude/skills/` once `davereid/claude-pr-skills` is in `extra.drupal-scaffold.allowed-packages`.

Or as a Claude Code plugin, where the command is `/pr-skills:pr-fix`:

```
/plugin marketplace add davereid/claude-pr-skills
/plugin install pr-skills@davereid
```

Use one or the other for the skill, not both. Full steps, including credentials and CI: [SETUP.md](SETUP.md).


## Usage

In Claude Code:

```
/pr-fix 123
```

With the plugin install, use `/pr-skills:pr-fix` instead of `/pr-fix`. `/pr-fix all` works through every failing bot PR and PR of your own in turn, asking before each push. With no argument, it lists them and asks which one to fix, or all.

With Composer, include the Taskfile from the project's root `Taskfile.yml`:

```yaml
includes:
  pr: ./vendor/davereid/claude-pr-skills/Taskfile.yml
```

| Task | What it does |
|---|---|
| `task pr:fix` | Starts Claude Code with the skill for every failing bot PR and PR of your own |
| `task pr:fix PR=123` | The same, for one PR |
| `task pr:install-skill` | Symlinks the skill into `.claude/skills/` |
| `task pr:install-workflow` | Copies the CI workflow into `.github/workflows/`, or shows a diff if it exists |


## What it will and won't do

- It only works on PRs opened by a bot or by you, whose branch is in the same repository. It refuses anyone else's PR and PRs from forks.
- It asks before every commit, push and PR comment.
- It makes at most 3 fix attempts per PR, then stops and drafts a comment.
- It never merges, force-pushes, pushes to other branches, or touches production or remote environments.
