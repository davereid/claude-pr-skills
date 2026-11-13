# Issue tracker: Jira

<!--
Copy to <repo root>/.claude/project-triage-issues.md and adapt it. Every section is optional:
"Fetching issues" makes project-triage use this file instead of the code host's issues, and
"Upstream trackers" adds ways to search dependencies' trackers. A project whose issues stay on
its code host can keep only "Upstream trackers". This example uses jira-cli
(https://github.com/ankitpokhrel/jira-cli); replace the commands with the tool your team uses,
such as another CLI or a connected Jira app.
-->

## Requirements

- `jira` (jira-cli), set up with `jira init` for `https://example.atlassian.net`.
- Project key: `EX`.

## Who

`jira me` prints the user's account.

## Ownership

The user owns the project's issues if they're the project lead, or the issue's component is one they lead. Otherwise only issues assigned to them are listed.

## Fetching issues

- Owned: `jira issue list -q 'project = EX AND statusCategory != Done AND reporter != currentUser()' --plain --columns key,summary,reporter,assignee,status,updated`
- Not owned: `jira issue list -q 'project = EX AND statusCategory != Done AND assignee = currentUser()' --plain --columns key,summary,reporter,assignee,status,updated`
- `--mine --issues`: `jira issue list -q 'project = EX AND statusCategory != Done AND reporter = currentUser()' --plain`
- One issue with its comments: `jira issue view EX-123 --comments 50 --plain`

## Comments and actions

- Comment: `jira issue comment add EX-123 "<text>"`
- Change status: `jira issue move EX-123 "<status>"` (e.g. "In Progress", "Waiting for reporter")
- Close: `jira issue move EX-123 "Done"`, with a resolution if the workflow asks for one.

## Searching

`jira issue list -q 'project = EX AND text ~ "<words>"' --plain --columns key,summary,status`

## Upstream trackers

- `example/payments-sdk` (private package): issues in the same Jira, project `PAY`: `jira issue list -q 'project = PAY AND text ~ "<words>"' --plain`.
- `vendor/search-client`: the vendor's public Jira. Search with `curl -sS -G "https://issues.example.org/rest/api/2/search" --data-urlencode 'jql=project = SEARCH AND text ~ "<words>"' --data-urlencode fields=key,summary,status`.