# Security Policy

## Overview

Company Intelligence is designed with security best practices to protect your API credentials and sensitive data. This document explains how we handle secrets, credentials, and sensitive information.

---

## 🔐 Credential Management

### How Credentials Are Stored

**n8n Credential Encryption:**

- All API keys, tokens, and credentials are **stored securely in n8n's encrypted database**, NOT in code or configuration files
- n8n uses **AES-256 encryption** for credential storage
- Credentials are encrypted at rest and never exposed in exported workflow JSON files
- The workflow export files only contain **credential IDs** (harmless references), not actual secrets

**Supabase Database:**

- Company data lives in Supabase (hosted Postgres)
- Row Level Security is enabled on all four company tables via `supabase/migrations/`
- Direct access from `public`, `anon`, and `authenticated` roles is revoked; only the backend's `service_role` can read the tables

**FastAPI Backend:**

- `SUPABASE_SECRET_KEY` lives only in `.env` on the server — it must never appear in frontend code, templates, or browser-visible responses
- The dashboard is a public page: anyone can view the data it displays, but they cannot query Supabase directly

**n8n Data Directory:**

- All encrypted credentials are stored in `n8n_data/` directory
- This directory is in `.gitignore` and should never be committed
- Back up this directory securely if you need to preserve credentials

### What's NOT in the Repository

The following are **intentionally excluded** from version control:

- `.env` files
- `n8n_data/` directory (encrypted credentials)
- API keys, tokens, or secrets of any kind

See `.gitignore` for complete exclusion list.

---

## 🚀 Setting Up Credentials Safely

### 1. Configure Credentials in n8n UI (Recommended)

When you first start the application:

1. **Access n8n**: Open `http://localhost:5678`
2. **Create Credentials**:
   - Go to **Settings** → **Credentials**
   - Click **New** for each credential type needed:
     - **AI provider APIs**: Groq, Google Gemini, OpenAI, etc.
     - **Supabase**: URL + secret key used by the workflows
     - **Discord Webhook**: Add your Discord webhook URL (optional)

3. **Import Workflows**:
   - Import the JSON files from `n8n-workflows/` (e.g. `companyNews.json`, `companyProfile.json`, ... etc)
   - The workflows automatically reference the credentials you created

**Advantages:**

- ✅ Credentials never leave n8n's secure storage
- ✅ Easy to rotate credentials
- ✅ Can revoke access without code changes
- ✅ Credentials stay encrypted in the database

### 2. Docker Environment Variables (For Advanced Users)

If you need to automate credential setup, n8n supports importing credentials via environment variables at startup. However, **we recommend the UI method above** for simplicity.

Credentials can be set via `docker-compose.yml`:

```yaml
environment:
  - N8N_CREDENTIALS_OVERWRITE_DATA='{"groqApi": {"apiKey": "${GROQ_API_KEY}"}}'
```

Then set environment variables before running:

```bash
export GROQ_API_KEY=your-key
docker-compose up -d
```

**Note:** Only do this if you understand Docker and secure environment variable handling.

---

## 🛡️ Best Practices

### API Keys

1. **Use Separate Keys for Different Environments**
   - Development key: Limited quota/permissions
   - Production key: Full permissions, monitored
   - Test key: For testing only

2. **Rotate Keys Regularly**
   - Groq API: Rotate every 90 days
   - Google APIs: Rotate every 90 days
   - NocoDB: Regenerate token if compromised

3. **Monitor API Usage**
   - Check your provider dashboards for unusual activity
   - Review n8n execution logs for failed requests
   - Monitor error logs in `profile and news - errors.csv`

### Discord Webhooks

1. **Webhook Security**
   - Discord webhooks are publicly accessible by URL
   - Treat webhook URLs as secrets (don't share them)
   - Regenerate if you suspect compromise

2. **Rotate Webhooks**
   - Recreate webhooks if they've been exposed
   - Update n8n credentials immediately

## 🚨 Incident Response

### If You Accidentally Committed a Secret

1. **Remove from Git History** (if secret was committed):

   ```bash
   # Use git-filter-branch or BFG Repo-Cleaner
   git filter-branch --tree-filter 'rm -f .env' HEAD
   git push --force-with-lease
   ```

2. **Rotate the Compromised Credential**:
   - Regenerate API keys immediately
   - Update credentials in n8n
   - Monitor for unauthorized usage

3. **Review Access Logs**:
   - Check API provider logs for suspicious activity
   - Monitor n8n execution logs

### If an API Key is Compromised

1. **Immediate Actions**:
   - Revoke the compromised key
   - Generate a new key
   - Update n8n credentials

2. **Investigation**:
   - Review API logs for unauthorized usage
   - Check workflow execution history in n8n
   - Monitor billing/quota usage

3. **Prevention**:
   - Use API key rotation policies
   - Implement rate limiting
   - Enable API provider security alerts

---

## 📋 Workflow Security

### What's in the Workflow Files?

The exported workflow JSON files in `n8n-workflows/` contain:

- ✅ Workflow logic and node configuration
- ✅ Credential ID references (NOT actual credentials)
- ✅ Data processing rules
- ✅ Error handling logic
- ❌ NO API keys, tokens, or secrets

**Safe to share:** You can safely share workflow files with others. They won't contain any secrets.

### Workflow Best Practices

1. **Error Logging**
   - See
   - Review these logs regularly for security issues
   - Don't include sensitive data in error messages

2. **Data Validation**
   - Workflows validate data before processing
   - Malformed requests are logged but not processed
   - Suspicious patterns are flagged

3. **Execution Logs**
   - Check n8n execution logs (`http://localhost:5678/workflows`)
   - Monitor for failed API calls
   - Review error patterns

---

## 📚 Additional Resources

- **n8n Security Docs**: https://docs.n8n.io/hosting/environment-variables/secure-credentials/
- **supabase Security Docs**: https://supabase.com/docs/guides/security/
- **Groq API Security**: https://console.groq.com/docs/api-overview
- **Google Gemini Security**: https://ai.google.dev/docs
- **Discord Webhook Security**: https://discord.com/developers/docs/resources/webhook

---

## ⚠️ Support & Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. **DO NOT** expose the vulnerability in the repository
3. Contact the repository maintainer privately
4. Allow time for a fix before public disclosure

### Security Best Practices Summary

| Practice                               | Why                          | How                          |
| -------------------------------------- | ---------------------------- | ---------------------------- |
| Never commit `.env` files              | Prevents credential leakage  | Use `.gitignore`             |
| Use n8n for credential storage         | Credentials are encrypted    | Configure in n8n UI          |
| Keep `SUPABASE_SECRET_KEY` server-side | Tables stay private via RLS  | `.env` + backend only        |
| Rotate credentials regularly           | Limits damage if compromised | Update credentials quarterly |
| Monitor API usage                      | Detect unauthorized access   | Check provider dashboards    |
| Backup securely                        | Disaster recovery            | Use encrypted backups        |
| Review error logs                      | Catch issues early           | Check workflow error logs    |

---

**Last Updated**: November 2026  
**Version**: 1.1  
**Maintainer**: iwaneth
