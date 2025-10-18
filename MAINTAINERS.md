# Maintainers Guide

## Repository Structure

```
frappe_postman_sync/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/              # CI/CD pipelines
│   └── ISSUE_TEMPLATE/         # Issue templates
├── frappe_postman_sync/        # Main app code
│   ├── doctype/               # DocTypes
│   ├── api/                   # API endpoints
│   └── hooks.py               # Frappe hooks
├── CONTRIBUTING.md            # Contribution guidelines
├── SECURITY.md               # Security policy
├── CHANGELOG.md              # Release notes
└── MAINTAINERS.md            # This file
```

## Branch Protection Rules

### Main Branch Protection

Configure these rules on GitHub:

1. **Require pull request reviews before merging**

   - Required number of reviewers: 1
   - Dismiss stale reviews when new commits are pushed: ✅
   - Require review from code owners: ✅

2. **Require status checks to pass before merging**

   - Require branches to be up to date before merging: ✅
   - Required status checks:
     - CI/CD Pipeline
     - Code Quality Check
     - Security Scan

3. **Require conversation resolution before merging**: ✅

4. **Restrict pushes that create files larger than 100MB**: ✅

5. **Allow force pushes**: ❌ (disabled)

6. **Allow deletions**: ❌ (disabled)

### Develop Branch Protection

Similar rules but with:

- Required reviewers: 0 (for maintainers)
- Allow force pushes: (for maintainers only)

## Release Process

### 1. Feature Development

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR to develop
git push origin feature/feature-name
```

### 2. Release Preparation

```bash
# Merge develop to main
git checkout main
git pull origin main
git merge develop

# Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Hotfix Process

```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-fix

# Make fixes and commit
git add .
git commit -m "fix: critical security issue"

# Merge to both main and develop
git checkout main
git merge hotfix/critical-fix
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

git checkout develop
git merge hotfix/critical-fix
```

## Code Review Guidelines

### For Reviewers

1. **Check for security issues**:

   - No hardcoded secrets
   - Proper input validation
   - Secure API usage

2. **Code quality**:

   - Follows project conventions
   - Proper error handling
   - Good documentation

3. **Testing**:
   - All tests pass
   - New features tested
   - No breaking changes

### For Contributors

1. **Before submitting**:

   - Run linting: `ruff check . && ruff format .`
   - Test thoroughly
   - Update documentation
   - Check for secrets

2. **PR requirements**:
   - Clear description
   - Link related issues
   - Add tests if needed
   - Update changelog

## Issue Management

### Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issue
- `priority: low`: Low priority issue
- `triage`: Needs review

### Milestones

- `v1.1.0`: Next minor release
- `v1.2.0`: Future minor release
- `Backlog`: Future consideration

## Security Management

### Regular Security Tasks

1. **Weekly**: Check for dependency vulnerabilities
2. **Monthly**: Review access permissions
3. **Quarterly**: Security audit of codebase

### Security Incident Response

1. **Immediate**: Assess and contain
2. **Within 24h**: Fix and test
3. **Within 48h**: Release patch
4. **Within 1 week**: Post-mortem

## Communication

### GitHub

- Issues: Bug reports and feature requests
- Discussions: General questions and ideas
- Pull Requests: Code contributions

### Release Announcements

- Update CHANGELOG.md
- Create GitHub release
- Post in Frappe forum (if applicable)

## Maintenance Tasks

### Weekly

- [ ] Review and triage new issues
- [ ] Check for dependency updates
- [ ] Review open pull requests

### Monthly

- [ ] Security audit
- [ ] Performance review
- [ ] Documentation review

### Quarterly

- [ ] Roadmap planning
- [ ] Dependency major updates
- [ ] Community feedback review

## Backup and Recovery

### Repository Backup

- GitHub provides automatic backups
- Regular exports to external storage
- Multiple maintainer access

### Data Recovery

- All code is version controlled
- Issues and PRs are backed up by GitHub
- Documentation is in the repository

## Contact Information

### Maintainers

- Primary: [Your Name] - [your-email@domain.com]
- Secondary: [Backup Maintainer] - [backup-email@domain.com]

### Security Contact

- Security: security@yourdomain.com

### Community

- GitHub Discussions: For general questions
- GitHub Issues: For bugs and features
- Frappe Forum: For Frappe-related questions
