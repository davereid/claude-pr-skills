---
name: setup-checkout
description: Clone or update a drupal.org project checkout: DDEV, tests and CI.
---

# Set up a checkout

Sets up a drupal.org module or theme for local development with [ddev-drupal-contrib](https://github.com/ddev/ddev-drupal-contrib), the layout drupal.org's GitLab CI uses: the project's repository is the DDEV project root, Composer builds Drupal in `web/` from the project's `composer.json`, and the project is linked into `web/modules/custom/`, in a folder named after the DDEV project.

It then reviews the project's agent instructions (`AGENTS.md`), and compares the project with [best practices](references/best-practices.md) for CI, Composer, tests and docs, and offers to bring it up to date.

Use it to clone a new project, or on an existing checkout to bring its setup and its project files up to date. Each step checks what's already there, so running it again is safe.

Needs Git with SSH access to `git.drupal.org`, and DDEV. Run it on the host: inside a DDEV container (`IS_DDEV_PROJECT=true`), `ddev` can't run, so stop and give the user the commands instead.


## Steps

1. **Find the project.** Take its machine name from the user, or from the main `*.info.yml` in an existing checkout. If the user's own instructions (such as their `AGENTS.md`) say where to keep checkouts or which extra DDEV add-ons to install, follow them. Otherwise ask where to clone, suggesting a directory named like the other checkouts next to it (e.g. `drupal-<name>` if they're `drupal-*`), or `<name>`.
2. **Clone or refresh.**
   - New: `git clone git@git.drupal.org:project/<name>.git <directory>`, which checks out the default branch.
   - Existing: `git fetch origin`, then report the current branch, uncommitted changes and how far it is behind its upstream. Don't pull, switch branches or touch uncommitted work without asking.
   - Note the untracked files (`git status --porcelain`) for step 7.
3. **Configure DDEV** without a `name:` in `.ddev/config.yaml`, so the project takes the directory's name (e.g. `drupal-helper`), and two checkouts of the same project can run side by side. ddev-drupal-contrib names the project's folder in `web/modules/custom/` after the DDEV project, with dashes as underscores (e.g. `drupal_helper`); Drupal finds the module by its `.info.yml`, so the folder name doesn't matter. Keep a name only if something depends on the URL (`<name>.ddev.site`): search the checkout for `.ddev.site` first, and ask the user if anything does.
   - If `ddev list` shows another project with the directory's name in a different directory, ask the user before going on.
   - New: `ddev config --project-type=drupal11 --docroot=web`. For a theme, also set `DRUPAL_PROJECTS_PATH=themes/custom` as the add-on's README describes.
   - Every `ddev config` run, including `ddev config --update` in step 5, writes `name:` into `.ddev/config.yaml`, even when it was left out. Remove the line again after each run.
   - Existing, with a `name:` in `.ddev/config.yaml` (e.g. `name: helper` in a `drupal-helper` directory): offer to remove it. Renaming deletes the project's containers and database, so first warn the user that the site's content and settings will be lost, and offer to keep them with a snapshot. Only go on once they agree. Then:
     1. `ddev snapshot`, if they want to keep the database. Snapshots are files in the checkout's `.ddev/db_snapshots/`, and the default name has a timestamp, so it can't clash with an earlier one.
     2. `ddev delete -Oy`, which removes the old project's containers, database and listing, and leaves the code and `.ddev/` alone.
     3. Remove the `name:` line from `.ddev/config.yaml`. If the file is committed, this is a change to the project, so tell the user.
     4. Delete what the old name left behind: `.ddev/traefik/certs/<old_name>.*` and `.ddev/traefik/config/<old_name>.yaml`, which DDEV otherwise warns about on each start, and the generated folder `web/modules/custom/<old_name>` (dashes as underscores), or Drupal finds the project twice.
     5. If a snapshot was taken, restore it with `ddev snapshot restore --latest` after the first `ddev restart` in "Build the site".
4. **Install add-ons.** `ddev add-on get` installs an add-on, or updates it to the latest release:
   - `ddev/ddev-drupal-contrib`;
   - `ddev/ddev-selenium-standalone-chrome`, if the project has FunctionalJavascript or Nightwatch tests (`tests/src/FunctionalJavascript`, `tests/src/Nightwatch`);
   - any add-ons the user's instructions list.
