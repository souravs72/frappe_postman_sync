# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release of Frappe Postman Sync
- Auto-generation of CRUD APIs for DocTypes
- Postman integration with collection sync
- Single DocType configuration (Postman Setting)
- Module-based API generation
- Whitelisted methods discovery and sync
- Clean request body templates with field filtering
- Comprehensive documentation and setup guides

### Security

- Secure password handling using Frappe's built-in encryption
- No hardcoded secrets or API keys
- Input validation for all user inputs

## [1.0.0] - 2024-01-XX

### Added

- Complete Frappe Postman Sync implementation
- Automatic API generation on DocType creation
- Postman API integration with secure credential management
- API Generator DocType for managing generated APIs
- Clean field filtering (excludes auditable/system fields)
- Comprehensive error handling and validation
- Developer-friendly documentation

### Technical Details

- Built with Frappe Framework
- Uses Postman API v1 for collection management
- Supports Python 3.8+
- Compatible with Frappe v14+

---

## Release Notes Format

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Breaking Changes

Breaking changes will be clearly marked and include migration instructions.
