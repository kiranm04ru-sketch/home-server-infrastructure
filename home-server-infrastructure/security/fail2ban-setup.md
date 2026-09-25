# Fail2ban: Brute-Force Protection

## What It Does

Monitors log files for failed login attempts. When a threshold is reached, bans the attacker's IP address for a set duration.

**Example:**
- IP 192.168.1.100 attempts SSH login 3 times (fails all)
- Within 10 minutes
- IP is blocked from SSH for 1 hour
- After 1 hour, block is lifted

## How It Works

1. Fail2ban watches `/var/log/auth.log` continuously
2. Detects pattern: "Failed password for X from Y"
3. Tracks failures by IP address
4. When failures exceed threshold → Ban IP using iptables
5. Ban persists for configured duration
6. Auto-unban after time expires

## Configuration

### Default Settings (SSH)
- **maxretry:** 3 failed attempts
- **findtime:** 600 seconds (10 minutes)
- **bantime:** 3600 seconds (1 hour)

**Translation:** 3 failed logins in 10 minutes → 1 hour ban

### Why These Values?
- **3 attempts:** User might mistype password 2x, should have 3rd chance
- **10 minutes:** Reasonable time window for "attack"
- **1 hour:** Long enough to stop attack, user can try again later

## Commands

```bash
# Check status
sudo fail2ban-client status sshd

# See banned IPs
sudo iptables -L -n | grep FAIL2BAN

# Manually ban IP
sudo fail2ban-client set sshd banip 192.168.1.100

# Manually unban IP
sudo fail2ban-client set sshd unbanip 192.168.1.100

# Check jail configuration
sudo fail2ban-client get sshd maxretry
```

## Security Effectiveness

### What It Protects Against
- Dictionary attacks (common password lists)
- Brute-force password guessing
- Credential stuffing (leaked password lists)

### What It Doesn't Protect Against
- Compromised SSH keys (use key-only auth)
- Vulnerable applications
- DDoS attacks (need different tools)
- Insider threats

## Combined with Other Protections

Fail2ban is one layer:

1. **Firewall (UFW)** - Block unnecessary ports
2. **Fail2ban** - Stop brute-force attempts
3. **SSH Hardening** - Disable passwords, use keys only
4. **Monitoring** - Alert on suspicious activity

Together = Defense in depth

## Logs

```bash
# View Fail2ban activity
sudo tail -f /var/log/fail2ban.log

# View SSH failures
sudo grep "Failed password" /var/log/auth.log | tail -20

# View bans
sudo grep "Ban " /var/log/fail2ban.log | tail -10
```

## Next Steps

- Monitor logs regularly
- Adjust maxretry based on experience
- Combine with SSH key-only authentication (Week 2 Part 3)
- Add more services (web app rate limiting, database protections)
