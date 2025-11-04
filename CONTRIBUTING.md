# Contributing to Auto-Revision Epistemic Engine

Thank you for your interest in contributing to the Auto-Revision Epistemic Engine! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- System information (OS, Python version)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- Clear use case description
- Proposed solution or approach
- Any relevant examples

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/ -v`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/auto-revision-epistemic-engine.git
cd auto-revision-epistemic-engine

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black isort

# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v
```

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Architecture Principles

1. **Maintain Audit Trail Integrity**: Never modify code that could break the audit chain
2. **Respect Ethical Axioms**: All changes must comply with ethical guidelines
3. **Preserve Reproducibility**: Ensure changes don't break reproducibility features
4. **Document Governance**: Update documentation for governance-related changes
5. **Test Thoroughly**: Add tests for all new functionality

### Testing

- Write unit tests for new functionality
- Ensure tests are isolated and don't depend on external state
- Use fixtures for common test setup
- Aim for high code coverage (>80%)

### Documentation

- Update DOCUMENTATION.md for major changes
- Add inline comments for complex logic
- Include examples in docstrings
- Update README.md if necessary

## Component Guidelines

### Audit Logger
- Never modify historical entries
- Always maintain chain integrity
- Use BLAKE3 for hashing
- Log all significant events

### State Manager
- Ensure snapshots are immutable
- Maintain reproducibility guarantees
- Hash all state data
- Version all configurations

### Ethics Framework
- Clearly document new axioms
- Specify enforcement levels
- Test normative audits
- Consider edge cases

### Resource Optimization
- Validate allocation algorithms
- Test waste calculations
- Document threshold changes
- Consider performance impact

### Human Review Gates
- Maintain SLA compliance
- Test escalation logic
- Document review workflows
- Ensure auditability

### Phase Manager
- Preserve phase ordering
- Test state transitions
- Document phase requirements
- Handle errors gracefully

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Brief description

Longer explanation of what changed and why.
Fixes #123
```

## Review Process

1. Automated tests must pass
2. Code coverage should not decrease
3. Changes must align with project architecture
4. Documentation must be updated
5. At least one maintainer approval required

## Questions?

If you have questions about contributing, please:
- Check existing issues and documentation
- Create a discussion topic
- Reach out to maintainers

Thank you for contributing! 🚀
