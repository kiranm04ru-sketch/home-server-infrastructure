#!/bin/bash

echo "=== Testing Nginx ==="
sudo systemctl status nginx
echo ""
echo "=== Testing PostgreSQL ==="
sudo systemctl status postgresql
echo ""
echo "=== Checking Nginx Port (80) ==="
sudo ss -tlnp | grep nginx
echo ""
echo "=== Checking PostgreSQL Port (5432) ==="
sudo ss -tlnp | grep postgres
echo ""
echo "=== Testing PostgreSQL Connection ==="
sudo -u postgres psql -c "SELECT version();"
