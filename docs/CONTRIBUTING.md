# Contributing to Nyamuk

Thank you for your interest in contributing to Nyamuk!

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Docker (for testing)

### Clone Repository

```bash
git clone https://github.com/thefulan123/nyamuk-mqtt.git
cd nyamuk-mqtt
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Setup Pre-commit Hooks

```bash
pre-commit install
```

## Code Style

### Python Code

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use `ruff` for linting

```bash
# Check code style
ruff check nyamuk/

# Format code
ruff format nyamuk/
```

### Docstrings

Use Google-style docstrings:

```python
def add_user(username: str, password: str) -> Tuple[bool, str]:
    """Add a new MQTT user.
    
    Args:
        username: MQTT username (3-20 chars, alphanumeric)
        password: Password (min 8 chars)
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Examples:
        >>> manager.add_user("esp32", "password123")
        (True, "User added successfully")
    """
```

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=nyamuk

# Run specific test
pytest tests/test_core/test_mosquitto.py -v
```

### Write Tests

Create tests in `tests/` directory:

```python
import pytest
from nyamuk.core.user_manager import UserManager

def test_validate_username():
    manager = UserManager()
    
    # Valid username
    valid, msg = manager.validate_username("esp32_sensor")
    assert valid is True
    
    # Invalid username (too short)
    valid, msg = manager.validate_username("ab")
    assert valid is False
```

## Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Add tests
5. Update documentation
6. Run linter: `ruff check nyamuk/`
7. Run tests: `pytest tests/ -v`
8. Commit changes: `git commit -m "Add my feature"`
9. Push to branch: `git push origin feature/my-feature`
10. Create Pull Request

### Commit Messages

Use conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code style changes
refactor: Code refactoring
test: Add tests
chore: Maintenance tasks
```

## Reporting Bugs

Use the bug report template when opening an issue.

Include:
- Operating system
- Python version
- Nyamuk version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages

## Feature Requests

Use the feature request template.

Include:
- Problem description
- Proposed solution
- Alternatives considered
- Additional context

## Code of Conduct

- Be respectful
- Be constructive
- Be helpful

## Questions?

- Check documentation
- Search existing issues
- Create new issue
