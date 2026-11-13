# Claude PR Skills

- When adding, renaming or removing a file in `skills/pr-fix/`, update `extra.drupal-scaffold.file-mapping` in `composer.json` to match. Drupal sites get the skill through scaffold, which copies only the mapped files.
- Write PR titles as [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `ci:`, `chore:` …; `feat!:` for breaking changes). Commits inside a PR can use any message: a ruleset blocks direct pushes to `main`, PRs are squash-merged with the title as the commit message, and release-please builds the version, tag and `CHANGELOG.md` from those titles. Don't edit `version` in `.claude-plugin/plugin.json` or `.release-please-manifest.json` by hand.
