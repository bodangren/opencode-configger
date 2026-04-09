# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Test-Driven Development:** Write unit tests before implementing functionality
4. **High Code Coverage:** Aim for >80% code coverage for all modules
5. **User Experience First:** Every decision should prioritize user experience

## Task Workflow

1. Select next available task from `plan.md`
2. Mark as `[~]` (in progress)
3. Write failing tests (Red Phase)
4. Implement to pass tests (Green Phase)
5. Refactor if needed
6. Verify coverage: `CI=true pytest --cov=app --cov-report=html`
7. Commit with message: `<type>(<scope>): <description>`
8. Attach task summary with Git Notes
9. Update plan.md: mark `[x]` with commit SHA

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python -m app.main
```

### Test
```bash
CI=true pytest --cov=app --cov-report=html
```

## Quality Gates

- All tests pass
- Code coverage >80%
- No syntax errors (`python -m py_compile`)
- Type hints on public APIs
- Docstrings on public functions
