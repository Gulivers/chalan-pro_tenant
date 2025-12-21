# Git: Sync Local and Remote Branches

This guide explains how to synchronize (homologate) your local and remote Git branches step by step.

## Overview

When working with Git, it's important to keep your local branches synchronized with the remote repository. This ensures that:
- Your local code matches what's in the remote repository
- You have the latest changes from other team members
- Your commits are properly shared with the team

## Step-by-Step Guide

### 1. Check Current Status

First, verify your current branch and status:

```bash
cd /opt/chalanpro/app
git status
```

**Output example:**
```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

This tells you:
- Which branch you're on
- If your local branch is ahead or behind the remote
- If there are uncommitted changes

### 2. Fetch Latest Changes from Remote

Fetch all the latest information from the remote repository (this doesn't change your local code):

```bash
git fetch origin
```

This command:
- Downloads the latest changes from the remote repository
- Updates your local references to remote branches
- **Does NOT merge or modify your local branches**

### 3. Check Commit History

Compare your local commits with the remote:

**View local commits:**
```bash
git log --oneline -5
```

**View remote commits:**
```bash
git log --oneline origin/main -5
```

This helps you see:
- Which commits are in your local branch
- Which commits are in the remote branch
- If there are differences between them

### 4. Synchronize Branches

#### Scenario A: Local is Ahead (has commits not in remote)

If your local branch is ahead (like in our example), push your commits to the remote:

```bash
git push origin main
```

**Output example:**
```
To github.com:Gulivers/chalan-pro_tenant.git
   8ee3049..2b99c06  main -> main
```

This pushes your local commits to the remote repository.

#### Scenario B: Remote is Ahead (has commits you don't have locally)

If the remote has commits you don't have locally, pull the changes:

```bash
git pull origin main
```

Or if you prefer to see what will be merged first:

```bash
git fetch origin
git merge origin/main
```

#### Scenario C: Branches have Diverged (both have different commits)

If both branches have different commits, you need to merge or rebase:

**Option 1: Merge (creates a merge commit)**
```bash
git pull origin main
```

**Option 2: Rebase (replays your commits on top of remote)**
```bash
git fetch origin
git rebase origin/main
```

⚠️ **Warning:** Only rebase if you're working alone on this branch or have coordinated with your team.

### 5. Verify Synchronization

After synchronizing, verify that everything is in sync:

```bash
git status
```

**Expected output when synchronized:**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## Complete Workflow Example

Here's the complete workflow we just performed:

```bash
# 1. Navigate to the repository
cd /opt/chalanpro/app

# 2. Check current status
git status

# 3. Switch to main branch (if not already on it)
git checkout main

# 4. Fetch latest information from remote
git fetch origin

# 5. Compare local and remote commits
git log --oneline -5
git log --oneline origin/main -5

# 6. Push local commits to remote (if local is ahead)
git push origin main

# 7. Verify synchronization
git status
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `git status` | Shows current branch status and if it's ahead/behind remote |
| `git fetch origin` | Downloads latest changes from remote without merging |
| `git pull origin main` | Fetches and merges remote changes into local branch |
| `git push origin main` | Pushes local commits to remote branch |
| `git log --oneline -5` | Shows last 5 commits in one-line format |
| `git log --oneline origin/main -5` | Shows last 5 commits from remote branch |
| `git branch -a` | Lists all local and remote branches |
| `git checkout main` | Switches to main branch |

## Tips and Best Practices

1. **Always check status first**: Run `git status` before pushing or pulling
2. **Fetch before pulling**: Use `git fetch` to see what will change before merging
3. **Keep branches updated**: Regularly sync your branches to avoid conflicts
4. **Pull before pushing**: If working with a team, pull first to get latest changes
5. **Work on feature branches**: Avoid working directly on `main` to keep it stable
6. **Commit frequently**: Small, frequent commits are easier to sync and manage

## Troubleshooting

### "Your branch and 'origin/main' have diverged"

This means both branches have different commits. You need to merge or rebase:

```bash
git pull origin main --no-rebase  # Merges with a merge commit
# or
git pull --rebase origin main     # Rebases your commits
```

### "Updates were rejected because the remote contains work"

Your local branch is behind the remote. Pull first, then push:

```bash
git pull origin main
git push origin main
```

### "Permission denied" or authentication errors

Check your SSH keys or Git credentials:

```bash
git remote -v  # Check remote URL
# If using HTTPS, you may need to update credentials
```

## Summary

To keep your local and remote branches synchronized:

1. **Check status** with `git status`
2. **Fetch changes** with `git fetch origin`
3. **Push** if local is ahead: `git push origin main`
4. **Pull** if remote is ahead: `git pull origin main`
5. **Verify** with `git status` that branches are synchronized

Remember: The goal is to have `git status` show "Your branch is up to date with 'origin/main'".

