# Security Guidelines

This document outlines security best practices for managing sensitive information in this repository.

## Secret Management

### Directory Structure
```
secrets/
├── .gitkeep                    # Ensures directory is tracked
├── secrets.example.env         # Example environment file (safe to commit)
├── secrets.env                 # Your actual secrets (DO NOT COMMIT)
├── github-app-private-key.pem  # GitHub App private key (DO NOT COMMIT)
└── README.md                   # Instructions (safe to commit)
```

### Setup Instructions

1. **Copy the example configuration:**
   ```bash
   cp config.example.ini config.ini
   cp secrets/secrets.example.env secrets/secrets.env
   ```

2. **Edit `config.ini` with non-sensitive settings:**
   - Project IDs
   - Domain names
   - File paths
   - Model configurations

3. **Edit `secrets/secrets.env` with sensitive values:**
   ```bash
   JIRA_API_KEY=your-actual-jira-api-key
   PRIVATE_KEY_PATH=./secrets/github-app-private-key.pem
   ```

4. **Place your GitHub App private key:**
   ```bash
   # Download your private key from GitHub App settings
   mv downloaded-key.pem secrets/github-app-private-key.pem
   chmod 600 secrets/github-app-private-key.pem
   ```

### Environment Variables

The application supports multiple ways to provide secrets (in order of precedence):

1. **Environment variables** (highest priority)
2. **secrets/secrets.env file**
3. **config.ini file** (for backward compatibility, not recommended for secrets)

#### Supported Environment Variables
- `JIRA_API_KEY` - Jira API token
- `PRIVATE_KEY_PATH` - Path to GitHub App private key file
- `GITHUB_TOKEN` - GitHub personal access token (alternative to App)

### Production Deployment

For production environments, use one of these approaches:

#### Option 1: Environment Variables
```bash
export JIRA_API_KEY="your-key"
export PRIVATE_KEY_PATH="/secure/path/to/key.pem"
python main.py
```

#### Option 2: Container Secrets
```dockerfile
# In your Dockerfile or docker-compose.yml
ENV JIRA_API_KEY_FILE="/run/secrets/jira_api_key"
ENV PRIVATE_KEY_PATH="/run/secrets/github_private_key"
```

#### Option 3: Cloud Secret Managers
- AWS Secrets Manager
- Azure Key Vault  
- Google Secret Manager
- HashiCorp Vault

## Security Best Practices

### File Permissions
```bash
# Restrict access to secrets directory
chmod 700 secrets/
chmod 600 secrets/secrets.env
chmod 600 secrets/*.pem
```

### What Never to Commit
- `config.ini` (contains your specific paths and settings)
- `secrets/*.env` (contains API keys and tokens)
- `secrets/*.pem` (private keys)
- `secrets/*.key` (any key files)
- `secrets/*.json` (service account files)

### What's Safe to Commit
- `config.example.ini` (template with placeholder values)
- `secrets/*.example.*` (example files with placeholder values)
- `secrets/.gitkeep` (ensures directory exists)
- `secrets/README.md` (documentation)

### Rotating Secrets

1. **Generate new API keys/tokens**
2. **Update secrets file or environment variables**
3. **Test the application**
4. **Revoke old credentials**

### Emergency Response

If secrets are accidentally committed:

1. **Immediately rotate all exposed credentials**
2. **Remove secrets from git history:**
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch secrets/secrets.env' \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push to remote repository**
4. **Notify team members to re-clone**

## Compliance Notes

- This setup supports SOC 2 Type II compliance
- Secrets are never logged or displayed in plain text
- File permissions restrict access to authorized users only
- Secrets can be managed through enterprise secret management systems