# SSL/TLS (HTTPS) Configuration

## What SSL/TLS Does

Encrypts traffic between client and server. Without it:
- Passwords sent in plaintext
- Data visible to network eavesdroppers

With HTTPS:
- All traffic encrypted
- Only client and server can read it
- Attacker sees gibberish even if they intercept

## Certificate Types

### Self-Signed (What We Use)
- Generate yourself
- No trusted authority
- Browsers show warning
- **Use:** Development, testing, internal systems
- **Cost:** Free
- **Trust:** Low (browser warns)

### Let's Encrypt (Production)
- Free certificate from trusted authority
- Browsers trust it (no warning)
- Auto-renews every 90 days
- **Use:** Production, public domains
- **Cost:** Free
- **Trust:** High (globally trusted)

## Current Setup: Self-Signed for Testing

### Certificate Location

Private Key: /etc/ssl/private/self-signed.key
Certificate: /etc/ssl/certs/self-signed.crt


### Nginx Configuration
Two server blocks:
1. Port 80 (HTTP) → Redirects to HTTPS
2. Port 443 (HTTPS) → Serves with SSL

### TLS Versions
- TLSv1.2 and TLSv1.3 only (modern, secure)
- TLSv1.0, 1.1 disabled (vulnerable)

### Cipher Suites
- HIGH encryption only
- No weak algorithms (aNULL, MD5)
- Server ciphers preferred

## Testing

```bash
# Test HTTP redirect to HTTPS
curl -i http://localhost

# Test HTTPS (ignore self-signed warning)
curl -k https://localhost

# Check certificate details
openssl x509 -in /etc/ssl/certs/self-signed.crt -text -noout
```

## Production Upgrade: Let's Encrypt

When you have a real domain (example.com):

```bash
# Install and auto-configure
sudo certbot --nginx -d example.com

# Let's Encrypt certificate is auto-installed
# Browser warning disappears
# Auto-renews every 90 days
```

Certbot will:
- Get certificate from Let's Encrypt
- Auto-update Nginx config
- Set up renewal cron job
- Redirect HTTP to HTTPS

## Security Best Practices

✅ HTTPS-only (HTTP redirects)
✅ TLS 1.2+ (disable old versions)
✅ Strong ciphers
✅ HSTS header (force HTTPS on reload)
