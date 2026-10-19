## What does this PR do?

<!-- One or two sentences. Link the related issue: Closes #N -->

## Type of change

- [ ] Bug fix
- [ ] New feature / domain / tooling script
- [ ] Documentation improvement
- [ ] CI / tooling change
- [ ] Refactor (no behaviour change)

## Checklist

- [ ] Tests pass locally: `python -m unittest discover -s tests -v`
- [ ] `bandit -r tooling/ -f txt -ll` produces no new HIGH or MEDIUM findings
- [ ] `pip-audit -r requirements-dev.txt` passes with no known CVEs
- [ ] Any new examples have secrets redacted and a scope/authorization note
- [ ] `DEVELOPER_GUIDE.md` updated if the repo structure changed
- [ ] `README.md` and `SKILL.md` domain tables updated if a new reference file was added

## Notes for reviewers
