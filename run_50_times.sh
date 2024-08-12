#!/bin/bash

PYTHON_SCRIPT="./scripts/RunEBF.py"

PYTHON_ARGS="-a 32 -p property-file/reach benchmarks/pthread/singleton.c"

# Initialize variables to store total time and total time squared
total_time=0
total_time_squared=0

# Initialize counters for different types of results
false_count=0

unknown_count=0

# Record the overall start time
overall_start_time=$(date +%s.%N)

# Loop 50 times
for i in {1..50}
do
    echo "Running iteration $i"
    
    # Measure the time taken to execute the Python script
    start_time=$(date +%s.%N)
    result=$($PYTHON_SCRIPT $PYTHON_ARGS) #this one is different maybe this is why script is notshowing (its puting the script into resutls in the other bash file)
    end_time=$(date +%s.%N)

    # Capture the output and increment counters based on it
    if [[ "$result" == *"False"* ]]; then
        ((false_count++))
   
    elif [[ "$result" == *"UNKNOWN"* ]]; then
        ((unknown_count++))
    fi

    # Calculate the elapsed time for this iteration
    elapsed=$(echo "$end_time - $start_time" | bc -l 2>/dev/null)
    echo "Iteration $i took $elapsed seconds"

    # Add the elapsed time to the total time and total time squared
    total_time=$(echo "$total_time + $elapsed" | bc -l 2>/dev/null)
    total_time_squared=$(echo "$total_time_squared + ($elapsed * $elapsed)" | bc -l 2>/dev/null)
done

# Record the overall end time
overall_end_time=$(date +%s.%N)

# Calculate the total elapsed time for all iterations
total_elapsed_time=$(echo "$overall_end_time - $overall_start_time" | bc -l 2>/dev/null)

# Calculate the mean
mean=$(echo "$total_time / 50" | bc -l 2>/dev/null)

# Calculate the standard deviation
mean_squared=$(echo "$total_time_squared / 50" | bc -l 2>/dev/null)
variance=$(echo "$mean_squared - ($mean * $mean)" | bc -l 2>/dev/null)
std_dev=$(echo "sqrt($variance)" | bc -l 2>/dev/null)

# Output results
echo "Total execution time for all iterations: $total_elapsed_time seconds"
echo "Mean execution time: $mean seconds"
echo "Standard deviation of execution time: $std_dev seconds"
echo "Number of 'False(reach)' results: $false_count"
echo "Number of 'UNKNOWN' results: $unknown_count"

