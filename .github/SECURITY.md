# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should not be disclosed publicly until they have been addressed.

### 2. Report privately

Please report security vulnerabilities privately by:

- **Email**: Send details to souravsingh2609@gmail.com
- **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature

### 3. Include the following information:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)
- Your contact information

### 4. Response timeline

We will respond to security reports within **48 hours** and provide regular updates on our progress.

### 5. Disclosure

We will coordinate with you to disclose the vulnerability after it has been fixed and we've had time to verify the fix works.

## Security Best Practices

### For Contributors

- **Never commit secrets**: API keys, passwords, or sensitive data
- **Use environment variables**: For configuration and secrets
- **Validate inputs**: Always validate user inputs
- **Follow Frappe guidelines**: Adhere to Frappe's security best practices
- **Regular updates**: Keep dependencies updated

### For Users

- **Keep Frappe updated**: Use the latest stable version of Frappe
- **Secure your environment**: Use HTTPS, secure passwords, and proper access controls
- **Monitor logs**: Regularly check error logs for suspicious activity
- **Backup regularly**: Maintain regular backups of your data

## Security Considerations

This app handles:

- **API Keys**: Postman API keys (stored encrypted)
- **Network Requests**: Makes HTTP requests to Postman API
- **Data Processing**: Processes DocType metadata

### Data Handling

- API keys are encrypted using Frappe's built-in encryption
- No sensitive data is logged
- Network requests use HTTPS only
- Input validation is implemented for all user inputs

## Security Audit

We regularly audit our codebase for:

- Hardcoded secrets
- Vulnerable dependencies
- Input validation issues
- Authentication/authorization problems

## Contact

For security-related questions or concerns:

- **Email**: souravsingh2609@gmail.com
- **GitHub**: Use private vulnerability reporting

Thank you for helping keep Frappe Postman Sync secure!
