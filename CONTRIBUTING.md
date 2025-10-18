# Contributing Guide

## Development Workflow

### Branch Structure

- `main` - Production-ready code (protected, requires PR)
- `develop` - Development branch for features (protected, requires PR)
- `feature/*` - Feature branches (e.g., `feature/new-api-endpoint`)
- `hotfix/*` - Critical bug fixes (e.g., `hotfix/security-patch`)
- `release/*` - Release preparation branches (e.g., `release/v1.1.0`)

### Branch Protection Rules

- **Main branch**: Requires 2 reviews, CI must pass, no direct pushes
- **Develop branch**: Requires 1 review, CI must pass, maintainers can bypass
- **Feature branches**: No restrictions, CI runs on PR

### Getting Started

1. **Fork the repository**
2. **Clone your fork**:

   ```bash
   git clone https://github.com/your-username/frappe_postman_sync.git
   cd frappe_postman_sync
   ```

3. **Set up upstream**:

   ```bash
   git remote add upstream https://github.com/souravs72/frappe_postman_sync.git
   ```

4. **Create feature branch**:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/your-feature-name
   ```

## Pull Request Process

### Before Submitting

1. **Test your changes**:

   ```bash
   bench --site your-site migrate
   bench --site your-site restart
   ```

2. **Run linting**:

   ```bash
   ruff check .
   ruff format .
   ```

3. **Update documentation** if needed

4. **Test the app functionality** thoroughly

### Submitting PR

1. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

2. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select `develop` as base branch
   - Fill in PR template (see below)

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tested on fresh Frappe installation
- [ ] Tested API generation functionality
- [ ] Tested Postman sync
- [ ] No breaking changes

## Checklist

- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No hardcoded secrets/values
- [ ] Generic and reusable code
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Approval** from at least one maintainer

## Issue Guidelines

### Bug Reports

Use this template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**

1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**

- Frappe Version:
- Python Version:
- Browser:
- OS:

**Error Logs**
Paste relevant error logs

**Screenshots**
If applicable
```

### Feature Requests

Use this template:

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this be implemented?

**Alternatives Considered**
Other solutions you've thought about

**Additional Context**
Any other relevant information
```

## Code Standards

### Python

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for functions
- No hardcoded secrets or specific values

### JavaScript

- Use consistent naming conventions
- Comment complex logic
- Follow Frappe's JS patterns

### Documentation

- Update README.md for significant changes
- Add inline comments for complex code
- Keep documentation concise and clear

## Security Guidelines

- **Never commit secrets** (API keys, passwords, etc.)
- **Use environment variables** for configuration
- **Validate all inputs** from users
- **Follow Frappe security best practices**

## Release Process

1. **Feature freeze** on develop branch
2. **Testing phase** with beta testers
3. **Create release branch** from develop
4. **Final testing** and bug fixes
5. **Merge to main** after approval
6. **Tag release** with version number
7. **Update changelog**

## Getting Help

- **GitHub Issues** for bug reports and feature requests
- **GitHub Discussions** for questions and general discussion
- **Frappe Forum** for Frappe-related questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
