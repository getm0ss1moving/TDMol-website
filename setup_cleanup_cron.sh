#!/bin/bash
# Setup cron job for automatic cleanup
# This script adds a cron job that runs cleanup_old_tasks.py daily at 2 AM

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup_old_tasks.py"

# Make cleanup script executable
chmod +x "$CLEANUP_SCRIPT"

# Create cron job entry
CRON_JOB="0 2 * * * /usr/bin/python3 $CLEANUP_SCRIPT >> $SCRIPT_DIR/logs/cleanup_cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$CLEANUP_SCRIPT"; then
    echo "Cron job for cleanup already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully"
    echo "Cleanup will run daily at 2:00 AM"
fi

echo ""
echo "Current crontab:"
crontab -l
