#!/bin/bash

echo "=== Fail2ban Status ==="
sudo fail2ban-client status sshd
echo ""
echo "=== SSH Jail Configuration ==="
sudo cat /etc/fail2ban/jail.local | grep -A 10 "^\[sshd\]"
echo ""
echo "=== Currently Banned IPs ==="
sudo iptables -L -n | grep FAIL2BAN || echo "No bans active"
echo ""
echo "=== Auth Log (Last 10 failed attempts) ==="
sudo grep "Failed password" /var/log/auth.log | tail -10
