// this is a modified version of myDelaylib.h to implement Random Distribution delay injection method. 

#ifndef MY_DELAY_LIB_H
#define MY_DELAY_LIB_H
#include <stdbool.h>
/**
 * @brief Increases the counter of active threads by 1.
 * This function is thread-safe.
 */
void add_thread();

/**
 * @brief Decreases the counter of active threads by 1.
 * This function is thread-safe.
 */
void join_thread();

/**
 * @brief Runs the delay logic based on internal criteria which may include probabilistic elements.
 * Ensure that the random number generator is initialized before calling this function.
 */
void _delay_function();

/**
 * @brief Decides whether to inject a delay based on a probability threshold.
 * @param threshold The probability threshold as a float where 0.0 means no delay and 1.0 means always delay.
 * @return Non-zero if a delay is to be injected, zero otherwise.
 */
bool __VERIFIER_nondet_prob_delay(double threshold);

#endif // MY_DELAY_LIB_H

