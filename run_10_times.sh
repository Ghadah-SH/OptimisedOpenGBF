#!/bin/bash


PYTHON_SCRIPT="./scripts/RunEBF.py"


PYTHON_ARGS="-a 32 -p property-file/reach benchmarks/pthread/sigma.c"

# Initialize variables to store total time and total time squared
total_time=0
total_time_squared=0

# Record the overall start time
overall_start_time=$(date +%s.%N)

# Loop 10 times
for i in {1..10}
do
    echo "Running iteration $i"
    
    # Measure the time taken to execute the Python script
    start_time=$(date +%s.%N)
    $PYTHON_SCRIPT $PYTHON_ARGS
    end_time=$(date +%s.%N)

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
mean=$(echo "$total_time / 10" | bc -l 2>/dev/null)

# Calculate the standard deviation
mean_squared=$(echo "$total_time_squared / 10" | bc -l 2>/dev/null)
variance=$(echo "$mean_squared - ($mean * $mean)" | bc -l 2>/dev/null)
std_dev=$(echo "sqrt($variance)" | bc -l 2>/dev/null)

echo "Total execution time for all iterations: $total_elapsed_time seconds"
echo "Mean execution time: $mean seconds"
echo "Standard deviation of execution time: $std_dev seconds"

