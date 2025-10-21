# Security Policy

## Supported Versions

We actively support the following versions of questionary-extended with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in questionary-extended, please report it to us responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to: `security@questionary-extended.dev` (or your actual security email)
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Any suggested fixes (if available)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress toward fixing the vulnerability
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Disclosure**: We will coordinate with you on the timing of public disclosure

### Security Best Practices

When using questionary-extended:

1. **Input Validation**: Always validate user input, especially in production environments
2. **Dependencies**: Keep dependencies up to date to receive security patches
3. **Environment**: Use virtual environments to isolate dependencies
4. **Secrets**: Never log or display sensitive information entered through prompts

### Security Considerations

questionary-extended processes user input through terminal interfaces. Be aware that:

- User input may contain special characters or escape sequences
- Terminal history may store sensitive information
- Screen sharing or recording may capture sensitive prompts
- Consider using password-type prompts for sensitive data

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 0.1.1, 0.1.2)
- Documented in the CHANGELOG.md
- Announced through GitHub releases
- Tagged with security labels

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities (with permission).

---

Thank you for helping keep questionary-extended and its users safe!