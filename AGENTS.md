# Claude PR Skills

- Skills live in `skills/<name>/SKILL.md`; list each one in `README.md` and in the plugin's description in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Keep each skill's `description` under 80 characters. Put details in the body.
- Skills are shared: no personal paths, scripts or tools. Bundle scripts a skill needs in its `scripts/` directory.
- Skills must work with any agent that reads `SKILL.md`, not only Claude Code: describe what to do rather than naming an agent's tools ("with the Edit tool"), and don't call an agent's CLI (`claude -p`) from scripts; the agent running the skill does the writing and judgment.
- When a skill stops writing a file into a project, or renames one, add a step to it that starts "Older versions of this skill wrote `<file>`", saying what replaces the file and how to move its content over before deleting it (as `update-docs` does for `project.html` and `summary.html`). `setup-checkout` finds old files by that phrase, so keep it exact.
- When adding, renaming or removing a file in `skills/pr-fix/`, update `extra.drupal-scaffold.file-mapping` in `composer.json` to match. Drupal sites get the skill through scaffold, which copies only the mapped files.
- Write PR titles as [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `ci:`, `chore:` …; `feat!:` for breaking changes). Commits inside a PR can use any message: a ruleset blocks direct pushes to `main`, PRs are squash-merged with the title as the commit message, and release-please builds the version, tag and `CHANGELOG.md` from those titles. Don't edit `version` in `.claude-plugin/plugin.json` or `.release-please-manifest.json` by hand.
