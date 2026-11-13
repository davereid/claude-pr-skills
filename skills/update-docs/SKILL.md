---
name: update-docs
description: Update a drupal.org project's README, docs and project page, e.g. for releases.
---

# Update docs

Keeps a drupal.org project's documentation in step with its code: the `README.md`, the `docs/` directory, the project page HTML generated from the README (`README.html`), and the project page's summary. It also looks for what the documentation is missing.

Use it whenever the docs may be out of date: when a change adds or changes a feature (a setting, service, public method, plugin or Drush command), when asked to update the README, docs or project page, and always before tagging a release (the `create-release` skill runs it).


## Steps

1. Find the project root: the directory with the main `*.info.yml` and `README.md`. If there's no `*.info.yml`, this isn't a Drupal project: say so and stop.
2. Work out what to document: the change at hand, or everything since the last release (`git describe --tags --abbrev=0`, then `git log` and `git diff --stat` from that tag).
3. **Find what's missing.** List what the changes add or change that users or developers rely on, and check each is documented in the README or `docs/`:
   - for site builders: settings and configuration forms, `$settings` keys in `settings.php`, permissions, pages and their paths, Drush commands and options, new requirements or a higher minimum Drupal core version;
   - for developers: plugin types and attributes, services, public methods on interfaces and base classes, hooks (`*.api.php`), events, render elements, theme hooks and libraries meant for reuse.

   Also check the other way: documented features, settings, commands or methods that were renamed or removed. List the gaps, with where each belongs (README section or `docs/` page). Document the ones the changes added; for older gaps, suggest them and ask before writing.
4. Update `README.md` to follow the template (below), and `docs/` (see README or docs/). Don't name client projects, sites or organizations: describe features generically.
5. If `README.html` exists, or the user asks for it, regenerate it:
   ```
   python3 <this skill's directory>/scripts/readme2html.py --base=https://git.drupalcode.org/project/<name>/-/blob/<default branch>/ [--docs=https://project.pages.drupalcode.org/<name>/] README.md > README.html
   ```
   `--base` turns the README's relative links, such as `LICENSE`, into full URLs that work on drupal.org. Add `--docs` when the project publishes its docs with MkDocs (the `setup-docs` skill sets it up): links to `docs/<page>.md` then go to the page on the docs site. Get the default branch from `git ls-remote --symref origin HEAD`. If `README.html` is tracked by git, ask before writing it: it's meant to be an untracked working file.

   If it's untracked and not ignored (`git check-ignore -q README.html` fails), offer to ignore it so it isn't committed by accident: by default in `.git/info/exclude`, which only affects this checkout, or in the project's `.gitignore` if it has one and other maintainers use this skill too.
6. Regenerating removes the summary, so before step 5, keep the existing `<!-- Summary: … -->` comment from `README.html`. Then write the summary (you've read the README and the change), starting from the old one and changing only what the README's changes affect, and add it as the first lines of `README.html`:
   ```
   <!-- Summary:

   First paragraph.

   Second paragraph.

   -->
   ```
   Two short paragraphs of plain text for site builders and content editors: what the module does for them and its most useful features. Open with what the module gives them, in concrete terms ("a clear, central place to see what's going on with your site's content and structure"), not a vague benefit ("keeps your site in good shape", "healthy", "powerful", "easy"): every claim should say what someone can see or do. No technical terms (plugins, APIs, Drush, cache tags, class names), no requirements, US English, no `--` (it ends an HTML comment).
7. Older versions of this skill wrote `project.html` and `summary.html`. If either is untracked, `README.html` and its summary comment replace them: move the summary over from either file, then ask before deleting them.
8. Remind the user to paste `README.html` (without the summary comment) into the project page's description, and the summary into its summary field, once the change is released, and to review the summary's wording first.


## README template

Follow drupal.org's [README.md template](https://www.drupal.org/docs/develop/managing-a-drupalorg-theme-module-or-distribution-project/documenting-your-project/readmemd-template):

- The project name is the only `#` heading.
- The introduction links to the issue queue, and to the full documentation if there is any. Leave out the template's "For a full description of the module, visit the project page" link: the project page is generated from the README's own content.
- Required sections are Requirements (every dependency outside core, or say there are none), Installation (link to the standard steps and only note what's different), and Configuration.
- Optional sections are a table of contents, Recommended modules, Troubleshooting and FAQ, and Maintainers.
- Headings use sentence case with two blank lines before them, and lists use `-` and `1.`. Don't wrap lines at 80 columns: it's hard to maintain and makes diffs noisy.


## README or docs/

The README, and the project page made from it, is for site builders: what the module does, requirements, installation, configuration, the features it includes and its Drush commands. Developer documentation goes in `docs/`, one Markdown page per topic: plugin APIs and how to write plugins, hooks, data formats, guides to extending the module, and long code examples.

- When the README's developer sections run past about a screen, or the project has `docs/` but no `mkdocs.yml`, suggest the `setup-docs` skill: list the pages you'd create and what each holds. It moves the text, and publishes `docs/` as a site at `https://project.pages.drupalcode.org/<name>/`.
- When a change adds developer-facing API to a project that already has `docs/`, document it there, not in the README, and add new pages to `docs/index.md`.
- In `docs/`, link to code with absolute URLs, since MkDocs' strict build fails on relative links outside `docs/`: the project's classes and files to GitLab (`https://git.drupalcode.org/project/<name>/-/blob/<default branch>/<path>`), and other projects' classes and methods to their published API docs when they have them (e.g. `https://project.pages.drupalcode.org/helper/api/EntityHelper/#getstate`), or to their code on GitLab when they don't.
- Link from the README to `docs/` pages with relative links (`docs/<page>.md`), so they work on GitLab, in a checkout and on every branch. In `README.html`, `readme2html.py --docs` points them at the docs site (or `--base` at GitLab, without one).


## README.html

`readme2html.py` leaves out the title, the table of contents and that project page link, and turns in-page links into plain text, since project page headings have no IDs.
