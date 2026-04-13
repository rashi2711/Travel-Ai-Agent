#!/bin/bash
# Minimal Health Monitor for TravelMind AI

LOG_FILE="health-check.log"
CHECK_INTERVAL=30
ALERT_THRESHOLD=3

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== TravelMind Health Monitor Started (Minimal) ==="
log "Using kubectl port-forward"
log "----------------------------------------"

failure_count=0

while true; do
  # Temporary port-forward
  kubectl port-forward service/travelmind-service 8501:80 > /dev/null 2>&1 &
  PF_PID=$!
  sleep 3

  if curl -s -f -m 5 http://127.0.0.1:8501/_stcore/health > /dev/null 2>&1; then
    log "✓ OK"
    failure_count=0
  else
    failure_count=$((failure_count + 1))
    log "✗ FAIL (consecutive: $failure_count)"
    if [ $failure_count -ge $ALERT_THRESHOLD ]; then
      log "🚨 ALERT — TravelMind appears DOWN!"
    fi
  fi

  kill $PF_PID 2>/dev/null || true
  sleep $CHECK_INTERVAL
done
