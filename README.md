# Claude PR Skills

[![Packagist Version](https://img.shields.io/packagist/v/davereid/skills)](https://packagist.org/packages/davereid/skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-pr--skills-black)](https://skills.sh/davereid/skills)

Agent skills for working with pull requests and maintaining drupal.org projects, for Claude Code, Codex, Cursor and other agents that read `SKILL.md`.


## Skills

### Pull requests

- [pr-fix](skills/pr-fix/README.md): diagnoses and fixes failing pull requests in DDEV projects, from bots such as Renovate and Dependabot or your own, works through open review feedback, and pushes only after you approve.
- [pr-triage](skills/pr-triage/README.md): lists the open PRs that need your attention, filtered by a profile of your skill set. It summarizes what changed since your last review, and offers to approve, comment or hand off to a full review. With `--mine`, it shows what your own PRs are waiting on.

### drupal.org projects

- [setup-checkout](skills/setup-checkout/SKILL.md): clones a project, or updates an existing checkout, and sets it up with DDEV and ddev-drupal-contrib to run the same checks as drupal.org's CI. It then compares the project's CI, Composer, tests and docs with best practices, and offers to bring them up to date.
- [update-docs](skills/update-docs/SKILL.md): keeps a project's `README.md` (to drupal.org's template) and `docs/` in step with its code, lists what they're missing, generates the project page HTML from the README, and writes a short, non-technical summary for the project page.
- [setup-docs](skills/setup-docs/SKILL.md): moves developer documentation from the README into `docs/`, and publishes it with MkDocs and GitLab Pages at `https://project.pages.drupalcode.org/<name>/`.
- [create-release](skills/create-release/SKILL.md): checks the branch and its pipeline, updates the docs with `update-docs`, tags the release, drafts release notes with `drupalorg maintainer:release-notes`, and links to drupal.org's release and project page forms.

`create-release` needs the [drupalorg CLI](https://github.com/mglaman/drupalorg-cli). `update-docs` and `setup-docs` need Python 3. `setup-checkout` needs [DDEV](https://ddev.com/).


## Installation

Each skill's README has its requirements, installation steps, usage and limits. In short:

With [`npx skills`](https://github.com/vercel-labs/skills), the recommended way: one command, short commands (`/pr-fix`, `/pr-triage`), and it also works with other agents it supports:

```
npx skills add https://github.com/davereid/skills
```

Add `--skill <name>` to install only some of the skills.

Other ways:

- With Composer, which also provides the `pr-fix` Taskfile tasks and CI workflow: `composer require --dev davereid/skills`
- As a Claude Code plugin: `/plugin marketplace add davereid/skills`, then `/plugin install pr-skills@davereid`. The commands are then `/pr-skills:pr-fix` and `/pr-skills:pr-triage`.


## AI disclosure

This project was built with Claude Code (Anthropic). Claude Code drafted the skills, the Taskfile, the CI workflow and this documentation from a brief written by the team and uploaded by me. I directed the implementation and design decisions, reviewed the output, and directed updates afterwards from the brief. Claude Code also drafted the drupal.org project skills, their script and their documentation; I directed their design decisions and reviewed the output.
