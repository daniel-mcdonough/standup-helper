# Secrets Directory

This directory contains sensitive configuration files that should never be committed to version control.

## Setup

1. Copy the example file:
   ```bash
   cp secrets.example.env secrets.env
   ```

2. Edit `secrets.env` with your actual API keys and credentials

3. Place your GitHub App private key file here (if using GitHub integration):
   ```bash
   mv your-github-app-key.pem github-app-private-key.pem
   chmod 600 github-app-private-key.pem
   ```

## Files in this directory

- `secrets.env` - Environment variables with API keys (DO NOT COMMIT)
- `*.pem` - Private key files (DO NOT COMMIT)  
- `*.key` - Any other key files (DO NOT COMMIT)
- `*.json` - Service account files (DO NOT COMMIT)
- `*.example.*` - Example files (safe to commit)
- `.gitkeep` - Ensures directory exists in git (safe to commit)
- `README.md` - This file (safe to commit)

## Security

All actual secret files are ignored by git. Only example files and documentation are tracked.