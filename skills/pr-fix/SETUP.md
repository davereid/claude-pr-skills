# Setup

You connect accounts and grant access yourself; the skill can't.

## Local

**Plugin only:** `/plugin marketplace add davereid/skills`, then `/plugin install pr-skills@davereid` (the command is then `/pr-skills:pr-fix`), then do steps 4–5 below. Composer and the Taskfile are only needed for `task pr:*` and the CI workflow. Don't also run `install-skill`, or the skill is loaded twice.

1. `composer require --dev davereid/skills`
2. Add to the project's root `Taskfile.yml`:
   ```yaml
   includes:
     pr: ./vendor/davereid/skills/Taskfile.yml
   ```
3. Install the skill into `.claude/skills/pr-fix`, using one of these:
   - **Drupal sites with `drupal/core-composer-scaffold`:** add `"davereid/skills"` to `extra.drupal-scaffold.allowed-packages` in the root `composer.json`, then run `composer install`. Add it to the existing list if there is one:
     ```json
     "extra": {
         "drupal-scaffold": {
             "allowed-packages": [
                 "davereid/skills"
             ]
         }
     }
     ```
     Scaffold copies the skill in and refreshes it on every `composer install` and `composer update`.
   - **Other projects:** run `task pr:install-skill`, which symlinks it.

   Commit `.claude/skills/pr-fix` to share it with the team, or ignore it in git.
4. GitHub: create a fine-grained token for this repository only, with Contents: read/write, Pull requests: read/write and Actions: read. Then run `gh auth login --hostname <your GitHub host>`.
5. Check that `git push` to the repo works with your SSH key (and signing, if required).
6. Run it with `task pr:fix` (every failing bot PR and PR of your own) or `task pr:fix PR=123`. In Claude Code, use `/pr-fix all` or `/pr-fix 123`.

**Unverified: ddev-claude container** (`marcoscano/ddev-claude`):

- Allowlist your GitHub host in the add-on's firewall. For Drupal projects with patches, also allowlist `git.drupalcode.org` and `www.drupal.org`.
- Pass a `gh` token into the container, for example as `GH_TOKEN`.
- Make sure git can push from the container, and that commit signing works there if your repo requires it.

## CI (comment only)

CI runs automatically only on failing Dependabot PRs. For any other PR in the repository, including your own, run the workflow manually with the PR number, or add the `fix-my-pr` label (create it first). To run it again, remove the label and add it again.

1. `task pr:install-workflow`, then edit `workflows:` under `workflow_run` to list the workflows to watch.
2. If the project installs DDEV through its own action, replace the `setup-ddev` step with it.
3. Add `ANTHROPIC_API_KEY` as an **Actions secret** and a **Dependabot secret**. If it isn't set, the workflow exits early. For client projects, the client must own or approve this key.
4. **Unverified:**
   - Confirm that your GitHub host allows `anthropics/claude-code-action` and `marocchino/sticky-pull-request-comment`. GitHub Enterprise may block marketplace actions.
5. Commit the workflow file.
