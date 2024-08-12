// this is a modified version of myDelaylib.c to implement Random Distribution delay injection method. 


#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <pthread.h>
#include "myDelaylib.h"

extern void __VERIFIER_assume(int expr);
extern pthread_t Global_refrence;
extern unsigned int __VERIFIER_delay_uint();
extern unsigned int __VERIFIER_nondet_uint();
extern pthread_mutex_t __VERIFIER_EBF_mutex;
extern void __VERIFIER_atomic_end();

size_t active_threads;
pthread_mutex_t __VERIFIER_EBF_lock_thread = PTHREAD_MUTEX_INITIALIZER;

void add_thread()
{
  pthread_mutex_lock(&__VERIFIER_EBF_lock_thread);
  active_threads++;
  pthread_mutex_unlock(&__VERIFIER_EBF_lock_thread);
}

void join_thread()
{
  pthread_mutex_lock(&__VERIFIER_EBF_lock_thread);
  active_threads--;
  pthread_mutex_unlock(&__VERIFIER_EBF_lock_thread);
}

void __Initialize_random()
{
  static char initialized = 0;
  
  if (!initialized){
    time_t t;
    srand((unsigned)time(&t));
    initialized = 1;
  }
}

int __VERIFIER_nondet_delay()
{
  __Initialize_random();
  return rand();
}

// A function that is used to decided whether to inject a delay or not based on probability (coin toss)
bool __VERIFIER_nondet_prob_delay(double threshold)
{
  __Initialize_random();
  double value = rand() / (RAND_MAX + 1.0); // random value between 0 and 1
  return value < threshold;
}

struct timespec createTimer(unsigned second, unsigned nsecond)
{
  struct timespec wait;
  //int ret;
  wait.tv_sec = second;
  wait.tv_nsec = nsecond;
  return wait;
}

void _delay_function()
{
  __VERIFIER_assume(active_threads < 1000);
  //__VERIFIER_assume(__VERIFIER_nondet_delay() % 10000);
  /**=-=-===-=-==-*=-=-==-*=-=-==-*=-=-==-*=-=-==-*-*/
  /**Fix the starvation problem */
  struct timespec wait = createTimer(15, 0);

  while (pthread_mutex_timedlock(&__VERIFIER_EBF_mutex, &wait))
  {
    printf("we are inside\n");
    //__VERIFIER_assume(__VERIFIER_nondet_delay() % 10000);
  }
  printf("we are outside\n");

  pthread_mutex_unlock(&__VERIFIER_EBF_mutex);

  /**=-=-===-=-==-*=-=-==-*=-=-==-*=-=-==-*=-=-==-*-*/

  // Injecting delay based on probabiltiy .
  if (__VERIFIER_nondet_prob_delay(0.1)) //50:50 = .5 || 90:10 = .9 || 10:90 = .1
  {
    int delay_ms = rand() % 100; // directly use rand() since RNG is already initialized.
    struct timespec r = createTimer(0, delay_ms * 1000);
    printf("Test delayFunction");
    nanosleep(&r, NULL);
  }
}




