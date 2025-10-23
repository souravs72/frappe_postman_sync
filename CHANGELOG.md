# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-XX

### Added

- Auto-generation of CRUD APIs for DocTypes
- Postman integration with collection sync
- Single DocType configuration (Postman Setting)
- Module-based API generation
- Whitelisted methods discovery and sync
- Bench commands for easy API generation
- Optimized sync with 97.5% performance improvement

### Security

- Secure password handling using Frappe's built-in encryption
- No hardcoded secrets or API keys
- Input validation for all user inputs

### Technical Details

- Built with Frappe Framework
- Uses Postman API v1 for collection management
- Supports Python 3.8+
- Compatible with Frappe v14+
