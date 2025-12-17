#!/bin/bash

# Check if PID is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <PID>"
    exit 1
fi

PID="$1"

wait_interval=1
k_iterations=10

# Check if PID exists at the start
if ! kill -0 "$PID" 2>/dev/null; then
    echo "[$(date)] Process $PID not found."
    exit 1
fi

# Loop until process dies
while kill -0 "$PID" 2>/dev/null; do
    echo "[$(date)] Killing process: $PID"
    kill "$PID" 2>/dev/null
    for i in {1..${k_iterations}}; do
        echo "[$(date)] Sleeping ${wait_interval} ..."
        sleep ${wait_interval}
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "[$(date)] Process $PID terminated."
            exit 0
        fi
        echo "[$(date)] Process $PID is still alive."
    done
done

echo "[$(date)] Process $PID terminated."

p_pids=$(pgrep -x python)
if [ -n "$p_pids" ]; then
    count=$(echo "$p_pids" | wc -l)
    echo "[$(date)] WARNING: $count Python process(es) still running. PIDs:"
    echo "$p_pids"
fi

