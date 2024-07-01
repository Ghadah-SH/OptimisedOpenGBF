#!/bin/bash

# Log file location
LOGFILE="/home/ghada/Improved_EBF2/logfile.log"

# Header for the log file
echo "Timestamp, %CPU, %MEM, Free Memory, Buffer/Cache" > $LOGFILE

# Interval in seconds between each measurement
INTERVAL=5

# Duration in seconds for how long the script should run
DURATION=600

# Calculate end time
END_TIME=$((SECONDS + DURATION))

while [ $SECONDS -lt $END_TIME ]; do
    # Capture CPU and memory usage using top (adjust field numbers as necessary)
    USAGE=$(top -b -n 1 | awk '/^%Cpu\(s\)/{print $2+$4","$10} /^MiB Mem/{print $6","$8}')
    
    # Write to log with timestamp
    echo "$(date +'%Y-%m-%d %H:%M:%S'),$USAGE" >> $LOGFILE
    
    # Sleep before next measurement
    sleep $INTERVAL
done

