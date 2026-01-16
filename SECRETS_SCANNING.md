# Secrets and Credentials Scanning

This repository includes automated secrets and credentials scanning using [Gitleaks](https://github.com/gitleaks/gitleaks).

## Workflow Triggers

The secrets scanning workflow (`.github/workflows/secrets-scan.yml`) is triggered on:

1. **Manual Dispatch**: Can be manually triggered from the GitHub Actions tab
2. **Pull Requests**: Automatically runs on all pull requests against any branch

## What It Scans For

Gitleaks scans for:
- AWS credentials (Access Keys, Secret Keys)
- API keys and tokens
- Database passwords
- Private keys (SSH, PGP, etc.)
- OAuth tokens
- Generic secrets following common patterns
- And many more credential types

## How to Use

### Automatic Scanning
The workflow automatically runs whenever a pull request is created or updated.

### Manual Scanning
1. Go to the **Actions** tab in the GitHub repository
2. Select **Secrets and Credentials Check** workflow
3. Click **Run workflow**
4. Select the branch to scan
5. Click **Run workflow** button

## What Happens When Secrets Are Found

If secrets are detected:
- The workflow will fail
- The pull request check will show as failed
- Details about the detected secrets will be available in the workflow logs
- The pull request should not be merged until the secrets are removed

## Remediation Steps

If secrets are found:
1. Remove the secrets from the code
2. Use environment variables or GitHub Secrets instead
3. Rotate any exposed credentials immediately
4. Update the pull request with the fixes

## Best Practices

- **Never commit secrets**: Use environment variables or secret management systems
- **Use GitHub Secrets**: For workflow secrets, use GitHub Actions secrets
- **Rotate compromised credentials**: If secrets are accidentally committed, rotate them immediately
- **Review before committing**: Always review your changes before committing

## Additional Resources

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [AWS Credentials Best Practices](https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html)
