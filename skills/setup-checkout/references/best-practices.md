# Best practices for a drupal.org project

What `setup-checkout` compares a project against. Each item says what to check and what to suggest when it's missing.


## CI (`.gitlab-ci.yml`)

- **Uses drupal.org's templates.** It includes `/includes/include.drupalci.main.yml`, `include.drupalci.variables.yml` and `include.drupalci.workflows.yml` from `$_GITLAB_TEMPLATES_REPO` at `$_GITLAB_TEMPLATES_REF`. Without a `.gitlab-ci.yml`, suggest starting from the [current template](https://git.drupalcode.org/project/gitlab_templates/-/raw/default-ref/gitlab-ci/template.gitlab-ci.yml). An existing file may predate parts of that template: compare them, and suggest only what's missing.
- **Tests other core versions.** These variables are set:
  ```yaml
  OPT_IN_TEST_PREVIOUS_MINOR: 1
  OPT_IN_TEST_NEXT_MINOR: 1
  OPT_IN_TEST_NEXT_MAJOR: 1
  OPT_IN_TEST_MAX_PHP: 1
  _AUTORUN_PREVIOUS_MINOR: 'all'
  _AUTORUN_NEXT_MINOR: 'all'
  _AUTORUN_NEXT_MAJOR: 'push-and-mr'
  _AUTORUN_MAX_PHP: 'push-and-mr'
  ```
  Set `OPT_IN_TEST_PREVIOUS_MAJOR: 1` only when `core_version_requirement` allows the previous major version.
- **Spell checking has a dictionary.** `_CSPELL_DICTIONARY` names a committed word list (e.g. `.cspell-words.txt`) for project-specific words.
- **Next major dependencies are explained.** Each module in `_LENIENT_ALLOW_LIST` (in `composer (next major)`) has a `@todo` comment linking to the issue for its next-major support.
- **Jobs aren't skipped silently.** Each `SKIP_*` variable set to `1` has a comment saying why.


## Composer and `.info.yml`

- **`composer.json` exists**, with the project's name (`drupal/<name>`), type and license.
- **CI can install the dependencies.** CI builds the test site from `composer.json` alone and ignores `.info.yml`, so each `.info.yml` dependency on another drupal.org project (`project:module`) is also in `require-dev`, as `"*"` unless a version is needed. A minimum version goes in `require`, not in `.info.yml`.
- **Optional integrations are installable too.** Modules the code integrates with but doesn't require (e.g. in tests or a submodule) are in `require-dev`.
- **Drush is available.** `require-dev` has `"drush/drush": "*"`, so `ddev drush` works.


## Tests

- **There are tests.** Kernel tests are the best start for most code; unit tests for code that doesn't need Drupal; functional and FunctionalJavascript tests only for what needs a browser. If there are none, offer to add a kernel test for the project's main feature, and don't write one without asking.
- **Tests use PHPUnit attributes**, not annotations: `#[Group('<name>')]`, `#[CoversClass]` (or `#[CoversMethod]`), and `#[RunTestsInSeparateProcesses]` on kernel and functional tests. PHPUnit 12 removed annotations.
- **phpstan is configured.** A committed `phpstan.neon` sets the level, with a `phpstan-baseline.neon` if needed. Suggest fixing baseline entries over time, not adding to them.
- **The checks pass**: `ddev phpcs`, `ddev phpstan`, `ddev phpunit`, and `ddev eslint` for JavaScript.


## Docs

- **The README follows drupal.org's template.** If it's missing sections or is out of date, suggest the `update-docs` skill.
- **Developer documentation has its own place.** If the README has grown developer sections (plugin APIs, hooks, long code examples) and there's no `mkdocs.yml`, suggest the `setup-docs` skill.
- **Docs use the templates' `pages` job.** If `.gitlab-ci.yml` has its own `mkdocs` or `pages` job that only runs `mkdocs build`, suggest `setup-docs`, which removes them.
- **API modules document their API.** If the project has a PHP API other modules use (services, traits, base classes), ask whether to generate API docs from its docblocks into the docs site, with `setup-docs`'s API docs step.