5. **Build the site.** `ddev restart`, then `ddev poser` (installs Drupal and the project's dependencies, as CI does) and `ddev symlink-project`. Then run `ddev config --update`, which picks the PHP version for the installed core, and `ddev restart` again if it changed `.ddev/config.yaml`. If the project has JavaScript, install core's JavaScript tools for ESLint: `ddev exec -d /var/www/html/web/core yarn install`.
6. **Run the checks.** `ddev phpcs`, `ddev phpstan`, `ddev eslint` if the project has JavaScript, and `ddev phpunit <path>` on one kernel or unit test if it has any. Report failures without fixing them: they can be real problems in the project.
7. **Keep `git status` clean.** Setup leaves files Git doesn't know about: `web/`, `vendor/`, `.ddev/`, Drupal's scaffold files (such as `.editorconfig`), and config the check commands download when the project has none (such as `phpcs.xml.dist`). Compare the untracked files with step 2's list, and offer to add the new ones to `.git/info/exclude`, which is never committed. In an existing checkout, step 2's list may already hold files from an earlier setup, such as `web/` and `.ddev/`: offer those too. Don't change the project's `.gitignore`.
8. **Find leftovers** from an older setup, in an existing checkout. List them with a suggested fix, and change nothing without asking:
   - untracked config the setup replaces, such as a local phpstan or PHPUnit config that adds extensions or database settings the add-on now provides;
   - instructions for agents or developers (`AGENTS.md`, local notes, the README's development section) that run checks another way, e.g. through a site that includes the project, with `vendor/bin/phpunit` and a core `phpunit.xml`, or with long phpcs and ESLint commands. Suggest the add-on's commands instead, and keep notes that still apply, such as CI quirks;
   - folders in `web/modules/custom/` (or `themes/custom/`) other than the project's own;
   - files that older versions of the other skills in this repository wrote: check each skill's `SKILL.md` for a step that starts "Older versions of this skill wrote", such as `update-docs`' `project.html` and `summary.html`, and hand them to that skill;
   - untracked files in the project's source that the checks report errors in. They may be someone's work in progress, so only point them out.
9. **Review the agent instructions.** Suggest each change and ask before making it:
   - `AGENTS.md` at the repository root: if there isn't one, offer to create it, with a short summary of the project, its architecture (main services, plugin types and base classes), its conventions that differ from Drupal's, and how to run the checks (step 11's commands). Ask whether it should be committed for every contributor, or kept untracked for the user (then add it to `.git/info/exclude`).
   - `CLAUDE.md` at the repository root, when `AGENTS.md` is committed: Claude Code reads `CLAUDE.md` but not `AGENTS.md`, so contributors using it would miss the instructions. If there isn't one, create it without asking, with just the line `@AGENTS.md`, to be committed alongside. If one exists with its own content, suggest moving that content to `AGENTS.md` and leaving the import.
   - If the user's own instructions describe personal files for each project, such as a local notes file that imports `AGENTS.md` or a backlog file, create the missing ones as those instructions describe. Check Git ignores them (`git check-ignore <file>`), and add any it doesn't to `.git/info/exclude`.
   - Compare the project's `AGENTS.md` and the user's local notes with the instructions the user's agent loads in every project (their global instructions), and with the README and docs. List what repeats them, and suggest removing it, keeping only what's specific to the project. A committed `AGENTS.md` should hold no personal preferences: suggest moving those to the local notes.
10. **Compare with best practices.** Check the project against each item in `references/best-practices.md`, and list what it's missing, each with the change you'd make. Ask which to make, then edit the working copy. Don't commit or create branches, since the user may want these in an issue and merge request of their own. Hand docs work to the skills the list names.
11. **Report** the directory, the site's URL, the branch status, the add-ons (`ddev add-on list --installed`), the check results, and the agent instruction and best-practice changes made or left to do. Include how to run the checks:
   - on the host: `ddev phpunit <path>` (put the path first, so the command adds core's test bootstrap), `ddev phpstan`, `ddev phpcs` and `ddev eslint`;
   - inside the web container: the same scripts, from `/var/www/html`, e.g. `.ddev/commands/web/phpunit tests/src/Kernel`.
