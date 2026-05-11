# Contributing

This repository uses a simple branch-based workflow.

## Rules

- Never commit directly to `main`
- Create one branch per feature or fix
- Merge the latest `origin/main` into your branch regularly
- Open a Pull Request to merge into `main`
- Prefer `Squash and merge` on GitHub
- Do not use force-push in this workflow

## Branch Naming

Use one of these patterns:

```text
feature/short-description
fix/short-description
docs/short-description
chore/short-description
```

Examples:

```text
feature/monte-carlo-pricing
fix/payoff-bug
docs/readme-setup
chore/update-gitignore
```

## Commit Style

Use short imperative commit messages:

```text
feat: add basket option circuit
fix: correct discount factor formula
docs: clarify local setup
chore: remove unused notebook output
```

## One-Time Setup

```bash
git clone https://github.com/TelesforoAleix/quantum-finance.git
cd quantum-finance
git config pull.ff only
git config fetch.prune true
git switch main
git pull origin main
```

## Start A New Branch

Always branch from an up-to-date `main`:

```bash
git switch main
git pull origin main
git switch -c feature/short-description
```

## Daily Workflow

Start work and sync with `main`:

```bash
git fetch origin
git switch feature/short-description
git merge origin/main
```

Check your changes:

```bash
git status
```

Commit your work:

```bash
git add -A
git commit -m "feat: short description"
```

Push your branch.

First push:

```bash
git push -u origin feature/short-description
```

Later pushes:

```bash
git push
```

## Pull Request Workflow

Open the Pull Request on GitHub with:

- Base branch: `main`
- Compare branch: `feature/short-description`

Use a Draft PR until the feature is ready.

Before requesting review or merging, update the branch again:

```bash
git fetch origin
git switch feature/short-description
git merge origin/main
git push
```

When approved, merge on GitHub with `Squash and merge`.

After merge, clean up locally:

```bash
git switch main
git pull origin main
git branch -D feature/short-description
```

## Conflict Resolution Basics

If `git merge origin/main` reports conflicts:

```bash
git status
```

Resolve each conflicted file by removing the markers and keeping the correct content:

```text
<<<<<<< HEAD
your changes
=======
changes from main
>>>>>>> origin/main
```

Then finish the merge:

```bash
git add -A
git commit
git push
```

If you want to stop and try again later:

```bash
git merge --abort
```

## PR Description Template

Copy this into the PR body if needed:

```md
## Summary
What changed?

## Why
Why is this needed?

## Testing
What did you run or verify?

## Notes
Risks, follow-ups, or anything reviewers should watch for.

## Checklist
- [ ] Branch is up to date with main
- [ ] Changes are scoped to one feature or fix
- [ ] I tested the change
- [ ] Ready for review
```