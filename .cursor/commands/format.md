# Format & Lint Changes

## Overview

Run all relevant formatting, linting, and prettifying commands before committing any changes.  
This command ensures the codebase is clean and consistent by:

- Formatting modified files
- Linting modified files
- Failing fast on any errors
- Running tasks as efficiently and in parallel as safely possible

> **Note:** This command is intended to be run *before* the `command.md` "Commit PR" flow.

---

## Steps

### 1. Safety & Branch Checks

1. Detect the current branch.
2. **If on `main` (or the repository’s primary protected branch):**
   - **Do not make any changes.**
   - Surface a clear error:  
     > "You are on `main`. Switch to a feature branch before running the format command."

---

### 2. Repository-Level Tidy (Default Workflow)

From the **repository root**, run the standard repo-wide tidy command:

```bash
rush tidy --sha main
