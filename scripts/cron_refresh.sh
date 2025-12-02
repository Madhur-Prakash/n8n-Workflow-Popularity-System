#!/bin/bash

# n8n Workflow Popularity System - Cron Refresh Script
# Add to crontab: 0 2 * * * /path/to/cron_refresh.sh

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/n8n_workflows"
export YOUTUBE_API_KEY="your_youtube_api_key_here"
export API_URL="http://localhost:8000"

# Log file
LOG_FILE="/var/log/n8n-popularity-refresh.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "Starting scheduled data refresh"

# Make API call to refresh data
response=$(curl -s -X POST "$API_URL/admin/refresh" \
    -H "Content-Type: application/json" \
    -d '{"platforms": ["YouTube", "Forum", "Google"], "force": false}' \
    -w "%{http_code}")

http_code="${response: -3}"
response_body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    log "Data refresh completed successfully: $response_body"
else
    log "Data refresh failed with HTTP $http_code: $response_body"
fi

log "Scheduled refresh completed"