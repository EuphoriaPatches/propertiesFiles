#!/bin/bash
WORKFLOWS=("process-properties-files.yml" "sort-addedMod-table-and-timestamp.yml")
STATUSES=("queued" "in_progress" "waiting" "pending")
TIMEOUT_SECONDS=1800
POLL_SECONDS=15

# Give runs triggered by the same push a moment to show up as queued
sleep 15

START=$(date +%s)
while true; do
  BUSY=""
  for wf in "${WORKFLOWS[@]}"; do
    for status in "${STATUSES[@]}"; do
      COUNT=$(gh run list --repo "$GITHUB_REPOSITORY" --workflow "$wf" --status "$status" --json databaseId --jq 'length' || echo 0)
      if [ "${COUNT:-0}" -gt 0 ]; then
        BUSY="$BUSY $wf($status:$COUNT)"
      fi
    done
  done

  if [ -z "$BUSY" ]; then
    echo "No other workflows are running, continuing."
    exit 0
  fi

  if [ $(( $(date +%s) - START )) -ge $TIMEOUT_SECONDS ]; then
    echo "ERROR: Timed out after ${TIMEOUT_SECONDS}s waiting for:$BUSY"
    exit 1
  fi

  echo "Waiting for:$BUSY"
  sleep $POLL_SECONDS
done
