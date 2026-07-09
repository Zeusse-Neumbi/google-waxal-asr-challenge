# Skill: github

## Purpose
Git hygiene, branching, PRs, and CI for the project.

## Inputs
- Branch name, PR title, target branch.

## Outputs
- Branches, PRs, CI runs.

## Best Practices
- Branch from `dev`; PR into `dev`.
- Use conventional-commit PR titles.
- Never force-push `main` or `dev`.
- Never commit secrets/datasets/checkpoints.
- Keep PRs small and focused.

## Common Mistakes
- Committing `data/raw/` or `outputs/` accidentally.
- Long-lived feature branches with merge conflicts.
- Skipping CI before merge.

## Examples
```bash
git checkout dev && git pull
git checkout -b feature/whisper-baseline
# ... commit ...
gh pr create --base dev --title "feat(models): add whisper baseline"
```

## References
- `.github/` for CI, templates, CODEOWNERS.
