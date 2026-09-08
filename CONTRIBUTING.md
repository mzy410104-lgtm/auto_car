# Git and GitHub Collaboration Guide for the Three-Person Team

Git records file versions. GitHub provides a shared repository, Issues, Pull Requests and Projects. This project uses one main branch and short-lived task branches, rather than three long-lived member versions that are never integrated.

## 1. Managing each task

1. In an Issue, state the problem/goal, owner, related plan tasks, dependencies and completion evidence. The six initial tasks are listed in [TASK_BOARD.md](TASK_BOARD.md).
2. Select one clearly bounded task at a time. If several members participate, name them and continue to count each person's actual time in the plan.
3. Create a task branch from an up-to-date main branch, then edit source code, configuration, documentation or test records there.
4. Review the diff, stage only files belonging to this task, commit and push the branch.
5. Open a Pull Request describing what changed, why, what has been verified and the related Issue. Have another teammate review it.
6. After merging, update the task according to actual completion evidence. A commit or merged PR does not automatically establish that a hardware task has passed.

GitHub accounts have not yet been mapped to A/B/C; role labels cannot be used to assign unconfirmed accounts. Maintain task status according to the team's rules. Status names in repository files do not mean matching GitHub Projects fields have been configured.

## 2. Daily operations

For their first checkout, other members run the following in their chosen parent directory:

```sh
git clone https://github.com/mzy410104-lgtm/auto_car.git
cd auto_car
```

Do not initialize or clone an existing local repository again. Run the following inside the actual repository directory:

```sh
git status -sb
git remote -v
git branch --show-current
```

After confirming that current changes are safely preserved, the main branch is actually named main and its upstream is configured, synchronize:

```sh
git switch main
git pull --ff-only
```

The project convention is `task/` followed by the actual task identifier. Specify the complete branch name for the task at hand. Check for an existing branch with that name before creating it; a documentation example does not establish an existing branch.

```text
git switch -c <exact-new-branch-name>
git diff
git add -- <actual-file-paths-changed-for-this-task>
git diff --cached
git commit -m "Describe the specific change"
git push --set-upstream <name-verified-in-git-remote> <exact-current-branch-name>
```

Replace all angle-bracket placeholders; do not run them literally. Do not stage the entire working directory for convenience. Create the PR on GitHub after pushing, and verify its actual source branch and target main branch on the page.

If pull --ff-only fails because histories have diverged, retain the error and existing changes, then inspect both histories before resolving the issue. Force-pushing, hard resets and deleting untracked files are not default repairs.

## 3. Record three types of results separately

| Record | What it establishes | What it does not establish |
|---|---|---|
| Commit / PR | File changes, review and integration | Correct hardware operation |
| Build / flashing record | Project build and programming process | Main-program execution or successful communication/control |
| Measured test record | Results under the recorded wiring, software version and conditions | Success under conditions that were not tested |

Use the [test-record template](tests/records/TEMPLATE.md). Record the commit, actual power/wiring, data, test duration, success/failure and next step. Leave missing results as pending evidence; do not enter example voltages or speeds as if they were measured.

## 4. Coordinating files and equipment

- A primarily maintains hardware, power and mechanical records; B maintains Raspberry Pi and lidar software; C maintains the STM32 project. B/C jointly review agreements in interfaces.
- Coordinate ownership before changing the same wiring record, interface or CubeMX project, to avoid conflicting simultaneous edits.
- Git branches isolate file edits, not physical wiring. Schedule rewiring, stationary scans and motion tests on the single vehicle according to the work plan.
- No actual firmware or Raspberry Pi project has been imported yet. Preserve the original project and dependency evidence on import, then add ignore rules based on actual build outputs. Do not invent generated directories or pin assignments.
- tmp, local configuration, downloaded manufacturer copies and large raw data remain local under .gitignore. Measurement tables, small logs and data indexes may be committed to tests/records.
- Check the content and source of each public submission. Store team credentials in Git credential-management tools or local configuration, not in the repository.

## 5. Starting three-person collaboration

1. After confirming the other two members' exact GitHub accounts, the repository owner adds them as collaborators and the members accept the invitations.
2. Each member clones the actual repository URL into their own working directory and uses their own real Git commit identity.
3. Each member selects a defined task, submits a small change and reviews another member's work. Do not modify another person's local working directory.
4. At the weekly review, update Issues with actual time spent, results, blockers and next steps; retain the overall arrangements in the work-plan documents.

The current decision is not to invite collaborators yet. No invitations have been sent and no GitHub accounts have been assigned to A/B/C. Confirm exact accounts when team collaboration begins. After the initial import, changes to main are recommended through PRs. This is a team convention; server-side branch protection requires separate verification.

## Official references

- [Git initialization](https://git-scm.com/docs/git-init), [diff inspection](https://git-scm.com/docs/git-diff), [pushing](https://git-scm.com/docs/git-push).
- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow), [Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).

These operation instructions were checked through Context7 and official documentation. Actual commands must still reflect the current repository state and verified identifiers.
