#!/usr/bin/env bash

echo "Looking for auto_switch.sh processes..."
ps aux | grep auto_switch.sh | grep -v grep
echo ""

pids=$(pgrep -f "auto_switch.sh")
if [[ -n "$pids" ]]; then
    echo "Killing processes: $pids"
    kill $pids
    echo "Done."
else
    echo "No auto_switch.sh processes found."
fi
