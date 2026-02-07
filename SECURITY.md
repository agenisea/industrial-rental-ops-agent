# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Ops Agent, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainers directly or use GitHub's private vulnerability reporting feature
3. Include a detailed description of the vulnerability
4. Provide steps to reproduce if possible

We will respond within 48 hours and work with you to understand and address the issue.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | Yes                |

## Security Considerations

### API Keys

- Never commit API keys to the repository
- Use `.env` for local development (gitignored by default)
- In production, use environment variables from your hosting provider

### Input Validation

All user inputs are validated using Pydantic schemas before processing.

## Best Practices for Deployment

1. Use HTTPS in production
2. Configure security headers on your reverse proxy
3. Monitor Anthropic API usage and costs
4. Consider adding authentication for production use

## Anthropic API Costs

This app uses the Anthropic Claude API, which has usage costs:
- Monitor your Anthropic dashboard for usage
- Consider implementing rate limits for public deployments
