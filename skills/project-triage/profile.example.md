---
# Copy to ~/.config/project-triage/profile.md (all repos) or <repo>/.claude/project-triage.md
# (one repo, overrides the user file: lists replace, they don't merge).
match:
  paths:
    - "src/migrations/**"
    - "docs/**"
  labels: [ci]
  keywords: [migrate, redirect]
  codeowners: true
exclude:
  authors: [renovate[bot], dependabot[bot]]
  labels: [dependencies]
always_show_requested: true
---

# My skill set

Write this in plain language. It is used to decide whether a PR with no rule match fits you, and
it tells teammates what to ask you about.

- Know well: Drupal module development (PHP, services, plugins, hooks), migrations, Composer.
- Comfortable with: PHPUnit kernel tests, CI workflows, developer documentation.
- Less involved in: front-end design, JavaScript build tooling, infrastructure.
