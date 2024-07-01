// This is an enhanced version of myDelaylib.c
// This file contains selective delay injection + delay value optimization.

#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include "myDelaylib.h"
#include "system_metrics.h"

extern void __VERIFIER_assume(int expr);
extern pthread_t Global_refrence;
extern unsigned int __VERIFIER_delay_uint();
extern unsigned int __VERIFIER_nondet_uint();
extern pthread_mutex_t __VERIFIER_EBF_mutex;
extern void __VERIFIER_atomic_end();

size_t active_threads = 0;
pthread_mutex_t __VERIFIER_EBF_lock_thread = PTHREAD_MUTEX_INITIALIZER;

void add_thread() {
    if (pthread_mutex_lock(&__VERIFIER_EBF_lock_thread) != 0) {
        printf("Error handling in add_thread: \n");
        return; // Early return on error 
    }
    active_threads++;
    printf("Active threads incremented: %zu\n", active_threads); // Debugging
    if (pthread_mutex_unlock(&__VERIFIER_EBF_lock_thread) != 0) {
        printf("Error handling in add_thread unlocking:\n");
    }
}

void join_thread() {
    if (pthread_mutex_lock(&__VERIFIER_EBF_lock_thread) != 0) {
        printf("Error locking in join_thread: \n");
        return; // Early return on error 
    }
    active_threads--;
    printf("Active threads decremented: %zu\n", active_threads); // Debugging
    if (pthread_mutex_unlock(&__VERIFIER_EBF_lock_thread) != 0) {
        printf("Error unlocking in join_thread: \n");
    }
}

struct timespec createTimer(unsigned second, unsigned nsecond) {
    struct timespec wait;
    wait.tv_sec = second;
    wait.tv_nsec = nsecond;
    return wait;
}

// Global or static variable to adjust delay factor based on feedback
static double delay_adjustment_factor = 1.0;

void update_delay_adjustment_factor(double current_response_time, double target_response_time) {
    if (current_response_time > target_response_time) {
        delay_adjustment_factor *= 0.9;  // Reduce the delay factor by 10%
    } else {
        delay_adjustment_factor *= 1.1;  // Increase the delay factor by 10%, up to a limit
        if (delay_adjustment_factor > 1.0) {
            delay_adjustment_factor = 1.0;
        }
    }
}

int calculate_delay() {
    double cpu_usage = get_cpu_usage(); 
    double memory_usage = get_memory_usage(); 
    int thread_count = get_thread_count(); 

    int base_delay_ms = 100;
    int cpu_based_delay = (int)(cpu_usage * 0.5);
    int memory_based_delay = (int)(memory_usage * 0.3);
    int thread_based_delay = thread_count * 5;

    int total_delay_ms = base_delay_ms + cpu_based_delay + memory_based_delay - thread_based_delay; 
    total_delay_ms = (total_delay_ms > 10) ? total_delay_ms : 10; // Ensure a minimum delay

    const int max_delay_ms = 500;  // Maximum allowable delay
    if (total_delay_ms > max_delay_ms) {
        total_delay_ms = max_delay_ms;
    }

    return total_delay_ms;
}

void insert_dynamic_delay() {
    int total_delay_ms = calculate_delay();
    printf("Dynamic Delay: CPU %f%%, Memory: %f%%, Threads: %d, Delay: %d ms\n", get_cpu_usage(), get_memory_usage(), get_thread_count(), total_delay_ms);
    usleep(total_delay_ms * 1000); // Convert ms to microseconds
}

int calculate_additional_delay() {
    double cpu_usage = get_cpu_usage();
    return (int)(100000 - cpu_usage * 1000); // This creates a smaller delay when CPU usage is high
}

void _delay_function() {
    insert_dynamic_delay(); // Use the dynamic delay function

    struct timespec wait = createTimer(15, 0);

    while (pthread_mutex_timedlock(&__VERIFIER_EBF_mutex, &wait)) { 
        printf("Inside delay function: potential resource contention or deadlock \n");
    }
    printf("Outside delay function: mutex acquired successfully \n");

    int additional_delay_ns = calculate_additional_delay();
    struct timespec r = createTimer(0, additional_delay_ns);
    printf("Nanosleep delay: %ld ns\n", r.tv_nsec);
    nanosleep(&r, NULL);
}

