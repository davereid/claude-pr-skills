# Claude PR Skills

[![Packagist Version](https://img.shields.io/packagist/v/davereid/claude-pr-skills)](https://packagist.org/packages/davereid/claude-pr-skills)
[![skills.sh](https://img.shields.io/badge/skills.sh-pr--skills-black)](https://skills.sh/davereid/claude-pr-skills)

Claude Code skills for working with pull requests.


## Skills

- [pr-fix](skills/pr-fix/README.md): diagnoses and fixes failing pull requests in DDEV projects, from bots such as Renovate and Dependabot or your own, and pushes only after you approve.
- [pr-triage](skills/pr-triage/README.md): lists the open PRs that need your attention, filtered by a profile of your skill set. It summarizes what changed since your last review, and offers to approve, comment or hand off to a full review.


## Installation

Each skill's README has its requirements, installation steps, usage and limits. In short:

- As a Claude Code plugin: `/plugin install pr-skills@davereid`
- With [`npx skills`](https://github.com/vercel-labs/skills): `npx skills add https://github.com/davereid/claude-pr-skills`
- With Composer: `composer require --dev davereid/claude-pr-skills`


## AI disclosure

This project was built with Claude Code (Anthropic). Claude Code drafted the skills, the Taskfile, the CI workflow and this documentation from a brief written by the team and uploaded by me. I directed the implementation and design decisions, reviewed the output, and directed updates afterwards from the brief.
