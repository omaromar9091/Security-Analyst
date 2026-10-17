# Contributing

Thanks for your interest in improving Security-Analyst. These notes explain the preferred workflow and minimal expectations for contributions.

- File issues for bugs, documentation gaps, or suggested improvements using the issue templates.
- Open a small, focused pull request per change. Link the related issue when appropriate.
- Keep changes to documentation and examples well explained — include the reason and any safety considerations.
- Run the repo checks before opening a PR:

```bash
python -m unittest discover -s tests -v
```

- If you add code or examples that require extra packages, list them in `requirements-dev.txt` and add a CI step.

Code style and tests
- Python code should be compatible with Python 3.11+.
- For small scripts, keep dependencies minimal; prefer the stdlib when practical.

Security and scope
- This repository is for defensive analysis only. Do not add tools or examples that enable unauthorized access, exploitation, or data exfiltration.
- When adding examples, redact any real secrets or PII and add a note in the example metadata.
